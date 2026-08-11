# MinIO 使用笔记（换热站项目 · Docker 部署）

---

## 1. MinIO 是什么，我们用它做什么

MinIO 是一个开源的高性能对象存储服务，完全兼容 Amazon S3 API。可视为一套**私有对象存储服务器**，用于集中管理文件。

**在换热站项目中的典型用途**：

- 存储现场设备抓拍的图片（热成像图、仪表盘照片）
- 历史数据备份文件（CSV 导出）长期归档
- 日志归档、固件升级包分发
- 边缘 AI 模型文件（模型权重、配置文件）的分发与更新
- 前端 Web 页面或移动端直接通过预签名 URL 上传/下载，避免后端中转

> **版本选择**：MinIO 在 `RELEASE.2023-04-20` 后将许可证从 Apache 2.0 改为 AGPL v3，且较新版本（约 `RELEASE.2025-04-28` 后）的 Docker 镜像移除了内置 Console（Web 管理界面）。**学习/内网使用推荐固定版本**：
> ```bash
> docker pull minio/minio:RELEASE.2025-04-08T15-41-24Z
> ```
> 该版本保留 Console 且许可证仍为 AGPL，对内部使用无影响。

---

## 2. Docker 快速安装与配置

### 2.1 单节点启动（测试用）

```bash
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v /data/minio:/data \
  minio/minio:RELEASE.2025-04-08T15-41-24Z \
  server /data --console-address ":9001"
```

**端口说明**：

- `9000`：S3 API 端口（程序上传下载用）
- `9001`：Web 管理控制台端口

> 生产环境务必修改默认用户名密码（密码至少 8 位），建议使用环境变量文件（`.env`）传递凭证，避免暴露在命令行。

启动后访问 `http://服务器IP:9001` 即可登录。

### 2.2 模拟纠删码的单机多盘测试

若想在不搭建集群的情况下体验纠删码特性，可在单节点指定多个数据目录：

```bash
docker run -d --name minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v /data/disk1:/data/disk1 \
  -v /data/disk2:/data/disk2 \
  -v /data/disk3:/data/disk3 \
  -v /data/disk4:/data/disk4 \
  minio/minio:RELEASE.2025-04-08T15-41-24Z \
  server /data/disk{1...4} --console-address ":9001"
```

此时 MinIO 会自动启用纠删码（EC:2），允许损坏任意 2 块盘而不丢失数据。

### 2.3 生产环境资源配置建议

- **内存**：默认 1~2GB 足够，可通过 `-m 2g` 限制容器内存。
- **文件描述符**：生产环境建议设置 `ulimit -n 65536`。
- **挂载目录**：除数据目录外，建议同时挂载 `certs` 目录用于 TLS 证书。

---

## 3. 核心概念与数据安全

| 概念 | 说明 | 类比 |
|------|------|------|
| **Bucket（桶）** | 存放文件的容器，类似顶层目录 | 相当于一个根文件夹 |
| **Object（对象）** | 存储的文件，包含数据本身和元数据 | 就是文件 |
| **Access Key / Secret Key** | 访问凭证，一对密钥 | 用户名 + 密码 |
| **Policy（策略）** | 控制桶的访问权限（公开/私有/读写） | 读写权限规则 |
| **Presigned URL** | 临时签名链接，可限定有效期和操作 | 有时效的分享链接 |

**换热站项目典型用法**：

- 创建多个桶：`heat-station-images`（设备图片，私有）、`firmware`（固件，私有）、`public-reports`（报表，公开只读）
- 为不同应用生成独立的 Access Key，授予最小权限
- **通过预签名 URL 让边缘设备安全上传/下载，避免在设备上保存长期凭证**
- 利用**生命周期管理**自动清理过期图片，控制存储成本
- 关键数据桶开启**版本控制**和**对象锁定**，防止误删或篡改

**纠删码基础**：分布式部署时 MinIO 使用纠删码（Erasure Code）代替多副本。典型配置：
- 4 盘：`EC:2`（可坏 2 盘）
- 8 盘及以上：`EC:4`（可坏 4 盘）
存储利用率 = (N - M) / N，例如 8 盘 EC:4 利用率为 50%。

---

## 4. 存储桶操作（Bucket 管理）

在 Web 控制台（`:9001`）左侧「Buckets」→ 创建或点击已有桶，可进行高级配置。

### 4.1 创建存储桶

