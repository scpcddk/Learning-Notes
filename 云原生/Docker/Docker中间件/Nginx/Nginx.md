# Nginx 工程实战手册（云原生 / AIOps 方向）

---

## 1. 全局骨架：一个请求如何被接管

**看懂 30%**：只要明白一个 `server` 块监听一个端口，一个 `location` 匹配一条路径。

```nginx
# 指定 Nginx 工作进程的数量，通常设置为服务器 CPU 核心数，
# 以充分利用多核 CPU 的并发处理能力。
worker_processes  1;

# events 块用于配置 Nginx 处理连接的方式
events {
    # 每个工作进程可以同时处理的最大连接数。
    # 该数值应根据系统资源（如文件描述符限制）和预期负载调整。
    worker_connections  1024;
}

# http 块是 Nginx 处理 HTTP 请求的核心配置
http {
    # 定义一个虚拟主机（server）配置
    server {
        # 监听 80 端口（默认的 HTTP 端口）
        listen       80;
        # 指定该虚拟主机响应的域名，当请求的 Host 头匹配 example.com 时生效
        server_name  example.com;

        # 匹配根路径 / 的请求
        location / {
            # 指定静态文件的根目录，Nginx 会在此目录下查找请求的文件
            root   /usr/share/nginx/html;
            # 当请求的是目录时，默认返回 index.html 文件（首页返回）
            index  index.html;
        }

        # 匹配以 /api/ 开头的请求，用于反向代理到后端服务
        location /api/ {
            # 将匹配到的请求转发给名为 backend 的上游服务器（需在 upstream 中定义）
            # 注意：这里仅作示例，实际需配置 upstream 块或直接写完整地址，如 http://127.0.0.1:8080
            proxy_pass http://backend;
        }
    }
}
```

![alt text](<Image/屏幕截图 2026-08-18 192520.png>)
![alt text](<Image/屏幕截图 2026-08-18 192715.png>)

---

## 2. location 匹配规则（绝对的配置核心）

**看懂 50%**：记住这张优先级表就能解决 90% 的转发问题。

| 优先级 | 符号 | 示例 | 行为 |
|--------|------|------|------|
| 最高 | `=` | `= /api/health` | **精确匹配**，立即停止搜索 |
| 高 | `^~` | `^~ /images/` | **前缀匹配**，匹配后不再检查正则 |
| 中 | `~` `~*` | `~ \.php$` | **正则匹配**（`~` 区分大小写，`~*` 不区分） |
| 低 | 无符号 | `/` | 普通前缀匹配，**最长匹配**优先 |

**手写要求（70%）**：必须牢记 `=` 和 `^~` 会截断正则。匹配顺序：先精确前缀，再带 `^~` 的前缀，然后按配置顺序逐个尝试正则，最后用最长的普通前缀。

---

## 3. 反向代理核心配置（proxy_pass 与请求头传递）

反向代理就是 Nginx 替客户端把请求转发给后端服务器，再把后端响应返回给客户端。这是 Nginx 最核心的用途。

**对比**：

| 核心维度 | 正向代理 | 反向代理 |
| :--- | :--- | :--- |
| **代理主体** | 代表**客户端**发起请求 | 代表**服务端**接收请求 |
| **隐藏对象** | 隐藏真实客户端IP，保护隐私 | 隐藏真实服务器IP，增强安全 |
| **典型应用** | VPN翻墙、突破地域限制 | Nginx / Apache、负载均衡、CDN |
| **核心价值** | 解决客户端访问受限问题 | 提升服务高可用与并发能力 |

> [!TIP]
> 正向代理是“替用户办事”，反向代理是“替服务器办事”，二者在网络传输中起到了完全不同的**桥梁作用**

![alt text](<Image/屏幕截图 2026-08-19 112411.png>)

### 3.1 proxy_pass 的尾巴区别（极易踩坑）

**看懂 30%**：加不加 `/` 影响路径拼接。

```nginx
location /api/ {
    # 有 /  : /api/user → http://backend/user
    proxy_pass http://backend/;

    # 无 /  : /api/user → http://backend/api/user
    proxy_pass http://backend;
}
```

> [!TIP]
> **建议**：一律在 `proxy_pass` 目标 URL 后加 `/`，`location` 也写成带 `/` 的前缀，关系最清晰。

### 3.2 必须传递的请求头（后端获取真实信息的关键）

