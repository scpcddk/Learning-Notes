# WSL2-Ubuntu MySQL 操作手册【最终完整版】

**适配**：Windows WSL2 + SpringBoot 本地开发  
**包含**：标准正规流程 + 网课 `debian.cnf` 抢救流程 + 端口、host账号、bind-address 配置知识点

---

## 一、安装 MySQL（WSL2 标准流程）

```bash
sudo apt update
sudo apt install mysql-server -y
```

- WSL安装 **不会** 弹出密码设置
- `root` 默认无密码，使用系统权限登录

---

## 二、WSL2 专属服务命令（重点）

> WSL 禁止使用 `systemctl`，全部用 `service`！

```bash
sudo service mysql start
sudo service mysql stop
sudo service mysql restart
sudo service mysql status
```

- WSL 无开机自启
- 每次新开终端必须执行 `start`

---

## 三、正常环境：修改 root 密码（正规标准方式）

**适用于**：刚安装、环境正常、没弄坏数据库

1. 免密登录 MySQL

```bash
sudo mysql
```

2. 设置可被 Java/SpringBoot 识别的密码

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root@123456';
FLUSH PRIVILEGES;
exit;
```

> [!TIP]
> 必须使用 `mysql_native_password`，否则 Java 连不上。

---

## 四、MySQL 核心文件路径（网课讲的配置文件）

1. 主配置文件夹

```
/etc/mysql/mysql.conf.d/
```

2. 主配置文件

```
/etc/mysql/mysql.conf.d/mysqld.cnf
```

3. 抢救专用文件

```
/etc/mysql/debian.cnf
```
> [!TIP]
> 这个文件就是“查看默认账号密码”文件

---

## 五、`debian.cnf` 抢救登录法

**使用场景**  
当你 `root` 密码乱改、锁住、`sudo mysql` 进不去时使用（正常情况不用，是修复手段）。

1. 查看系统隐藏维护账号密码

```bash
sudo cat /etc/mysql/debian.cnf
```

可以看到固定账号：

- `user`：`debian-sys-maint`
- `password`：一串自动生成的密码

2. 登录 MySQL

```bash
mysql -u debian-sys-maint -p
```

粘贴刚刚看到的密码。

3. 登录成功后重置 `root` 密码

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root@123456';
FLUSH PRIVILEGES;
exit;
```

> [!WARNING]
> `debian.cnf` 文件绝对不要手动修改！只允许查看！

---

## 六、SpringBoot 连接配置（WSL 专用）

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/testdb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: Root@123456
```

- WSL2 直接用 `127.0.0.1`
- 不需要改 `bind-address=0.0.0.0`
- 不需要防火墙
- 不需要查看 WSL IP

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

- `host='localhost'`：只允许本机访问（WSL本地开发推荐，安全）
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

配置文件 `/etc/mysql/mysql.conf.d/mysqld.cnf`

```ini
bind-address        = 127.0.0.1
mysqlx-bind-address = 127.0.0.1
```

- `127.0.0.1`：仅本机访问（WSL本地开发默认、推荐），外部设备无法连接。
- `0.0.0.0`：监听全部网卡，允许其他机器访问。

> [!NOTE]
> ✨ 外部机器访问数据库两个条件必须同时成立：
> 1. `bind-address` 设置为 `0.0.0.0`
> 2. 数据库账号 `host='%'`，允许任意IP登录

修改配置后，**一定要重启服务才生效**：

```bash
sudo service mysql restart
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

**备份**

```bash
mysqldump -uroot -p 库名 > ~/备份名.sql
```

**恢复**

```bash
# 恢复前需要先手动创建目标数据库
mysql -uroot -p 库名 < ~/备份名.sql
```

---

## 九、安全脚本（可选）

本地学习不用，服务器必须用。

```bash
sudo mysql_secure_installation
```

---

## 十、关键区分（考试 + 面试 + 上课必懂）

1. **正常安装** → 使用 `sudo mysql` 登录改密码（正规方式）
2. **弄坏 root 密码** → 使用网课 `debian.cnf` 方式抢救（修复方式）
3. WSL 永远不用 `systemctl`
4. 本地开发永远不用改 `0.0.0.0`
5. `FLUSH PRIVILEGES`：使用 `ALTER USER`、`GRANT` 等官方语句时，MySQL 8.0 可自动刷新，但建议加上；直接修改 `mysql.user` 系统表时必须执行。

---

## 十一、常见报错解决

1. `systemd not supported`  
   → 不用 `systemctl`，全部用 `service`

2. Java 连接不上  
   → 必须设置 `mysql_native_password`

3. `root` 拒绝登录  
   → 用上面网课 `debian-sys-maint` 方式重置

---

## 十二、`FLUSH PRIVILEGES` 使用原则

- **什么时候必须写**：当你直接使用 `UPDATE`、`INSERT`、`DELETE` 修改 `mysql.user` 或 `mysql.db` 等系统权限表时，**必须**执行 `FLUSH PRIVILEGES;` 才能使更改生效。
- **什么时候可以不写（但建议写上）**：使用 `ALTER USER`、`CREATE USER`、`GRANT`、`REVOKE` 等官方语句时，MySQL 8.0 会自动刷新权限缓存，理论上可以省略。但为了兼容旧版本（如 MySQL 5.7）并避免遗忘，**习惯性加上是最稳妥的做法**。
- **一句话记忆**：凡是对用户权限做了修改，就在后面跟一句 `FLUSH PRIVILEGES;`，版本兼容，万无一失。

---
