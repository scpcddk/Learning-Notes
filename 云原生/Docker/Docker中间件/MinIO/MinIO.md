# MinIO 使用笔记（换热站项目 · Docker 部署）

---

## 1. MinIO 是什么，我们用它做什么

MinIO 是一个开源的高性能对象存储服务，完全兼容 Amazon S3 API。可以理解为搭建一个**私有的对象存储服务器**，像网盘一样存取文件。

**在换热站项目中的用途：**

- 存储现场设备抓拍的图片（如热成像图、仪表盘照片）
- 存储历史数据备份文件（CSV 导出）
- 存储日志归档、固件升级包
- 前端 Web 页面直接上传/下载文件，不需经过后端转发
- **冷数据长期归档**：将 EMQX 收集的原始消息或 InfluxDB 的历史数据导出为 JSON/CSV 文件，存入 MinIO 降低时序库存储压力
- **模型/配置文件分发**：边缘计算盒子可从 MinIO 下载更新后的 AI 模型或换热站控制策略，通过预签名 URL 安全分发

> [!NOTE]
> 💡 **补充：版本选择建议**
>
> 由于 MinIO 在 RELEASE.2023-04-20 后将许可证从 Apache 2.0 改为 AGPL v3，且较新版本（约 RELEASE.2025-04-28 后）的 Docker 镜像默认移除了内置 Console（Web 管理界面），**学习/内网使用推荐固定版本**：
> 
> ```bash
> docker pull minio/minio:RELEASE.2025-04-08T15-41-24Z
> ```
>
> 该版本同时保留 Console 且许可证仍为 AGPL，对内部使用无影响。

---

## 2. Docker 快速安装

### 2.1 单节点启动（测试用）

```bash
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v /data/minio:/data \
  minio/minio server /data --console-address ":9001"
```

**端口说明**：

- `9000`：S3 API 端口（程序上传下载用）
- `9001`：Web 管理控制台端口

> ⚠️ 生产环境务必修改用户名密码，且使用环境变量文件而非命令行传参。密码至少 8 位，否则容器无法启动。

启动后访问 `http://服务器IP:9001`，用 `minioadmin / minioadmin` 登录。

> [!NOTE]
> 💡 **补充：模拟纠删码的单机多盘测试**
>
> 如果想在不搭建集群的情况下体验纠删码特性，可以在单节点指定多个数据目录：
> 
> ```bash
> docker run -d --name minio \
>   -p 9000:9000 -p 9001:9001 \
>   -e MINIO_ROOT_USER=minioadmin \
>   -e MINIO_ROOT_PASSWORD=minioadmin \
>   -v /data/disk1:/data/disk1 \
>   -v /data/disk2:/data/disk2 \
>   -v /data/disk3:/data/disk3 \
>   -v /data/disk4:/data/disk4 \
>   minio/minio server /data/disk{1...4} --console-address ":9001"
> ```
>
> 此时 MinIO 会自动启用纠删码（EC:2），允许损坏 2 块盘而不丢失数据。

> [!NOTE]
> 💡 **补充：内存与资源配置**
>
> MinIO 对内存要求不高（默认 1-2GB 足够），但使用纠删码时建议加上内存限制：
> 
> ```bash
> docker run -d --name minio \
>   -m 2g \
>   --restart=unless-stopped \
>   ...
> ```
>
> 如果磁盘是 SSD，可在启动时添加 `--add-host` 解决网络解析问题；生产环境建议设置 `ulimit -n 65536` 提高文件描述符限制。

### 2.2 数据持久化

上面 `-v /data/minio:/data` 把容器内数据映射到宿主机目录。生产环境建议挂载独立硬盘或使用 Docker Volume。**建议同时挂载 `certs` 目录用于 TLS 证书。**

> [!NOTE]
> 💡 **补充：使用环境变量文件（推荐生产）**
>
> 创建 `.env` 文件：
> 
> ```env
> MINIO_ROOT_USER=your_secure_user
> MINIO_ROOT_PASSWORD=your_secure_password_8chars_min
> ```
>
> 启动时：
> 
> ```bash
> docker run -d --name minio --env-file .env ...
> ```
>
> 这样凭证不会出现在命令行历史或 docker ps 中，更安全。

