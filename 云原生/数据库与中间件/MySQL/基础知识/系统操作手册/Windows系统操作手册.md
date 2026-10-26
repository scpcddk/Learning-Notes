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
   - 优先采用当前版本默认的强认证方式（如 caching_sha2_password），并使用兼容的 Connector/J。MySQL 8.4 默认禁用 mysql_native_password，9.0 已移除，不能把 Legacy Authentication 作为 Java 的必需项。

5. 在 **Accounts and Roles** 步骤：
   - 设置 `root` 密码（例如 `Root@123456`），牢记该密码。
   - 可以添加一个普通用户（可选）。

6. 在 **Windows Service** 步骤：
   - 确保勾选 **Configure MySQL Server as a Windows Service**
   - 服务名称默认为 `MySQL`（或带版本号如 `MySQL80`），可自定义，后续服务管理需要使用。
   - 建议勾选 **Start the MySQL Server at System Startup**（可选，本地开发可不勾）

7. 完成安装，确保服务已启动。

> [!TIP]
> 安装器界面随版本不同；遇到认证错误先核对驱动和服务器版本，见第三节。

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

修改密码时保留兼容的认证方式；MySQL 8.0/8.4 可明确使用 caching_sha2_password：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'Root@123456';
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
   mysqld --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" --console --skip-grant-tables --shared-memory
   ```

   > 该命令会启动一个临时的 MySQL 服务器，跳过权限检查。窗口保持打开，不要关闭。

3. 另开一个管理员 CMD 窗口，通过共享内存连接（跳过授权表时 TCP 默认被禁用）：

   ```cmd
   mysql --protocol=MEMORY -u root
   ```

4. 登录成功后重置密码：

   ```sql
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'Root@123456';
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
   ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'Root@123456';
   ```

2. 停止 MySQL 服务。

3. 以管理员身份运行：

   ```cmd
   mysqld --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" --init-file=C:\mysql-init.txt --console
   ```

   等待服务器启动并执行初始化文件后，按 Ctrl+C 停止。

4. 正常启动服务，使用新密码登录。

> [!WARNING]
> 示例 my.ini 路径须替换为实际服务所用路径，--defaults-file 必须是第一个选项。操作完成后停止临时进程、删除含密码的初始化文件，再启动正常服务。

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
> **提示**：正常执行 CREATE USER、ALTER USER、GRANT、REVOKE 后无需 FLUSH PRIVILEGES。跳过授权表重置密码等特殊流程才需要。

### 📌 1. 查看端口相关变量

```sql
show variables like '%port%';
```

- `port=3306`：业务程序、JDBC、普通客户端连接端口（日常使用）
- `mysqlx_port=33060`：MySQL X Protocol 端口，普通开发不用
- `admin_port=33062`：管理接口端口默认值，只有配置了 admin_address 等条件时才监听

> [!WARNING]
> Spring Boot 的普通 JDBC URL 使用 MySQL classic protocol 的实际监听或映射端口，默认是 3306，可能被修改；33060 通常是 X Protocol 端口。

### 📌 2. 查看账号允许登录 IP（host）

```sql
select user, host from mysql.user where user='root';
```

- `host='localhost'`：只允许本机访问（Windows本地开发推荐，安全）
- `host='%'`：百分号代表允许任意IP连接该账号，生产环境 `root` 禁止设置为 `%`

**不要直接 UPDATE mysql.user 修改账号主机范围**。使用账号管理语句，并先确认目标账号不存在，避免覆盖已有的 root@localhost。

**修改账号主机范围：`RENAME USER`（无需 FLUSH PRIVILEGES）**

```sql
RENAME USER 'root'@'%' TO 'root'@'localhost';
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
> 远程连接需要：监听可达的网卡地址、路由及防火墙放行、匹配客户端来源的 MySQL 账号及正确凭据。不必监听全部网卡，也不必把账号 host 设为 `%`。

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

**备份**（以下在 CMD 执行，避免旧版 PowerShell 重定向改变编码；也可使用 mysqldump 的 --result-file）

```cmd
mysqldump -uroot -p 库名 > C:\备份路径\备份名.sql
```

**恢复**（在 CMD 执行；PowerShell 不支持这种 `<` 输入重定向）

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
5. `FLUSH PRIVILEGES`：账号管理语句即时生效，无需额外刷新；避免直接修改权限系统表。

---

## 十一、常见报错解决

1. `'mysql' 不是内部或外部命令`  
   → 将 MySQL 的 `bin` 目录（如 `C:\Program Files\MySQL\MySQL Server 8.0\bin`）添加到系统环境变量 `Path` 中。

2. Java 连接报错 `Client does not support authentication protocol requested by server`  
   → 先检查并升级 MySQL Connector/J，核对 TLS/RSA 及账号认证配置，不应默认降级认证插件。

3. `Can't connect to MySQL server on 'localhost' (10061)`  
   → MySQL 服务未启动，使用 `net start MySQL` 启动服务。

4. 忘记 root 密码无法登录  
   → 使用第五节抢救流程重置密码。

5. 修改配置后不生效  
   → 确认修改的是正确的配置文件，并重启了 MySQL 服务。

---

## 十二、`FLUSH PRIVILEGES` 使用原则

- `CREATE USER`、`ALTER USER`、`RENAME USER`、`GRANT`、`REVOKE` 会即时更新权限，无需额外执行 FLUSH PRIVILEGES，MySQL 5.7/8.0 都如此。
- 正常管理使用账号语句，不直接修改 mysql.user 等权限系统表。
- 临时以 `--skip-grant-tables` 启动后，重置密码前执行 FLUSH PRIVILEGES，随后 ALTER USER，并停止临时实例、恢复正常服务。

参考：[MySQL 权限生效规则](https://dev.mysql.com/doc/refman/8.0/en/privilege-changes.html)、[认证插件版本说明](https://dev.mysql.com/doc/refman/8.4/en/native-pluggable-authentication.html)。