点击 **「Create Bucket」**，输入桶名（全局唯一），配置以下选项：

| 配置项 | 说明 | 换热站项目建议 |
|--------|------|----------------|
| **Versioning（版本控制）** | 开启后保留对象所有历史版本，可随时回滚 | `heat-station-images` 建议开启，防止误覆盖抓拍图片 |
| **Object Locking（对象锁定）** | 开启后桶内对象可设置「禁止删除/修改」的保留期 | **必须在创建桶时决定**，不可事后开启。归档/审计类数据建议开启 |
| **Quota（配额）** | 限制桶的最大存储容量（如 100GB） | 为每个换热站桶设置配额，避免单站占用过多空间 |

> ⚠️ **注意**：Object Locking 一旦开启即**不可关闭**，且需同时启用 Versioning，请谨慎决策。

### 4.2 版本控制（Versioning）

开启后，每次上传同名文件都会生成新版本，旧版本保留并可随时恢复。

**Web 操作**：Bucket → Config → Versioning → Enable

**命令行操作**：
```bash
mc version enable myminio/heat-station-images
```

**查看历史版本**：
```bash
mc ls --versions myminio/heat-station-images/station1/snapshot.jpg
```

**恢复历史版本**（下载特定版本并重新上传）：
```bash
mc cp --version-id <版本ID> myminio/heat-station-images/station1/snapshot.jpg ./restored.jpg
```

### 4.3 对象锁定（Object Locking）与保留策略

**适用场景**：合规审计数据、证据固化、关键配置文件防篡改。

**创建支持锁定的桶**：
```bash
mc mb --with-lock myminio/audit-logs
```

**设置默认保留策略**（合规模式，保留 30 天）：
```bash
mc retention set --default compliance 30d myminio/audit-logs
```

**保留模式对比**：

| 模式 | 特性 | 适用场景 |
|------|------|----------|
| **Compliance（合规）** | 保留期内**任何人**（含 root）都无法删除/修改 | 金融审计、司法证据、政府监管数据 |
| **Governance（治理）** | 普通用户不可删，但拥有特殊权限的管理员可提前释放 | 企业内控、项目文档归档（需要灵活性） |

**对单个对象设置 Legal Hold（法律保留）**：
```bash
mc legalhold set myminio/audit-logs/2026-08-11-station1.log
```

### 4.4 配额（Quota）

限制桶的存储上限，防止单桶无限膨胀。

**Web 操作**：Bucket → Config → Quota → 输入上限（如 `100GB`）

**命令行设置**：
```bash
mc admin bucket quota myminio/heat-station-images --quota 100GB
```

**查看当前配额使用情况**：
```bash
mc du myminio/heat-station-images
```

### 4.5 生命周期管理（Lifecycle）

自动清理过期文件，降低存储成本。

**场景示例**：设备抓拍图片 30 天后自动删除。

**命令行设置（30 天后自动删除）**：
```bash
mc ilm rule add myminio/heat-station-images --expire-days 30
```

**设置转换到冷存储**（若 MinIO 配置了冷热分层）：
```bash
mc ilm rule add myminio/heat-station-images --transition-days 7 --transition-tier cold-tier
```

**查看已有生命周期规则**：
```bash
mc ilm rule list myminio/heat-station-images
```

### 4.6 访问策略（Bucket Policy）

在 Web 控制台 Bucket → Config → Policy 中，可快速设置：
- **Private（私有）**：仅授权用户可读写（默认）
- **Public（公开读）**：所有人可下载，但不可上传/删除
- **Custom（自定义）**：粘贴 JSON 策略，精细控制读写权限

**命令行设置公开读**：
```bash
mc anonymous set download myminio/public-reports
```

---

## 5. 客户端工具与代码集成

### 5.1 使用 MinIO Client（mc）

`mc` 是官方命令行客户端，功能强大。

**安装**（Linux）：
```bash
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

**配置别名连接服务器**：
```bash
mc alias set myminio http://192.168.1.100:9000 minioadmin minioadmin
```

**常用操作**：
```bash
mc mb myminio/heat-station-images          # 创建桶
mc cp ./snapshot.jpg myminio/heat-station-images/station1/20260101.jpg   # 上传
mc ls myminio/heat-station-images           # 列出桶内容
mc rm myminio/heat-station-images/temp/     # 删除对象（慎用）
mc share download --expire 168h myminio/heat-station-images/station1/20260101.jpg   # 生成临时下载链接（7天有效）
mc mirror myminio/heat-station-images /backup/   # 同步/备份到本地目录
```

### 5.2 Python SDK 操作示例

换热站边缘网关常用 Python，可直接集成上传功能：

```python
from minio import Minio
from datetime import timedelta

