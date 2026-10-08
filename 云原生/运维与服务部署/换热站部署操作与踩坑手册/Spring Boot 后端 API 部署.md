# 校园网零成本 Spring Boot 后端 API 部署完整复盘

---

## 1. 项目背景与核心需求

**项目**：换热站边缘计算平台（CloudPlatform）  
**硬件**：实验室一台 Ubuntu 22.04 服务器（内网 IP `202.199.6.249`），校园网内可路由  
**成员分布**：后端开发、前端开发、边缘设备调试，分散在实验室和宿舍  
**核心目标**：为前端页面和 Jetson 边缘盒子提供一个**稳定、可路由、长期可用**的后端 API 地址，使得所有人无论在实验室还是宿舍，都能像调用线上服务一样调用后端接口，且整个过程不花一分钱。

**面临的约束**：

- 服务器无公网 IP，且校园网出口限制导致**无法访问外网**（Docker Hub、apt 源均不可达）
- 服务器上已运行大量 Docker 容器（Dify 平台、Nginx、MySQL 等），**不能影响现有业务**
- 零预算，不允许购买云服务器、域名等

---

## 2. 前期调研：摸清服务器现状

> [!IMPORTANT]
> 任何部署的第一步，不是动手，而是**看清现场**

### 2.1 查看现有容器与端口占用

```bash
docker ps
```

输出显示已经有 `docker-nginx-1`（占用 80、443）、`mysql_8.0`（3306）、以及 Dify 相关的 api、worker、web 等容器。

**这一步的意义**：

- **避免端口冲突**：80、443 已被占，我不能在宿主机再装 Nginx，也不能用 3306 启动新 MySQL
- **复用已有服务**：既然已有 MySQL 和 Nginx 容器，就可以直接配置对接，而不是重新创建

### 2.2 检查宿主机 Nginx 状态

```bash
sudo systemctl status nginx
# Unit nginx.service could not be found.
```

说明宿主机本身没有安装 Nginx，所有 Web 流量都是通过 Docker 里的 Nginx 处理的。这决定了后续反向代理的实现方式——**必须在已有容器内修改配置**。

### 2.3 检查 Java 环境

```bash
java -version
# openjdk version "11.0.31"
```

服务器自带 Java 11，但我本地项目用的是 **Spring Boot 3.x，要求 Java 17**，必须升级。又因为无法 `apt install`，只能离线安装。

---

## 3. 环境准备：Docker 权限与离线 JDK 17 安装

### 3.1 用户加入 docker 组

```bash
sudo usermod -aG docker $USER
newgrp docker
```

**原因**：普通用户直接运行 `docker ps` 会报权限错误，每次加 `sudo` 太麻烦。把自己加入 `docker` 组后，当前会话立即生效，不再需要 `sudo`。

### 3.2 **离线安装 JDK 17**

**为什么需要离线安装？**  
**服务器外网不通**，`apt update` 或 `apt install openjdk-17-jdk` 都会失败。因此采用“个人电脑下载 → SCP 上传 → 解压”的方式。

- 在个人 Windows 电脑下载 Linux 版 JDK 17 压缩包：`OpenJDK17U-jdk_x64_linux_hotspot_17.0.20_8.tar.gz`
- 上传到服务器：

  ```powershell
  scp "C:\Users\Lenovo\Downloads\OpenJDK17U-jdk_x64_linux_hotspot_17.0.20_8.tar.gz" neu@202.199.6.249:/home/neu/
  ```

- 服务器端解压到 `/opt`：

  ```bash
  sudo tar -xzf /home/neu/OpenJDK17U-jdk_x64_linux_hotspot_17.0.20_8.tar.gz -C /opt/
  ```

- 验证：
  
  ```bash
  /opt/jdk-17.0.20+8/bin/java -version
  # openjdk version "17.0.20" ...
  ```

**为什么解压到 `/opt`？**
`/opt` 目录通常用于安装第三方独立软件，不干扰系统自带的 Java 11。将来如果不需要，直接删除目录即可，干干净净。

---

## 4. 打包 Spring Boot 应用：Maven Wrapper 的巧妙运用

### 4.1 为什么不用 `mvn` 命令？

在本地 Windows 终端直接敲 `mvn clean package` 提示“找不到 mvn”，因为**系统 PATH 中没有配置 Maven**。重新配置环境变量费时费力，而且不同机器 Maven 版本可能不一致。

**项目自带 Maven Wrapper (`mvnw`)**，它会**自动下载指定版本**的 Maven，确保所有开发者和 CI 环境构建行为一致。

### 4.2 **打包命令**

在项目根目录 `D:\换热站\CloudPlatform\CloudPlatform` 下打开 PowerShell：

```bash
./mvnw clean package -DskipTests
```

