# EMQX + MinIO 部署手册

---

## 项目背景

> **目标**：为 Jetson 边缘 AI 盒子搭建一个与云端通信的基础设施层，实现设备指令下发、数据回传、模型安全分发。

- **MQTT Broker（EMQX）**：充当 Jetson 与云端服务的“对讲机”，负责双向消息传递。
- **对象存储（MinIO）**：存放 Jetson 回传的图片/视频，以及云端更新的 AI 模型文件（如 `.engine`、`.onnx`）。
- **运行环境**：学校实验室的一台 Ubuntu 22.04 服务器，**仅限校园网访问，无法直接连接外网**，且已承载其他生产容器（Nginx、MySQL、Dify 等），需要在不影响现有服务的前提下部署。

---

## 准备工作

登录服务器 `202.199.6.249`（用户 `neu`）后，先摸清现有资源：

```bash
# 用容器状态和近期日志确认启动进度及失败位置。
docker ps
```

输出显示已有 10+ 个容器运行中，包括：

- `nginx`、`mysql:8.0`、`postgres:15-alpine`、`redis:6-alpine`
- Dify 应用全家桶（`dify-api`、`dify-web`、`dify-sandbox` 等）

**关键发现**：

- Docker 已安装，版本 27.5.1，无需安装。
- 服务器未配置外网代理，无法直接拉取 Docker Hub 镜像。
- 存在 Docker 组权限问题，用户 `neu` 需加入 `docker` 组才能无 `sudo` 使用。

---

## 第一阶段：解决 Docker 网络隔离与权限

### 1. 用户权限修复

`docker ps` 报错 `permission denied`。  
**解决**：将 `neu` 加入 `docker` 组并刷新会话。  

```bash
sudo usermod -aG docker $USER
newgrp docker   # 或退出重新登录
```

### 2. 镜像拉取失败：IPv6 超时 + 无外网

首次 `docker run emqx/emqx:latest` 报错：

```
dial tcp [2a03:2880:...]:443: connect: connection timed out
```

查看已有镜像源配置：

```bash
sudo docker info | grep "Registry Mirrors"
# 输出：https://docker.gh-proxy.com/
```

这表明本次镜像访问仍失败；需结合 DNS、镜像站和守护进程代理配置排查，单凭该日志不能断定代理失效或全局优先使用 IPv6。

#### 尝试配置镜像加速 + 禁用 IPv6

```bash
# 通过服务管理器操作目标进程，再核对它的状态和错误日志。
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"],
  "ipv6": false
}
EOF
sudo systemctl restart docker
```

`"ipv6": false` 只控制默认 bridge 的容器 IPv6，不会关闭宿主机或守护进程拉取镜像时的 IPv6。修改 daemon.json 前应保留现有配置，重启 Docker 需安排维护窗口。

重启后 `docker pull` 仍失败，因为**校园网服务器根本不能访问外网**，加速器同样需要出校。

#### 代理探测

根据实验室提供的 `202.199.6.249` 测试 HTTP 代理（常见端口 8080、3128）：

```bash
curl -I --proxy http://202.199.6.249:8080 https://www.baidu.com   # 连接被拒绝
curl -I --proxy http://202.199.6.249:3128 https://www.baidu.com   # 连接被拒绝
```

确认该地址并非 HTTP 代理，不能据此确定代理服务位置，且 `202.199.6.249` 不属于 RFC 1918 私有 IPv4 地址段。

### 3. 最终方案：离线镜像导入

**思路**：在个人电脑（可上网）拉取镜像并打包，再通过 SCP 传到服务器加载。

- 个人电脑（Windows + Docker Desktop 29.5.2）：
  
  ```powershell
  # 处理镜像仓库与标签。先核对仓库地址、制品版本和所用身份。
  docker pull emqx/emqx:latest
  docker save emqx/emqx:latest -o emqx.tar
  docker pull minio/minio:latest
  docker save minio/minio:latest -o minio.tar
  ```

- SCP 传输到服务器（首次连接核对 SSH 主机指纹）：
  
  ```powershell
  # 核对远端账号、主机与目标路径。区分本机文件和远端文件。
  scp emqx.tar neu@202.199.6.249:/home/neu/
  scp minio.tar neu@202.199.6.249:/home/neu/
  ```