client = Minio(
    "192.168.1.100:9000",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=False          # 内网可 False，公网应启用 TLS
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
# 设备拿到此 URL 后可直接 PUT 上传文件
```

**大文件分片上传**（超过 128MB 自动分片，可手动指定分片大小）：
```python
client.fput_object(
    "heat-station-images",
    "large_firmware.bin",
    "/path/to/large_firmware.bin",
    part_size=64 * 1024 * 1024   # 64MB 分片
)
```

**自定义元数据**（标签）：
```python
client.fput_object(
    "heat-station-images",
    "snapshot.jpg",
    "/tmp/snapshot.jpg",
    metadata={
        "x-amz-meta-station-id": "station-001",
        "x-amz-meta-capture-time": "2026-08-11T12:00:00Z"
    }
)
```

### 5.3 Java SDK 操作示例

换热站边缘网关若基于 Java 开发，可直接集成 MinIO Java SDK。添加 Maven 依赖：

```xml
<dependency>
    <groupId>io.minio</groupId>
    <artifactId>minio</artifactId>
    <version>8.5.7</version>
</dependency>
```

**完整示例代码**：

```java
import io.minio.*;
import io.minio.http.Method;
import io.minio.messages.Part;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

public class MinioExample {
    public static void main(String[] args) throws Exception {
        // 1. 创建客户端
        MinioClient minioClient = MinioClient.builder()
                .endpoint("http://192.168.1.100:9000")
                .credentials("your-access-key", "your-secret-key")
                .build();

        // 2. 上传文件（小文件）
        minioClient.uploadObject(
                UploadObjectArgs.builder()
                        .bucket("heat-station-images")
                        .object("station1/snapshot.jpg")
                        .filename("/tmp/snapshot.jpg")
                        .build()
        );

        // 3. 生成预签名下载 URL（1小时有效）
        String downloadUrl = minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket("heat-station-images")
                        .object("station1/snapshot.jpg")
                        .expiry(1, TimeUnit.HOURS)
                        .build()
        );
        System.out.println("下载URL: " + downloadUrl);

        // 4. 下载文件
        minioClient.downloadObject(
                DownloadObjectArgs.builder()
                        .bucket("heat-station-images")
                        .object("station1/snapshot.jpg")
                        .filename("/tmp/downloaded.jpg")
                        .build()
        );

        // 5. 生成预签名上传 URL（30分钟有效，设备可直接 PUT 上传）
        String uploadUrl = minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.PUT)
                        .bucket("heat-station-images")
                        .object("station1/new_snapshot.jpg")
                        .expiry(30, TimeUnit.MINUTES)
                        .build()
        );
        System.out.println("上传URL: " + uploadUrl);

        // 6. 大文件分片上传（手动管理分片）
        String bucketName = "heat-station-images";
        String objectName = "large_firmware.bin";
        String filePath = "/path/to/large_firmware.bin";
        long partSize = 64 * 1024 * 1024; // 64MB 分片

        // 创建分片上传请求
        String uploadId = minioClient.createMultipartUpload(
                CreateMultipartUploadArgs.builder()
                        .bucket(bucketName)
                        .object(objectName)
                        .build()
        ).result().uploadId();

        // 分片上传（示例：假设文件大小已知，实际需循环读取）
        try (FileInputStream fis = new FileInputStream(filePath)) {
            int partNumber = 1;
            byte[] buffer = new byte[(int) partSize];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) > 0) {
                // 实际需要将每个分片上传并收集 etag
                // 这里仅示意，完整实现需使用 uploadPart 方法
                // UploadPartResponse response = minioClient.uploadPart(...);
                // 收集 Part 信息
                partNumber++;
            }
        }
        // 完成分片上传（需传入所有 Part 的 etag 和 partNumber）
        // minioClient.completeMultipartUpload(...);

        // 7. 设置自定义元数据（标签）
        minioClient.uploadObject(
                UploadObjectArgs.builder()
                        .bucket("heat-station-images")
                        .object("snapshot.jpg")
                        .filename("/tmp/snapshot.jpg")
                        .userMetadata(Map.of(
                                "x-amz-meta-station-id", "station-001",
                                "x-amz-meta-capture-time", "2026-08-11T12:00:00Z"
                        ))
                        .build()
        );
    }
}
```

> **说明**：
> - 预签名 URL 生成使用 `getPresignedObjectUrl`，支持 GET（下载）和 PUT（上传）。
> - 大文件分片上传需要自行管理 `uploadId` 和 `Part` 列表，建议对于超大文件（> 5GB）采用此方式；若文件小于 128MB，直接使用 `uploadObject` 即可自动处理。
> - 元数据通过 `userMetadata` 设置，注意键需以 `x-amz-meta-` 开头。
> - 生产环境中应使用连接池、超时配置等，可通过 `.build()` 前设置 `connectTimeout`、`writeTimeout` 等参数。

---

## 6. 用户权限与安全加固

### 6.1 创建专用 Access Key

在 Web 控制台 → Access Keys → Create Access Key，为不同服务创建独立密钥：
- `station-gateway`：只允许上传到 `heat-station-images`
- `web-backend`：可读写所有桶
- `report-reader`：只读 `public-reports`

**命令行管理用户**：
```bash
mc admin user add myminio station-gateway password123
mc admin policy attach myminio readwrite --user station-gateway
mc admin user list myminio
mc admin user disable myminio station-gateway
```

### 6.2 桶策略示例

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

**精细策略**：限制某个用户只能访问特定前缀（例如 station1 只能操作自己的目录）：
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

### 6.3 安全加固措施

- **使用预签名 URL 代替长期密钥**：边缘设备不应硬编码 Access Key。
- **定期轮换 Access Key**：通过脚本定期更新并分发。
- **启用 TLS 加密**：公网或不可信内网必须配置证书。
- **IP 白名单**：在策略中加入 `aws:SourceIp` 条件限制访问来源。
- **禁用 Console 公网暴露**：生产环境可将 Console 端口绑定为 `127.0.0.1`，通过 SSH 隧道或内网代理访问。
- **启用审计日志**：配置 `MINIO_AUDIT_*` 将操作日志写入文件或 Elasticsearch。

---

## 7. Docker Compose & Nginx 反向代理生产配置

### 7.1 Docker Compose 部署（固定版本）

```yaml
services:
  minio:
    image: minio/minio:RELEASE.2025-04-08T15-41-24Z
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
      - ./certs:/root/.minio/certs   # TLS 证书挂载
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  minio-data:
    driver: local
