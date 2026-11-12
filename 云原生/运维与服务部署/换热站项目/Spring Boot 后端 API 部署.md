# 校园网零成本 Spring Boot 后端 API 部署完整复盘

---

## 1. 项目背景与核心需求

**项目**：换热站边缘计算平台（CloudPlatform）  
**硬件**：实验室一台 Ubuntu 22.04 服务器（校园网地址 `202.199.6.249`），校园网内可路由
**成员分布**：后端开发、前端开发、边缘设备调试，分散在实验室和宿舍  
**核心目标**：为前端页面和 Jetson 边缘盒子提供一个**稳定、可路由、长期可用**的后端 API 地址，使得所有人无论在实验室还是宿舍，都能像调用线上服务一样调用后端接口，且整个过程不花一分钱。

**面临的约束**：

- 该校园网地址不代表校外一定可达，且当时的校园网出口限制导致**无法访问外网**（Docker Hub、apt 源均不可达）
- 服务器上已运行大量 Docker 容器（Dify 平台、Nginx、MySQL 等），**不能影响现有业务**
- 零预算，不允许购买云服务器、域名等

---

## 2. 前期调研：摸清服务器现状

> [!IMPORTANT]
> 任何部署的第一步，不是动手，而是**看清现场**

### 2.1 查看现有容器与端口占用

```bash
# 用容器状态和近期日志确认启动进度及失败位置。
docker ps
```

输出显示已经有 `docker-nginx-1`（占用 80、443）、`mysql_8.0`（3306）、以及 Dify 相关的 api、worker、web 等容器。

**这一步的意义**：

- **避免端口冲突**：80、443 已被占，我不能在宿主机再装 Nginx，也不能用 3306 启动新 MySQL
- **复用已有服务**：既然已有 MySQL 和 Nginx 容器，就可以直接配置对接，而不是重新创建

**当时为什么复用已有容器**

早期手册（`c5cfc39`）记下了 80、443 已有服务占用，数据库也已有容器提供。选择复用现有 Nginx 和 MySQL，部署时只增加后端进程与必要配置。复用前应确认已有服务的归属、实际监听和权限，后端接入时单独验证自己的库名与代理路径。


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
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
sudo usermod -aG docker $USER
newgrp docker
```

**原因**：普通用户直接运行 `docker ps` 会报权限错误，每次加 `sudo` 太麻烦。加入组后需 newgrp 或重新登录刷新组成员身份，随后会话生效，不再需要 `sudo`。

### 3.2 **离线安装 JDK 17**

**为什么需要离线安装？**  
**服务器外网不通**，`apt update` 或 `apt install openjdk-17-jdk` 都会失败。因此采用“个人电脑下载 → SCP 上传 → 解压”的方式。

- 在个人 Windows 电脑下载 Linux 版 JDK 17 压缩包：`OpenJDK17U-jdk_x64_linux_hotspot_17.0.20_8.tar.gz`
- 上传到服务器：

  ```powershell
  # 核对远端账号、主机与目标路径。区分本机文件和远端文件。
  scp "C:\Users\Lenovo\Downloads\OpenJDK17U-jdk_x64_linux_hotspot_17.0.20_8.tar.gz" neu@202.199.6.249:/home/neu/
  ```

- 服务器端解压到 `/opt`：

  ```bash
  # 核对归档输入和输出位置，完成后检查文件清单。
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

```powershell
# 在包含 pom.xml 的项目目录运行，查看构建阶段和输出制品。
.\mvnw.cmd clean package -DskipTests
```

- `clean`：清空上次构建产物
- `package`：执行编译、测试（跳过）、打包成 JAR
- `-DskipTests`：**跳过测试**。因为本地开发环境没有连接数据库，一运行测试就会因数据库连接失败而中断构建。部署阶段我们只关心能否打出包，测试应在其他地方做。

**结果**：`BUILD SUCCESS`，在 `target/` 目录生成 `CloudPlatform-0.0.1-SNAPSHOT.jar`

### 4.3 上传 JAR 到服务器

```powershell
# 核对远端账号、主机与目标路径。区分本机文件和远端文件。
scp "D:\换热站\CloudPlatform\CloudPlatform\target\CloudPlatform-0.0.1-SNAPSHOT.jar" neu@202.199.6.249:/home/neu/
```

#### 核对构建产物与目标机 Java