默认情况下，Nginx 转发请求时不会自动带上客户端的真实 IP、原始协议等信息，后端 Spring Boot 拿到的可能是 `127.0.0.1`。必须手动设置：

```nginx
location /api/ {
    proxy_pass http://backend/;

    # 保留原始 Host 头，后端才能知道用户访问的是哪个域名
    proxy_set_header Host $host;

    # 传递客户端真实 IP（后端通过 X-Real-IP 获取）
    proxy_set_header X-Real-IP $remote_addr;

    # 传递代理链路上的所有 IP（标准写法，后端通过 X-Forwarded-For 获取）
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # 传递原始协议（http 或 https），后端用于判断是否走 HTTPS
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

<details><summary>补充理解</summary>

### 补充理解

这段配置是 **Nginx 反向代理时的“信息传递”设置**，目的是让后端的 Spring Boot 服务能知道“真正的客户端是谁、用的什么协议、访问的哪个域名”，而不是只知道“请求是从 Nginx 转发过来的”。

---

#### 为什么需要这些配置？

默认情况下，客户端请求流程是这样的：

```
客户端(浏览器)  →  Nginx(反向代理)  →  后端 Spring Boot(8080)
```

如果 Nginx 不做任何设置，后端 Spring Boot 收到请求时，看到的信息是：

- **来源 IP**：`127.0.0.1` 或 Nginx 所在机器的 IP（因为请求是 Nginx 发起的）
- **Host 头**：可能变成了 `backend` 或 `127.0.0.1:8080`（取决于 Nginx 配置）
- **协议**：后端以为客户端用的是 HTTP，而实际上客户端可能用的是 HTTPS

**结果就是**：后端无法知道真正的客户端是谁、用的什么协议，日志里全是内网 IP，无法做用户分析、安全审计、限流等。

---

#### 逐行解释这段配置的作用

```nginx
location /api/ {
    proxy_pass http://backend/;

    # 1. 保留原始 Host 头
    proxy_set_header Host $host;

    # 2. 传递客户端真实 IP
    proxy_set_header X-Real-IP $remote_addr;

    # 3. 传递代理链路上的所有 IP
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # 4. 传递原始协议
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

| 配置行 | 作用 | 后端如何获取 |
|--------|------|--------------|
| `proxy_set_header Host $host;` | 把客户端请求的原始 `Host` 头（如 `www.example.com`）传给后端，而不是 Nginx 自己定义的 `backend` | Spring Boot 通过 `request.getServerName()` 或 `@RequestHeader("Host")` 获取 |
| `proxy_set_header X-Real-IP $remote_addr;` | 把真实客户端 IP 放在 `X-Real-IP` 头里传给后端 | Spring Boot 通过 `request.getHeader("X-Real-IP")` 获取 |
| `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` | 把客户端 IP 追加到 `X-Forwarded-For` 头中，如果请求已经经过其他代理，会保留完整链路 | Spring Boot 通过解析 `X-Forwarded-For` 获取（需配置） |
| `proxy_set_header X-Forwarded-Proto $scheme;` | 把客户端使用的协议（http 或 https）放在 `X-Forwarded-Proto` 头里 | Spring Boot 判断请求是否走 HTTPS（如生成绝对 URL） |

---

#### 不配置会有什么问题？

假设你的项目上线后，后端 Spring Boot 的访问日志里记录到的 IP 全是 `127.0.0.1`：

- 无法统计用户地域分布
- 无法对恶意 IP 进行封禁
- 无法实现基于 IP 的限流
- 如果后端生成回调地址或 OAuth 重定向地址，可能用 `http` 而不是 `https`，导致安全警告

所以，**在 Nginx 做反向代理时，这几行是标准配置，直接复制即可**。

---

#### 后端 Spring Boot 如何配合

光有 Nginx 配置还不够，Spring Boot 需要**信任这些头**，并从中解析出真实信息。常见做法：

##### 方法一：开启 Forwarded Headers 支持（推荐）

在 `application.yml` 中添加：

```yaml
server:
  forward-headers-strategy: native
```

这样 Spring Boot 会自动使用 `X-Forwarded-For`、`X-Forwarded-Proto` 等头来修正 `request.getRemoteAddr()`、`request.isSecure()` 等。

##### 方法二：手动获取

也可以在代码中手动读取：

```java
String clientIp = request.getHeader("X-Forwarded-For");
if (clientIp == null || clientIp.isEmpty()) {
    clientIp = request.getRemoteAddr();
}
```

---

#### 总结

这段配置就是 **让后端“看见”真实世界的桥**。没有它，后端就像被蒙住了眼睛，只能看到 Nginx 这一层。加上它，后端就能知道客户端是谁、用的什么协议、访问的哪个域名，从而做出正确的业务判断和日志记录。
</details>


> [!TIP]
> 在 Spring Boot 中，如果想要正确获取客户端 IP，通常需要配置 `server.forward-headers-strategy=NATIVE` 或使用 `X-Forwarded-For` 解析。

### 3.3 超时与缓冲控制（防止后端拖垮 Nginx）

```nginx
location /api/ {
    proxy_pass http://backend/;

    # 连接后端超时时间（默认 60s，建议调小）
    proxy_connect_timeout 2s;

    # 等待后端响应超时时间（默认 60s）
    proxy_read_timeout 10s;

    # 发送请求体到后端的超时时间
    proxy_send_timeout 10s;
}
```

> [!TIP]
> 这些超时参数在微服务场景下非常重要，如果后端某个服务挂起，Nginx 能快速失败并返回错误，而不是无限等待。

---

## 4. 常用内置变量（日志与观测必用）

**理解即可**，需要时查表。这些是 AIOps 日志分析的基础。

| 变量 | 含义 |
|------|------|
| `$remote_addr` | 客户端 IP |
| `$time_local` | 本地时间 |
| `$request` | 原始请求行 (`GET /api HTTP/1.1`) |
| `$status` | 响应状态码 |
| `$body_bytes_sent` | 响应体大小 |
| `$request_time` | 请求处理总时间（秒） |
| `$upstream_response_time` | 上游服务器响应时间（秒） |
| `$upstream_addr` | 上游服务器地址 |

---

## 5. 静态文件与缓存（前端部署必备）

```nginx
# 1. 根路径 / 的请求处理规则
location / {
    # 指定静态文件的根目录，最终路径为 /app/dist + 请求的 URI
    # 例如请求 /css/style.css 则查找 /app/dist/css/style.css
    root   /app/dist;

    # 当请求的 URI 以 / 结尾（即目录）时，默认返回 index.html
    index  index.html;

    # try_files 按顺序尝试(先查找文件，再尝试目录，最后回退到 index.html，确保 SPA 路由正常工作)：
    #   $uri          —— 尝试直接匹配文件（如 /about.html）
    #   $uri/         —— 尝试作为目录处理（如 /about/ 则查找 /app/dist/about/index.html）
    #   /index.html   —— 如果以上都不存在，则返回根目录的 index.html
    # 这解决了 Vue/React 等 SPA 应用使用 history 模式时，刷新非根路径（如 /user/123）导致 404 的问题，
    # 因为所有路径都会 fallback 到 index.html，由前端路由接管。
    try_files $uri $uri/ /index.html;
}

# 2. 静态资源（图片、CSS、JS）的缓存策略
# 使用 ~* 表示不区分大小写的正则匹配，匹配常见的静态文件扩展名
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    # 设置浏览器缓存过期时间为 30 天（客户端可缓存）
    expires 30d;

    # 添加响应头 Cache-Control: public，允许任何中间代理（如 CDN）缓存该资源，
    # 同时与 expires 配合，告知浏览器缓存的有效期。
    add_header Cache-Control "public";
}
```

> [!TIP]
> `root` vs `alias`：`root` 会把 location 路径拼到后面；`alias` 是别名替换。日常用 `root` 就够了。

![alt text](<Image/屏幕截图 2026-08-18 193249.png>)

---

## 6. 跨域与常见头处理（直接复制）

```nginx
location /api/ {
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
    add_header Access-Control-Allow-Headers 'Content-Type, Authorization';
    if ($request_method = OPTIONS) {
        return 204;
    }
    proxy_pass http://backend/;
}
```

---

## 7. 负载均衡与高级容灾

**基础（看懂 30%）**：用 `upstream` 定义一组后端。
**进阶（看懂 70%）**：配置权重、失败重试、备份节点和重试策略。

![alt text](<Image/屏幕截图 2026-08-19 163209.png>)

```nginx
# 定义上游服务器组（后端服务集群）
upstream backend {
    # 主节点 1：权重 3（每 4 次请求中，约 3 次转发到此节点）
    # max_fails=2 表示在 fail_timeout（30秒）内，若该节点失败次数达到 2 次，则将其标记为“不可用”
    # fail_timeout=30s 既是失败计数窗口，也是节点被摘除后的恢复探测周期（30秒后重新尝试连接）
    server 10.0.0.1:8080 weight=3 max_fails=2 fail_timeout=30s;

    # 主节点 2：权重 1（普通节点，无额外失败阈值，使用默认值：max_fails=1，fail_timeout=10s）
    server 10.0.0.2:8080 weight=1;

    # 热备节点：仅在所有非 backup 节点（即 10.0.0.1 和 10.0.0.2）均被标记为不可用时，才会接收请求
    # 平时不参与负载均衡，也无需设置 max_fails（因为只有被启用后才会开始统计）
    server 10.0.0.3:8080 backup;
}

server {
    # 匹配 /api/ 路径的请求
    location /api/ {
        # 将请求代理到 upstream 组 "backend"
        # 注意：末尾带 "/" 表示将匹配路径部分替换（如 /api/user -> /user）
        proxy_pass http://backend/;

        # 与后端建立连接的超时时间（2 秒），超时则视为失败
        proxy_connect_timeout 2s;

        # 从后端读取响应的超时时间（10 秒），超时则视为失败
        proxy_read_timeout 10s;

        # 定义在何种情况下，Nginx 会将请求尝试转发给下一个后端节点（重试）
        # error             ：建立连接、发送请求或读取响应头时发生网络错误
        # timeout           ：连接超时、读取超时等
        # http_502/503/504  ：后端返回这些状态码时触发重试（5xx 类错误）
        proxy_next_upstream error timeout http_502 http_503 http_504;

        # 重试的最大次数（包括第一次尝试），这里设置为 2，即最多尝试 2 个节点
        # 若所有节点均失败，则返回最后一次尝试的错误响应给客户端
        proxy_next_upstream_tries 2;

        # 重试的总时间限制（10 秒），如果在这段时间内所有重试均未成功，则终止重试并返回错误
        proxy_next_upstream_timeout 10s;
    }
}
```

### 7.1 关键行为总结

| 参数/机制 | 作用 |
|--------|------|
| `weight` | 加权轮询，权重越高被选中的概率越大 |
| `max_fails` + `fail_timeout` | 故障摘除机制：在 `fail_timeout` 秒内，若某节点失败次数达到 `max_fails`，则该节点被临时标记为“不可用”，后续请求不再转发给它，直到 `fail_timeout` 结束后重新探测。 |
| `backup` | 备用节点，平时不参与调度；仅当所有非 `backup` 节点均不可用时才启用。 |
| `proxy_next_upstream` | 允许在遇到指定错误时自动重试下一个节点，提高可用性。 |
| `proxy_next_upstream_tries` | 限制重试次数（含首次），避免无限重试。 |
| `proxy_next_upstream_timeout` | 限制整个重试过程的最大耗时，超时则直接返回错误。 |

### 7.2 注意事项

1. **超时与重试的关系**  
   - 当 `proxy_connect_timeout` 或 `proxy_read_timeout` 触发时，会被 `proxy_next_upstream` 捕获并触发重试。
   - 重试的总时间受 `proxy_next_upstream_timeout` 限制，若所有重试均超时，最终响应时间可能接近此值。

2. **故障恢复机制**  
   - 节点被摘除后，Nginx 会在 `fail_timeout` 结束后，尝试将请求转发给它（相当于探测），若探测成功则恢复权重，否则再次开始计数。

3. **`backup` 节点的行为**  
   - `backup` 节点本身也会受到 `max_fails` 和 `fail_timeout` 影响，但只有在它被激活（即主节点全挂）后，这些参数才生效。

4. **使用建议**  
   - 若业务对稳定性要求高，可适当调大 `proxy_next_upstream_tries` 和 `proxy_next_upstream_timeout`。
   - 若后端服务经常出现非致命错误（如偶发 502），可加入 `http_500` 到重试条件中，但需注意幂等性（GET/HEAD 重试安全，POST 等非幂等请求需谨慎）。
   - `fail_timeout` 不宜过短，否则可能因网络抖动频繁摘除节点；也不宜过长，会导致故障恢复慢。

---

## 8. JSON 格式日志（直通 AIOps）

**看懂 70%**：自定义日志字段，供 ELK 或 AIOps 算法消费。

```nginx
log_format json_combined escape=json '{'
    '"timestamp":"$time_iso8601",'
    '"request_id":"$request_id",'
    '"client_ip":"$remote_addr",'
    '"request":"$request",'
    '"status":$status,'
    '"body_bytes_sent":$body_bytes_sent,'
    '"request_time":$request_time,'
    '"upstream_response_time":"$upstream_response_time",'
    '"upstream_addr":"$upstream_addr"'
'}';

access_log /var/log/nginx/access.log json_combined;
```

---

## 9. 注入全链路追踪 ID（为 AIOps 铺路）

**理解即可**：让每条请求在 Nginx 和后端日志中带上同一个 ID，方便故障串联。

```nginx
location /api/ {
    proxy_set_header X-Request-Id $request_id;   # Nginx 1.11.0+ 内置变量
    proxy_pass http://backend/;
}
```

后端（Spring Boot）从请求头取出 `X-Request-Id` 并打印到日志，即可完成全链路串联。

---

## 10. 开启基本监控指标（直通 Prometheus）

**看懂 50%**：`stub_status` 能暴露连接数、请求数。

```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;          # 只允许本机或 exporter 访问
    deny all;
}
```

页面输出示例：

```
Active connections: 3
server accepts handled requests
 100 100 200
Reading: 0 Writing: 1 Waiting: 2
```

Prometheus 会通过 exporter 将这些数字转成时序数据。

---

## 11. 一键接入 Prometheus Exporter（云原生必备）

**会用即可**：Docker 启动 exporter 抓取 `stub_status`。

```bash
docker run -d \
  --name nginx-exporter \
  --network host \
  -p 9113:9113 \
  nginx/nginx-prometheus-exporter:latest \
  -nginx.scrape-uri=http://127.0.0.1:80/nginx_status
```

之后在 Prometheus 配置 target 为 `你的IP:9113`，Grafana 即可画出 QPS、并发等面板。

---

## 12. HTTPS 与安全加固（生产必备）

**看懂 50%**：知道 HTTPS 在 Nginx 上就是加一个 443 端口的 server 块，配上证书路径，再把 HTTP 跳转到 HTTPS
**看懂 70%**：能配置 TLS 版本、安全响应头，并理解与 Spring Boot 配合时的协议传递

![alt text](<Image/屏幕截图 2026-08-19 175053.png>)

### 12.1 基础 HTTPS 配置

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    # 证书文件路径（公钥证书）
    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    # 私钥文件路径
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # 只启用 TLS 1.2 和 1.3（禁用过时的 SSLv3、TLS 1.0、1.1）
    ssl_protocols TLSv1.2 TLSv1.3;

    # 选用安全的加密套件（可参考 Mozilla SSL Configuration Generator）

    # 指定服务器允许使用的 TLS 加密套件列表。
    # 加密套件决定了客户端与服务器之间如何加密通信，直接关系到连接的安全性。
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';

    # 让服务器优先使用自己定义的加密套件顺序，而不是客户端的偏好顺序。
    # 好处：防止客户端故意选择较弱的加密套件（降级攻击），确保始终使用我们指定的安全套件。
    ssl_prefer_server_ciphers on;

    # 其他 location 配置...
    location / {
        root /app/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

> [!NOTE]
> **证书获取方式**：
> 
> - **自签名**：`openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout privkey.pem -out fullchain.pem`
> - **Let's Encrypt**：使用 `certbot` 自动申请和续期。

### 12.2 HTTP 自动跳转 HTTPS

再配一个 80 端口的 server，将所有 HTTP 请求 301 重定向到 HTTPS。

```nginx
server {
    listen 80;
    server_name example.com;

    # 保留原始路径和查询参数，重定向到 https
    return 301 https://$host$request_uri;
}
```

> 这样用户访问 `http://example.com/api/user` 会自动跳到 `https://example.com/api/user`。

### 12.3 安全响应头（防常见 Web 攻击）

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    # 防止点击劫持：禁止页面被嵌入 iframe
    add_header X-Frame-Options "SAMEORIGIN" always;

    # 防止 MIME 类型嗅探
    add_header X-Content-Type-Options "nosniff" always;

    # 启用浏览器 XSS 过滤
    add_header X-XSS-Protection "1; mode=block" always;

    # 内容安全策略（CSP），按需调整
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # 强制浏览器在指定时间内使用 HTTPS（HSTS，只加在 HTTPS server 块）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 其余 location...
}
```

> [!NOTE]
> `always` 参数确保即使返回错误页（如 404、500）也会带上这些头。

### 12.4 其他安全加固措施

```nginx
# 1. 隐藏 Nginx 版本号（放在 http 块，全局生效）
server_tokens off;

# 2. 限制请求方法（放在 server 或 location 块）
if ($request_method !~ ^(GET|POST)$) {
    return 405;
}

# 3. 防盗链（放在静态资源 location 中）
location ~* \.(jpg|jpeg|png|gif|css|js)$ {
    valid_referers none blocked example.com *.example.com;
    if ($invalid_referer) {
        return 403;
    }
}

# 4. 限流防 CC 攻击（放在 http 块定义，location 中引用）
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend/;
        }
    }
}
```

> [!NOTE]
>
> - `server_tokens off;` 建议放在 `http` 块，全局隐藏版本号
> - 限制请求方法通常放在 `server` 或具体 `location` 中，注意避免误伤正常请求
> - 防盗链的 `valid_referers` 需根据你的实际域名调整白名单
> - 限流使用 `limit_req_zone` 定义内存区域，`limit_req` 应用规则，`burst` 允许突发流量，`nodelay` 表示超出部分立即丢弃

### 12.5 与 Spring Boot 配合的注意事项

当 Nginx 终止 HTTPS 后，内部转发给 Spring Boot 的通常又是 HTTP。所以需要正确传递协议信息，让后端知道原始请求是 HTTPS。

```nginx
location /api/ {
    proxy_pass http://backend/;

    # 关键：传递原始协议（https），后端才知道用户用的是 HTTPS
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
}
```

Spring Boot 侧配置信任这些头：

```yaml
server:
  forward-headers-strategy: native
