# SRS 流媒体服务器通用操作手册

> **定位**：SRS 是一个开源的流媒体服务器，核心作用就是**协议转换**——接收并分发 RTMP 等流，可转封装为 HLS/HTTP-FLV 或接入 WebRTC；RTSP 摄像头通常需 FFmpeg 等先转推，HTTP-FLV 通常需网页播放器库。
> **学习目标**：掌握 50% 可以检查别人部署的 SRS 是否正确，掌握 80% 可以独立完成部署与排错。

---

## 1. 核心概念（10 分钟建立认知）

SRS 在项目中扮演的角色就是 **“视频格式翻译官”**。你不需要知道它内部怎么翻译的，只需要知道三种地址：

| 地址类型 | 格式 | 谁来用 |
|----------|------|--------|
| **推流地址** | `rtmp://服务器IP:1935/live/流名` | 摄像头/Jetson/FFmpeg/OBS |
| **拉流地址（FLV）** | `http://服务器IP:8080/live/流名.flv` | 前端网页（延迟 1-3 秒） |
| **拉流地址（HLS）** | `http://服务器IP:8080/live/流名.m3u8` | 前端网页（延迟 5-10 秒，兼容性好） |

**关键理解**：推流协议（RTMP/RTSP）和播放协议（FLV/HLS）是两套不同的东西，SRS 在启用对应配置后转封装或桥接；不支持的编码仍需转码。推流端和播放端互不关心对方用的是什么协议。

---

## 2. Docker 部署（最常用方式）

### 2.1 一条命令启动

```bash
docker run -d --name srs \
  --restart=always \
  -p 1935:1935 \
  -p 8080:8080 \
  -p 1985:1985 \
  -p 8000:8000/udp \
  ossrs/srs:5
```

> [!NOTE]
> 
> - **“前”（左侧）**：代表宿主机（你的物理机或云服务器）的端口。
> - **“后”（右侧）**：代表容器内部（SRS 服务进程监听）的端口。
> 
> **访问规则**：外部客户端（如 OBS、浏览器）访问你服务器的 左侧端口，Docker 会自动将流量转发给容器内 SRS 监听的 右侧端口

### 2.2 Docker Compose 方式（推荐，便于维护）

如果不习惯记长命令，可以用 `docker-compose.yml` 统一管理：

```yaml
version: '3'
services:
  srs:
    image: ossrs/srs:5
    container_name: srs
    restart: always
    ports:
      - "1935:1935"
      - "8080:8080"
      - "1985:1985"
      - "8000:8000/udp"
```

之后只需 `docker compose up -d` 即可启动。

### 2.3 端口说明

| 端口 | 协议 | 用途 |
|------|------|------|
| `1935` | TCP | RTMP 推流/播放 |
| `8080` | TCP | HTTP-FLV、HLS 文件服务；管理 API 通常在 1985 |
| `1985` | TCP | HTTP API（查询、控制） |
| `8000` | UDP | WebRTC 媒体传输（可选） |

> [!WARNING]
> 按实际启用的协议放行所需端口；管理 API 1985 应限制来源，使用 Nginx 统一入口时不一定需要公开 8080。这是新手最容易忘记的一步。

### 2.4 常见问题：端口冲突

如果宿主机 8080 已经被其他服务占用（如 Spring Boot），换一个映射端口即可：

```bash
docker run -d --name srs \
  --restart=always \
  -p 1935:1935 \
  -p 8081:8080 \
  -p 1985:1985 \
  -p 8000:8000/udp \
  ossrs/srs:5
```

此时 FLV/HLS 地址变成 `http://服务器IP:8081/live/流名.flv`。

---

## 3. 推流与播放地址速查

### 3.1 推流地址

```
rtmp://服务器IP:1935/live/流名
```

- `流名` 是自定义的字符串，比如 `camera01`、`device001`、`rgb-a-lab`
- 用 FFmpeg 推流示例：
  
  ```bash
  ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -f flv rtmp://39.102.213.11:1935/live/camera01
  ```

- 用 OBS 推流：设置 → 推流 → 服务选“自定义” → 服务器填 `rtmp://39.102.213.11:1935/live/` → 串流密钥填 `camera01`

### 3.2 播放地址

| 格式 | 地址模板 | 前端播放器 |
|------|---------|-----------|
| HTTP-FLV | `http://服务器IP:8080/live/流名.flv` | `mpegts.js` 或 `flv.js` |
| HLS | `http://服务器IP:8080/live/流名.m3u8` | `hls.js` 或 `video.js` |
| WebRTC | 需通过 API 获取 | SRS WebRTC SDK |

**注意**：先用 video.canPlayType 检测原生 HLS 支持；不支持时再用 hls.js（需浏览器具备相应能力）。HTTP-FLV 通常需 mpegts.js/flv.js，且编码必须为浏览器支持的格式；转封装不等于转码。

---

## 4. Nginx 反向代理（生产环境推荐）

**为什么需要？**

- 统一入口，隐藏非标准端口（8080/8081）
- 避免跨域问题
- 方便后续配置 HTTPS

**Nginx 配置片段**：

```nginx
location /live/ {
    proxy_pass http://127.0.0.1:8080/live/;   # 如果 SRS 映射到宿主机的 8081，这里改 8081
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

配置后，播放地址变成 `http://服务器IP/live/流名.flv`，不再需要带端口号。

