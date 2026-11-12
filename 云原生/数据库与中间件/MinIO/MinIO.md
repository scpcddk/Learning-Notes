---
markmap:
  initialExpandLevel: 2
---

# MinIO 使用笔记（换热站项目 · Docker 部署）

---

## 1. MinIO 是什么，我们用它做什么

MinIO 是一个开源的高性能**对象存储服务**，提供 S3 兼容 API（具体兼容范围以所用版本为准）。可视为一套**私有对象存储服务器**，用于集中管理文件。

**在换热站项目中的典型用途**：

- 存储现场设备抓拍的图片（热成像图、仪表盘照片）
- 历史数据备份文件（CSV 导出）长期归档
- 日志归档、固件升级包分发
- 边缘 AI 模型文件（模型权重、配置文件）的分发与更新
- 前端 Web 页面或移动端直接通过预签名 URL 上传/下载，避免后端中转

> [!TIP]
> **版本选择**：MinIO 在 2021 年已转为 AGPL v3。2025 年 5 月后的社区 Console 缩减了管理功能，并非完全移除 Web 界面。以下固定版本用于复现本文示例：
>
> ```bash
> # 处理镜像仓库与标签。先核对仓库地址、制品版本和所用身份。
> docker pull minio/minio:RELEASE.2025-04-08T15-41-24Z
> ```
> 该版本保留原有管理界面；许可证适用性需结合实际使用、修改和分发方式判断，不能笼统认定“内部使用无影响”。生产版本还需核对维护状态与安全修复。

**早期手册里的对象用途**

最早版本（`34b2038`）记录了现场热成像图、仪表盘照片与历史 CSV 备份，也列出了边缘模型和配置文件分发的设想。交接时可分别核对原始图片、归档导出与分发制品的前缀、权限和保留期。设想中的分发用途需要单独做版本和权限验收。


---

## 2. Docker 快速安装与配置

### 2.1 单节点启动（测试用）

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
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

> [!TIP]
> 生产环境务必修改默认用户名密码（密码至少 8 位），建议使用环境变量文件（`.env`）传递凭证，避免暴露在命令行。

启动后访问 `http://服务器IP:9001` 即可登录。

### 2.2 模拟纠删码的单机多盘测试

若想在不搭建集群的情况下体验纠删码特性，可在单节点指定多个数据目录：

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run -d --name minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v /data/disk1:/data/disk1 \
  -v /data/disk2:/data/disk2 \
  -v /data/disk3:/data/disk3 \
  -v /data/disk4:/data/disk4 \
  minio/minio:RELEASE.2025-04-08T15-41-24Z \
  server '/data/disk{1...4}' --console-address ":9001"
