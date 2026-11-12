# SRS 流媒体服务器部署全流程复盘

> [!IMPORTANT]
> **目标**：为 Jetson 摄像头提供推流接收服务，并将 RTMP 流转换为 HLS 格式，使前端可通过网页直接播放 
> **环境**：实验室 Ubuntu 22.04 服务器（校园网地址 `202.199.6.249`），已运行 Spring Boot 后端（占用 8080）、Nginx 容器（占用 80）、MySQL 等。
> **约束**：服务器无外网，需离线部署；不能影响已有服务；最终通过统一入口（80 端口）提供播放地址

---

## 1. 为什么需要 SRS

Jetson 摄像头采集的视频原始流通常是 RTSP 或 RTMP 协议，**浏览器无法直接播放**。需要一台流媒体服务器在中间做转换，将 RTMP 流转封装为 **HLS**（`.m3u8` 分片文件），浏览器才能通过 hls.js 或 video.js 加载播放

**选择 SRS 的原因**：

- 开源、轻量，单节点部署即可满足需求
- 支持 RTMP 推流 → HLS / HTTP-FLV 自动转封装
- 提供 HTTP API 可查询流状态、支持 WebRTC（未来低延迟场景）
- Docker 部署，与现有架构一致

---

## 2. 镜像准备（离线方式）

服务器无外网，需在个人电脑下载镜像后打包上传

### 2.1 个人电脑下载镜像

```powershell
# 处理镜像仓库与标签。先核对仓库地址、制品版本和所用身份。
docker pull ossrs/srs:5
docker save ossrs/srs:5 -o srs.tar
```

### 2.2 上传到服务器

```powershell
# 核对远端账号、主机与目标路径。区分本机文件和远端文件。
scp C:\Users\Lenovo\Desktop\srs.tar neu@202.199.6.249:/home/neu/
```

### 2.3 服务器加载镜像

```bash
# 在文件和 Docker 制品之间转换，导入后核对标签或容器所需文件。
docker load -i /home/neu/srs.tar
```

---

## 3. 启动 SRS 容器（第一次踩坑：端口冲突）

### 3.1 首次启动失败

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run -d --name srs \
  --restart=always \
  -p 1935:1935 \
  -p 8080:8080 \
  -p 1985:1985 \
  -p 8000:8000/udp \
  ossrs/srs:5
```

**错误**：

```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use.
```

**原因**：宿主机的 **8080 端口已被 Spring Boot 后端占用**。SRS 的 HTTP 服务（提供 HLS 文件）默认也使用容器内 8080 端口，映射到宿主机时发生冲突

### 3.2 解决方法：更换宿主机映射端口
```bash
docker rm srs   # 删除失败的容器
docker run -d --name srs \
  --restart=always \
  -p 1935:1935 \
  -p 8081:8080 \
  -p 1985:1985 \
  -p 8000:8000/udp \
  ossrs/srs:5
```

- 容器内的 SRS 依然监听 8080，但宿主机用 8081 对外暴露，**避免与后端冲突**。
- 验证：`docker ps | grep srs`，确认 STATUS 为 `Up`。

### 3.3 端口说明

| 端口 | 协议 | 用途 |
|------|------|------|
| 1935 | TCP | RTMP 推流/播放 |
| 8081 | TCP | HTTP 服务（HLS 文件分发、简单 API） |
| 1985 | TCP | SRS 管理 API（查询流状态、WebRTC） |
| 8000 | UDP | WebRTC 媒体传输（可选） |

---

## 4. 集成到 Nginx 统一入口

### 4.1 为什么需要 Nginx 代理

- SRS 的 HLS 播放地址为 `http://202.199.6.249:8081/live/device1.m3u8`，带非标准端口，不美观。
- 前端页面和 API 都在 80 端口，统一入口可避免跨域问题和端口不一致的麻烦。

### 4.2 复用已有 Nginx 容器