校园网部署时，机器预装 Java 版本与项目需要的版本不同，Maven Wrapper 和离线 JDK 解决的是两个环节。Wrapper 决定用哪个 Maven 构建，实际执行 JAR 的 Java 由目标主机或 systemd 的 `ExecStart` 决定。登录后运行 `java -version` 只检查当前终端，不能代替核对服务用的绝对路径。

| 阶段 | 要留的证据 | 问题出现时看什么 |
|---|---|---|
| 开发机构建 | 源码提交、Wrapper 版本、实际 JDK、构建日志 | Wrapper 下载失败与项目依赖下载失败分别定位 |
| 传输 | JAR 文件名、大小和 SHA-256 | 对照发送端与接收端，发现截断或上传旧文件 |
| 目标机启动 | Java 路径、版本、服务用户、工作目录 | class 版本不兼容、文件不可读或相对路径解析错误 |
| 服务就绪 | 启动日志、真实监听地址、只读 API | 进程存在但配置、连接池或业务依赖尚未就绪 |
| 入口访问 | 直接请求与反代请求的响应 | 检查路径、协议、认证和实际返回内容 |

```bash
# 在部署目录核对传输后的 JAR。BUILD_JAVA 填该服务 ExecStart 使用的 Java。
: "${APP_JAR:?请设置实际部署的 JAR 路径}"
: "${BUILD_JAVA:?请设置目标服务使用的 Java 可执行文件}"
sha256sum "$APP_JAR"
"$BUILD_JAVA" -version
# 只看归档结构，确认是能直接运行的 Spring Boot 制品。
jar tf "$APP_JAR" | grep -E '(^META-INF/MANIFEST.MF$|^BOOT-INF/(classes|lib)/)' | sed -n '1,12p'
```

不同构建插件可能同时产出普通 JAR 与可执行 JAR。应从产物命名、manifest 或实际试启动确认要上传的文件，避免把 `original` 备份或旧版本拷到运行目录。离线场景若没有 Wrapper 所需依赖，优先在联网的构建端完成构建并传入制品。目标机只安装运行环境，不需要把整个 Maven 缓存带进去。


---

## 5. 部署 JAR 并创建 systemd 服务：让程序永不停机

### 5.1 目录规划

```bash
# 修改指定文件或目录的权限，核对实际运行服务的用户。
sudo mkdir -p /opt/iot-backend
sudo mv /home/neu/CloudPlatform-0.0.1-SNAPSHOT.jar /opt/iot-backend/app.jar
sudo chown -R neu:neu /opt/iot-backend
```

将 JAR 统一放在 `/opt/iot-backend/app.jar`，便于管理和后续更新（只需替换该文件即可）。

### 5.2 编写 systemd 服务文件

`/etc/systemd/system/iot-api.service`内容：