---

## 3. 核心概念（快速理解）

| 概念 | 说明 | 类比 |
|------|------|------|
| **Bucket（桶）** | **存放文件的容器**，类似顶层目录 | 相当于一个根文件夹 |
| **Object（对象）** | **存储的文件**，包含数据本身和元数据 | 就是文件 |
| **Access Key / Secret Key** | **访问凭证**，一对密钥 | 用户名 + 密码 |
| **Policy（策略）** | 控制桶的**访问权限**（公开/私有/读写） | 读写权限规则 |
| **Presigned URL** | 临时**签名链接**，可限定有效期和操作 | 有时效的分享链接 |

**我们项目中的典型用法：**

- 创建桶 `heat-station-images`（设备图片，私有）、`firmware`（固件，私有）、`public-reports`（报表，公开只读）
- 为不同应用生成不同的 Access Key，授予最小权限
- **通过预签名 URL 让边缘设备安全上传/下载，避免在设备上保存长期凭证**
- 利用**生命周期管理**自动清理过期图片，控制存储成本

> [!NOTE]
> 💡 **补充：副本与纠删码基础**
>
> MinIO 默认不复制单盘数据，生产环境分布式部署时使用**纠删码**（Erasure Code）代替多副本。典型配置：
> 
> - 4 盘：`EC:2`（可坏 2 盘）
> - 8 盘及以上：`EC:4`（可坏 4 盘）
> 存储利用率 = (N - M) / N，例如 8 盘 EC:4 利用率为 50%。
>
> 设置纠删码仅在**首次启动分布式集群时**通过命令行隐式确定，参数为 `server /mnt/disk{1...8}`，MinIO 会自动按节点和盘数计算 EC 配置。

---

## 4. 客户端工具与基本操作

### 4.1 使用 MinIO Client（mc）

`mc` 是 MinIO 官方命令行客户端，功能强大

**安装：**

```bash
# Docker 方式运行 mc
docker run --rm -it --entrypoint=/bin/sh minio/mc

# 或直接下载二进制（Linux）
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

**配置别名连接服务器：**

```bash
mc alias set myminio http://192.168.1.100:9000 minioadmin minioadmin
```

**创建桶：**

```bash
mc mb myminio/heat-station-images
```

**上传文件：**

```bash
mc cp ./snapshot.jpg myminio/heat-station-images/station1/20260101.jpg
```

**设置桶为公开读：**

```bash
mc anonymous set download myminio/public-reports
```

**生成临时分享链接（7天有效）：**

```bash
mc share download --expire 168h myminio/heat-station-images/station1/20260101.jpg
```

**生命周期管理（自动删除 N 天前的图片）：**

```bash
# 为 heat-station-images 桶添加生命周期规则：30天后自动删除对象
mc ilm rule add myminio/heat-station-images --expire-days 30
```

**桶备份（同步到另一个 MinIO 或本地目录）：**

```bash
mc mirror myminio/heat-station-images myminio-backup/heat-station-images
```

> [!NOTE]
> 💡 **补充：mc 的更多实用运维命令**
>
> 查看桶大小和对象数量：
> 
> ```bash
> mc du myminio/heat-station-images
> ```
>
> 批量删除前缀匹配的对象（清理临时文件）：
> 
> ```bash
> mc rm --recursive --force myminio/heat-station-images/temp/
> ```
>
> 查看桶的当前策略：
> 
> ```bash
> mc anonymous get myminio/heat-station-images
> ```
>
> 设置上传/下载带宽限速（单位：bit/s）：
> 
> ```bash
> mc --limit-rate 1MiB cp largefile.dat myminio/heat-station-images/
> ```
>
> 通过 `--json` 输出结构化日志，方便对接监控系统：
> 
> ```bash
> mc admin info myminio --json | jq '.info.buckets.count'
> ```

### 4.2 Python SDK 操作示例

换热站边缘网关经常用 Python，可以直接集成上传功能：

```python
from minio import Minio
from datetime import timedelta

# 创建客户端
client = Minio(
    "192.168.1.100:9000",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=False  # 内网用 False，公网应配置 TLS
)