- 服务器加载：
  
  ```bash
  # 在文件和 Docker 制品之间转换，导入后核对标签或容器所需文件。
  docker load -i /home/neu/emqx.tar
  docker load -i /home/neu/minio.tar
  ```

**收获**：掌握了 Docker 离线部署能力，理解守护进程配置、代理设置与镜像分发的多种手段。

#### 导入后检查镜像和持久化数据

旧部署中最费时间的是把网络不通、镜像架构不匹配和容器启动失败混在一起。离线交接时先记下镜像名、版本标签、平台和归档校验值。传输前后检查同一份归档。镜像能加载，只说明部署制品到位。EMQX 的认证、授权和持久化配置，以及 MinIO 的 Bucket、对象和访问策略，要按各自的备份恢复。

```bash
# 设置为手册中实际选用的镜像标签和已经上传的归档。
: "${IMAGE_TAG:?请设置镜像名及标签}"
: "${IMAGE_ARCHIVE:?请设置归档路径}"
uname -m
sha256sum "$IMAGE_ARCHIVE"
# 导入后对照清单中的平台和镜像 ID。
docker image inspect --format '{{.Os}}/{{.Architecture}} {{.Id}}' "$IMAGE_TAG"
```

运行报 `exec format error` 时，对照目标平台、镜像平台和入口脚本格式。镜像标签一致也可能对应不同的镜像 ID。改版前记录运行容器的实际镜像和挂载来源，迁移时才知道旧配置和数据从哪里恢复。端口被占用时先查占用的是原容器、宿主服务还是反代，避免把改端口作为第一步。改完端口还要重新核对后端、浏览器和设备的连接入口。


---

## 第二阶段：部署 EMQX

### 启动容器

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run -d \
  --name emqx \
  -p 1883:1883 \
  -p 18083:18083 \
  -e EMQX_DASHBOARD__DEFAULT_PASSWORD=123456 \
  emqx/emqx:latest
```

- `1883`：MQTT 协议端口，供设备连接。
- `18083`：Web 管理界面端口。
- 设置管理员密码（测试环境用弱密码，生产需强化）。

验证：浏览器访问 `http://202.199.6.249:18083`（账号 `admin`，密码 `123456`），进入 Dashboard 即成功。

---

## 第三阶段：部署 MinIO（对象存储）

### 第一次尝试失败

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=123456 \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

`docker ps` 看不见容器，`docker logs minio` 显示：

```
FATAL: MINIO_ROOT_PASSWORD length should be at least 8 characters
```

**原因**：MinIO 强制密码长度 ≥8，`123456` 仅 6 位。

### 解决

删除容器并重建，设置新密码 `admin123456`：

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker rm minio
docker run -d ... -e MINIO_ROOT_PASSWORD=admin123456 ...
```

访问 `http://202.199.6.249:9001`，用 `admin / admin123456` 登录成功。

**体会**：环境变量的细微约束往往在日志中直白体现，`docker logs` 是排错第一利器。

---

## 第四阶段：安全配置与验证

### 1. EMQX 开启 MQTT 账号认证

**作用**：防止未授权设备（或恶意客户端）随意连接 MQTT Broker，确保只有持有用户名/密码的 Jetson 才能收发指令。

- 如果没有认证，**任何人只要知道你的 MQTT 服务器 IP 和端口，就能直接发布指令**（比如让 Jetson 重启、更改模型参数、甚至下发恶意代码）。
- 配置用户名密码后，Jetson 连接 EMQX 时必须提供正确凭据，否则会被立刻拒绝。
- **对应你的场景**：Jetson 作为边缘设备，需要定时上报传感器数据或图片，同时接收云端的模型更新指令。认证验证客户端身份，授权（ACL）限制可操作的主题；用户名密码认证不提供加密，需配合 TLS。

操作流程（通过 Web 界面）：

1. 登录 `http://202.199.6.249:18083` → `Access Control` → `Authentication`。
2. 创建 `Password-Based` 认证，后端选择 `Built-in Database`。
3. 进入新认证器的 `Users` 页，添加用户如 `jetson` / `jetson123`。