```ini
# 分开描述服务依赖、启动命令与运行身份，修改后由服务管理器重新加载配置。
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

- `After=network.target`：仅规定启动顺序，不保证网络或数据库已就绪；应用需连接重试，必要时结合 network-online.target 与对应 wait-online 服务。
- `User=neu`：以普通用户而非 root 运行，安全。
- `WorkingDirectory`：设置工作目录，某些应用可能依赖相对路径。
- `ExecStart`：指定 Java 17 路径，避免使用系统 Java 11。
- `SuccessExitStatus=143`：Java 程序收到 `SIGTERM`（正常停止信号）时会返回 143，systemd 默认认为非 0 就是失败。加上这行将 143 归类为成功退出；Restart=always 仍会重启自行退出的进程，但 systemctl stop 主动停止不会触发它。
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

#### 核对自启和主机重启后的恢复

发布完成后可在交接记录中标注自启方式，区分 systemd 服务、Compose 启动顺序和容器重启策略。主机重启验证应在计划好的演练环境进行。应用起来之前先确认数据库卷是否挂载、数据库是否就绪、服务用户能否读取必要配置。若服务配置用相对路径，核对 systemd 的 WorkingDirectory；若依赖环境变量，检查来源是否随服务加载。

```bash
# 查询自启和服务当前状态。enabled 只表示配置了开机启动。
systemctl is-enabled "$APP_SERVICE"
systemctl is-active "$APP_SERVICE"
# 检查指定配置路径每一级目录的权限，避免服务用户无法遍历。
: "${APP_CONFIG:?请设置实际外部配置路径}"
namei -l "$APP_CONFIG"
```

记录主机重启时间和应用实际就绪时间。如果容器与宿主上的应用有启动先后关系，就绪检查和有限重试应在应用或服务定义中有明确边界。应用成功启动后再查原业务样本，排除自动初始化误把旧数据覆盖。新机器或新容器恢复成功时，分别记录数据库行和前端页面看到的结果。需要交接给下一位运维时，提供上一版制品、外部配置路径、服务名、检查入口与回退触发条件。


---

## 6. 首次启动失败：数据库连接错误排查

### 6.1 现象

`systemctl status iot-api` 反复显示 `activating (auto-restart)`，最终变为 `failed`。

**查看日志**（后端最重要的排错命令）：

```bash
# 查看近期日志，按时间定位和当前操作对应的记录。
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
# 数据库地址从应用所在网络选择，连接信息与驱动、字符集配置一起核对。
spring.datasource.url=jdbc:mysql://localhost:3306/cloudplatform
spring.datasource.username=root
spring.datasource.password=
```
而服务器上的 MySQL 容器**不允许 root 无密码登录**，且数据库名也不对（服务器上是 `cloud_platform` 或有密码保护）

### 6.3 解决思路

我们不能每次都去改源码重新打包（太麻烦），而是采用 **Spring Boot 外部化配置** 特性，用一个外部文件覆盖 JAR 内的配置

#### 从应用所在网络验证数据库连接

旧记录里使用了 Docker 中的数据库和宿主上的 Java 进程。宿主连接容器数据库时，使用对宿主可达的映射地址与端口。若后来把应用也放进同一 Compose 网络，可按服务名和容器端口连接。应用里的 `127.0.0.1` 始终指向应用自身所在的网络环境。核对 JDBC URL 的主机、端口、库名和账号，不要从容器名推断对外端口。

排错时先区分失败阶段：

- **连接拒绝或超时。** 从应用所在位置验证监听与网络，检查端口映射和代理是否指到实际服务。错误从拒绝变成认证失败，说明已经推进到下一层。
- **Access denied。** 账号是否匹配当前客户端来源、是否使用正确凭据、对目标库有哪些授权。使用与应用相同的权限边界做验证，避免用管理员连接掩盖问题。
- **Unknown database 或缺表。** 对照迁移清单和实际 JDBC 库名。确认 SQL 导入完成，并检查应用要求的表、索引与必要初始数据。
- **能查询但中文不对。** 分开看表字段编码、会话字符集、JAR 中的初始化数据与 API 响应。参照[站点乱码复盘](站点乱码问题排查与修复全记录.md)保留同一行的证据。
- **HTTP 401 或 403。** 先确认请求是否到了后端，应用是否正在使用迁移后的账号表和配置。再检查认证与授权，避免将重置账户或放宽权限作为第一个动作。


---

## 7. 配置与代码分离：外部化配置解决数据库问题

### 7.1 创建外部配置文件

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
sudo nano /opt/iot-backend/application.properties
```

写入正确的数据库连接信息：

```properties
# 数据库地址从应用所在网络选择，连接信息与驱动、字符集配置一起核对。
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/cloudplatform?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
spring.datasource.username=clouduser
spring.datasource.password=cloudpass123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.hibernate.ddl-auto=update
```

（此时先使用数据库 `cloudplatform`，后续会调整为实际库名）

#### 核对配置来源、加载位置与优先级

同一个 Spring Boot 程序可能同时读取 JAR 内配置、外部文件、激活的 profile、环境变量和命令行参数。`spring.config.location` 用于替换默认位置，`spring.config.additional-location` 用于在默认位置之外增加位置。目录位置通常用斜杠结尾，具体文件则直接指到文件。`optional:` 会允许某些配置位置缺失，数据库等必要配置应该让缺失能在启动时暴露。

| 现象 | 先核对 | 为什么 |
|---|---|---|
| 改了外部文件却没生效 | 当前服务命令的配置位置、profile、文件权限 | 进程可能根本没读这份文件 |
| 配置路径看起来没错，仍连旧库 | 环境变量、命令行参数和 profile 覆盖 | 更高优先级配置可能覆盖旧值 |
| 终端直接启动能连库，systemd 启动失败 | 工作目录、运行用户、读取权限和服务环境 | 登录 shell 与 systemd 的环境不同 |
| 数据库连通但查到空表 | 实际库名、迁移结果和接口查询条件 | 连接成功不能证明应用使用了正确的数据集 |
| 新服务启动后站点值被覆盖 | 初始化配置、运行日志和同一行前后值 | 排查启动补数、固定数据和定时任务 |

