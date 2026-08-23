# Linux 系统 MySQL 操作手册

本文档涵盖在 Linux 系统下安装、配置、管理和维护 MySQL 数据库的常用操作，适用于 Ubuntu/Debian 和 CentOS/RHEL 等主流发行版。


## 一、安装 MySQL

### 1.1 Ubuntu/Debian 系统（使用 APT）

更新包列表并安装 MySQL 服务器：

```bash
sudo apt update
sudo apt install mysql-server
```

### 1.2 CentOS/RHEL 系统（使用 YUM）

安装 MySQL 社区版：

```bash
sudo yum install mysql-server
```

如需安装特定版本，可先添加官方 YUM 仓库：

```bash
sudo rpm -ivh mysql80-community-release-el7-3.noarch.rpm
sudo yum install mysql-community-server
```

### 1.3 二进制包安装（通用方式）

适用于不支持官方仓库的 Linux 发行版：

```bash
# 创建 mysql 用户和组
groupadd mysql
useradd -r -g mysql -s /bin/false mysql

# 解压二进制包到 /usr/local
cd /usr/local
tar xvf /path/to/mysql-VERSION-OS.tar.gz
ln -s /usr/local/mysql-VERSION/ /usr/local/mysql
```


## 二、服务管理

### 2.1 启动与停止

**使用 systemctl（主流发行版）** ：

```bash
sudo systemctl start mysql        # 启动服务
sudo systemctl stop mysql         # 停止服务
sudo systemctl restart mysql      # 重启服务
sudo systemctl status mysql       # 查看服务状态
```

CentOS/RHEL 中服务名可能为 `mysqld`：

```bash
sudo systemctl start mysqld
sudo systemctl status mysqld
```

**使用 service（旧版系统）** ：

```bash
sudo service mysqld start
sudo service mysqld stop
```

### 2.2 开机自启

```bash
sudo systemctl enable mysql        # Ubuntu/Debian
sudo systemctl enable mysqld       # CentOS/RHEL
```


## 三、安全初始化

安装完成后，建议立即运行安全配置脚本：

```bash
sudo mysql_secure_installation
```

该脚本会引导完成以下设置：
- 设置 root 密码
- 删除匿名用户
- 禁止 root 远程登录
- 删除测试数据库


## 四、连接 MySQL

### 4.1 本地连接

```bash
mysql -u root -p
```

输入密码后进入 MySQL 命令行客户端。

### 4.2 远程连接

```bash
mysql -h 主机地址 -u 用户名 -p
```

指定端口（默认 3306）：

```bash
mysql -h 192.168.137.10 -u root -p -P 3306
```

### 4.3 退出客户端

```bash
exit
# 或
quit
# 或按 Ctrl + D
```


## 五、数据库与表基本操作

### 5.1 数据库操作

| 命令 | 说明 |
|------|------|
| `SHOW DATABASES;` | 显示所有数据库 |
| `CREATE DATABASE 库名;` | 创建数据库 |
| `USE 库名;` | 切换当前数据库 |
| `DROP DATABASE 库名;` | 删除数据库 |

### 5.2 表操作

| 命令 | 说明 |
|------|------|
| `SHOW TABLES;` | 显示当前库所有表 |
| `DESCRIBE 表名;` | 查看表结构 |
| `CREATE TABLE 表名 (字段定义);` | 创建表 |
| `DROP TABLE 表名;` | 删除表 |

### 5.3 数据操作（CRUD）

**插入数据（Create）** ：

```sql
INSERT INTO users (id, name) VALUES (1, 'Alice');
```

**查询数据（Read）** ：

```sql
SELECT * FROM users;
SELECT name FROM users WHERE id = 1;
```

**更新数据（Update）** ：

```sql
UPDATE users SET name = 'Bob' WHERE id = 1;
```

**删除数据（Delete）** ：

```sql
DELETE FROM users WHERE id = 1;
```


## 六、用户与权限管理

### 6.1 查看用户

```bash
SELECT User, Host FROM mysql.user;
```

### 6.2 创建用户

```sql
CREATE USER '用户名'@'主机' IDENTIFIED BY '密码';
```

示例：创建仅本地登录的用户

```sql
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
```

### 6.3 授予权限

基本语法：

```sql
GRANT 权限 ON 数据库.表 TO '用户名'@'主机';
```

**常用示例**：

```sql
-- 授予对某个库所有表的全部权限
GRANT ALL PRIVILEGES ON mydb.* TO 'newuser'@'localhost';

-- 授予对所有库的所有权限（并允许授权他人）
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 授予特定操作权限
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'newuser'@'localhost';
```

### 6.4 刷新权限

修改权限后必须执行：

```sql
FLUSH PRIVILEGES;
```

### 6.5 查看与撤销权限

```sql
-- 查看用户权限
SHOW GRANTS FOR '用户名'@'主机';
```

```sql
-- 撤销权限
REVOKE 权限 ON 数据库.表 FROM '用户名'@'主机';
```

### 6.6 修改密码与删除用户

```sql
-- 修改密码
ALTER USER '用户名'@'主机' IDENTIFIED BY '新密码';
```

```sql
-- 删除用户
DROP USER '用户名'@'主机';
```


## 七、备份与恢复

### 7.1 逻辑备份（mysqldump）

**备份所有数据库** ：