```

该版本的 4 盘默认 EC:2 可容忍最多 2 个分片丢失并读取已有对象，但写入通常至少需要 3 盘在线；同一物理盘上的 4 个目录仅能演示布局，不能提供物理磁盘故障容错。

### 2.3 生产环境资源配置建议

- **内存**：小规模测试可从 1~2GB 起实测；生产按盘数、并发、对象大小和部署指南规划，不能把 2GB 视为通用上限。
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

- **创建多个桶**：`heat-station-images`（设备图片，私有）、`firmware`（固件，私有）、`public-reports`（报表，公开只读）
- 为不同应用生成独立的 Access Key，授予最小权限
- **通过预签名 URL 让边缘设备安全上传/下载，避免在设备上保存长期凭证**
- 利用**生命周期管理**自动清理过期图片，控制存储成本
- 关键数据桶开启**版本控制**和**对象锁定**，防止误删或篡改

**纠删码基础**：分布式部署时 MinIO 使用纠删码（Erasure Code）代替多副本。典型配置：

- 4 盘：`EC:2`（可坏 2 盘）
- 8 盘及以上：`EC:4`（可坏 4 盘）

上述盘数和容错均以单个纠删码集合为单位，不能直接套用整个多集合/多池部署。读取和写入 quorum 也不相同。

存储利用率 = (N - M) / N，例如 8 盘 EC:4 利用率为 50%。

### 区分对象数据、业务索引和临时链接

项目里的录像、截图或文件可以存在对象存储，MySQL 负责保存可查询的站点、设备、采集时间和对象引用。Bucket 是命名空间。对象键包含的斜杠通常表示前缀约定，不能按本地文件系统目录理解。一个对象地址至少需要 Bucket 与 Object Key。开启版本控制且必须定位某次上传时，还要记录 Version ID。下载地址可按需签发，业务库长期保存的应是稳定引用与必要元数据。

| 信息 | 建议保存位置 | 排障用途 |
|---|---|---|
| 站点、设备、采集或录像起止时间 | 业务数据库 | 供页面查找，便于对齐具体记录 |
| Bucket、Object Key、必要时 Version ID | 业务数据库或对象关联表 | 指向实际对象，避免旧签名过期后无法重新定位 |
| 对象大小、内容类型与校验值 | 对象元信息和必要的业务记录 | 确认可用与传输完整性 |
| 创建者、访问范围与状态 | 业务权限与操作记录 | 判定谁可查、谁可下载，以及是否可以清理 |
| 临时签名 URL | 临时下发给授权客户端 | 控制可用时间，避免把可访问凭据写进长期日志 |

键的命名使用一致的前缀和稳定标识。上传文件的原始名称可作为业务展示字段；当对象键包含中文、空格或特殊字符时，让 SDK 按签名和 URL 规则处理，避免前端手工拼接或二次转义。对象键区分大小写。迁移时核对是否有近似路径、重名或旧前缀，避免相同文件名在不同站点之间串用。


---

## 4. 存储桶操作（Bucket 管理）

在 Web 控制台（`:9001`）左侧「Buckets」→ 创建或点击已有桶，可进行高级配置。

### 4.1 创建存储桶

点击 **「Create Bucket」**，输入桶名（在本 MinIO 部署内唯一），配置以下选项：

| 配置项 | 说明 | 换热站项目建议 |
|--------|------|----------------|
| **Versioning（版本控制）** | 开启后保留对象所有历史版本，可随时回滚 | `heat-station-images` 建议开启，防止误覆盖抓拍图片 |
| **Object Locking（对象锁定）** | 开启后桶内对象可设置「禁止删除/修改」的保留期 | **必须在创建桶时决定**，不可事后开启。归档/审计类数据建议开启 |
| **Quota（配额）** | 限制桶的最大存储容量（如 100GB） | 为每个换热站桶设置配额，避免单站占用过多空间 |

> [!WARNING]
> Object Locking 一旦开启即**不可关闭**，且需同时启用 Versioning，请谨慎决策。

### 4.2 版本控制（Versioning）

开启后，每次上传同名文件都会生成新版本，旧版本保留并可随时恢复。

**Web 操作**：Bucket → Config → Versioning → Enable

**命令行操作**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc version enable myminio/heat-station-images
```

**查看历史版本**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc ls --versions myminio/heat-station-images/station1/snapshot.jpg
```

**恢复历史版本**（先下载特定版本，再上传为新的当前版本；尖括号替换为实际 ID）：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc cp --version-id "实际版本ID" myminio/heat-station-images/station1/snapshot.jpg ./restored.jpg
mc cp ./restored.jpg myminio/heat-station-images/station1/snapshot.jpg
```

#### 分清历史版本、保留规则和独立备份

| 机制 | 解决什么 | 仍要验证 |
|---|---|---|
| Versioning | 保存同一键的历史版本 | 能找到目标版本，删除标记与业务逻辑是否一致 |
| 生命周期规则 | 按条件清理或处理对象与版本 | 规则作用范围、过期时间、未完成分片及误清理可能 |
| Object Lock / 保留 | 在配置的约束下保护对象版本 | 适用模式、最短保留期、权限与合规要求 |
| 复制或镜像 | 把对象同步到另一个存储 | 同步延迟、失败和版本、元信息、标签的边界 |
| 独立备份 | 为恢复提供固定的可用来源 | 对象、权限、配置和引用数据能否一起恢复 |

版本控制下，普通删除可能写入删除标记，使默认读取看不到该对象，旧版本仍可能存在。检查和恢复时用有授权的方式列出版本，核对目标版本与业务时间。不能看到文件就判断已彻底删除，也不能看到 404 就判断历史数据一定不存在。设置保留与清理前，先确认业务最长回放时间、备份周期和错误恢复窗口。直播、事件引用、历史录像的生命周期可能不同。


### 4.3 对象锁定（Object Locking）与保留策略

**适用场景**：合规审计数据、证据固化、关键配置文件防篡改。

**创建支持锁定的桶**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc mb --with-lock myminio/audit-logs
```

**设置默认保留策略**（合规模式，保留 30 天）：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc retention set --default compliance 30d myminio/audit-logs
```

**保留模式对比**：