```bash
# 查询服务实际使用的 unit、工作目录和进程，不输出数据库口令。
: "${APP_SERVICE:?请设置 systemd 服务名}"
systemctl show "$APP_SERVICE" \
  -p FragmentPath -p DropInPaths -p WorkingDirectory -p User -p MainPID -p ActiveState
journalctl -u "$APP_SERVICE" --since "10 minutes ago" --no-pager -n 100
```

部署时把数据库地址、端口、库名、账号来源与密码交付分开记录。外部配置按服务用户最小权限读取，排障截图遮盖凭据。要确认实际数据源时，可使用受控只读检查或应用启动日志中的脱敏信息。无需为查配置临时开放所有 Actuator 端点，也不要用运行环境完整转储当作交接文件。


### 7.2 修改 systemd 启动命令

编辑服务文件：

```bash
# 通过服务管理器操作目标进程，再核对它的状态和错误日志。
sudo nano /etc/systemd/system/iot-api.service
```

将 `ExecStart` 改为：

```ini
# 把键值放到读取该配置的文件或节中，核对覆盖顺序与重启后的生效值。
ExecStart=/opt/jdk-17.0.20+8/bin/java -jar /opt/iot-backend/app.jar --spring.config.additional-location=file:/opt/iot-backend/application.properties
```

`--spring.config.additional-location` 会让 Spring Boot 额外加载指定位置的配置文件，其属性**优先级高于** JAR 内的默认配置。这就实现了“不改代码，只改外部文件”的灵活部署

### 7.3 **重载并重启**

```bash
# 通过服务管理器操作目标进程，再核对它的状态和错误日志。
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
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -it mysql_8.0 mysql -u root -p
```

输入 root 密码后：

```sql
-- 创建独立数据库作为练习范围，后续建表前核对当前库。
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
# 核对远端账号、主机与目标路径。区分本机文件和远端文件。
scp "C:\...\cloud_platform2.sql" neu@202.199.6.249:/home/neu/
```

**查看文件头**：

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
head -30 /home/neu/cloud_platform2.sql
```

发现没有 `CREATE DATABASE` 语句，因此需要手动建库。

**创建实际数据库**（以 `cloud_platform` 为名）：

```sql
-- 创建独立数据库作为练习范围，后续建表前核对当前库。
CREATE DATABASE IF NOT EXISTS cloud_platform CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON cloud_platform.* TO 'clouduser'@'%';
```

**导入数据**：

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -i mysql_8.0 mysql -u clouduser -pcloudpass123 cloud_platform < /home/neu/cloud_platform2.sql
```

检查导入命令退出码，并核对表数、关键行数和业务查询，不能仅凭无输出认定完整导入成功。