- `clean`：清空上次构建产物
- `package`：执行编译、测试（跳过）、打包成 JAR
- `-DskipTests`：**跳过测试**。因为本地开发环境没有连接数据库，一运行测试就会因数据库连接失败而中断构建。部署阶段我们只关心能否打出包，测试应在其他地方做。

**结果**：`BUILD SUCCESS`，在 `target/` 目录生成 `CloudPlatform-0.0.1-SNAPSHOT.jar`

### 4.3 上传 JAR 到服务器

```powershell
scp "D:\换热站\CloudPlatform\CloudPlatform\target\CloudPlatform-0.0.1-SNAPSHOT.jar" neu@202.199.6.249:/home/neu/
```

---

## 5. 部署 JAR 并创建 systemd 服务：让程序永不停机

### 5.1 目录规划

```bash
sudo mkdir -p /opt/iot-backend
sudo mv /home/neu/CloudPlatform-0.0.1-SNAPSHOT.jar /opt/iot-backend/app.jar
sudo chown -R neu:neu /opt/iot-backend
```

将 JAR 统一放在 `/opt/iot-backend/app.jar`，便于管理和后续更新（只需替换该文件即可）。

### 5.2 编写 systemd 服务文件

`/etc/systemd/system/iot-api.service`内容：

```ini
[Unit]
Description=IoT Backend API Service
After=network.target

[Service]
User=neu
WorkingDirectory=/opt/iot-backend
ExecStart=/opt/jdk-17.0.20+8/bin/java -jar /opt/iot-backend/app.jar
SuccessExitStatus=143
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**逐行解释**：

- `After=network.target`：确保网络启动后才启动服务，避免数据库连不上。
- `User=neu`：以普通用户而非 root 运行，安全。
- `WorkingDirectory`：设置工作目录，某些应用可能依赖相对路径。
- `ExecStart`：指定 Java 17 路径，避免使用系统 Java 11。
- `SuccessExitStatus=143`：Java 程序收到 `SIGTERM`（正常停止信号）时会返回 143，systemd 默认认为非 0 就是失败。加上这行告诉 systemd：143 也是正常退出，不必无限重启。
- `Restart=always`：进程崩溃或异常退出后，自动在 10 秒后重启。
- `RestartSec=10`：重启间隔，防止疯狂重启造成日志风暴。
- `WantedBy=multi-user.target`：开机自启。

**为什么用 systemd 而不是 `nohup java -jar &` 或 `screen`？** 

- `nohup` 的方式无法自动重启，进程挂了就真死了。
- `screen` 需要手动进入会话，不方便自动化。
- `systemd` 是 Linux 标准的服务管理器，开机自启、崩溃自愈、日志集中管理（`journalctl`），更适合生产环境。

### 5.3 **启动服务**

```bash
sudo systemctl daemon-reload          # 重载配置
sudo systemctl enable --now iot-api   # 设置开机自启并立即启动
sudo systemctl status iot-api         # 查看状态
```

此时 `status` 显示 `active (running)`，说明程序已启动。但我们马上就会遇到一个致命错误。

---

## 6. 首次启动失败：数据库连接错误排查

### 6.1 现象

`systemctl status iot-api` 反复显示 `activating (auto-restart)`，最终变为 `failed`。

**查看日志**（后端最重要的排错命令）：

```bash
sudo journalctl -u iot-api -n 50 --no-pager
```

**关键错误**：

```
Access denied for user 'root'@'192.168.100.1' (using password: NO)
```

**意思**：程序试图用 `root` 用户、无密码去连接 MySQL，被拒绝。

### 6.2 原因分析

JAR 包内的 `application.properties` 文件配置的数据库连接信息（可能来自开发环境）是：
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/cloudplatform
spring.datasource.username=root
spring.datasource.password=
```
而服务器上的 MySQL 容器**不允许 root 无密码登录**，且数据库名也不对（服务器上是 `cloud_platform` 或有密码保护）

### 6.3 解决思路

我们不能每次都去改源码重新打包（太麻烦），而是采用 **Spring Boot 外部化配置** 特性，用一个外部文件覆盖 JAR 内的配置

---

## 7. 配置与代码分离：外部化配置解决数据库问题

### 7.1 创建外部配置文件

```bash
sudo nano /opt/iot-backend/application.properties
```

写入正确的数据库连接信息：

```properties
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/cloudplatform?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
spring.datasource.username=clouduser
spring.datasource.password=cloudpass123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.hibernate.ddl-auto=update
```

（此时先使用数据库 `cloudplatform`，后续会调整为实际库名）

### 7.2 修改 systemd 启动命令

编辑服务文件：

```bash
sudo nano /etc/systemd/system/iot-api.service
```

将 `ExecStart` 改为：

```ini
ExecStart=/opt/jdk-17.0.20+8/bin/java -jar /opt/iot-backend/app.jar --spring.config.additional-location=file:/opt/iot-backend/application.properties
```