```

> **TLS 启用**：将 `private.key` 和 `public.crt` 放入 `./certs` 目录，MinIO 自动启用 HTTPS。SDK 需设置 `secure=True`。

### 7.2 Nginx 反向代理（推荐）

不在公网直接暴露 MinIO 端口，通过 Nginx 代理，统一管理域名和证书。

```nginx
upstream minio_api {
    server 127.0.0.1:9000;
}
upstream minio_console {
    server 127.0.0.1:9001;
}

server {
    listen 443 ssl;
    server_name minio-api.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://minio_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 10G;          # 支持大文件上传
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_request_buffering off;       # 避免 Nginx 缓冲大文件导致内存占满
    }
}

server {
    listen 443 ssl;
    server_name minio-console.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://minio_console;
        proxy_set_header Host $host;
    }
}
```

同时设置环境变量让 MinIO 感知外部代理地址：
```yaml
environment:
  - MINIO_SERVER_URL=https://minio-api.your-domain.com
  - MINIO_BROWSER_REDIRECT_URL=https://minio-console.your-domain.com
```

**自签名证书（测试/内网）**：
```bash
openssl req -x509 -newkey rsa:4096 -keyout private.key -out public.crt -days 3650 -nodes -subj "/CN=minio.local"
```

---

## 8. 与 EMQX / 物联网架构集成（预签名直传最佳实践）

MinIO 在换热站 IoT 场景中的核心价值是配合 EMQX 实现**轻量、可靠的文件传输**。

### ❌ 不推荐方案：MQTT 承载图片 Base64

将图片转为 Base64 通过 MQTT 发送会带来严重问题：
- 数据膨胀（Base64 增加 33% 体积）
- 占用 EMQX 大量内存，易导致丢包
- 大消息增加 MQTT 代理负载，影响实时控制指令

### ✅ 推荐架构：预签名直传 + MQTT 通知

设备流程：
1. **申请上传链接**：设备（或边缘网关）先向后端服务发起 HTTP 请求，申请一个预签名上传 URL（有效期内可用）。
2. **直传文件**：设备使用 HTTP PUT 方法将图片二进制流直接上传至 MinIO（不经过后端，不经过 EMQX）。
3. **MQTT 通知**：上传成功后，设备向 EMQX 发送一条极小 JSON 报文，包含 `station_id`、`timestamp`、`object_name` 等元数据，后端订阅该 topic 后处理后续业务（如更新数据库、触发分析等）。

**后端生成预签名 URL（Python 示例）**：
```python
from minio import Minio
from datetime import timedelta