**验证表结构**：

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -it mysql_8.0 mysql -u clouduser -pcloudpass123 cloud_platform -e "SHOW TABLES;"
```

返回 27 张表，包括 `station`、`device`、`alarm`、`sensor_data` 等。

### 8.3 切换后端配置到新库

之前外部配置中数据库名是 `cloudplatform`，但实际数据在 `cloud_platform`（有下划线）。修改 `/opt/iot-backend/application.properties`：

```properties
# 数据库地址从应用所在网络选择，连接信息与驱动、字符集配置一起核对。
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/cloud_platform?...
```

重启服务：

```bash
sudo systemctl restart iot-api
curl http://localhost:8080/   # 只验证该端点可响应；另查实际读写 cloud_platform 的业务接口
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
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -it docker-nginx-1 bash
```

**查看主配置**：

```bash
# 读取或筛选本地文件，按实际路径与输出核对关键字段。
cat /etc/nginx/conf.d/default.conf
```

看到已有 `server` 块监听 80，其中 `/api`、`/console/api` 等路径已被 Dify 占用。为了不与现有业务冲突，我新加一个**专属前缀** `/iot-api/`

### 9.3 添加反向代理规则

在原有 `server` 块中，`location / {` 之前插入：

```nginx
# 根据 location 选择代理路径，核对 proxy_pass 的 URI、上游地址和转发头。
location /iot-api/ {
    proxy_pass http://202.199.6.249:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

- `proxy_pass` 地址使用宿主机真实 IP `202.199.6.249`，而不是 `127.0.0.1` 或 `172.17.0.1`
- **原因**：经测试，容器内访问 `172.17.0.1:8080` 返回 504 超时，而访问 `202.199.6.249:8080` 正常（200）。因为 Docker 默认桥接在某些网络配置下无法直接访问宿主机端口，但宿主机内网 IP 是可达的

**测试并重载**：

```bash
# 检查配置语法后再重载，随后验证实际流量入口。
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

#### 对照直连、容器与外部入口

选择一个当前版本已知可用、无副作用的 API。先从宿主直连，然后从 Nginx 所在位置按上游配置请求，最后通过真实入口访问。保持路径语义和请求方法一致。记录状态、响应类型和关键字段。如果某层出现 HTML、重定向或 404，先确认它路由到了哪个服务，再调整代理或应用。

```bash
# DIRECT_URL 和 EDGE_URL 应指向同一业务功能的直连与代理入口。
: "${DIRECT_URL:?请设置后端只读检查 URL}"
: "${EDGE_URL:?请设置反代只读检查 URL}"
curl -sS --max-time 10 -w '\nHTTP %{http_code}\n' "$DIRECT_URL"
curl -sS --max-time 10 -w '\nHTTP %{http_code}\n' "$EDGE_URL"
```

健康端点能用只说明服务能响应当前检查。真正的后端验收还应包括一次读取数据库的业务查询、一条授权路径和对应前端操作。对于带登录的应用，测试账户应限制范围。登录成功后另验角色允许的接口，确认不能访问的功能仍被拒绝。通过可复现样本检验数据，而非只看 `code: 200`。


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
- **进程自动恢复**：systemd 可自动重启并随系统启动；单机故障、网络中断和应用持续报错仍会导致不可用，不能等同高可用。
- **配置分离**：数据库、密钥等敏感信息外部化，修改无需重打包。
- **统一入口**：Nginx 反向代理，隐藏内部端口，支持路径隔离。
- **安全**：数据库使用专用用户，最小权限。

---

## 11. 日常更新流程

后端代码修改后，只需四步：

1. **本地打包**
   
   ```powershell
   # 在包含 pom.xml 的项目目录运行，查看构建阶段和输出制品。
   .\mvnw.cmd clean package -DskipTests
   ```

2. **上传 JAR**
   
   ```powershell
   # 核对远端账号、主机与目标路径。区分本机文件和远端文件。
   scp target\CloudPlatform-0.0.1-SNAPSHOT.jar neu@202.199.6.249:/home/neu/
   ```

3. **服务器替换 JAR 并重启**
   
   ```bash
   # 通过服务管理器操作目标进程，再核对它的状态和错误日志。
   sudo systemctl stop iot-api
   sudo mv /home/neu/CloudPlatform-0.0.1-SNAPSHOT.jar /opt/iot-backend/app.jar
   sudo systemctl start iot-api
   ```

4. **验证**
   
   ```bash
   # 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
   curl http://localhost/iot-api/
   ```

如果数据库配置有变，只需编辑 `/opt/iot-backend/application.properties` 然后 `sudo systemctl restart iot-api`，无需重新打包上传

### 记录更新结果和回退位置

部署前留存上一版可运行 JAR 和校验值、外部配置来源、服务 unit、当时的数据库 schema 版本。新产物先上传到独立文件名，校验无误再切换运行路径或按已有发布方式替换。若 unit 改了再执行 daemon reload，重启后核对 PID、启动时间和新版本日志。只看到重新上传文件不等于进程已经更新。

遇到启动失败、核心接口持续 5xx、连到错误库或关键数据异常时，暂停后续动作，恢复与上一版配套的 JAR 和配置，再验证直接入口和 Nginx 入口。若已经做数据库结构或数据变更，先确认旧应用是否兼容当前 schema。对于不可逆的数据更新，必须使用事先准备的恢复方案。一次成功发布记录制品、配置、服务、依赖、接口证据和回退目标，便于下次交接。 [Spring Boot 外部配置](https://docs.spring.io/spring-boot/reference/features/external-config.html)


---

## 12. 面试亮点与个人收获

### 12.1 可以说的亮点

- **受限环境下的部署能力**：在无公网、无外网的校园网环境，利用离线方式安装 JDK、传输镜像，保障服务上线
- **复用已有资源**：不破坏现有 Dify 系统，利用已有 Nginx 和 MySQL 容器，通过路径前缀 `/iot-api/` 实现多服务共存
- **配置外部化实践**：通过 `--spring.config.additional-location` 实现数据库连接与代码分离，体现 DevOps 思维
- **生产级进程管理**：采用 `systemd` 替代 `nohup`，实现自动重启、开机自启，改善进程恢复能力，实际可用性仍需监控、健康检查与冗余
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