# 上传文件
client.fput_object(
    "heat-station-images",
    "station1/snapshot.jpg",
    "/tmp/snapshot.jpg"
)

# 生成预签名 URL（1小时有效，用于前端直接展示）
url = client.presigned_get_object(
    "heat-station-images",
    "station1/snapshot.jpg",
    expires=timedelta(hours=1)
)
print(url)

# 下载文件
client.fget_object(
    "heat-station-images",
    "station1/snapshot.jpg",
    "/tmp/downloaded.jpg"
)

# 生成预签名上传 URL（允许设备直接上传，无需长期凭证）
upload_url = client.presigned_put_object(
    "heat-station-images",
    "station1/new_snapshot.jpg",
    expires=timedelta(minutes=30)
)
# 设备拿到这个 URL 后可用 PUT 请求上传文件
```

> [!NOTE]
> 💡 **补充：大文件分片上传（超过 128MB）**
>
> 超过 128MB 的文件，MinIO SDK 会自动进行分片（Multipart Upload）：
>
> ```python
> # 上传大文件（SDK 自动分片，默认分片大小 128MB）
> client.fput_object(
>     "heat-station-images",
>     "large_firmware.bin",
>     "/path/to/large_firmware.bin",
>     part_size=64 * 1024 * 1024  # 手动指定分片大小为 64MB
> )
> ```
>
> 分片上传支持断点续传吗？**原生不支持**，但可结合 `upload_id` 管理实现。对换热站场景，如果网络不稳定，建议使用预签名 URL 直传配合前端重试机制。
>
> **设置元数据（自定义标签）**：
> 
> ```python
> client.fput_object(
>     "heat-station-images",
>     "snapshot.jpg",
>     "/tmp/snapshot.jpg",
>     metadata={
>         "x-amz-meta-station-id": "station-001",
>         "x-amz-meta-capture-time": "2026-08-11T12:00:00Z"
>     }
> )
> ```

---

## 5. 用户与权限管理

### 5.1 创建专用 Access Key

在 Web 控制台 → Access Keys → Create Access Key，为不同服务创建独立密钥：

- `station-gateway`：只允许上传到 `heat-station-images`
- `web-backend`：可读写所有桶
- `report-reader`：只读 `public-reports`

> [!NOTE]
> 💡 **补充：mc 命令创建 Access Key**
>
> ```bash
> mc admin user add myminio station-gateway password123
> mc admin policy attach myminio readwrite --user station-gateway
> ```
>
> 查看已有用户列表：
> 
> ```bash
> mc admin user list myminio
> ```
>
> 禁用/启用用户：
> 
> ```bash
> mc admin user disable myminio station-gateway
> mc admin user enable myminio station-gateway
> ```

### 5.2 桶策略示例

以下策略授予对某个桶的只读权限（JSON 格式，在桶设置中粘贴）：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": ["*"] },
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::public-reports/*"]
    }
  ]
}
```

