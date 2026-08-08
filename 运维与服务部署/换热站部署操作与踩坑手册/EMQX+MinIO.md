# EMQX + MinIO

---

## 项目背景

> **目标**：为 Jetson 边缘 AI 盒子搭建一个与云端通信的基础设施层，实现设备指令下发、数据回传、模型安全分发。

- **MQTT Broker（EMQX）**：充当 Jetson 与云端服务的“对讲机”，负责双向消息传递。
- **对象存储（MinIO）**：存放 Jetson 回传的图片/视频，以及云端更新的 AI 模型文件（如 `.engine`、`.onnx`）。
- **运行环境**：学校实验室的一台 Ubuntu 22.04 服务器，**仅限校园网访问，无法直接连接外网**，且已承载其他生产容器（Nginx、MySQL、Dify 等），需要在不影响现有服务的前提下部署。

---

## 

登录服务器 `202.199.6.249`（用户 `neu`）后，先摸清现有资源：

```bash
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

但该代理已失效，Docker 仍尝试直连 Docker Hub 且优先走 IPv6。

#### 尝试配置镜像加速 + 禁用 IPv6

```bash
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"],
  "ipv6": false
}
EOF
sudo systemctl restart docker
```

重启后 `docker pull` 仍失败，因为**校园网服务器根本不能访问外网**，加速器同样需要出校。

#### 代理探测

根据实验室提供的 `202.199.6.249` 测试 HTTP 代理（常见端口 8080、3128）：

```bash
curl -I --proxy http://202.199.6.249:8080 https://www.baidu.com   # 连接被拒绝
curl -I --proxy http://202.199.6.249:3128 https://www.baidu.com   # 连接被拒绝
```

确认该地址并非 HTTP 代理，很可能仅是内网 IP。

### 3. 最终方案：离线镜像导入

**思路**：在个人电脑（可上网）拉取镜像并打包，再通过 SCP 传到服务器加载。

- 个人电脑（Windows + Docker Desktop 29.5.2）：
  
  ```powershell
  docker pull emqx/emqx:latest
  docker save emqx/emqx:latest -o emqx.tar
  docker pull minio/minio:latest
  docker save minio/minio:latest -o minio.tar
  ```

- SCP 传输到服务器（跳过首次主机验证）：
  
  ```powershell
  scp -o StrictHostKeyChecking=no emqx.tar neu@202.199.6.249:/home/neu/
  scp minio.tar neu@202.199.6.249:/home/neu/
  ```

- 服务器加载：
  
  ```bash
  docker load -i /home/neu/emqx.tar
  docker load -i /home/neu/minio.tar
  ```

**收获**：掌握了 Docker 离线部署能力，理解守护进程配置、代理设置与镜像分发的多种手段。

---

## 第二阶段：部署 EMQX

### 启动容器

```bash
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
- **对应你的场景**：Jetson 作为边缘设备，需要定时上报传感器数据或图片，同时接收云端的模型更新指令。认证保证了这条通道是“专线”，不会混入干扰信息。

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
  你的后端服务（用 MinIO 的管理账号）生成一个**带有效期、防篡改的 URL**，然后下发给 Jetson。Jetson 拿着这个 URL 就能在指定时间内下载最新的模型，或者上传一段视频。
- **举例**：  
  你更新了 `yolov8.engine` 模型上传到 `models` Bucket。  
  后端调用 MinIO API 生成一个 24 小时有效的预签名 URL：  `http://202.199.6.249:9000/models/yolov8.engine?X-Amz-...&X-Amz-Expires=86400`  
  Jetson 收到这个 URL 后直接下载，无需知道自己身在哪个 MinIO 实例，也不知道密码。24 小时后链接自动失效，别人即使抓包拿到链接也没用了。


#### 操作：

1. 登录 MinIO Console → `Buckets` → 分别创建 `models` 和 `images`（访问策略设为私有）。
2. 向 `models` 上传测试文件 `test.txt`。
3. 点击文件右侧 `Share`，设置过期时间（如 1 小时），生成预签名 URL。
4. 在新标签页访问该 URL，成功直接下载文件，无需凭证。

**安全意义**：链接过期即失效，可防重放攻击。Jetson 只拿到一个“临时票”，永远不接触 MinIO 的 root 账号。

---

## 技术栈与架构梳理

```
┌──────────┐       MQTT (1883)        ┌─────────┐
│  Jetson  │────────────────────────▶│  EMQX   │
│ 边缘盒子  │◀────────────────────────│ (MQTT)  │
└────┬─────┘   ＜指令、数据同步＞       └────┬────┘
     │                                     │
     │  HTTPS (9000)                       │ WebHook/REST
     │  上传图片 / 下载模型                 │
     ▼                                     ▼
┌─────────┐                          ┌─────────┐
│  MinIO  │                          │ 后端服务 │
│ (存储)  │                          │ (未来)   │
└─────────┘                          └─────────┘
```

- **MinIO** 提供 S3 兼容 API，可无缝对接各类云原生工具。
- **EMQX** 内置规则引擎，未来可将设备消息直接转发至 Kafka/HTTP 端点。

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