| 模式 | 特性 | 适用场景 |
|------|------|----------|
| **Compliance（合规）** | 保留期内**任何人**（含 root）都无法删除/修改 | 金融审计、司法证据、政府监管数据 |
| **Governance（治理）** | 普通用户不可删，但拥有特殊权限的管理员可提前释放 | 企业内控、项目文档归档（需要灵活性） |

**对单个对象设置 Legal Hold（法律保留）**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc legalhold set myminio/audit-logs/2026-08-11-station1.log
```

### 4.4 配额（Quota）

限制桶的存储上限，防止单桶无限膨胀。

**Web 操作**：Bucket → Config → Quota → 输入上限（如 `100GB`）

**命令行设置**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc quota set myminio/heat-station-images --size 100GB
```

**查看当前配额使用情况**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc du myminio/heat-station-images
```

### 4.5 生命周期管理（Lifecycle）

自动清理过期文件，降低存储成本。

**场景示例**：设备抓拍图片 30 天后自动删除。

**命令行设置（30 天后自动删除）**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc ilm rule add myminio/heat-station-images --expire-days 30
```

**设置转换到冷存储**（若 MinIO 配置了冷热分层）：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc ilm rule add myminio/heat-station-images --transition-days 7 --transition-tier cold-tier
```

**查看已有生命周期规则**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc ilm rule list myminio/heat-station-images
```

### 4.6 访问策略（Bucket Policy）

在 Web 控制台 Bucket → Config → Policy 中，可快速设置：

- **Private（私有）**：仅授权用户可读写（默认）
- **Public（公开读）**：所有人可下载，但不可上传/删除
- **Custom（自定义）**：粘贴 JSON 策略，精细控制读写权限

**命令行设置公开读**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc anonymous set download myminio/public-reports
```

---

## 5. 客户端工具与代码集成

### 5.1 使用 MinIO Client（mc）

`mc` 是官方命令行客户端，功能强大。

**安装**（Linux）：

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

**配置别名连接服务器**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc alias set myminio http://192.168.1.100:9000 minioadmin minioadmin
```

**常用操作**：

```bash
mc mb myminio/heat-station-images          # 创建桶
mc cp ./snapshot.jpg myminio/heat-station-images/station1/20260101.jpg   # 上传
mc ls myminio/heat-station-images           # 列出桶内容
mc rm myminio/heat-station-images/temp/example.jpg  # 删除指定对象（慎用）
mc share download --expire 168h myminio/heat-station-images/station1/20260101.jpg   # 生成临时下载链接（7天有效）
mc mirror myminio/heat-station-images /backup/   # 同步/备份到本地目录
```

#### 用同一个样本核对对象与完整性

先从与后端相同的网络，用已配置且权限受限的客户端核对对象。再使用后端签发给实际客户端的地址，核对从用户网络是否可用。Console 与对象 API 是不同入口。后端 SDK 能通过内网访问，不代表浏览器也能访问签名 URL 中的主机。

```bash
# 使用已有 mc 别名读取对象元信息，不修改对象。
: "${MINIO_ALIAS:?请设置已配置的 mc 别名}"
: "${TEST_BUCKET:?请设置用于复测的桶名}"
: "${TEST_KEY:?请设置样本对象键}"
mc stat "$MINIO_ALIAS/$TEST_BUCKET/$TEST_KEY"
```

用一个小文件验证直接上传。记录大小和校验值，上传后检查对象类型、大小和元信息，再下载同一对象做对照。对象的 ETag 不应一概当成整文件 MD5，特别是分片上传或某些加密方式。要做文件完整性校验时，用交接清单里的 SHA-256 或所用接口支持的校验字段，按同一算法对照。