**验证**：使用 MQTTX 客户端连接 `mqtt://202.199.6.249:1883`，输入上述凭据，成功订阅/发布消息。

### 2. MinIO 创建 Bucket 并测试预签名 URL

#### 创建 Bucket（存储桶）

**作用：组织和管理文件的逻辑分区。**

- `models` Bucket 专门存放 AI 模型文件（`.engine`、`.onnx`），比如你训练好的 TensorRT 模型。
- `images` Bucket 专门存放 Jetson 回传的图片/视频，比如质检拍的照片或监控视频帧。
- 你可以为不同 Bucket 设置不同的访问策略（例如 `images` 只允许写入，`models` 只允许读取），实现**最小权限原则**。

#### 生成预签名 URL（临时分享链接）

**作用：安全地向特定设备或服务临时授权文件访问，避免暴露存储系统的访问密钥。**

- **为什么需要？**  
  Jetson 通常没有权限直接访问 MinIO 的后端管理账号。如果直接把 MinIO 的 `admin` 密码烧录到 Jetson 上，一旦设备被破解，整个存储系统就失控了。
- **怎么做？**  
  你的后端服务（用仅有相应对象权限的专用账号）生成一个**带有效期、防篡改的 URL**，然后下发给 Jetson。Jetson 拿着这个 URL 就能在指定时间内下载最新的模型，或者上传一段视频。
- **举例**：  
  你更新了 `yolov8.engine` 模型上传到 `models` Bucket。  
  后端调用 MinIO API 生成一个 24 小时有效的预签名 URL：  `http://202.199.6.249:9000/models/yolov8.engine?X-Amz-...&X-Amz-Expires=86400`  
  Jetson 收到这个 URL 后直接下载，无需知道自己身在哪个 MinIO 实例，也不知道密码。链接到期后失效；有效期内任何持有链接的人均可能重复使用，应通过 HTTPS 传输并避免泄露。


#### 操作：

1. 登录 MinIO Console → `Buckets` → 分别创建 `models` 和 `images`（访问策略设为私有）。
2. 向 `models` 上传测试文件 `test.txt`。
3. 点击文件右侧 `Share`，设置过期时间（如 1 小时），生成预签名 URL。
4. 在新标签页访问该 URL，成功直接下载文件，无需凭证。

**安全意义**：链接提供有期限的访问授权，不是一次性令牌；有效期内仍可重放。Jetson 只拿到一个“临时票”，永远不接触 MinIO 的 root 账号。

#### 从两个服务各自通过到直传联动

| 环节 | 验收动作 | 失败时的判断 |
|---|---|---|
| EMQX Listener | 分别验证使用中的 TCP 或 WebSocket 入口，订阅并发布隔离测试消息 | 控制台能打开只说明管理面可达，MQTT 以 CONNACK 和实际收发为准 |
| MinIO API | 使用受限练习账号向指定 Bucket 写入一个小对象，再读取或查看元信息 | Console 登录正常不代表应用使用的对象 API 可达 |
| 容器间网络 | 从后端与代理所在网络分别验证依赖地址 | 容器内 localhost 指向当前容器，同网络才可直接用服务名访问 |
| 预签名上传 | 按原方法使用签名 URL，成功后查对象键、大小和内容类型 | 方法、域名、端口、路径、签名请求头和有效期可能参与验签 |
| MQTT 通知 | 对象写入成功后才发布 Bucket、对象键和事件编号 | Broker 收到通知并不说明后端已建立对象关联 |

**先确定谁访问签名 URL。** 后端 SDK 通过容器 DNS 连通对象 API，浏览器却可能无法解析同一地址。若内外入口不同，要分别验证 SDK 操作和浏览器上传地址，并保持代理转发的请求语义一致。外部 TLS、证书、CORS 和 DNS 由客户端所在网络验证。签名 URL 可以授予限时访问，排障记录只保留状态码、错误类型和脱敏路径。

```bash
# 使用已配置的 MinIO Client 别名，只查看隔离测试对象的元信息。
: "${MINIO_ALIAS:?请设置已配置的 mc 别名}"
: "${TEST_BUCKET:?请设置隔离测试桶}"
: "${TEST_OBJECT:?请设置测试对象键}"
mc stat "$MINIO_ALIAS/$TEST_BUCKET/$TEST_OBJECT"
```