```bash
mysqldump -u root -p --all-databases > all_backup.sql
```

**备份单个数据库** ：

```bash
mysqldump -u root -p 数据库名 > 备份文件.sql
```

**备份时压缩** ：

```bash
mysqldump -u root -p 数据库名 | gzip > 备份文件.sql.gz
```

### 7.2 定时备份（cron）

通过 crontab 设置定时备份：

```bash
crontab -e
# 每天凌晨 2 点备份
0 2 * * * mysqldump -u root -p密码 数据库名 > /path/to/backup/$(date +\%F).sql
```

### 7.3 恢复数据

**从 SQL 文件恢复** ：

```bash
mysql -u root -p 数据库名 < 备份文件.sql
```

**恢复前需确保数据库存在** ：

```sql
CREATE DATABASE 数据库名;
```

**恢复压缩备份** ：

```bash
gunzip 备份文件.sql.gz
mysql -u root -p 数据库名 < 备份文件.sql
```

### 7.4 物理备份

停止服务后直接复制数据目录：

```bash
sudo systemctl stop mysql
cp -R /var/lib/mysql /path/to/backup/
```


## 八、性能优化

### 8.1 配置文件位置

- Ubuntu/Debian：`/etc/mysql/mysql.conf.d/mysqld.cnf` 或 `/etc/mysql/my.cnf`
- CentOS/RHEL：`/etc/my.cnf`

### 8.2 核心参数调优

**innodb_buffer_pool_size**（最重要参数）

InnoDB 核心缓存池，建议设置为物理内存的 50%-75%：

```ini
innodb_buffer_pool_size = 20G    # 32GB 内存服务器示例
```

**max_connections**（最大连接数）

根据应用并发需求设置：

```ini
max_connections = 500
```

**innodb_log_buffer_size**（日志缓冲区）

写密集场景可调大：

```ini
innodb_log_buffer_size = 128M
```

**innodb_flush_log_at_trx_commit**（刷盘策略）

- `1`（默认）：最安全，性能最低
- `2`：性能与安全平衡
- `0`：性能最高，风险最大

```ini
innodb_flush_log_at_trx_commit = 2
```

**innodb_flush_method**（I/O 方式）

建议设为 `O_DIRECT` 避免双重缓存：

```ini
innodb_flush_method = O_DIRECT
```

### 8.3 监控与调优工具

```sql
-- 查看数据库状态
SHOW STATUS;
SHOW VARIABLES;

-- 分析查询语句
EXPLAIN SELECT ...;
```


## 九、常见问题排查

### 9.1 服务无法启动

**排查步骤**：

```bash
# 1. 查看服务状态
sudo systemctl status mysql

# 2. 查看错误日志
sudo tail -f /var/log/mysql/error.log      # Ubuntu/Debian
sudo tail -f /var/log/mysqld.log           # CentOS/RHEL

# 3. 检查端口是否被占用
sudo netstat -tuln | grep 3306
```

**常见原因**：
- 配置文件语法错误
- 端口 3306 被占用
- 数据目录权限不正确
- 磁盘空间不足

### 9.2 连接被拒绝

**检查项**：

1. 确认服务正在运行：`sudo systemctl status mysql`
2. 检查防火墙是否放行 3306 端口：
   ```bash
   sudo ufw allow 3306/tcp        # Ubuntu UFW
   sudo firewall-cmd --add-service=mysql --permanent   # CentOS firewalld
   sudo firewall-cmd --reload
   ```
3. 检查 `bind-address` 配置：
   - 如需远程访问，设为 `0.0.0.0` 或服务器 IP
   - 配置文件路径：`/etc/mysql/mysql.conf.d/mysqld.cnf`

### 9.3 忘记 root 密码

**重置步骤**：

```bash
# 1. 停止 MySQL 服务
sudo systemctl stop mysqld

# 2. 跳过授权表启动
sudo mysqld_safe --skip-grant-tables &

# 3. 无密码登录
mysql -u root

# 4. 在 MySQL 中重置密码
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';

# 5. 退出并正常重启服务
exit;
sudo systemctl start mysqld
```

### 9.4 权限问题

```sql
-- 查看用户权限
SHOW GRANTS FOR '用户名'@'主机';

-- 重新授予权限
GRANT ALL PRIVILEGES ON *.* TO '用户名'@'主机';
FLUSH PRIVILEGES;
```


## 十、常用命令速查

| 操作 | 命令 |
|------|------|
| 登录 MySQL | `mysql -u root -p` |
| 查看所有数据库 | `SHOW DATABASES;` |
| 创建数据库 | `CREATE DATABASE 库名;` |
| 切换数据库 | `USE 库名;` |
| 查看所有表 | `SHOW TABLES;` |
| 查看表结构 | `DESCRIBE 表名;` |
| 查看版本 | `SELECT VERSION();` |
| 查看当前连接 | `STATUS;` |
| 查看运行线程 | `SHOW PROCESSLIST;` |
| 执行 SQL 文件 | `SOURCE 路径/文件.sql;` |
| 退出客户端 | `EXIT;` 或 `QUIT;` |


> **说明**：本文档基于 MySQL 8.0 版本编写，部分命令在早期版本中可能略有差异。生产环境中请根据实际硬件配置和应用负载调整性能参数，并定期进行数据备份。