client = Minio(...)
upload_url = client.presigned_put_object(
    "heat-station-images",
    f"station1/{datetime.now().isoformat()}.jpg",
    expires=timedelta(minutes=5)
)
# 返回给设备，设备直接 PUT 文件到该 URL
```

**设备端上传（使用 curl）**：
```bash
curl -X PUT -T /path/to/image.jpg "<预签名URL>"
```

**EMQX 规则引擎处理通知**：
设备上传成功后发送 MQTT 消息：
```json
{
  "station_id": "station001",
  "timestamp": "2026-08-11T12:00:00Z",
  "object": "station1/2026-08-11T12:00:00.jpg"
}
```
EMQX 规则引擎可将该消息转发到后端 HTTP 服务或存入数据库，触发后续业务逻辑（如缩略图生成、告警分析）。

### 补充：MinIO 原生桶事件通知

MinIO 本身支持将桶内的 PUT/DELETE 事件通过 Webhook、Kafka、AMQP 等渠道推送。可配置 Webhook 回调后端，无需经过 EMQX：

```bash
mc admin config set myminio notify_webhook:1 \
  endpoint="http://your-backend:8080/minio-callback" \
  queue_dir="/tmp/webhook" \
  queue_limit="10000"
mc event add myminio/heat-station-images \
  arn:minio:sqs::1:webhook \
  --event put,delete
```

这样每次文件上传/删除时，MinIO 会自动回调指定接口，用于异步任务触发。

---

## 9. 监控与运维

### 9.1 健康检查

MinIO 提供健康端点：
```bash
curl http://localhost:9000/minio/health/live
curl http://localhost:9000/minio/health/ready
```

### 9.2 Prometheus 监控

抓取配置（需认证）：
```yaml
- job_name: minio
  metrics_path: /minio/v2/metrics/cluster
  static_configs:
    - targets: ['192.168.1.100:9000']
  authorization:
    credentials: "Bearer <access-key>:<secret-key>"
```

或使用 `mc admin prometheus generate myminio` 自动生成抓取配置。

**关键指标**：
- `minio_bucket_usage_total_bytes` - 桶已用容量
- `minio_bucket_usage_object_total` - 桶对象总数
- `minio_node_disk_free_bytes` / `minio_node_disk_total_bytes` - 磁盘剩余/总容量
- `minio_s3_requests_total` - API 请求速率
- `minio_s3_errors_total` - 错误请求数
- `minio_healing_disk_count` - 正在修复的磁盘数

推荐使用 Grafana 官方仪表盘（ID: 13502）。

### 9.3 日志管理

查看容器日志：
```bash
docker logs -f minio
```

启用 JSON 格式日志（便于 ELK/Loki）：
```yaml
environment:
  - MINIO_JSON_LOGGING=on
