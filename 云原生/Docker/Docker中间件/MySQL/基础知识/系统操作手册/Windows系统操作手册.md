# Windows MySQL 操作手册【最终完整版】

**适配**：Windows 10/11 + SpringBoot 本地开发  
**包含**：标准正规流程 + 忘记 root 密码抢救流程 + 端口、host 账号、bind-address 配置知识点

---

## 一、安装 MySQL（Windows 标准流程）

1. 访问 MySQL 官网下载 **MySQL Community Server**（推荐使用 `.msi` 安装包）：  
   https://dev.mysql.com/downloads/mysql/

2. 运行安装程序，选择 **Developer Default** 或 **Server only**（本地开发建议 Developer Default，包含常用工具）。

3. 在 **Type and Networking** 步骤：
   - 保持默认端口 `3306`
   - 勾选 **TCP/IP** 并确保端口为 `3306`
   - 选择 **Open Windows Firewall port for network access**（可选，本地开发可不勾）

4. 在 **Authentication Method** 步骤：
   - **必须选择** `Use Legacy Authentication Method (Retain MySQL 5.x Compatibility)`  
     这是因为 Java 的 JDBC 驱动（尤其是旧版）需要使用 `mysql_native_password` 插件。

5. 在 **Accounts and Roles** 步骤：
   - 设置 `root` 密码（例如 `Root@123456`），牢记该密码。
   - 可以添加一个普通用户（可选）。

6. 在 **Windows Service** 步骤：
   - 确保勾选 **Configure MySQL Server as a Windows Service**
   - 服务名称默认为 `MySQL`（或带版本号如 `MySQL80`），可自定义，后续服务管理需要使用。
   - 建议勾选 **Start the MySQL Server at System Startup**（可选，本地开发可不勾）

7. 完成安装，确保服务已启动。

> [!TIP]
> 如果安装时忘记选择 Legacy Authentication，后续可通过命令行修改认证插件，见第三节。

---

## 二、Windows 专属服务命令（重点）

> Windows 中 MySQL 作为系统服务运行，可通过命令行或图形界面管理。

### 1. 命令行（以管理员身份运行 CMD 或 PowerShell）

假设服务名称为 `MySQL`（根据安装时设置，可能为 `MySQL80` 等，可通过 `services.msc` 查看）。

```cmd
net start MySQL        # 启动服务
net stop MySQL         # 停止服务
net restart MySQL      # 无效，需分别执行 stop 和 start
```

也可使用 PowerShell：

```powershell
Start-Service MySQL
Stop-Service MySQL
Restart-Service MySQL
```

### 2. 图形界面

- 按 `Win + R` 输入 `services.msc` 打开服务管理器。
- 找到 MySQL 服务，右键可启动/停止/重启。

> [!WARNING]
> 若安装时未设置为开机自启，每次开机后需手动启动服务（或设置为自动启动）。

---

## 三、正常环境：修改 root 密码（正规标准方式）

**适用于**：已安装、可正常登录，但需要修改密码或调整认证插件。

1. 打开命令行（以管理员身份运行 CMD 或 PowerShell），输入：

```cmd
mysql -u root -p
```

输入当前密码登录。

2. 查看当前认证插件：

```sql
SELECT user, host, plugin FROM mysql.user WHERE user='root';
```

如果 `plugin` 不是 `mysql_native_password`，执行以下命令修改：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root@123456';
FLUSH PRIVILEGES;
exit;
```

> [!TIP]
> 密码根据自己需求设置，此处示例为 `Root@123456`。

---

## 四、MySQL 核心文件路径（配置文件）

1. 主配置文件（Windows 下通常为 `my.ini` 或 `my.cnf`）：

   路径取决于安装方式：
   - **默认安装（MSI）**：`C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
   - **自定义安装**：可在安装目录下查找，如 `C:\Program Files\MySQL\MySQL Server 8.0\my.ini`
   - **便携版/解压版**：解压目录下的 `my.ini`（如无则需自行创建）