**更精细的策略：限制某个用户只能访问特定前缀**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": ["arn:aws:iam:::user/station1"] },
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": ["arn:aws:s3:::heat-station-images/station1/*"]
    }
  ]
}
```

> [!NOTE]
> 💡 **补充：策略中支持的常用 Action**
>
> | Action | 说明 |
> |--------|------|
> | `s3:PutObject` | 上传文件 |
> | `s3:GetObject` | 下载/读取文件 |
> | `s3:DeleteObject` | 删除文件 |
> | `s3:ListBucket` | 列出桶内文件列表（需同时授权桶本身） |
> | `s3:GetObjectVersion` | 读取文件的历史版本（开启版本控制后） |
>
> 注意：`ListBucket` 的 `Resource` 必须指向桶本身（不带 `/*`），而 `PutObject`/`GetObject` 的 `Resource` 必须带 `/*`。

### 5.3 安全建议

- **使用预签名 URL 代替长期密钥**：边缘设备网络环境不可控，避免将 Access Key 硬编码在设备固件中。
- **定期轮换 Access Key**：通过脚本定期更新密钥并分发。
- **启用 TLS 加密**：在公网或不可信内网中，配置 MinIO 的 TLS 证书，杜绝明文传输。
- **设置桶的默认加密**：可以配置服务端加密（SSE-S3），确保数据在磁盘上加密存储。

> [!NOTE]
> 💡 **补充：更多安全加固措施**
>
> - **IP 白名单**：使用 `mc admin policy` 结合 `Condition` 中的 `aws:SourceIp` 限制访问来源 IP：
>   
>  ```json
>   {
>     "Effect": "Deny",
>     "Action": ["s3:*"],
>     "Resource": ["arn:aws:s3:::heat-station-images/*"],
>     "Condition": {
>       "NotIpAddress": { "aws:SourceIp": "192.168.1.0/24" }
>     }
>   }
>   ```
>
> - **禁用 Console 公网暴露**：生产环境可将 Console 端口（9001）绑定为 `127.0.0.1`，通过 SSH 隧道或内网代理访问。
> - **启用审计日志**：通过环境变量 `MINIO_AUDIT_*` 将操作日志写入文件或 Elasticsearch。

> [!NOTE]
> 💡 **补充：对象锁定（Object Lock）实现防篡改与合规**
>
> 若换热站图片、归档数据需要防止被意外删除或恶意篡改，可在**开启版本控制**的桶上启用对象锁定：
> 
> - 创建桶时指定 `--with-lock`：`mc mb --with-lock myminio/locked-bucket`
> - 然后可以设置默认保留模式（合规/治理）和保留期限
> - 也可以对单个对象设置 Legal Hold（法律保留），阻止任何删除操作
> 
> **注意**：对象锁定一经设置，在保留期内**连 root 用户都无法删除**，适合关键证据固化。

---

## 6. Docker Compose 生产部署

```yaml
version: '3.7'
services:
  minio:
    image: minio/minio:latest
    container_name: minio
    restart: always
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: your-strong-password-here
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
      - ./certs:/root/.minio/certs  # TLS 证书挂载
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  minio-data:
    driver: local
```

**TLS 启用方法**：将公私钥文件（`private.key` 和 `public.crt`）放入 `./certs` 目录，MinIO 会自动启用 HTTPS。访问时需用 `https://`，SDK 设置 `secure=True`。

执行 `docker-compose up -d` 即可。

> [!NOTE]
> 💡 **补充：Nginx 反向代理配置（推荐生产）**
>
> 通常不在公网直接暴露 MinIO 端口，而是通过 Nginx 代理，统一管理域名和证书：
>
> ```nginx
> upstream minio_api {
>     server 127.0.0.1:9000;
> }
> upstream minio_console {
>     server 127.0.0.1:9001;
> }
>
> server {
>     listen 443 ssl;
>     server_name minio-api.your-domain.com;
>
>     ssl_certificate /path/to/cert.pem;
>     ssl_certificate_key /path/to/key.pem;
>
>     location / {
>         proxy_pass http://minio_api;
>         proxy_set_header Host $host;
>         proxy_set_header X-Real-IP $remote_addr;
>         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
>         # 大文件上传需要调大超时
>         client_max_body_size 10G;
>         proxy_read_timeout 300s;
>         proxy_connect_timeout 300s;
>     }
> }
>
> server {
>     listen 443 ssl;
>     server_name minio-console.your-domain.com;
>
>     ssl_certificate /path/to/cert.pem;
>     ssl_certificate_key /path/to/key.pem;
>
>     location / {
>         proxy_pass http://minio_console;
>         proxy_set_header Host $host;
>     }
> }
> ```
>
> 然后设置环境变量让 MinIO 感知外部代理地址：
> 
> ```yaml
> environment:
>   - MINIO_SERVER_URL=https://minio-api.your-domain.com
>   - MINIO_BROWSER_REDIRECT_URL=https://minio-console.your-domain.com
> ```

> [!NOTE]
> 💡 **补充：快速生成自签名 TLS 证书（测试/内网用）**
>
> ```bash
> # 生成私钥和证书（有效期 3650 天）
> openssl req -x509 -newkey rsa:4096 -keyout private.key -out public.crt -days 3650 -nodes -subj "/CN=minio.local"
> # 将两个文件放入 ./certs 目录挂载即可
> ```
>
> 正式公网服务建议使用 Let's Encrypt 或受信任 CA 签发证书。

---

## 7. 与 EMQX 规则引擎集成

MinIO 通常作为 EMQX 数据流的目标之一，比如设备图片通过 MQTT 上传后自动存入 MinIO。

### 方案一：EMQX → HTTP 服务 → MinIO

EMQX 规则引擎将消息转发到自建 HTTP 服务，该服务负责处理二进制数据并调用 MinIO SDK 存储。

**典型流水线**：
1. 换热站 PLC 通过 MQTT 发送 JSON 消息，其中图片字段为 Base64 编码。
2. EMQX 规则引擎提取 `clientid`、`topic` 和图片 Base64 字符串。
3. 规则动作发送到后端 HTTP 接口 `/api/image-upload`。
4. 后端服务解码 Base64，生成唯一文件名，调用 MinIO SDK 上传。
5. 返回预签名 URL 存储到数据库供前端查看。

### 方案二：使用 MinIO 的 MQTT 通知（企业版）

MinIO 支持通过 MQTT 发送桶事件通知，反过来也可以配合使用，但需注意版本和企业版功能差异。

**简单场景：设备直接上传图片**

设备 → (MQTT 消息，图片 Base64 编码) → EMQX → 规则引擎 → HTTP 服务（解码并存入 MinIO）

如果项目有此种需求，可在 EMQX 规则动作中选择“发送数据到 Web 服务”，将消息体 POST 给中间服务处理。

**性能优化建议**：大图片不适合用 Base64 走 MQTT，应让设备通过预签名 URL 直传 MinIO，MQTT 只传递上传完成的通知（包含对象名）。

> [!NOTE]
> 💡 **补充：MinIO 原生桶事件通知机制**
>
> MinIO 本身支持将桶内的 PUT/DELETE 事件通过 Webhook、AMQP、Kafka、Redis、NATS 等渠道推送。
>
> **配置 Webhook 通知（接收上传完成事件）**：
> 
> ```bash
> mc admin config set myminio notify_webhook:1 \
>   endpoint="http://your-backend:8080/minio-callback" \
>   queue_dir="/tmp/webhook" \
>   queue_limit="10000"
> ```
>
> 然后重启 MinIO 生效，再通过 `mc event add` 为指定桶绑定事件：
> 
> ```bash
> mc event add myminio/heat-station-images \
>   arn:minio:sqs::1:webhook \
>   --event put,delete
> ```
>
> 这样每次文件上传/删除时，MinIO 会自动回调你指定的后端接口，携带对象元数据信息，非常适合用于异步触发后续任务（如缩略图生成、入库记录）。
>
> 对于 Kafka 用户，原生也支持将事件推送给 Kafka，可集成进现有的数据管道。

---

## 8. 监控与运维备忘

### 8.1 健康检查

MinIO 提供健康端点：
```bash
curl http://localhost:9000/minio/health/live
curl http://localhost:9000/minio/health/ready
```

可在 Prometheus 配置中抓取监控指标：
```yaml
- job_name: minio
  metrics_path: /minio/v2/metrics/cluster
  static_configs:
    - targets: ['192.168.1.100:9000']
```

> [!NOTE]
> 💡 **补充：Prometheus 抓取需启用认证（Bearer Token）**
>
> 如果 MinIO 启用了认证，需要按如下方式配置：
> 
> ```yaml
> - job_name: minio
>   metrics_path: /minio/v2/metrics/cluster
>   static_configs:
>     - targets: ['192.168.1.100:9000']
>   authorization:
>     credentials: "Bearer <your-access-key>:<your-secret-key>"
> ```
>
> 也可以使用 `mc admin prometheus generate myminio` 自动生成带认证的抓取配置。
>
> **关键监控指标**：
> 
> - `minio_bucket_usage_total_bytes`：桶已用容量
> - `minio_bucket_usage_object_total`：桶对象总数
> - `minio_node_disk_free_bytes` / `minio_node_disk_total_bytes`：磁盘剩余与总容量
> - `minio_s3_requests_total`：API 请求速率（按 method 分类）
> - `minio_s3_errors_total`：错误请求总数（按 error code 分类）
> - `minio_healing_disk_count`：正在修复的磁盘数
>
> **Grafana 仪表盘推荐**：官方提供 `MinIO Cluster Dashboard` (ID: 13502)，可快速导入。

### 8.2 日志查看

```bash
docker logs -f minio
```

> [!NOTE]
> 💡 **补充：结构化日志输出（便于对接日志系统）**
>
> MinIO 支持将日志以 JSON 格式输出，便于 ELK/Loki 采集：
> ```yaml
> environment:
>   - MINIO_JSON_LOGGING=on
> ```
> 同时可配置审计日志目标：
> ```bash
> mc admin config set myminio audit_webhook:1 endpoint="http://your-loki:3100/loki/api/v1/push"
> ```
> 将详细操作记录转发给日志聚合系统，便于事后审计。

### 8.3 备份

```bash
# 使用 mc mirror 同步整个桶到备份目录
mc mirror myminio/heat-station-images /backup/heat-station-images/

# 同步到远程 MinIO 实例（异地灾备）
mc mirror myminio/heat-station-images myminio-backup/heat-station-images
```

> [!NOTE]
> 💡 **补充：使用 `mc admin` 进行集群元数据备份**
>
> 除了文件数据，IAM 用户、策略等元数据也需要备份：
> ```bash
> mc admin cluster iam export myminio > minio-iam-backup.json
> ```
>
> 恢复时：
> ```bash
> mc admin cluster iam import myminio < minio-iam-backup.json
> ```
>
> 这一步在灾难恢复时能快速恢复权限体系，非常关键。

### 8.4 扩容

单机容量不足时可使用 MinIO 分布式模式，启动多个节点组成集群。需要至少 4 个节点（纠删码要求），规划时注意。

**分布式启动示例（4节点）：**
```bash
docker run -d --name minio1 ... minio/minio server http://minio{1...4}/data
```
需配置统一的网络和存储，生产环境建议结合 Kubernetes 或使用官方推荐的编排方式。

> [!NOTE]
> 💡 **补充：分布式集群的扩容方式**
>
> MinIO 支持两种扩容方式：
> 
> 1. **增加节点**（推荐）：新节点加入现有集群，MinIO 自动重平衡数据（需使用相同的 `MINIO_ROOT_USER` 和 `MINIO_ROOT_PASSWORD`）。
> 2. **增加磁盘**（需重启）：在现有节点增加磁盘挂载点，修改启动命令中的磁盘路径列表后重启，MinIO 会在后台逐步扩展数据分布。
>
> 扩容时注意：新加节点/盘数必须与现有集群的节点数/盘数**成倍数关系**（如现有 4 节点，可扩至 8 节点），否则纠删码配置会改变导致数据重建性能下降。
>
> 使用 K8s 部署时，推荐使用 MinIO Operator（`minio-operator`）进行自动化和滚动扩容。

### 8.5 故障排查

- **容器启动失败，日志提示密码过短**：Root 密码长度需 ≥ 8 位。
- **上传失败，提示签名不匹配**：检查系统时间是否同步，MinIO 依赖正确的时间进行签名校验。使用 `ntpdate` 或 `chrony` 同步。
- **存储空间不足**：配置监控告警并启用生命周期管理自动清理；定期检查 `mc admin info` 的磁盘使用情况。

> [!NOTE]
> 💡 **补充：更多常见问题**
>
> - **Web UI 不显示 Console 入口**：新版镜像已移除内置 Console，需指定旧版本 `RELEASE.2025-04-08T15-41-24Z` 或单独部署 Console 容器。
> - **通过 Nginx 代理后上传大文件超时或失败**：除调大 `client_max_body_size` 和 `proxy_read_timeout` 外，还需添加 `proxy_request_buffering off;` 避免 Nginx 缓冲导致内存占用过高。
> - **`mc` 命令连接提示 `The request signature we calculated does not match the signature you provided`**：检查服务器和客户端时间差是否在 15 分钟以内；检查 Access Key/Secret Key 是否正确且未过期。
> - **MinIO 服务运行但 `mc admin info` 很慢**：检查磁盘 IO 是否有问题，或 bucket 数量过多（单实例建议不超过 10 万个 bucket）。
> - **磁盘即将写满的预警阈值**：MinIO 默认磁盘使用率达到 90% 时会进入只读模式，可通过环境变量 `MINIO_DISK_USAGE_WARNING_PERCENT`（默认 90）和 `MINIO_DISK_USAGE_CRITICAL_PERCENT`（默认 95）调整预警阈值。

> [!NOTE]
> 💡 **补充：调整日志级别与调试输出**
>
> 排查复杂问题时，可临时开启更详细的日志：
> ```bash
> mc admin config set myminio logger_webhook:1 endpoint="http://logstash:5000" level="debug"
> ```
> 或通过环境变量 `MINIO_LOG_LEVEL=DEBUG` 启动容器，输出更丰富的请求处理细节（注意：生产环境不宜长期开启 DEBUG）。

---

## 9. 常用命令速查

```bash
mc alias set <别名> <服务地址> <AccessKey> <SecretKey>  # 添加服务
mc ls <别名>                       # 列出所有桶
mc mb <别名>/<桶名>               # 创建桶
mc cp <源> <目标>                  # 复制文件
mc rm <别名>/<桶名>/<对象>        # 删除对象
mc policy set download <别名>/<桶名>   # 设为公开读
mc policy set none <别名>/<桶名>       # 设为私有
mc admin info <别名>               # 查看服务信息
mc admin user add <别名> <用户> <密码>  # 添加用户
mc admin policy attach <别名> readwrite --user <用户>  # 绑定策略
mc ilm rule add <别名>/<桶名> --expire-days <天数>  # 设置生命周期
mc share download --expire <时间> <别名>/<桶名>/<对象>  # 生成临时下载链接
mc share upload --expire <时间> <别名>/<桶名>/<对象>  # 生成临时上传链接
mc mirror <源别名>/<桶> <目标别名>/<桶>  # 镜像/备份整个桶
```

> [!NOTE]
> 💡 **补充：命令速查扩展**
>
> **站点复制（Site Replication）**：当有多个 MinIO 集群时，可通过站点复制实现 Bucket 和 IAM 的跨集群同步：
> 
> ```bash
> mc admin replicate add myminio1 myminio2
> ```
>
> 注意：站点复制需所有集群版本一致，且启用虚拟主机风格（`MINIO_DOMAIN`）。
>
> **服务状态和重启**：
> 
> ```bash
> mc admin service status myminio        # 查看服务状态
> mc admin service restart myminio       # 重启服务（分布式集群会逐个重启）
> ```
>
> **查看桶配额**：
> 
> ```bash
> mc admin bucket quota myminio/heat-station-images
> ```
>
> **对象版本控制操作（若已开启）**：
> 
> ```bash
> mc ls --versions myminio/heat-station-images/station1/snapshot.jpg
> mc rm --version-id <version-id> myminio/heat-station-images/station1/snapshot.jpg  # 删除特定版本
> ```

> [!NOTE]
> 💡 **补充：版本控制与对象锁定相关命令**
>
> ```bash
> mc version enable myminio/<桶名>                     # 开启桶版本控制
> mc mb --with-lock myminio/<桶名>                      # 创建支持锁定的桶
> mc retention set --default compliance 30d myminio/<桶名>   # 设置默认保留30天（合规模式）
> mc legalhold set myminio/<桶名>/<对象>                # 对某个对象设置法律保留
> mc admin update myminio                               # 更新 MinIO 服务（热更新，保留数据）
> ```

---

> **提示**：这份笔记已涵盖开发、运维、安全及与 EMQX 配合的多种场景，可根据项目阶段按需查阅。后续深化时可补充 Kubernetes 部署、版本控制（Bucket Versioning）及站点复制等高阶特性。

---

[参考文档](https://www.fengfengzhidao.com/article/64cHuJsB0_1Q2CSUEGs3)

[参考网课](https://www.bilibili.com/video/BV1kFrjBQEoY/?spm_id_from=333.1391.0.0&vd_source=e0c0ad2a316e90d4078b1131e8182407)

---