```bash
# 在自己的演练目录比对上传前原件和授权下载的副本。
: "${SOURCE_FILE:?请设置样本原文件}"
: "${DOWNLOADED_FILE:?请设置已下载的验证副本}"
sha256sum "$SOURCE_FILE" "$DOWNLOADED_FILE"
# cmp 无差异时退出码为 0，可用于自动验收。
cmp -s "$SOURCE_FILE" "$DOWNLOADED_FILE"
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

**大文件分片上传**（SDK 按对象大小与分片配置自动处理，没有统一的 128MB 门槛）：

```python
client.fput_object(
    "heat-station-images",
    "large_firmware.bin",
    "/path/to/large_firmware.bin",
    part_size=64 * 1024 * 1024   # 64MB 分片
)
```

**自定义元数据**（与对象标签 tagging 是不同功能）：

```python
# 按桶和对象键上传数据，核对上传类型、文件来源及结果。
client.fput_object(
    "heat-station-images",
    "snapshot.jpg",
    "/tmp/snapshot.jpg",
    metadata={
        "station-id": "station-001",
        "capture-time": "2026-08-11T12:00:00Z"
    }
)
```

### 5.3 Java SDK 操作示例

换热站边缘网关若基于 Java 开发，可直接集成 MinIO Java SDK。添加 Maven 依赖：

```xml
<!-- 放到 pom.xml 的对应节点，区分依赖版本管理、实际依赖与构建插件。 -->
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
import java.util.Map;
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

        // 6. 大文件上传：由 SDK 自动选择并执行分片上传
        minioClient.uploadObject(
                UploadObjectArgs.builder()
                        .bucket("heat-station-images")
                        .object("large_firmware.bin")
                        .filename("/path/to/large_firmware.bin")
                        .build()
        );

        // 7. 设置自定义元数据（不是对象标签）
        minioClient.uploadObject(
                UploadObjectArgs.builder()
                        .bucket("heat-station-images")
                        .object("snapshot.jpg")
                        .filename("/tmp/snapshot.jpg")
                        .userMetadata(Map.of(
                                "station-id", "station-001",
                                "capture-time", "2026-08-11T12:00:00Z"
                        ))
                        .build()
        );
    }
}
```

> [!NOTE]
>
> - 预签名 URL 生成使用 `getPresignedObjectUrl`，支持 GET（下载）和 PUT（上传）。
> - `uploadObject` 会自动处理分片上传，包括超过单次 PUT 限制的大文件；原示例中的 `CreateMultipartUploadArgs` 不是该版本公开的同步客户端调用方式。
> - 元数据通过 `userMetadata` 设置，传入如 `station-id` 的键即可，SDK 处理 `x-amz-meta-` 前缀；对象标签使用独立的 tagging API。
> - 生产环境中应使用连接池、超时配置等，可构造配置好 `connectTimeout`、`writeTimeout` 等参数的 OkHttpClient，再通过 `.httpClient(...)` 注入 builder。

---

## 6. 用户权限与安全加固

### 6.1 创建专用 Access Key

在 Web 控制台 → Access Keys → Create Access Key，为不同服务创建独立密钥：

- `station-gateway`：只允许上传到 `heat-station-images`
- `web-backend`：可读写所有桶
- `report-reader`：只读 `public-reports`

**命令行管理用户**（先将 6.2 节精细策略保存为 `station1-policy.json`；按实际站点调整前缀）：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc admin user add myminio station-gateway password123
mc admin policy create myminio station1-objects ./station1-policy.json
mc admin policy attach myminio station1-objects --user station-gateway
mc admin user list myminio
mc admin user disable myminio station-gateway
```

### 6.2 桶策略示例

以下桶策略授予所有访问者匿名读取对象的权限（`Principal: *`），仅适合公开桶：

**阅读提示**　按 Statement 核对允许的 Action、资源范围和生效条件。

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

**精细 IAM 策略**：以下身份策略不含 Principal，创建后附加给 `station1` 用户，使其只读写自己的对象前缀；这不是匿名桶策略：