服务器已有 `docker-nginx-1` 容器监听 80 端口（为 Dify 等服务提供代理）。**不能新建 Nginx 容器抢 80 端口**，只能在现有容器中添加配置。

### 4.3 进入容器查看现有配置

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -it docker-nginx-1 bash
cat -n /etc/nginx/conf.d/default.conf | grep -E "location /|server_name"
```

输出：

```
     5      server_name _;
     7      location /console/api {
    12      location /api {
    17      location /v1 {
    22      location /files {
    27      location /explore {
    32      location /e/ {
    38      location /iot-api/ {      ← 这是之前加的后端代理
    43      location / {              ← 这是默认的
```

需要新增一个 `/live/` 路径代理到 SRS 的 8081 端口。

### 4.4 在已有 server 块中插入 /live/ 代理

**为避免冲突，不新建 server 块，直接在原有 server 块中插入一个 location。**

使用 `sed` 在 `location / {` 前面插入：

```bash
# 读取或筛选本地文件，按实际路径与输出核对关键字段。
sed -i '43i\    location /live/ {\n        proxy_pass http://202.199.6.249:8081/live/;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n    }' /etc/nginx/conf.d/default.conf
```

- `43i`：在第 43 行（`location / {`）之前插入新内容
- `proxy_pass` 使用宿主机真实 IP `202.199.6.249`，而不是 `127.0.0.1` 或 Docker 网关，因为容器内测试发现 Docker 网关 `172.17.0.1` 不通，但宿主机内网 IP 可达

### 4.5 测试并重载

```bash
# 检查配置语法后再重载，随后验证实际流量入口。
nginx -t && nginx -s reload
exit
```

### 4.6 验证 Nginx 代理

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl -I http://localhost/live/
```

单凭 `404` 不能确认响应来自 SRS；需结合 Nginx 上游日志和直连 SRS 的结果。推流后用实际 `.m3u8` 路径及分片请求完成验证。

**当时验收到哪一步。** 此时记录了 SRS、`/live/` 代理与后端播放地址接口的部署结果，Jetson 实际推流和前端播放仍待联调。设备到位后，使用同一个流名核对 SRS 收流、外部入口的 m3u8 和分片，以及浏览器实际出画面，才算完成播放链路验收。

#### 从流名、清单和分片核对代理

记录推流端使用的 RTMP 地址、SRS 看到的流名、服务端直接播放地址和浏览器通过站点拿到的地址。播放地址的 `app/stream` 要对应推流端命名，后端生成的 URL 也要从浏览器所在网络可达。SRS API 看到了流，只证明推流抵达媒体服务，后续还有清单、分片、反代和播放器四个位置需要分别验证。

| 阶段 | 要找的证据 | 优先排查 |
|---|---|---|
| 推流端 → SRS | 服务日志或已启用的 HTTP API 出现预期流名与连接 | RTMP 端口、路径、输入源、编码器日志 |
| SRS → HLS | 能读取 m3u8，持续推流时清单序号前进 | 是否启用 HLS、分片目录及权限、首批分片是否已生成 |
| 入口 → 播放端 | 清单和至少一个分片从实际入口可获取 | 反代路径、相对 URL、Host、鉴权和 HTTPS |
| 播放器 | 能看到画面，重新连接后可恢复 | 浏览器协议支持、跨域、缓冲和解码错误 |

```bash
# SRS_API 填当前终端可达且已启用的 HTTP API 基地址。
: "${SRS_API:?请设置 SRS HTTP API 基地址}"
: "${HLS_URL:?请设置外部 m3u8 播放地址}"
curl -fsS --max-time 10 "${SRS_API%/}/api/v1/streams/"

# 看清单前几行，留意媒体序号、分片地址以及是否返回 HTML。
curl -fsS --max-time 10 "$HLS_URL" | sed -n '1,24p'
```

清单首行应为 `#EXTM3U`。取其中一个分片，用清单 URL 作为基准解析相对路径，再从同一个客户端请求。只看清单 200 容易漏掉分片路径错误。分片 404 时，核对清单是否被缓存并引用了已滚出的文件，或者反代在 m3u8 与分片使用了不同规则。HTTPS 页面播放 HTTP 内容时，看浏览器是否拦截混合内容。响应是 200 HTML 时应先排查路径回退，暂时不用改编码参数。


### 4.7 代理前后的播放地址对比

| 方式 | 地址 |
|------|------|
| 直接访问 SRS | `http://202.199.6.249:8081/live/device1.m3u8` |
| 通过 Nginx（最终使用） | `http://202.199.6.249/live/device1.m3u8` |

---

## 5. 后端添加流媒体播放地址接口

### 5.1 为什么需要后端接口

前端不应该直接拼接播放地址，而应**通过后端 API 获取**。这样将来更换 IP、切换协议（HLS→WebRTC）时，只需修改后端，前端代码不变。

### 5.2 新增 StreamController

```java
// 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
@RestController
@RequestMapping("/api/stream")
public class StreamController {

    @Value("${stream.base-url:http://202.199.6.249/live}")
    private String streamBaseUrl;

    @GetMapping("/{deviceId}")
    public ResponseEntity<Map<String, String>> getStreamUrls(@PathVariable String deviceId) {
        String hlsUrl = streamBaseUrl + "/" + deviceId + ".m3u8";
        String flvUrl = streamBaseUrl + "/" + deviceId + ".flv";
        Map<String, String> urls = new HashMap<>();
        urls.put("hls", hlsUrl);
        urls.put("flv", flvUrl);
        return ResponseEntity.ok(urls);
    }
}
```

对外完整路径：`GET /iot-api/stream/{deviceId}`  
返回示例：

**阅读提示**　hls 和 flv 是同一流的两个播放入口，客户端按所用协议选择。

```json
{"hls":"http://202.199.6.249/live/device1.m3u8","flv":"http://202.199.6.249/live/device1.flv"}
```

### 5.3 解决 Spring Security 403 拦截

项目使用了 Spring Security，新增的 `/api/stream/**` 路径未被放行（本例 Nginx 将 `/iot-api/` 重写为 `/api/`，且应用未另设 context-path），导致 403。

在 `SecurityConfig.java` 中新增一行：

```java
// 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
.requestMatchers("/api/stream/**").permitAll()
```

**区分推流授权和播放授权**

推流端用发布入口，播放器只需要读取许可。交接时分别核对谁能推哪一路、谁能看哪个站点，后端接口返回的应是当前用户有权访问的播放地址。若部署用签名或鉴权回调，隔离环境测试一个允许样本和一个拒绝样本，日志仅保留流名、入口和结果，便于区分无流与无权限。


### 5.4 重新打包部署

```bash
# 通过服务管理器操作目标进程，再核对它的状态和错误日志。
./mvnw clean package -DskipTests
scp target/*.jar neu@202.199.6.249:/home/neu/
sudo systemctl stop iot-api
sudo mv /home/neu/*.jar /opt/iot-backend/app.jar
sudo systemctl start iot-api
```

### 5.5 验证接口

```bash
curl http://localhost/iot-api/stream/device1
# 返回 {"hls":"http://202.199.6.249/live/device1.m3u8","flv":"http://202.199.6.249/live/device1.flv"}
```

---

## 6. 最终数据流

```
Jetson 摄像头
    │
    │ FFmpeg 推 RTMP 流
    │ rtmp://202.199.6.249:1935/live/device1
    ▼
SRS 容器 (:1935)
    │
    │ 自动转封装为 HLS
    │ http://202.199.6.249:8081/live/device1.m3u8
    ▼
Nginx 容器 (:80)  location /live/
    │ proxy_pass → SRS 的 8081
    │
    ▼
前端浏览器
    │ 1. 调用 /iot-api/stream/device1 获取播放地址
    │ 2. hls.js 加载 http://202.199.6.249/live/device1.m3u8
    ▼
用户看到实时视频
```

### 直播和历史录像分别验证

录像文件产生、上传对象存储、写入索引和签发回放 URL 分属不同阶段。用同一流名和起止时间比对录像文件、对象键、数据库引用和播放器请求。直播正常时也可能由于录制配置、目录权限或上传失败而没有回放。历史文件可以读却找不到记录时，查录像索引而非推流配置。 [SRS HTTP Server](https://www.ossrs.net/lts/en-us/docs/v5/doc/http-server)


---

## 7. 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| SRS 启动失败（端口冲突） | 8080 被 Spring Boot 占用 | 映射 8081:8080 避开冲突 |
| Nginx 容器内无法连宿主机 8080 | Docker 默认网桥 `172.17.0.1` 不通 | 使用宿主机真实校园网地址 `202.199.6.249` |
| 新增 `/live/` 代理后 404 | 可能尚无流，也可能路径或配置错误；需比较上游日志与直连结果 | 推流后验证 `m3u8` 文件下载正常 |
| 后端接口 403 | Spring Security 未放行 `/stream/**` | 在 SecurityConfig 中 permitAll |
| 服务器无外网 | 校园网限制 | 离线 docker save/load + scp 传输 |

### 如何区分播放失败、延迟和停推

HLS 首帧需要等待分片产生，还要有播放器缓冲。比较两种配置时，用同一输入源、同一客户端网络和相同测试时长记录首帧、持续延迟和卡顿次数。较短分片和关键帧间隔会影响切片时机、请求数量和缓存压力，调参后重新验证清单与分片。HTTP-FLV 或 WebRTC 的延迟和浏览器支持条件不同，按部署版本和所选播放器另验收。

```bash
# 用播放端可见的 URL 查看轨道、编码与分辨率。
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height \
  -of default=noprint_wrappers=1 "$HLS_URL"
```

复盘时记录推流启动时间、流名、首帧时间、播放器报错和一个成功分片。停推后观察清单是否还返回旧片段，重推时观察是否恢复和多久恢复。若 RTMP 正常而 HLS 失败，可先试 SRS 原生播放入口，再对照 Nginx 入口。如果后端返回播放地址，分别测试无流、正常流和过期签名，以便前端判断是稍后重试、重新取链接，还是显示配置错误。

### 用连续两次清单验证恢复

同一次推流中隔几秒请求两次清单，记录 `EXT-X-MEDIA-SEQUENCE`、最后一个分片名和响应时间。随着直播前进，清单窗口通常会滚动。若 SRS 原生地址持续更新、外部入口始终返回同一份，先查代理或客户端缓存；两处都停住则看推流、转码或切片。若只有特定浏览器卡住，可用 ffprobe 或另一客户端交叉确认网络、媒体格式和播放器支持。

另做一次停推再恢复。停推后读到旧片段不等于还在直播。恢复时需要验证媒体序号或分片更新、浏览器能继续播放、后端返回的 URL 仍指向同一流。换流名时还要确认历史回放不会引用新流。记录「开始推流、首个分片、首帧、停推、恢复」五个时间点，比只记“可以播”更容易复查。


---

## 8. 给团队的使用信息

| 角色 | 需要的信息 |
|------|-----------|
| **Jetson 同学** | 推流地址：`rtmp://202.199.6.249:1935/live/设备编号` |
| **前端同学** | 调用 `GET /iot-api/stream/设备编号` 获取 HLS 地址，用 hls.js 播放 |
| **后端同学** | `stream.base-url` 配置在 `/opt/iot-backend/application.properties` |

---

## 9. 当前状态

| 组件 | 状态 | 地址 |
|------|:--:|------|
| SRS 流媒体服务器 | ✅ | RTMP `1935`，HTTP `8081` |
| Nginx 代理 `/live/` | ✅ | 转发至 SRS 8081 |
| 后端播放地址接口 | ✅ | `/iot-api/stream/{deviceId}` |
| 推流 | 🔜 | 等 Jetson 硬件到位 |
| 前端播放 | 🔜 | 推流后即可测试 |

---