签名返回 `403` 时，先看错误代码区分权限不足、签名不一致、请求时间偏差或链接过期。用同一客户端先请求对象 API，再从外部入口测试，比较方法、Host 和实际路径。`404` 时核对 Bucket、对象键和路径转义。`200` 但内容是 HTML 时，检查是否进入了 Console 或前端 SPA 回退页。浏览器跨域失败时，在开发者工具里区分预检失败与实际 PUT 返回失败。


---

## 技术栈与架构梳理

```
┌──────────┐       MQTT (1883)        ┌─────────┐
│  Jetson  │────────────────────────▶│  EMQX   │
│ 边缘盒子  │◀────────────────────────│ (MQTT)  │
└────┬─────┘   ＜指令、数据同步＞       └────┬────┘
     │                                     │
     │  HTTP (9000，当前未配置 TLS)                       │ WebHook/REST
     │  上传图片 / 下载模型                 │
     ▼                                     ▼
┌─────────┐                          ┌─────────┐
│  MinIO  │                          │ 后端服务 │
│ (存储)  │                          │ (未来)   │
└─────────┘                          └─────────┘
```

- **MinIO** 提供 S3 兼容 API，可无缝对接各类云原生工具。
- **EMQX** 内置规则引擎，未来可将设备消息直接转发至 Kafka/HTTP 端点。

### 对象、消息与业务记录如何对照

选一个测试站点和唯一编号。上传后记录对象存储的对象键与时间，订阅端记录收到的 MQTT 消息，最后从后端查询业务记录。若只有对象没有消息，查上传确认到发布之间的进程日志。若消息到了却没有业务行，查消费权限、解析或数据库写入。若业务行和对象都有但页面打不开，重点查后端重新签发的地址、有效期及浏览器网络。

上传与消息发布有先后关系。对象成功写入后，进程可能在发通知前退出。稳定事件编号和对象键让恢复时能补发。消费端收到相同编号两次时，应保持原记录或幂等更新，不再创建第二份关联。清理隔离测试对象前，先确认业务记录与待处理通知可一起回收，不把测试留在真实站点历史里。 [Docker 镜像归档](https://docs.docker.com/reference/cli/docker/image/save/) · [EMQX MQTT 概念](https://docs.emqx.com/en/emqx/latest/get-started/messaging/mqtt-concepts.html)

把镜像 ID、隔离对象键、测试事件编号、客户端所在网络和结果写在同一条记录里。后续更换主机或反代后复测同样的顺序，便于判断是部署变化还是旧样本失效。


---

## 面试讲述亮点

- **复杂网络环境适应**：在无外网、无代理的校园内网，采用离线镜像导入方案，体现了对 Docker 镜像传输机制的深入理解（`save`/`load`、SCP、镜像分层）。
- **快速排错方法论**：
  - 日志驱动：`docker logs` 秒级定位 MinIO 密码约束。
  - 端口测试：`curl` + `telnet` 判断网络连通性。
  - 配置核查：`docker info`、`systemctl show docker` 检查代理/守护进程参数。
- **安全设计原则**：最小权限、临时授权、凭证分离。不是“能用就行”，而是从一开始就按照生产标准规划认证与访问控制。
- **与现有系统共存**：在已承载 10+ 容器的服务器上平滑添加服务，未影响 Dify 等业务，体现了端口规划与资源隔离意识。

---

## 可进一步优化的方向（面试拔高）

1. **TLS 加密**：为 MQTT（8883）和 MinIO API（9000）添加自签名证书，确保数据传输安全。
2. **EMQX 规则引擎**：配置规则将特定主题的消息直接持久化到 MinIO 或转发到后端 API。
3. **MinIO 版本控制与生命周期**：对 `images` Bucket 开启版本控制，并设置自动过期删除老旧数据。
4. **监控与告警**：集成 Prometheus + Grafana 监控 EMQX 连接数、消息速率、MinIO 存储使用量。
5. **设备自动注册**：结合 EMQX 的 HTTP 认证/WebHook，实现 Jetson 首次上电时自动注册并分配权限。

---
