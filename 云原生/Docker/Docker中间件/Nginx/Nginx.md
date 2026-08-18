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

## 3. proxy_pass 的尾巴区别（极易踩坑）

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

- `root` vs `alias`：`root` 会把 location 路径拼到后面；`alias` 是别名替换。日常用 `root` 就够了。

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

```nginx
upstream backend {
    server 10.0.0.1:8080 weight=3 max_fails=2 fail_timeout=30s;
    server 10.0.0.2:8080 weight=1;
    server 10.0.0.3:8080 backup;       # 所有非 backup 都挂时才启用
}

server {
    location /api/ {
        proxy_pass http://backend/;
        proxy_connect_timeout 2s;
        proxy_read_timeout 10s;

        # 遇到这些错误自动换下一台
        proxy_next_upstream error timeout http_502 http_503 http_504;
        proxy_next_upstream_tries 2;
        proxy_next_upstream_timeout 10s;
    }
}
```

- `max_fails` + `fail_timeout`：在 `fail_timeout` 内失败 `max_fails` 次，节点被临时摘除。
- `backup`：热备节点，平时不接流量。

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

## 12. 平滑重启与零中断变更（运维红线）

**看懂即可，必须记住操作**。

- `nginx -t`：检查配置语法。
- `nginx -s reload`：热加载配置，不中断连接。  
  过程：Master 启动新 worker，旧 worker 处理完已有请求后优雅退出。

> 严禁直接 `kill` 或 `nginx -s stop` 导致流量瞬间切断。

---

## 13. 坚决不碰的红线（笔记边界）

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
