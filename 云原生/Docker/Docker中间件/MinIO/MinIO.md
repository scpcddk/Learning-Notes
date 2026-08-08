# MinIO 使用笔记（换热站项目 · Docker 部署）

## 1. MinIO 是什么，我们用它做什么

MinIO 是一个开源的高性能对象存储服务，完全兼容 Amazon S3 API。可以理解为搭建一个**私有的对象存储服务器**，像网盘一样存取文件。

**在换热站项目中的用途：**
- 存储现场设备抓拍的图片（如热成像图、仪表盘照片）
- 存储历史数据备份文件（CSV 导出）
- 存储日志归档、固件升级包
- 前端 Web 页面直接上传/下载文件，不需经过后端转发
- **冷数据长期归档**：将 EMQX 收集的原始消息或 InfluxDB 的历史数据导出为 JSON/CSV 文件，存入 MinIO 降低时序库存储压力
- **模型/配置文件分发**：边缘计算盒子可从 MinIO 下载更新后的 AI 模型或换热站控制策略，通过预签名 URL 安全分发

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

端口说明：
- `9000`：S3 API 端口（程序上传下载用）
- `9001`：Web 管理控制台端口

> ⚠️ 生产环境务必修改用户名密码，且使用环境变量文件而非命令行传参。密码至少 8 位，否则容器无法启动。

启动后访问 `http://服务器IP:9001`，用 `minioadmin / minioadmin` 登录。

### 2.2 数据持久化

上面 `-v /data/minio:/data` 把容器内数据映射到宿主机目录。生产环境建议挂载独立硬盘或使用 Docker Volume。**建议同时挂载 `certs` 目录用于 TLS 证书。**

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

---

## 5. 用户与权限管理

### 5.1 创建专用 Access Key

在 Web 控制台 → Access Keys → Create Access Key，为不同服务创建独立密钥：
- `station-gateway`：只允许上传到 `heat-station-images`
- `web-backend`：可读写所有桶
- `report-reader`：只读 `public-reports`

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

### 5.3 安全建议

- **使用预签名 URL 代替长期密钥**：边缘设备网络环境不可控，避免将 Access Key 硬编码在设备固件中。
- **定期轮换 Access Key**：通过脚本定期更新密钥并分发。
- **启用 TLS 加密**：在公网或不可信内网中，配置 MinIO 的 TLS 证书，杜绝明文传输。
- **设置桶的默认加密**：可以配置服务端加密（SSE-S3），确保数据在磁盘上加密存储。

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

### 8.2 日志查看

```bash
docker logs -f minio
```

### 8.3 备份

```bash
# 使用 mc mirror 同步整个桶到备份目录
mc mirror myminio/heat-station-images /backup/heat-station-images/

# 同步到远程 MinIO 实例（异地灾备）
mc mirror myminio/heat-station-images myminio-backup/heat-station-images
```

### 8.4 扩容

单机容量不足时可使用 MinIO 分布式模式，启动多个节点组成集群。需要至少 4 个节点（纠删码要求），规划时注意。

**分布式启动示例（4节点）：**
```bash
docker run -d --name minio1 ... minio/minio server http://minio{1...4}/data
```
需配置统一的网络和存储，生产环境建议结合 Kubernetes 或使用官方推荐的编排方式。

### 8.5 故障排查

- **容器启动失败，日志提示密码过短**：Root 密码长度需 ≥ 8 位。
- **上传失败，提示签名不匹配**：检查系统时间是否同步，MinIO 依赖正确的时间进行签名校验。使用 `ntpdate` 或 `chrony` 同步。
- **存储空间不足**：配置监控告警并启用生命周期管理自动清理；定期检查 `mc admin info` 的磁盘使用情况。

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

---

> 提示：这份笔记已涵盖开发、运维、安全及与 EMQX 配合的多种场景，可根据项目阶段按需查阅。后续深化时可补充 Kubernetes 部署、版本控制（Bucket Versioning）及站点复制等高阶特性。