```

这样后端在生成绝对 URL、处理重定向、安全校验时，会认为是 HTTPS。

### 12.6 常用安全排查点

- 证书过期：`openssl x509 -enddate -noout -in fullchain.pem`
- 测试 TLS 安全性：使用在线工具（如 SSL Labs）或 `nmap --script ssl-enum-ciphers`
- 别忘了给 80 端口做跳转，否则用户手动输入 `http://` 就无法升级到 HTTPS。

---

## 13. 性能调优与故障排查

**看懂 30%**：知道 Nginx 有哪些常见性能配置项，以及遇到 502/504/403/404 时能定位到后端、超时或路径权限问题。  
**看懂 70%**：能根据业务场景调整连接复用、压缩、缓冲区，并通过日志和监控快速定位慢请求、后端故障及静态资源问题。

### 13.1 基础性能优化配置（直接复制）

```nginx
# 放在 http 块，全局生效

# 1. 开启高效文件传输模式
sendfile on;
# 在 sendfile 开启时，将 HTTP 响应头与文件数据合并发送，减少网络包
tcp_nopush on;
# 对于 keep-alive 连接，关闭 Nagle 算法，及时发送小数据包（降低延迟）
tcp_nodelay on;

# 2. 客户端长连接超时时间（秒）
keepalive_timeout 65;

# 3. Gzip 压缩响应体，降低带宽消耗（传输量减少 60%~80%）
gzip on;
# 仅压缩大于 1KB 的响应，避免微小文件压缩反而耗 CPU
gzip_min_length 1k;
# 压缩级别（1-9），6 是性能与压缩率的平衡点（性价比最优）
gzip_comp_level 6;
# 指定需要压缩的 MIME 类型
gzip_types text/plain text/css application/json application/javascript image/svg+xml;
# 在响应头中添加 Vary: Accept-Encoding，告知缓存服务器根据编码区分缓存
gzip_vary on;

# 4. 每个 worker 进程可打开的最大文件描述符数
worker_rlimit_nofile 65535;
```