**阅读提示**　按 Statement 核对允许的 Action、资源范围和生效条件。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": ["arn:aws:s3:::heat-station-images/station1/*"]
    }
  ]
}
```

#### 分别验证桶前缀和对象读取权限

应用不需要复用运维管理员账号。把写入、浏览、读和删除按角色拆开。列表是 Bucket 范围操作，读取是对象范围操作。需要按前缀限制列表时，还要约束列表请求的前缀。下面仅用于说明策略结构，假定测试桶为 `archive-lab`，只读身份只需要查看 `staging/` 前缀。实际部署在隔离桶先验收，再按所用 MinIO 版本确认策略生效方式。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::archive-lab"],
      "Condition": {"StringLike": {"s3:prefix": ["staging/*"]}}
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::archive-lab/staging/*"]
    }
  ]
}
```

验收用三组请求：允许前缀的列表和下载应成功，其他前缀应拒绝，上传或删除也应拒绝。如果测试环境已给用户附加其他宽权限，先核对实际身份与组合策略，不把一次成功误认为当前策略有效。需要读取历史版本时按实际使用的版本接口评估额外权限。签名链接由能访问目标对象的身份创建，但后端仍须独立判断当前用户的业务权限。

配置轮换时先加新身份和规则，在测试客户端验证后切换业务，再退役旧身份。依赖相同凭据的 Console、后端、自动化任务和备份工具应分别核对。新旧凭据共存的窗口和交接日志只记录状态，不记录秘密值本身。


### 6.3 安全加固措施

- **使用预签名 URL 代替长期密钥**：边缘设备不应硬编码 Access Key。
- **定期轮换 Access Key**：通过脚本定期更新并分发。
- **启用 TLS 加密**：公网或不可信内网必须配置证书。
- **IP 白名单**：在策略中加入 `aws:SourceIp` 条件限制访问来源。
- **禁用 Console 公网暴露**：生产环境可将 Console 端口绑定为 `127.0.0.1`，通过 SSH 隧道或内网代理访问。
- **启用审计日志**：使用 audit_webhook 等该版本支持的审计目标，经接收服务转发到日志系统。

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
      - "127.0.0.1:9000:9000"
      - "127.0.0.1:9001:9001"
    volumes:
      - minio-data:/data
      # 本模板由 Nginx 终止 TLS，MinIO 上游使用 HTTP
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  minio-data:
    driver: local
```

> 本例假设 Nginx 在宿主机运行，并在外层终止 TLS。若改为 MinIO 原生 TLS，挂载含 `private.key`、`public.crt` 的证书目录，同时把健康检查、Nginx 上游和 SDK 的协议改成 HTTPS 并配置信任链。

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
# 按层级合并到对应配置位置，保持缩进并核对引用的服务、端口或文件。
environment:
  - MINIO_SERVER_URL=https://minio-api.your-domain.com
  - MINIO_BROWSER_REDIRECT_URL=https://minio-console.your-domain.com
```

**自签名证书（测试/内网）**：

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
openssl req -x509 -newkey rsa:4096 -keyout private.key -out public.crt -days 3650 -nodes -subj "/CN=minio.local"
```

**对照对象 API 和浏览器签名入口**

先直连对象 API 成功，再经外部入口走同一业务请求。代理终止 TLS 时也要保留签名要求的 Host 与请求目标。带子路径的反代尤其要验证实际 URI，避免签名是一个路径、上游收到另一个路径。用测试对象对照错误 XML、请求 ID 与代理日志，截取证据时遮盖查询字符串。

#### 单独验收大文件、Range 和媒体回放

小文件上传成功后，再用与实际录像接近的样本验证。关注是否在浏览器、代理、应用或存储端触发请求体限制或超时。客户端走分片上传时，需要确认初始化、每个分片回执和最终完成，只有分片上传成功并不代表完整对象已出现。分片重试要能恢复原上传任务，失败后按策略处理未完成分片。调整阈值前观察是哪一层先返回错误，不建议一次同时放宽所有服务的限制。

播放器经常按字节范围读取历史媒体。用足够大的隔离样本验证。以下命令适用于已经获得授权、且允许发送所示 Range 头的签名 GET 请求。只查看响应头和本次下载长度，不把签名 URL 贴入日志或聊天记录。

```bash
# SIGNED_GET_URL 填隔离对象的短期下载 URL。
: "${SIGNED_GET_URL:?请设置授权下载地址}"
curl -sS --max-time 15 --range 0-1023 -D - -o /dev/null \
  -w '\nHTTP %{http_code}, downloaded %{size_download} bytes\n' "$SIGNED_GET_URL"
```

一般预期收到 `206 Partial Content` 与 `Content-Range`。若返回 200 且下载整对象，检查代理或客户端是否保留 Range。若返回 416，核对请求范围和对象长度。403 先看错误代码，确认签名有效期、请求头以及是否被重新签发或改写。直连能分段、经站点入口无法分段时，优先对照反代转发和响应头。浏览器还会应用 CORS，命令行成功只表明网络和 HTTP 能走通。

回放失败也可能是有效期不足或页面沿用了旧签名。回放链接过期后应重新走应用鉴权与签发流程，不能通过长期公开 Bucket 掩盖问题。记录首次播放时间、请求分段、拖动进度后触发的请求、过期后的行为与是否能重新播放。若播放器只能接受某些媒体类型，检查实际 Content-Type、编码与播放器库，不要把可以下载误当成可以在线播放。


---

## 8. 与 EMQX / 物联网架构集成（预签名直传最佳实践）

MinIO 在换热站 IoT 场景中的核心价值是配合 EMQX 实现**轻量、可靠的文件传输**。

### ❌ 不推荐方案：MQTT 承载图片 Base64

将图片转为 Base64 通过 MQTT 发送会带来严重问题：

- 数据膨胀（Base64 增加 33% 体积）
- 占用 EMQX 大量内存，易导致丢包
- 大消息增加 MQTT 代理负载，影响实时控制指令

**早期方案与最终链路的对应**

早期手册曾把 Base64 图像随 MQTT 消息送到 HTTP 服务，由后端解码再上传到 MinIO，作为联调方案。阅读后续预签名直传方案时，重点对照哪一层传输文件、哪一层只传对象键。保留这个演进过程，能解释为什么后来要分别验证文件上传和 MQTT 通知。


### ✅ 推荐架构：预签名直传 + MQTT 通知

设备流程：

1. **申请上传链接**：设备（或边缘网关）先向后端服务发起 HTTP 请求，申请一个预签名上传 URL（有效期内可用）。
2. **直传文件**：设备使用 HTTP PUT 方法将图片二进制流直接上传至 MinIO（不经过后端，不经过 EMQX）。
3. **MQTT 通知**：上传成功后，设备向 EMQX 发送一条极小 JSON 报文，包含 `station_id`、`timestamp`、`object_name` 等元数据，后端订阅该 topic 后处理后续业务（如更新数据库、触发分析等）。

**后端生成预签名 URL（Python 示例）**：

```python
from minio import Minio
from datetime import datetime, timedelta, timezone

client = Minio("192.168.1.100:9000", access_key="your-access-key",
               secret_key="your-secret-key", secure=False)
upload_url = client.presigned_put_object(
    "heat-station-images",
    f"station1/{datetime.now(timezone.utc).isoformat()}.jpg",
    expires=timedelta(minutes=5)
)
# 返回给设备，设备直接 PUT 文件到该 URL
```

**设备端上传（使用 curl）**：

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl -X PUT -T /path/to/image.jpg "<预签名URL>"
```

**EMQX 规则引擎处理通知**：

设备上传成功后发送 MQTT 消息：

**阅读提示**　object 标识已经上传的对象，消费端按这个对象定位数据，消息中不承载文件正文。

```json
{
  "station_id": "station001",
  "timestamp": "2026-08-11T12:00:00Z",
  "object": "station1/2026-08-11T12:00:00.jpg"
}
```

EMQX 规则引擎可将该消息转发到后端 HTTP 服务或存入数据库，触发后续业务逻辑（如缩略图生成、告警分析）。

#### 浏览器直传、确认对象和通知的顺序

1. 应用先校验当前用户是否可向该站点或资源写入，为这次请求生成新的对象键，避免直接复用用户提供的路径。
2. 后端按所需 HTTP 方法和时限签发 URL。如要求 `Content-Type` 或其他参与签名的请求头，客户端必须按约定原样发送。
3. 浏览器用该 URL 执行上传，记录上传请求的状态，不把整条签名 URL 留在日志或报错页面。
4. 后端用可信的服务身份核对对象是否写入、大小是否合理，再更新业务记录或发出通知。浏览器的“上传完成”提示只是一条客户端证据。
5. 下游按对象键与事件编号幂等处理。页面需要展示或回放时重新校验访问权限，并按需签发下载地址。

上传文件后客户端可能在通知后端前退出，形成没有业务引用的对象。也可能先收到通知，业务行存在但实际对象还不可读。用一条有编号的上传记录、对象信息和下游处理日志对照，可以判断需要补发通知、补关联还是清理隔离数据。回收策略要给重试和异步处理留出合理时间。


### 补充：MinIO 原生桶事件通知

MinIO 本身支持将桶内的 PUT/DELETE 事件通过 Webhook、Kafka、AMQP 等渠道推送。可配置 Webhook 回调后端，无需经过 EMQX：

```bash
mc admin config set myminio notify_webhook:1 \
  endpoint="http://your-backend:8080/minio-callback" \
  queue_dir="/tmp/webhook" \
  queue_limit="10000"
# 按配置命令输出的提示，在维护窗口重启服务使通知目标生效
mc admin service restart myminio
mc event add myminio/heat-station-images \
  arn:minio:sqs::1:webhook \
  --event put,delete
```

这样每次文件上传/删除时，MinIO 会自动回调指定接口，用于异步任务触发。

**用同一事件验证重发和回放**

联调时让一条测试记录关联对象，保存稳定的事件编号，再重复提交一次相同编号。检查对象键是否一致，业务列表是否只保留一个有效关联。如果浏览器有多次请求，也要区分重复上传和同一对象的多个 Range 请求。后者可以是正常回放行为。复测时从业务记录重新获取链接，避免使用已过期的旧 URL。

### 直传、通知与回放的验收单

- **最小权限**：测试账号只访问指定桶和前缀，拒绝越界读取与写入。
- **浏览器直传**：一个可识别样本成功上传，服务端能核对对象，页面可重新获得授权下载地址。过期后重新申请链接。
- **异步联动**：对象写入与 MQTT 事件使用同一对象键和事件编号，重发同一事件后业务只留一条关联。
- **回放**：从真实用户网络验证历史对象可访问，媒体类型和分段请求符合播放器要求。
- **迁移恢复**：在独立位置复测对象、索引、策略和入口，记录对象数量、样本验证和恢复时长。
- **交接**：留存部署版本、数据位置、桶和前缀约定、账号职责与复测方式。签名 URL 和长期凭据通过约定渠道管理。

这套验收把旧笔记中的 Docker 部署、预签名直传、MQTT 通知与备份复测串成一条完整流程。再次使用时以实际版本、部署方式和数据范围为准。 [MinIO 对象同步](https://min.io/docs/minio/linux/reference/minio-mc/mc-mirror.html)


---

## 9. 监控与运维

### 9.1 健康检查

MinIO 提供健康端点：

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl http://localhost:9000/minio/health/live
curl http://localhost:9000/minio/health/ready
```

### 9.2 Prometheus 监控

抓取配置（需认证）：

```yaml
# 抓取目标的地址必须从 Prometheus 所在网络可达，路径以应用实际暴露值为准。
- job_name: minio
  metrics_path: /minio/v2/metrics/cluster
  static_configs:
    - targets: ['192.168.1.100:9000']
  authorization:
    type: Bearer
    credentials: "<mc admin prometheus generate 生成的 JWT>"
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
# 用容器状态和近期日志确认启动进度及失败位置。
docker logs -f minio
```

启用 JSON 格式日志（便于 ELK/Loki），使用启动参数：
```yaml
# 按层级合并到对应配置位置，保持缩进并核对引用的服务、端口或文件。
command: server --json /data --console-address ":9001"
```

配置审计日志 Webhook：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc admin config set myminio audit_webhook:1 endpoint="http://audit-receiver:8080/minio-audit"
```

审计 Webhook 接收的是 MinIO 审计 JSON，不能直接指向 Loki push API；应由接收服务转换格式后写入 Loki。

### 9.4 备份与恢复

**数据同步（mc mirror）**：

```bash
# 使用配置好的 MinIO 别名。确认桶、对象路径和当前账号权限。
mc mirror myminio/heat-station-images /backup/heat-station-images/
mc mirror myminio/heat-station-images myminio-backup/heat-station-images
```

**IAM 元数据备份**（用户、策略等）：

```bash
mc admin cluster iam export myminio
# 根据上条命令输出的实际 ZIP 路径导入
mc admin cluster iam import myminio ./myminio-iam-info.zip
```

#### 隔离目标上的同步预演和数据验收

跨环境迁移时，先用只读方式比较范围。下例只预览同步，目标应是独立演练位置。实际使用 `mc mirror` 要按版本确认功能范围，一般应把它理解为对象同步工具。完整保留历史版本、权限、Bucket 配置和对象锁时，采用适用的备份或复制方案另验。

```bash
# 两端为已配置的别名与已核对的 Bucket/前缀。
: "${SOURCE_PREFIX:?请设置来源别名/桶/前缀}"
: "${RESTORE_PREFIX:?请设置隔离恢复目标}"
mc mirror --dry-run "$SOURCE_PREFIX" "$RESTORE_PREFIX"
```

同步后对照对象数量、样本对象键、大小和可读性。要恢复应用，还需恢复后端数据库里的对象引用、服务访问策略与签名对外入口。能从管理端下载只是最初的一关，还要用真实客户端所在网络和应用账号权限做回放。文件清单、导出时间和引用数据的截止时间一并记录，避免看起来都恢复了却来自不同时间点。

#### 恢复后的抽查口径

准备恢复清单时，把小文件、大录像、带特殊字符的对象键以及需要历史版本的对象分别列样本。每种至少能回答「在哪个桶和前缀」「由谁读取」「校验什么」「在哪个网络验收」。如果对象和业务索引来自不同的备份时点，先标记两边各自截止时间，再对照对象缺失或孤立引用。可以先用对象清单和数据库样本核对差异，实际清理应在确认不再需要回滚和补录之后安排。

交接时将对象可读、业务可查与浏览器可播分别登记。对象可读验证存储和身份，业务可查验证索引，浏览器可播还需要外部入口、签名、Range、媒体格式与播放器一起工作。涉及跨域时，只为实际前端入口配置所需的方法和请求头。若前端需要读取某个响应头，再配置相应的暴露范围，避免放开所有来源后才发现问题没有解决。


### 9.5 扩容

单机容量不足时可规划分布式部署；节点与磁盘数需满足版本及纠删码集合要求，并非固定至少 4 节点。旧单盘数据需通过受支持的迁移方式转入新部署。启动示例（4 节点）：

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run -d --name minio1 ... minio/minio:RELEASE.2025-04-08T15-41-24Z server 'http://minio{1...4}/data'
```

注意：分布式扩容通常添加新的 server pool；按版本要求规划新池磁盘、纠删码集合和启动参数，不能简单按现有节点数倍增。

### 9.6 故障排查常见问题

| 现象 | 可能原因及解决 |
|------|----------------|
| 容器启动失败，日志提示密码过短 | Root 密码长度 ≥ 8 位 |
| 上传失败，签名不匹配 | 检查系统时间是否同步（`chrony` 或 `ntpdate`） |
| Web UI 不显示 Console | 先检查 Console 启动参数、端口映射与日志；新版可能仅提供对象浏览，不能仅凭界面变化判断未启动 |
| Nginx 代理上传大文件超时 | 增加 `client_max_body_size`、`proxy_read_timeout`，并添加 `proxy_request_buffering off;` |
| `mc` 连接提示签名不匹配 | 检查 Access Key/Secret Key 是否准确；时间差是否在 15 分钟内 |
| `mc admin info` 响应很慢 | 检查磁盘 IO 或 bucket 数量是否过多（单实例建议 < 10 万个） |
| 磁盘使用率过高进入只读模式 | 检查实际磁盘剩余空间、inode 与写入 quorum；不要依赖未核实的百分比阈值或配置项 |
| 调试时需要详细日志 | 使用 `mc admin trace myminio` 观察请求，并结合 `docker logs` 排查；trace 可能包含敏感请求信息 |

#### 用错误类型区分签名、路径和权限

| 客户端证据 | 优先核对 |
|---|---|
| 网络错误、证书失败 | URL 主机从客户端是否可达，域名、端口、证书是否匹配 |
| 浏览器预检失败，应用看不到实际 PUT | Origin、允许方法、请求头和站点代理的 OPTIONS 行为 |
| `SignatureDoesNotMatch` | HTTP 方法、Host、端口、路径、查询参数与签名头是否被重写 |
| `AccessDenied` 或链接过期 | 使用者权限、签名时限、时钟与访问规则 |
| `NoSuchKey` | 桶、对象键、版本、URI 转义以及对象上传是否确认 |
| 返回 200 但浏览器显示 HTML | 对象 API 请求是否误进入 Console、反代错误页或前端路由回退 |
| 小文件成功，大文件失败 | 入口请求体上限、缓冲、上游超时、分片上传和磁盘情况 |

#### 核对实际挂载、磁盘与异常请求

在单机环境，确认数据挂载到了预期磁盘，容器重建不丢对象。多盘或分布式部署需要同时检查节点与磁盘的可用状态、访问路径和数据保护假设。容量规划除对象大小外，还需估算版本历史、未完成分片、复制或修复流量和增长趋势。不要把磁盘目录直接等同于一个可独立移动的对象，迁移应按对象接口或产品支持的流程进行。

```bash
# 核对当前容器的数据挂载、端口和相关时间段日志。
: "${MINIO_CONTAINER:?请设置实际 MinIO 容器名}"
docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$MINIO_CONTAINER"
docker port "$MINIO_CONTAINER"
docker logs --since 10m "$MINIO_CONTAINER"
```

按「目标入口 → API 状态 → 身份权限 → 对象元信息 → 实际读写 → 业务关联」查故障。出现延迟时区分代理上传超时、S3 请求排队、磁盘压力、网络带宽与客户端重试。大量 `4xx` 优先查签名、权限和对象命名，持续 `5xx` 则结合节点状态、磁盘和错误日志。监控图表配合一次真实小对象读写，避免只看探针状态。对于断续的回放，浏览器网络页检查分片或 Range 请求的响应、类型和长度，再定位播放器、签名或存储。


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
| `mc admin cluster iam export <别名>` | 导出 IAM 配置（用户、策略） |
| `mc admin cluster iam import <别名> ./实际导出的-iam-info.zip` | 导入 IAM 配置 |

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
