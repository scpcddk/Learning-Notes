# SRS 流媒体服务器部署全流程复盘

> [!IMPORTANT]
> **目标**：为 Jetson 摄像头提供推流接收服务，并将 RTMP 流转换为 HLS 格式，使前端可通过网页直接播放 
> **环境**：实验室 Ubuntu 22.04 服务器（内网 IP `202.199.6.249`），已运行 Spring Boot 后端（占用 8080）、Nginx 容器（占用 80）、MySQL 等。 
> **约束**：服务器无外网，需离线部署；不能影响已有服务；最终通过统一入口（80 端口）提供播放地址

---

## 1. 为什么需要 SRS

Jetson 摄像头采集的视频原始流通常是 RTSP 或 RTMP 协议，**浏览器无法直接播放**。需要一台流媒体服务器在中间做转换，将 RTMP 流转封装为 **HLS**（`.m3u8` 分片文件），浏览器才能通过 hls.js 或 video.js 加载播放

选择 SRS 的原因：
- 开源、轻量，单节点部署即可满足需求
- 支持 RTMP 推流 → HLS / HTTP-FLV 自动转封装
- 提供 HTTP API 可查询流状态、支持 WebRTC（未来低延迟场景）
- Docker 部署，与现有架构一致

---

## 2. 镜像准备（离线方式）

服务器无外网，需在个人电脑下载镜像后打包上传。

### 2.1 个人电脑下载镜像

```powershell
docker pull ossrs/srs:5
docker save ossrs/srs:5 -o srs.tar
```

### 2.2 上传到服务器

```powershell
scp C:\Users\Lenovo\Desktop\srs.tar neu@202.199.6.249:/home/neu/
```

### 2.3 服务器加载镜像

```bash
docker load -i /home/neu/srs.tar
```

---

## 3. 启动 SRS 容器（第一次踩坑：端口冲突）

### 3.1 首次启动失败

```bash
docker run -d --name srs \
  --restart=always \
  -p 1935:1935 \
  -p 8080:8080 \      # ← 这里出问题了
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
  -p 1935:1935 \      # RTMP 推流端口
  -p 8081:8080 \      # 将 SRS HTTP 服务映射到宿主机的 8081 端口
  -p 1985:1985 \      # SRS API 端口
  -p 8000:8000/udp \  # WebRTC 候选端口（UDP）
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
sed -i '43i\    location /live/ {\n        proxy_pass http://202.199.6.249:8081/live/;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n    }' /etc/nginx/conf.d/default.conf
```

- `43i`：在第 43 行（`location / {`）之前插入新内容
- `proxy_pass` 使用宿主机真实 IP `202.199.6.249`，而不是 `127.0.0.1` 或 Docker 网关，因为容器内测试发现 Docker 网关 `172.17.0.1` 不通，但宿主机内网 IP 可达

### 4.5 测试并重载

```bash
nginx -t && nginx -s reload
exit
```

### 4.6 验证 Nginx 代理

```bash
curl -I http://localhost/live/
```

返回 `HTTP/1.1 404 Not Found` 说明请求已到达 SRS（因为还没有流，所以 404），但 **Nginx 代理链路已通**。

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
@RestController
@RequestMapping("/stream")
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

```json
{"hls":"http://202.199.6.249/live/device1.m3u8","flv":"http://202.199.6.249/live/device1.flv"}
```

### 5.3 解决 Spring Security 403 拦截

项目使用了 Spring Security，新增的 `/stream/**` 路径未被放行，导致 403。

在 `SecurityConfig.java` 中新增一行：

```java
.requestMatchers("/stream/**").permitAll()
```

### 5.4 重新打包部署

```bash
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

---

## 7. 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| SRS 启动失败（端口冲突） | 8080 被 Spring Boot 占用 | 映射 8081:8080 避开冲突 |
| Nginx 容器内无法连宿主机 8080 | Docker 默认网桥 `172.17.0.1` 不通 | 使用宿主机真实内网 IP `202.199.6.249` |
| 新增 `/live/` 代理后 404 | 只是没有流推上来，非配置错误 | 推流后验证 `m3u8` 文件下载正常 |
| 后端接口 403 | Spring Security 未放行 `/stream/**` | 在 SecurityConfig 中 permitAll |
| 服务器无外网 | 校园网限制 | 离线 docker save/load + scp 传输 |

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