2. 数据目录（存放数据库文件）：

   默认路径：`C:\ProgramData\MySQL\MySQL Server 8.0\Data\`

3. 日志文件：

   错误日志通常位于数据目录中，如 `C:\ProgramData\MySQL\MySQL Server 8.0\Data\hostname.err`

> [!NOTE]
> 修改配置文件后必须重启 MySQL 服务才能生效。

---

## 五、忘记 root 密码的抢救流程（Windows 版）

**使用场景**  
当忘记 `root` 密码、或者因修改错误导致无法登录时使用（正常情况不用，是修复手段）。

### 方法一：使用 `--skip-grant-tables` 启动服务器（推荐）

1. 停止 MySQL 服务：

   ```cmd
   net stop MySQL
   ```

2. 以管理员身份打开一个新的 CMD 窗口，进入 MySQL 的 `bin` 目录（例如 `C:\Program Files\MySQL\MySQL Server 8.0\bin`），执行：

   ```cmd
   mysqld --console --skip-grant-tables --shared-memory
   ```

   > 该命令会启动一个临时的 MySQL 服务器，跳过权限检查。窗口保持打开，不要关闭。

3. 另开一个管理员 CMD 窗口，无密码登录：

   ```cmd
   mysql -u root
   ```

4. 登录成功后重置密码：

   ```sql
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root@123456';
   FLUSH PRIVILEGES;
   exit;
   ```

5. 关闭步骤 2 中的 `mysqld` 窗口（或按 Ctrl+C），然后正常启动 MySQL 服务：

   ```cmd
   net start MySQL
   ```

6. 使用新密码验证登录。

### 方法二：使用初始化文件（`init_file`）

1. 创建一个文本文件（如 `C:\mysql-init.txt`），内容为：

   ```
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root@123456';
   ```

2. 停止 MySQL 服务。

3. 以管理员身份运行：

   ```cmd
   mysqld --init-file=C:\mysql-init.txt --console
   ```

   等待服务器启动并执行初始化文件后，按 Ctrl+C 停止。

4. 正常启动服务，使用新密码登录。

> [!WARNING]
> 抢救过程中请确保没有其他程序占用 MySQL 端口，且操作完成后务必关闭临时启动的服务器进程。

---

## 六、SpringBoot 连接配置（Windows 专用）

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/testdb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: Root@123456
```

- Windows 本地开发使用 `127.0.0.1` 或 `localhost` 即可。
- 无需修改 `bind-address`（除非需要外部访问）。
- 确保 Windows 防火墙允许 3306 端口（若本地程序访问一般无需特别设置）。

---

## 七、常用数据库命令

```sql
SHOW DATABASES;
CREATE DATABASE 库名;
USE 库名;
SHOW TABLES;
exit;
```

> [!TIP]
> **提示**：`FLUSH PRIVILEGES;` 不属于日常查询命令，仅修改账号/权限时才执行，不要随便敲。

### 📌 1. 查看端口相关变量

```sql
show variables like '%port%';
```

- `port=3306`：业务程序、JDBC、普通客户端连接端口（日常使用）
- `mysqlx_port=33060`：X-API文档协议端口，普通开发不用
- `admin_port=33062`：管理员故障抢救端口，业务程序不使用

> [!WARNING]
> ⚠️ SpringBoot连接填写端口固定写 `3306`，不要填 `33060` 或 `33062`，填错会连不上数据库。

### 📌 2. 查看账号允许登录 IP（host）

```sql
select user, host from mysql.user where user='root';
```

- `host='localhost'`：只允许本机访问（Windows本地开发推荐，安全）
- `host='%'`：百分号代表允许任意IP连接该账号，生产环境 `root` 禁止设置为 `%`

**方式1：直接更新系统表（旧写法，必须 `FLUSH PRIVILEGES`）**

```sql
update mysql.user set host='localhost' where user='root';
FLUSH PRIVILEGES;
```

**方式2：`ALTER USER` 官方语法（MySQL 8 推荐，不需要强制 `FLUSH`）**

```sql
ALTER USER 'root'@'%' RENAME TO 'root'@'localhost';
```

### 📌 3. bind-address 监听IP配置

配置文件 `my.ini`（或 `my.cnf`）中查找或添加：