`--spring.config.additional-location` 会让 Spring Boot 额外加载指定位置的配置文件，其属性**优先级高于** JAR 内的默认配置。这就实现了“不改代码，只改外部文件”的灵活部署

### 7.3 **重载并重启**

```bash
sudo systemctl daemon-reload
sudo systemctl restart iot-api
```

**验证成功**：

```bash
curl http://localhost:8080/
# 返回 {"code":200,"message":"success","data":"CloudPlatform is running"}
```

此时后端已经能连上数据库并正常启动。

---

## 8. MySQL 数据库准备与数据导入

### 8.1 创建业务数据库与用户（如果之前没创建）

服务器已有 `mysql_8.0` 容器，直接复用：

```bash
docker exec -it mysql_8.0 mysql -u root -p
```

输入 root 密码后：

```sql
CREATE DATABASE IF NOT EXISTS cloudplatform CHARACTER SET utf8mb4;
CREATE USER 'clouduser'@'%' IDENTIFIED BY 'cloudpass123';
GRANT ALL PRIVILEGES ON cloudplatform.* TO 'clouduser'@'%';
FLUSH PRIVILEGES;
EXIT;
```

- 为什么用 `'clouduser'@'%'`？ 表示允许该用户从任何 IP 连接，适合容器化环境
- 为什么单独建用户？ 遵循最小权限原则，防止 root 泄露导致所有数据库暴露

### 8.2 导入团队提供的 SQL 文件

队友通过微信发了 `cloud_platform2.sql`（实际数据库名 `cloud_platform`）

**上传文件**：

```powershell
scp "C:\...\cloud_platform2.sql" neu@202.199.6.249:/home/neu/
```

**查看文件头**：

```bash
head -30 /home/neu/cloud_platform2.sql
```

发现没有 `CREATE DATABASE` 语句，因此需要手动建库。

**创建实际数据库**（以 `cloud_platform` 为名）：

```sql
CREATE DATABASE IF NOT EXISTS cloud_platform CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON cloud_platform.* TO 'clouduser'@'%';
```

**导入数据**：

```bash
docker exec -i mysql_8.0 mysql -u clouduser -pcloudpass123 cloud_platform < /home/neu/cloud_platform2.sql
```

无报错即导入成功。

**验证表结构**：

```bash
docker exec -it mysql_8.0 mysql -u clouduser -pcloudpass123 cloud_platform -e "SHOW TABLES;"
```

返回 27 张表，包括 `station`、`device`、`alarm`、`sensor_data` 等。

### 8.3 切换后端配置到新库

之前外部配置中数据库名是 `cloudplatform`，但实际数据在 `cloud_platform`（有下划线）。修改 `/opt/iot-backend/application.properties`：

```properties
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/cloud_platform?...
```

重启服务：

```bash
sudo systemctl restart iot-api
curl http://localhost:8080/   # 仍然返回 success，说明连接新库成功
```

---

## 9. Nginx 反向代理：统一入口，告别端口号

### 9.1 **为什么需要反向代理？**

- 后端端口 `8080` 需要用户记住，不友好
- 前端调用时带端口号可能引发跨域问题
- 服务器 80 端口已被 Nginx 容器占用，正好用来统一入口，通过路径分流到不同后端服务

### 9.2 复用已有 Nginx 容器

宿主机没有 Nginx，但有一个 `docker-nginx-1` 容器管理着 80 端口。我不需要创建新容器，直接在其中添加配置即可。

**进入容器**：

```bash
docker exec -it docker-nginx-1 bash
```

**查看主配置**：

```bash
cat /etc/nginx/conf.d/default.conf
```

看到已有 `server` 块监听 80，其中 `/api`、`/console/api` 等路径已被 Dify 占用。为了不与现有业务冲突，我新加一个**专属前缀** `/iot-api/`

### 9.3 添加反向代理规则

在原有 `server` 块中，`location / {` 之前插入：

```nginx
location /iot-api/ {
    proxy_pass http://202.199.6.249:8080/;
    include proxy.conf;
}
```

- `proxy_pass` 地址使用宿主机真实 IP `202.199.6.249`，而不是 `127.0.0.1` 或 `172.17.0.1`
- **原因**：经测试，容器内访问 `172.17.0.1:8080` 返回 504 超时，而访问 `202.199.6.249:8080` 正常（200）。因为 Docker 默认桥接在某些网络配置下无法直接访问宿主机端口，但宿主机内网 IP 是可达的

**测试并重载**：

```bash
nginx -t
nginx -s reload
exit
```

### 9.4 验证反向代理

```bash
curl http://localhost/iot-api/
# 返回 {"code":200,"data":"CloudPlatform is running"}
```