```

配置审计日志 Webhook：
```bash
mc admin config set myminio audit_webhook:1 endpoint="http://your-loki:3100/loki/api/v1/push"
```

### 9.4 备份与恢复

**数据同步（mc mirror）**：
```bash
mc mirror myminio/heat-station-images /backup/heat-station-images/
mc mirror myminio/heat-station-images myminio-backup/heat-station-images
```

**IAM 元数据备份**（用户、策略等）：
```bash
mc admin cluster iam export myminio > minio-iam-backup.json
mc admin cluster iam import myminio < minio-iam-backup.json
```

### 9.5 扩容

单机容量不足时可搭建分布式集群（至少 4 节点）。启动示例（4 节点）：
```bash
docker run -d --name minio1 ... minio/minio:RELEASE.2025-04-08T15-41-24Z server http://minio{1...4}/data
```
注意：新加节点数必须与现有节点数成倍数关系，以保证纠删码配置稳定。

### 9.6 故障排查常见问题

| 现象 | 可能原因及解决 |
|------|----------------|
| 容器启动失败，日志提示密码过短 | Root 密码长度 ≥ 8 位 |
| 上传失败，签名不匹配 | 检查系统时间是否同步（`chrony` 或 `ntpdate`） |
| Web UI 不显示 Console | 使用了过新镜像，换回固定版本 `RELEASE.2025-04-08T15-41-24Z` |
| Nginx 代理上传大文件超时 | 增加 `client_max_body_size`、`proxy_read_timeout`，并添加 `proxy_request_buffering off;` |
| `mc` 连接提示签名不匹配 | 检查 Access Key/Secret Key 是否准确；时间差是否在 15 分钟内 |
| `mc admin info` 响应很慢 | 检查磁盘 IO 或 bucket 数量是否过多（单实例建议 < 10 万个） |
| 磁盘使用率过高进入只读模式 | 默认 90% 预警，95% 只读。可通过环境变量 `MINIO_DISK_USAGE_WARNING_PERCENT` 和 `MINIO_DISK_USAGE_CRITICAL_PERCENT` 调整 |
| 调试时需要详细日志 | 设置 `MINIO_LOG_LEVEL=DEBUG` 或通过 `mc admin config set` 调整日志级别（生产慎用） |

---

## 10. 常用命令速查表

### mc 命令

| 命令 | 说明 |
|------|------|
| `mc alias set <别名> <URL> <AccessKey> <SecretKey>` | 添加/配置服务 |
| `mc ls <别名>` | 列出所有桶 |
| `mc mb <别名>/<桶名>` | 创建桶 |
| `mc cp <源> <目标>` | 复制文件（上传/下载） |
| `mc rm <别名>/<桶名>/<对象>` | 删除对象（可加 `--recursive` 批量） |
| `mc anonymous set download <别名>/<桶名>` | 设置桶为公开读 |
| `mc anonymous set none <别名>/<桶名>` | 设置桶为私有 |
| `mc admin info <别名>` | 查看服务信息（磁盘、集群状态） |
| `mc admin user add <别名> <用户名> <密码>` | 添加用户 |
| `mc admin policy attach <别名> <策略名> --user <用户>` | 为用户绑定策略（`readwrite`/`readonly`/`writeonly`） |
| `mc ilm rule add <别名>/<桶名> --expire-days <天数>` | 设置生命周期自动删除 |
| `mc share download --expire <时长> <别名>/<桶名>/<对象>` | 生成临时下载链接（如 `168h` 表示 7 天） |
| `mc share upload --expire <时长> <别名>/<桶名>/<对象>` | 生成临时上传链接 |
| `mc mirror <源别名>/<桶> <目标别名>/<桶>` | 镜像/备份整个桶 |
| `mc du <别名>/<桶名>` | 查看桶大小和对象数量 |
| `mc version enable <别名>/<桶名>` | 开启桶版本控制 |
| `mc mb --with-lock <别名>/<桶名>` | 创建支持对象锁定的桶 |
| `mc retention set --default <模式> <天数>d <别名>/<桶名>` | 设置默认保留策略（模式：`compliance` 或 `governance`） |
| `mc legalhold set <别名>/<桶名>/<对象>` | 对单个对象设置法律保留（阻止删除） |
| `mc ls --versions <别名>/<桶名>/<对象>` | 查看对象历史版本 |
| `mc admin cluster iam export <别名> > backup.json` | 导出 IAM 配置（用户、策略） |
| `mc admin cluster iam import <别名> < backup.json` | 导入 IAM 配置 |

### Docker 常用运维命令

| 命令 | 说明 |
|------|------|
| `docker logs -f minio` | 查看 MinIO 容器日志 |
| `docker restart minio` | 重启容器 |
| `docker exec -it minio sh` | 进入容器内部调试 |
| `docker run --rm -it --entrypoint=/bin/sh minio/mc` | 临时运行 mc 命令行 |

---

> **提示**：本手册已覆盖开发、运维、安全及与 EMQX 协同的多种场景，可按项目阶段按需查阅。后续若涉及 Kubernetes 部署或跨数据中心复制，可参考官方文档扩展，但换热站项目当前单机/小集群架构已足够。

---

[参考文档](https://www.fengfengzhidao.com/article/64cHuJsB0_1Q2CSUEGs3)

[参考网课](https://www.bilibili.com/video/BV1kFrjBQEoY/?spm_id_from=333.1391.0.0&vd_source=e0c0ad2a316e90d4078b1131e8182407)

---