```ini
[mysqld]
bind-address        = 127.0.0.1
mysqlx-bind-address = 127.0.0.1
```

- `127.0.0.1`：仅本机访问（Windows本地开发默认、推荐），外部设备无法连接。
- `0.0.0.0`：监听全部网卡，允许其他机器访问。

> [!NOTE]
> ✨ 外部机器访问数据库两个条件必须同时成立：
> 1. `bind-address` 设置为 `0.0.0.0`
> 2. 数据库账号 `host='%'`，允许任意IP登录

修改配置后，**一定要重启服务才生效**：

```cmd
net stop MySQL
net start MySQL
```

命令行快速查看运行时生效值，不用打开配置文件：

```sql
show variables like 'bind_address';
```

💡 **两层关卡逻辑**：
1. `bind-address`：MySQL服务接收哪个网卡来的连接（操作系统网络层面）
2. 用户表 `host` 字段：MySQL账号允许哪个IP登录（数据库权限层面）

两层全部放行，外部机器才可以连接数据库。

---

## 八、备份与恢复

**备份**（在 CMD 或 PowerShell 中执行）

```cmd
mysqldump -uroot -p 库名 > C:\备份路径\备份名.sql
```

**恢复**

```cmd
# 恢复前需要先手动创建目标数据库
mysql -uroot -p 库名 < C:\备份路径\备份名.sql
```

> [!TIP]
> 若 `mysqldump` 或 `mysql` 命令无法识别，请将 MySQL 的 `bin` 目录添加到系统环境变量 PATH 中，或使用完整路径执行。

---

## 九、安全脚本（可选）

Windows 安装时通常已引导完成基本安全设置。若需再次运行安全脚本，可使用：

```cmd
mysql_secure_installation
```

该命令会引导设置密码强度、移除匿名用户、禁止 root 远程登录等。

---

## 十、关键区分（考试 + 面试 + 上课必懂）

1. **正常安装** → 安装时设置密码，安装后使用 `mysql -u root -p` 登录管理（正规方式）
2. **忘记 root 密码** → 使用 `--skip-grant-tables` 或初始化文件抢救（修复方式）
3. Windows 服务管理使用 `net start/stop` 或 `services.msc`，不使用 `systemctl`
4. 本地开发默认 `bind-address=127.0.0.1`，不需要修改为 `0.0.0.0`
5. `FLUSH PRIVILEGES`：使用 `ALTER USER`、`GRANT` 等官方语句时，MySQL 8.0 可自动刷新，但建议加上；直接修改 `mysql.user` 系统表时必须执行。

---

## 十一、常见报错解决

1. `'mysql' 不是内部或外部命令`  
   → 将 MySQL 的 `bin` 目录（如 `C:\Program Files\MySQL\MySQL Server 8.0\bin`）添加到系统环境变量 `Path` 中。

2. Java 连接报错 `Client does not support authentication protocol requested by server`  
   → 需要将用户认证插件改为 `mysql_native_password`，见第三节。

3. `Can't connect to MySQL server on 'localhost' (10061)`  
   → MySQL 服务未启动，使用 `net start MySQL` 启动服务。

4. 忘记 root 密码无法登录  
   → 使用第五节抢救流程重置密码。

5. 修改配置后不生效  
   → 确认修改的是正确的配置文件，并重启了 MySQL 服务。

---

## 十二、`FLUSH PRIVILEGES` 使用原则

- **什么时候必须写**：当你直接使用 `UPDATE`、`INSERT`、`DELETE` 修改 `mysql.user` 或 `mysql.db` 等系统权限表时，**必须**执行 `FLUSH PRIVILEGES;` 才能使更改生效。
- **什么时候可以不写（但建议写上）**：使用 `ALTER USER`、`CREATE USER`、`GRANT`、`REVOKE` 等官方语句时，MySQL 8.0 会自动刷新权限缓存，理论上可以省略。但为了兼容旧版本（如 MySQL 5.7）并避免遗忘，**习惯性加上是最稳妥的做法**。
- **一句话记忆**：凡是对用户权限做了修改，就在后面跟一句 `FLUSH PRIVILEGES;`，版本兼容，万无一失。

---
