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
- Ubuntu 仓库安装的 root 通常使用 auth_socket，可用 sudo mysql 登录；以实际账号认证插件为准

---

## 二、WSL2 专属服务命令（重点）

> 现代 WSL 支持 systemd。先执行 `ps -p 1 -o comm=`：PID 1 为 systemd 时可用 `sudo systemctl start mysql`、`sudo systemctl enable mysql`；未启用时使用下面的 service 命令。

```bash
sudo service mysql start
sudo service mysql stop
sudo service mysql restart
sudo service mysql status
```

- 启用 systemd 后，已 enable 的服务可随 WSL 发行版启动；这不等于 Windows 开机自动启动 WSL。
- 同一个 WSL 实例新开终端不会停止已有 MySQL，无需每次重复 start。

---

## 三、正常环境：修改 root 密码（正规标准方式）

**适用于**：刚安装、环境正常、没弄坏数据库

1. 免密登录 MySQL

```bash
sudo mysql
```

2. 保留 Ubuntu 的 root socket 管理方式，为应用创建专用账号（以下适用于 MySQL 8.0/8.4）：

```sql
CREATE DATABASE IF NOT EXISTS testdb CHARACTER SET utf8mb4;
CREATE USER 'app_user'@'localhost' IDENTIFIED WITH caching_sha2_password BY '替换为强密码';
GRANT SELECT, INSERT, UPDATE, DELETE ON testdb.* TO 'app_user'@'localhost';
```

Java 使用兼容的 Connector/J，无需强制改为 mysql_native_password。该旧插件在 8.4 默认禁用，9.0 移除。

---

## 四、MySQL 核心文件路径

1. 主配置文件夹

```
/etc/mysql/mysql.conf.d/
```

2. 主配置文件

```
/etc/mysql/mysql.conf.d/mysqld.cnf
```

3. 发行版维护配置（旧版本可能存在）

`/etc/mysql/debian.cnf` 的内容取决于发行版和安装版本，不能假设一定保存了可用的 debian-sys-maint 账号密码。

---

## 五、无法登录时的恢复思路

先尝试 `sudo mysql`。如果 root 使用 auth_socket，这依赖系统用户身份，不等于数据库对任意用户开放空密码登录。旧版维护账号只有在实际存在且拥有相应权限时才可用于恢复。

若仍无法登录，按 [MySQL 官方密码重置流程](https://dev.mysql.com/doc/refman/8.0/en/resetting-permissions.html) 操作：停止正常实例，使用相同配置和数据目录启动隔离的临时实例，在本地重置密码，停止临时实例，再启动正常服务。不能把 --skip-grant-tables 传给 mysql 客户端。

---

## 六、SpringBoot 连接配置（WSL 专用）

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/testdb?useSSL=false&serverTimezone=Asia/Shanghai
    username: app_user
    password: ${DB_PASSWORD}
```

- 应用与 MySQL 都在同一 WSL 实例时，可用 127.0.0.1。
- Windows 访问 WSL 中的 MySQL 通常可用 localhost 转发；失败时核对 WSL 网络模式、监听地址、端口冲突及防火墙。
- Docker 容器或其他电脑访问 WSL 时，应按实际路由和来源配置监听、账号权限与防火墙，不能一概认为无需配置。

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

- `host='localhost'`：只允许本机访问（WSL本地开发推荐，安全）
- `host='%'`：百分号代表允许任意IP连接该账号，生产环境 `root` 禁止设置为 `%`

**不要直接 UPDATE mysql.user 修改账号主机范围**。使用账号管理语句，并先确认目标账号不存在，避免覆盖已有的 root@localhost。

**修改账号主机范围：`RENAME USER`（无需 FLUSH PRIVILEGES）**

```sql
RENAME USER 'root'@'%' TO 'root'@'localhost';
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
> 远程连接需要：监听可达的网卡地址、路由及防火墙放行、匹配客户端来源的 MySQL 账号及正确凭据。不必监听全部网卡，也不必把账号 host 设为 `%`。

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

## 十、关键区分与常见排查

1. `sudo mysql` 常使用 auth_socket 管理身份，应用另建最小权限账号。
2. systemctl 是否可用取决于 WSL 是否启用 systemd；未启用时可使用 service。
3. 连接失败先检查服务、监听端口、网络与账号来源，再检查 JDBC 驱动及认证。
4. debian.cnf 不是所有 Ubuntu 版本都可用的密码恢复入口。

参考：[WSL 的 systemd 支持](https://learn.microsoft.com/en-us/windows/wsl/systemd)。

---

## 十二、`FLUSH PRIVILEGES` 使用原则

- `CREATE USER`、`ALTER USER`、`RENAME USER`、`GRANT`、`REVOKE` 会即时更新权限，无需额外执行 FLUSH PRIVILEGES，MySQL 5.7/8.0 都如此。
- 正常管理使用账号语句，不直接修改 mysql.user 等权限系统表。
- 临时以 `--skip-grant-tables` 启动后，重置密码前执行 FLUSH PRIVILEGES，随后 ALTER USER，并停止临时实例、恢复正常服务。

参考：[MySQL 权限生效规则](https://dev.mysql.com/doc/refman/8.0/en/privilege-changes.html)、[认证插件版本说明](https://dev.mysql.com/doc/refman/8.4/en/native-pluggable-authentication.html)。