> [!TIP]
> **效果参考**：200KB 的静态资源经 Gzip 压缩后可降至约 40KB（体积 -80%），同等带宽下用户下载速度提升 5 倍以上。`gzip_comp_level 6` 是 CPU 与压缩率的最佳平衡点。

### 13.2 上游连接复用（降低后端延迟）

默认 Nginx 每次转发请求都要新建 TCP 连接，高并发时开销大。配置 `upstream keepalive` 复用连接：

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;

    # 保持与后端的空闲长连接数量（每个 worker 进程）
    keepalive 32;
}

server {
    location /api/ {
        proxy_pass http://backend/;

        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

> [!TIP]
> 能显著降低 Spring Boot 后端的 TIME_WAIT 连接数，提高吞吐量。

### 13.3 缓冲区大小调整（防止大响应报错）

后端返回较大的响应头或响应体时，默认缓冲区可能不够，导致 502 或截断：

```nginx
location /api/ {
    proxy_pass http://backend/;

    proxy_buffer_size 16k;
    proxy_buffers 8 32k;
    proxy_busy_buffers_size 64k;
    proxy_max_temp_file_size 0;  # 禁止写临时文件，直接转发
}
```

> [!TIP]
> 若后端返回超大 JSON（如导出报表），可适当调大 `proxy_buffers` 或设 `proxy_max_temp_file_size 0` 避免磁盘 I/O 瓶颈。

### 13.4 浏览器缓存 — 30 天秒开（新增）

对静态资源设置强缓存，减少重复请求，大幅提升加载速度：

```nginx
location ~* \.(jpg|png|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, max-age=2592000";
}
```

> [!TIP]
> **流程**：首次访问走网络下载并缓存；之后 30 天内直接从本地读取，实现“秒开”，大幅减轻服务器压力。

### 13.5 故障排查：502 Bad Gateway

**含义**：Nginx 作为代理，无法与后端建立有效连接或收到无效响应。

**核心排查三步法**：

1. **查看 Nginx 错误日志**（第一步）  
   `tail -20 /var/log/nginx/error.log`  
   关键词：`connect() failed (111: Connection refused)` 或 `upstream prematurely closed connection`

2. **识别典型错误特征**  
   - 连接被拒（Connection refused）→ 后端服务未启动、端口错误或防火墙拦截  
   - 无此文件或目录 → 后端配置路径错误  
   - 主动断开连接 → 后端进程崩溃或超时断开

3. **直接探测后端服务**  
   `curl http://后端IP:端口/health` 模拟 Nginx 请求，验证端口是否存活

**常见原因与解决方法**：

| 可能原因 | 排查方法 | 解决方法 |
|----------|----------|----------|
| 后端服务挂了或未启动 | `curl` 或检查容器状态 | 启动后端，修复健康检查 |
| 后端端口与 Nginx 配置不一致 | 检查 `upstream` 端口 | 修正配置并 `nginx -s reload` |
| 连接超时（`proxy_connect_timeout` 太短） | 查看 error.log 超时信息 | 适当调大 `proxy_connect_timeout` |
| 后端响应头过大或格式错误 | 检查后端日志，确认返回非法 HTTP 头 | 修复后端，或调大 `proxy_buffer_size` |
| 防火墙/SELinux 拦截 | 检查 iptables、SELinux 日志 | 临时关闭测试或配置放行规则 |

> [!TIP]
> **口诀**：**502 = 后端服务不可达**（连不上或拒绝连接）

### 13.6 故障排查：504 Gateway Timeout

**含义**：Nginx 已与后端建立 TCP 连接，但后端处理耗时超过 `proxy_read_timeout` 阈值。

**定位与优化**：

- **日志线索**：`error.log` 中出现 `upstream timed out`
- **诊断后端瓶颈**：检查数据库慢 SQL、代码死循环、CPU/内存资源耗尽或容器限制
- **应急方案**：临时调大超时  
  ```nginx
  location /api/slow/ {
      proxy_pass http://backend/;
      proxy_read_timeout 120s;
  }
  ```
- **长期根治**：优化业务逻辑与数据库索引，或增加缓存/限流

**502 vs 504 对比**：

| 错误码 | 连接状态 | 核心原因 | 口诀 |
|--------|----------|----------|------|
| 502 Bad Gateway | 连接失败 | 后端未启动、端口错误、网络阻断 | 后端不可达 |
| 504 Gateway Timeout | 连接成功，但响应超时 | 后端处理太慢（慢 SQL、高负载） | 后端太慢 |

### 13.7 故障排查：403 和 404（新增）

#### 403 Forbidden（权限拒绝）
- **文件自身权限不足** → `chmod 644 filename`
- **上级目录权限不足**（缺少执行权限） → `chmod 755 dirname`
- **SELinux 安全策略拦截** → 临时测试 `setenforce 0`（生产需配置策略）

#### 404 Not Found（资源不存在）
- **`root` / `alias` 路径配置错误** → 检查指令指向的根目录
- **目标文件物理不存在** → `ls -la /path/to/file` 确认
- **`location` 匹配规则冲突** → 检查正则优先级与顺序

### 13.8 通过日志定位慢请求

利用 JSON 日志中的 `$request_time` 和 `$upstream_response_time`：

```bash
cat /var/log/nginx/access.log | jq -r '[.request_time, .request, .upstream_response_time] | @tsv' | sort -nr | head -10
```

- `$request_time`：Nginx 总耗时（含客户端网络）
- `$upstream_response_time`：后端处理耗时

若前者高而后者低，问题在客户端网络或响应体过大；若后者高，问题在后端。

### 13.9 高并发连接数打满的处理（含 Worker 调优三件套）

#### Worker 调优三件套（核心配置）

```nginx
worker_processes auto;          # 自动匹配 CPU 物理核数，充分利用多核
worker_connections 10240;       # 单 worker 最大并发连接（默认 1024 过小）
worker_cpu_affinity auto;       # 绑定 CPU 核心，减少上下文切换开销
```

**理论并发公式**：  
`worker_processes × worker_connections / 2`  
（除 2 是因为通常一个连接占用两个文件描述符，或考虑长连接比例）

示例：4 核 × 10240 / 2 = 20,480 并发连接。

#### 当 `Active connections` 接近上限时：

**短期缓解**：
- 调大 `worker_connections`（同步调大 `worker_rlimit_nofile` 和系统 `ulimit -n`）
- 增加 `worker_processes`（建议等于 CPU 核数，过多反而上下文切换）

**长期方案**：
- 水平扩容后端，引入负载均衡
- 使用 CDN 分担静态资源
- 对热点接口启用 `proxy_cache` 或限流（第 12.4 节）

### 13.10 性能调优自查清单（更新）

| 检查项 | 推荐值 | 影响 |
|--------|--------|------|
| `worker_processes` | CPU 核数（或 `auto`） | 并发处理能力 |
| `worker_connections` | 10240（视硬件） | 单 worker 最大连接 |
| `worker_cpu_affinity` | `auto` | 减少上下文切换 |
| `keepalive_timeout` | 60~75 | 连接复用与资源占用平衡 |
| `sendfile` | `on` | 静态文件传输效率 |
| `gzip` | `on`, level 6 | 带宽消耗（减少 60%~80%） |
| `upstream keepalive` | 32 | 后端连接复用 |
| `proxy_read_timeout` | 10~30s（按接口调整） | 避免 504 |
| `expires` / `Cache-Control` | 30d（静态资源） | 客户端缓存，秒开 |
| `limit_req` | 按接口 QPS | 防突发流量 |

---

## 14. 平滑重启与零中断变更（运维红线）

**看懂即可，必须记住操作**。

- `nginx -t`：检查配置语法。
- `nginx -s reload`：热加载配置，不中断连接。  
  过程：Master 启动新 worker，旧 worker 处理完已有请求后优雅退出。

> [!WARNING]
> 严禁直接 `kill` 或 `nginx -s stop` 导致流量瞬间切断。

---

## 15. 坚决不碰的红线（笔记边界）

| 不学内容 | 原因 |
|----------|------|
| 源码分析（C 语言模块） | 你是 Java 云原生方向，不是 Nginx 开发 |
| OpenResty / Lua 脚本 | 除非专职 API 网关，否则 K8s Ingress 更合适 |
| 死记硬背指令语法 | AI 和文档随时能查 |
| Nginx Plus 商业功能 | 开源版足以满足学习阶段 |

---

## 📌 使用效果与学习策略
- **看懂 30%~50%**：掌握 `server/location` 骨架、`proxy_pass`、常用变量和基本负载均衡，已能看懂 GitHub 上 90% 的业务 Nginx 配置。
- **看懂 70%~80%**：消化掉 location 优先级、`proxy_pass` 尾斜线规则、JSON 日志定义、健康检查参数及 Prometheus 接入后，你就能独立为微服务项目手写生产可用的 Nginx 配置。

**阶段建议**：
- **当前**：收藏本手册。你已在项目实战中完成反向代理、静态托管和跨域解决，阶段一圆满收官。（2026-08）
- **大二上**：学习 Prometheus 和微服务时，花 1–2 小时配置第 8–11 节，直接将 Nginx 接入可观测性体系。
- **大二下 / 面试前**：重点回顾第 2 节（匹配规则）、第 12 节（平滑重启）和第 7 节（容灾策略），足以应对大厂云原生岗位的 Nginx 理论题。

---

[参考网课](https://www.bilibili.com/video/BV1GKgQ64EL6/?spm_id_from=333.337.search-card.all.click&vd_source=e0c0ad2a316e90d4078b1131e8182407)（必看3，6，7节，选看4，5，8节）

---