完美！从今往后，所有人只需记住一个地址：`http://202.199.6.249/iot-api/`

---

## 10. 整体架构与数据流

```
┌───────────────────────────────────────────────┐
│          实验室服务器 202.199.6.249            │
│                                               │
│  ┌──────────────────────────────────┐         │
│  │  docker-nginx-1 (80)             │         │
│  │    location /iot-api/ → 202...   │         │
│  └────────────┬─────────────────────┘         │
│               │ proxy_pass                    │
│               ▼                               │
│  ┌──────────────────────────────────┐         │
│  │  Spring Boot 后端 (8080)         │         │
│  │  systemd 守护：iot-api.service   │         │
│  │  外部配置：application.properties│         │
│  └────────────┬─────────────────────┘         │
│               │ JDBC                          │
│               ▼                               │
│  ┌──────────────────────────────────┐         │
│  │  mysql_8.0 (3306)                │         │
│  │  数据库：cloud_platform          │         │
│  └──────────────────────────────────┘         │
│                                               │
└───────────────────────────────────────────────┘
         ▲
         │ 校园网 HTTP 请求
         │ http://202.199.6.249/iot-api/xxx
         │
┌────────┴────────┐
│  宿舍/实验室电脑 │
│  前端、Postman  │
└─────────────────┘
```

**关键特性**：

- **零成本**：未购买任何云服务。
- **高可用**：systemd 自动重启，开机自启。
- **配置分离**：数据库、密钥等敏感信息外部化，修改无需重打包。
- **统一入口**：Nginx 反向代理，隐藏内部端口，支持路径隔离。
- **安全**：数据库使用专用用户，最小权限。

---

## 11. 日常更新流程

后端代码修改后，只需四步：

1. **本地打包**
   
   ```bash
   ./mvnw clean package -DskipTests
   ```

2. **上传 JAR**
   
   ```powershell
   scp target\CloudPlatform-0.0.1-SNAPSHOT.jar neu@202.199.6.249:/home/neu/
   ```

3. **服务器替换 JAR 并重启**
   
   ```bash
   sudo systemctl stop iot-api
   sudo mv /home/neu/CloudPlatform-0.0.1-SNAPSHOT.jar /opt/iot-backend/app.jar
   sudo systemctl start iot-api
   ```

4. **验证**
   
   ```bash
   curl http://localhost/iot-api/
   ```

如果数据库配置有变，只需编辑 `/opt/iot-backend/application.properties` 然后 `sudo systemctl restart iot-api`，无需重新打包上传

---

## 12. 面试亮点与个人收获

### 12.1 可以说的亮点

- **受限环境下的部署能力**：在无公网、无外网的校园网环境，利用离线方式安装 JDK、传输镜像，保障服务上线
- **复用已有资源**：不破坏现有 Dify 系统，利用已有 Nginx 和 MySQL 容器，通过路径前缀 `/iot-api/` 实现多服务共存
- **配置外部化实践**：通过 `--spring.config.additional-location` 实现数据库连接与代码分离，体现 DevOps 思维
- **生产级进程管理**：采用 `systemd` 替代 `nohup`，实现自动重启、开机自启，保障服务 7×24 小时在线
- **故障排查方法论**：从日志入手（`journalctl`），结合网络测试（`curl`），快速定位数据库连接和反向代理问题

### 12.2 个人技术成长

- 理解了 Docker 网络模型（容器访问宿主机的几种方式）
- 掌握了 Nginx 反向代理的路径匹配与多项目并存技巧
- 熟悉了 Spring Boot 外部配置的优先级规则
- 提高了在受限网络下解决问题的能力（离线包、scp 传输）

---

## 13. 常用运维命令速查

| 操作 | 命令 |
|------|------|
| 查看后端状态 | `sudo systemctl status iot-api` |
| 重启后端 | `sudo systemctl restart iot-api` |
| 查看后端实时日志 | `sudo journalctl -u iot-api -f` |
| 查看最近日志 | `sudo journalctl -u iot-api -n 50 --no-pager` |
| 测试后端直接访问 | `curl http://localhost:8080/` |
| 测试通过 Nginx 访问 | `curl http://localhost/iot-api/` |
| 进入 MySQL 容器 | `docker exec -it mysql_8.0 mysql -u clouduser -pcloudpass123` |
| 查看数据库列表 | `docker exec mysql_8.0 mysql -u clouduser -pcloudpass123 -e "SHOW DATABASES;"` |

---

**写在最后**：这次部署不仅仅是跑起来一个 Spring Boot 应用，更重要的是建立起了一套**可维护、可扩展、安全稳定**的 API 服务体系。它证明了一个后端工程师的价值不仅仅在于写代码，更在于**让代码在真实环境中可靠地运行，并让团队所有人都能方便地使用它**。这正是从“只会写接口”到“能独当一面”的跨越

---