> SRS 常用 WebRTC 信令走 `/rtc/v1/play/`、WHIP/WHEP 等 HTTP API，并不要求 WebSocket 升级。需另外代理对应信令路径；媒体链路还需正确的 candidate、公网地址及 UDP/TCP 可达性，必要时配置 TURN。HTTP 代理成功不代表媒体链路已通。

---

## 5. 常用排查命令

### 5.1 查看 SRS 自身日志（最重要）

```bash
docker logs -f --tail 50 srs
```

如果推流/播放异常，日志里通常会有直接提示，如：
- `accept client`：有连接进入
- `publish`：有推流开始
- `stream not found`：流不存在（推流没成功或流名不对）

### 5.2 查看谁在推流

```bash
curl http://IP:1985/api/v1/clients | python3 -m json.tool
```

返回 JSON 中，找到 `"publishing": true` 的条目就是正在推流的客户端。

### 5.3 测试播放地址是否可访问

```bash
curl -I http://IP:8080/live/流名.flv
```

- 返回 `200 OK`：流存在，可正常播放
- 返回 `404 Not Found`：推流没成功，或流名错误

---

## 6. 常见排错清单

### 6.1 推流失败

| 现象 | 排查步骤 |
|------|---------|
| 推流端报连接超时 | 1. 检查安全组/防火墙是否放行 **1935** 端口<br>2. `telnet 服务器IP 1935` 测试连通性<br>3. `docker ps \| grep srs` 确认容器在运行<br>4. `docker logs -f --tail 50 srs` 查看 SRS 日志 |
| 推流端报认证失败 | SRS 默认无认证，检查 URL 格式是否正确（`/live/` 不能少） |

### 6.2 播放失败

| 现象 | 排查步骤 |
|------|---------|
| 前端播放黑屏/报错 | 1. 确认是否引入了 `hls.js` 或 `mpegts.js`，不能用原生 `<video>` 标签<br>2. `curl -I http://服务器IP:8080/live/流名.flv` 测试地址是否可访问<br>3. 返回 404 → 说明推流没成功，检查推流端 |
| curl 测试返回 200，前端仍不能播 | 前端跨域问题，检查 Nginx 或 SRS 是否配置了 CORS |

### 6.3 HLS 延迟高

**默认切片 10 秒，窗口 60 秒，会导致 30-60 秒延迟**

优化配置（需要挂载配置文件或进入容器修改 `srs.conf`）：

```nginx
hls {
    enabled on;
    hls_fragment 2;    # 每片 2 秒（默认 10）
    hls_window 6;      # 窗口保留 6 秒（默认 60）
}
```

如果还需要更低延迟（1-3 秒），直接改用 HTTP-FLV，HLS 协议本身有延迟下限。

---

## 7. 进阶功能速查（需要时再查，不必深究）

| 功能 | 关键配置/API | 用途 |
|------|-------------|------|
| 录制直播流 | `dvr` 块配置 | 把直播流保存为 MP4 文件 |
| 推流认证 | `security` IP 访问控制或 `http_hooks.on_publish` 业务鉴权 | 防止未授权推流 |
| WebRTC 播放 | 调用 `http://IP:1985/rtc/v1/play/` API | 超低延迟（<1 秒） |
| HTTP API 查询 | `http://IP:1985/api/v1/clients` | 查看当前连接数、推流状态 |
| 回调通知 | `http_hooks` 块配置 | 推流/断流时通知后端接口 |

**不要深学的原则**：上面这些功能，你只需要知道它们存在，需要用时去查官方文档（`https://ossrs.net`）对应的配置块，复制粘贴改参数即可。

---

## 8. 与后端/前端的对接规范

**给硬件同学**：

- 推流地址：`rtmp://服务器IP:1935/live/设备编号`
- 设备编号需与前端约定一致

**给前端同学**：

- 播放地址模板：`http://服务器IP/live/设备编号.flv`（或 `.m3u8`）
- FLV 通常用 mpegts.js；HLS 优先检测原生支持，否则使用 hls.js
- 推荐让后端提供一个接口，返回播放地址，前端调用接口获取，而不是前端硬编码拼接

**给后端同学**：

- 可以提供 API 返回播放地址（如 `/iot-api/stream/{deviceId}`），这样将来换协议只需改后端，不需要改前端

---

## 9. 一句话速查表

| 需求 | 操作 |
|------|------|
| 启动 SRS | `docker run -d --name srs --restart=always -p 1935:1935 -p 8080:8080 -p 1985:1985 ossrs/srs:5` |
| 检查是否在运行 | `docker ps \| grep srs` |
| 查看 SRS 日志 | `docker logs -f --tail 50 srs` |
| 查看谁在推流 | `curl http://IP:1985/api/v1/clients \| python3 -m json.tool` |
| 测试播放地址 | `curl -I http://IP:8080/live/流名.flv` |
| 降低 HLS 延迟 | 改配置：`hls_fragment 2; hls_window 6;` |
| 安全组放行 | 按需放行 1935、HTTP 入口和 WebRTC 媒体端口；1985 管理 API 限制来源 |

---
> [!IMPORTANT]
**总结**：SRS 就是一个“格式转换黑盒”。你只需要记住三种地址（推流、FLV 播放、HLS 播放），会 Docker 启动，会看日志，会测试连通性，就已经掌握了 80% 的实用技能。剩下的 20% 高级功能（录制、WebRTC、回调），遇到时查文档即可。

---
