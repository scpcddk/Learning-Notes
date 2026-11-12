# Nginx 部署运维手册

> **环境**：阿里云 ECS，Ubuntu 22.04，Docker 部署 Nginx（`docker-nginx-1`）  
> **作用**：统一入口，反向代理后端 API、流媒体、前端静态文件  
> **核心配置文件**：`/opt/nginx/conf.d/default.conf`（挂载到容器内 `/etc/nginx/conf.d/default.conf`）

---

## 1. Nginx 在项目中的角色

```
浏览器 / Jetson
        │
        ▼
   Nginx (80) ───────── 反向代理分发
        │
        ├── /iot-api/       → 后端 Spring Boot (8080)
        ├── /live/          → SRS 流媒体 (8081)
        ├── /ws/            → WebSocket (8080)
        └── /CloudPlatform/ → 前端静态文件
```

---

## 2. 当前正确配置（完整版）

```nginx
server {
    listen 80;
    server_name _;

    # 此静态响应仅检测 Nginx 入口，不代表后端、数据库或鉴权正常
    location = /iot-api/ {
        return 200 '{"status":"ok"}';
        default_type application/json;
    }

    # 后端 API 代理（将 /iot-api/ 重写为 /api/）
    location /iot-api/ {
        proxy_pass http://172.27.119.137:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 流媒体 HLS/FLV 代理
    location /live/ {
        proxy_pass http://172.27.119.137:8081/live/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://172.27.119.137:8080/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 前端静态文件
    location /CloudPlatform/ {
        alias /opt/iot-frontend/CloudPlatform/;
        try_files $uri $uri/ /CloudPlatform/index.html;
        index index.html;
    }

    # 根路径跳转到前端
    location / {
        return 301 /CloudPlatform/;
    }
}
```

### 确认哪一个实例读取这份配置

项目曾经切换校园网和云端入口，宿主进程、容器进程与前端文件挂载曾造成混淆。接手时先记录当前部署用哪个 Nginx、实际监听端口和挂载源。修改宿主文件后，需要确认它是否被目标实例 include 或绑定挂载。配置落盘和成功重载是两回事。

```bash
# NGINX_CONTAINER 填当前部署实际使用的容器名。
: "${NGINX_CONTAINER:?请设置 Nginx 容器名}"
docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$NGINX_CONTAINER"
docker exec "$NGINX_CONTAINER" nginx -t
docker logs --since 5m "$NGINX_CONTAINER"
```

宿主机部署就在宿主检查 `nginx -t` 和对应服务状态。需要确认 include 时，可在目标实例执行 `nginx -T` 查实际配置。整份输出可能包含内网地址和敏感参数，交接只记录命中的 `server_name`、location、上游以及配置文件。尤其要区分访问地址用的端口与上游监听端口，修改一个不会自动改另一个。


---

## 3. 常见问题排查与解决

### 3.1 502 Bad Gateway

**现象**：访问任何路径返回 502，后端服务正常运行（8080 端口 `LISTEN`）。

**原因**：Nginx 容器无法访问宿主机的后端端口。通常是宿主机内网 IP 发生变化，导致 `proxy_pass` 中写死的旧 IP 失效。

**排查步骤**：

```bash
# 1. 确认后端端口监听正常
ss -tlnp | grep 8080

# 2. 测试 Nginx 容器能否访问宿主机后端
docker exec docker-nginx-1 curl -s -o /dev/null -w "%{http_code}" http://172.27.119.137:8080/
```

- 返回 `200`：该目标 HTTP 路径可达，需继续核对实际失败路径及当前配置，不代表必须重载。
- 返回 `000`：curl 未取得 HTTP 状态码；检查退出码、DNS、连接拒绝、路由、防火墙和服务状态，不能直接断定 IP 改变。

**解决方法**：

```bash
# 获取当前宿主机内网 IP
NEW_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# 替换 Nginx 配置中的旧 IP
sed -i "s/172\.[0-9.]*:8080/$NEW_IP:8080/g" /opt/nginx/conf.d/default.conf
sed -i "s/172\.[0-9.]*:8081/$NEW_IP:8081/g" /opt/nginx/conf.d/default.conf

# 重载 Nginx
docker exec docker-nginx-1 nginx -t && docker exec docker-nginx-1 nginx -s reload
```

**预防**：bridge 容器内 `127.0.0.1` 指向容器自身。可为 Linux 容器配置 `--add-host=host.docker.internal:host-gateway`，或让相关服务加入同一自定义网络并使用服务名；网关地址以实际网络为准。每次服务器重启后执行一次连通性检查。

#### 用同一语义的请求检查入口和上游

先通过站点入口访问已知只读 API，再从 Nginx 所在网络直连上游，核对方法、路径和实际响应。尚未切 DNS 且部署启用了 HTTPS 时，可以使用 `curl --resolve` 明确目标 IP，仍保留原域名、Host 和 TLS SNI。证书错误先核对域名和证书链，避免用跳过校验当作修复。

```bash
# 取目标站点响应头，观察状态码、响应类型和重定向地址。
: "${SITE_HOST:?请设置站点域名}"
: "${EDGE_IP:?请设置目标入口 IP}"
: "${CHECK_PATH:?请设置已知的只读路径}"
curl -sS --max-time 10 --resolve "$SITE_HOST:443:$EDGE_IP" \
  -D - -o /dev/null "https://$SITE_HOST$CHECK_PATH"
```

**早期排障分支如何复测**

早期版本（`38a9411`）把 Nginx 容器内直连返回 200 作为继续检查配置与重载的分支。复用这一步时先确认访问的是预期上游和路径，再核对实际生效配置、命中站点和重载结果。一次 200 能证明该请求可用，上游地址是否变化仍要对照记录。


### 3.2 403 Forbidden

**现象**：访问 `/iot-api/` 或前端页面返回 403。

**常见原因及解决**：

**原因 A：Spring Security 拦截根路径**

前端若用业务根路径探测服务，可能遇到鉴权拒绝。应区分 Nginx 入口存活、后端健康和用户权限；静态 200 不能验证后端健康。

**解决**：在 Nginx 中精确匹配根路径，直接返回 200，不再转发给后端：

```nginx
# 先匹配请求路径，再执行对应处理。核对匹配修饰符和资源路径。
location = /iot-api/ {
    return 200 '{"status":"ok"}';
    add_header Content-Type application/json;
}
```

后端健康检查应使用专门的健康端点，并按访问范围配置权限；不要通过放行业务路径来掩盖鉴权问题。

**两个 200 的验收口径。** 当时访问 `/iot-api/` 时，Nginx 的 `return` 直接生成响应，没有访问 Spring Boot。这一步只验证入口和匹配规则。验收后端时，再通过代理请求一个已知会转发的只读接口，核对响应是否为预期业务数据，并在 Nginx 上游日志或后端访问日志中找到对应请求。

**原因 B：静态文件权限不足**

前端 `css`、`js` 目录权限为 `700`（`drwx------`），Nginx 进程（通常为 `nginx` 用户）无法读取。

**解决**：

```bash
# 修改指定文件或目录的权限，核对实际运行服务的用户。
chmod -R 755 /opt/iot-frontend/CloudPlatform/
```

**原因 C：文件被锁定（`chattr +i`）**

不可变属性会阻止文件修改、删除或替换，但本身不会禁止 Nginx 读取；403 应检查路径权限、访问规则和安全模块。

**解决**：

```bash
# 检查文件属性
lsattr /opt/nginx/conf.d/default.conf

# 如果带有 'i' 标志，解锁
chattr -i /opt/nginx/conf.d/default.conf
```

### 3.3 404 Not Found

**现象**：登录接口或前端页面返回 404。

**常见原因及解决**：

**原因 A：前端 `baseURL` 配置错误**

前端代码中 `baseURL` 写成了 `/api`，而 Nginx 只代理了 `/iot-api/`，导致请求未命中任何 location。

**解决**：确保前端 `baseURL` 为 `/iot-api`，并在打包后验证：

```bash
# 读取或筛选本地文件，按实际路径与输出核对关键字段。
grep -o 'baseURL:"[^"]*"' /opt/iot-frontend/CloudPlatform/js/app.*.js
```

必须输出 `baseURL:"/iot-api"`。

**原因 B：Nginx 配置缺失路径**

新增了 WebSocket 或流媒体等路径，但 Nginx 配置中没有相应的 location 块。

**解决**：在 `/opt/nginx/conf.d/default.conf` 中添加对应的 location。

**原因 C：前端 `index.html` 引用的 JS 文件不存在**

多次部署后，`index.html` 中引用的 JS 文件名（如 `app.xxxxx.js`）与实际存在的文件不匹配，导致资源 404。

**解决**：

```bash
# 找到实际最新的 app JS 文件
NEW_APP=$(ls -t /opt/iot-frontend/CloudPlatform/js/app.*.js | head -1 | xargs basename)

# 更新 index.html 中的引用
sed -i "s|app\.[0-9a-f]*\.js|$NEW_APP|g" /opt/iot-frontend/CloudPlatform/index.html

# 重载 Nginx
docker exec docker-nginx-1 nginx -s reload
```

#### 核对 proxy_pass 的前缀改写

常规前缀匹配中，`location /api/ { proxy_pass http://backend; }` 保留原路径。`proxy_pass http://backend/;` 则用 `/` 替换匹配的 `/api/` 前缀。访问 `/api/health` 时，两个配置分别会让上游看到 `/api/health` 和 `/health`。正则、重写与变量的场景另按 Nginx 规则判断。先看后端路由定义和日志里的实际 URI，再选写法。


### 3.4 前端更新后页面不刷新

**现象**：重新上传前端文件后，浏览器访问仍是旧页面，强制刷新、无痕模式均无效。

**常见原因及解决**：

**原因 A：实际挂载目录或文件与更新目标不一致**

`:ro` 不阻止宿主机更新。先检查 `docker inspect docker-nginx-1` 中的 Mounts，再对比宿主机与容器内目标文件的 `sha256sum`。若只挂载了单个文件，编辑器原子替换文件可能令容器仍引用旧 inode，可改为挂载父目录。更新 Nginx 配置后执行 `nginx -t`，通过后 reload；更新静态文件通常无需重启。

**原因 B：浏览器顽固缓存**

即使服务器返回新文件，浏览器仍使用本地缓存。

**解决**：

1. 使用无痕模式
2. `Ctrl+Shift+Del` 清除所有时间段的缓存和 Cookie
3. 注销 Service Worker：`chrome://serviceworker-internals` → 找到站点 → Unregister
4. 在 Nginx 中添加禁用 HTML 缓存的头：
   
   ```nginx
   # 先匹配请求路径，再执行对应处理。核对匹配修饰符和资源路径。
   location ~* \.html$ {
       add_header Cache-Control "no-cache, no-store, must-revalidate";
       expires -1;
   }
   ```

**原因 C：`index.html` 引用的 JS 文件不存在**

同 3.3 原因 C，文件名不匹配导致加载旧缓存。

**用入口与资源哈希核对当前版本**

更新前保存已验证的上一版配置、前端构建目录和资源对应关系。更新后先从磁盘检查新入口文件，再通过站点访问首页和它引用的一份带哈希资源。若浏览器拿到新首页却请求旧文件，检查是否有旧标签页、Service Worker 或缓存规则。对 HTML 入口和带内容哈希的静态文件采用适合各自更新频率的缓存策略。


### 3.5 WebSocket 连接失败

**现象**：前端控制台报 `WebSocket connection to 'ws://...' failed`，返回 403、502 或 301。

**原因**：Nginx 没有正确代理 WebSocket 升级请求，或者后端 Spring Security 拦截。

**解决**：

1. 在 Nginx 配置中添加 WebSocket 升级头：
   
   ```nginx
   # 根据 location 选择代理路径，核对 proxy_pass 的 URI、上游地址和转发头。
   location /ws/ {
       proxy_pass http://172.27.119.137:8080/ws/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

2. 后端 `SecurityConfig` 中放行 `/ws/**`

### 3.6 配置文件“Operation not permitted”

**现象**：试图修改 `/opt/nginx/conf.d/default.conf` 时提示权限不足。

**原因**：之前执行过 `chattr +i` 锁定文件，防止误覆盖。

**解决**：

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
chattr -i /opt/nginx/conf.d/default.conf
```

修改完成后可重新锁定：

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
chattr +i /opt/nginx/conf.d/default.conf
```

### 3.7 新增路径后 403

**现象**：新增了 `/api/` 临时代理后，其他路径突然出现 403。

**原因**：Spring Security 拦截了未放行的路径。尤其是 Nginx 同时代理了 `/iot-api/` 和 `/api/` 时，两者可能产生路由混乱。

**解决**：

- 统一使用 `/iot-api/` 作为前端调用入口
- 后端在 `SecurityConfig` 中明确放行需要的路径
- 在 Nginx 中精确匹配根路径，避免将不需要的请求转发到后端

---

## 4. 配置维护与更新规范

### 4.1 修改前备份

```bash
# 操作前区分源路径和目标路径，核对操作后的文件位置。
cp /opt/nginx/conf.d/default.conf /opt/nginx/conf.d/default.conf.bak.$(date +%Y%m%d_%H%M%S)
```

### 4.2 修改后测试

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec docker-nginx-1 nginx -t
```
看到 `syntax is ok` 和 `test is successful` 后再重载。

### 4.3 重载配置

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec docker-nginx-1 nginx -s reload
```

### 4.4 验证关键路径

```bash
# 后端 API
# 仅测 Nginx 静态入口；后端健康需另查实际健康端点
curl -i http://localhost/iot-api/

# 前端
curl -I http://localhost/CloudPlatform/

# 流媒体
curl -I http://localhost/live/

# WebSocket
curl --http1.1 -i --max-time 5 \
  -H "Upgrade: websocket" -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://localhost/ws/events
```

#### 同时验收 API、媒体和静态资源

站点同时承载 API、静态页和视频时，保留一张「外部路径 → 命中规则 → 上游地址 → 上游收到的路径」表。重载后分别验证首页、静态资源、只读 API、HLS 清单和一个分片。WebSocket 除握手外要收到一次应用层消息。若回退，应恢复同一版本的配置和前端产物，再重复这些检查。 [Nginx 代理模块](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) · [Nginx 上游模块](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)


### 4.5 恢复备份

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
cp /opt/nginx/conf.d/default.conf.bak.xxxxxx /opt/nginx/conf.d/default.conf
docker exec docker-nginx-1 nginx -s reload
```

---

## 5. 快速诊断命令集

| 需求 | 命令 |
|------|------|
| 检查容器运行 | `docker ps \| grep docker-nginx-1` |
| 检查配置语法 | `docker exec docker-nginx-1 nginx -t` |
| 重载配置 | `docker exec docker-nginx-1 nginx -s reload` |
| 查看最近错误日志 | `docker logs --tail 50 docker-nginx-1 \| grep -i "error\|403\|404\|502"` |
| 查看当前生效配置 | `docker exec docker-nginx-1 cat /etc/nginx/conf.d/default.conf` |
| 测试容器到宿主机连通性 | `docker exec docker-nginx-1 curl -s -o /dev/null -w "%{http_code}" http://宿主机IP:端口/` |
| 检查文件锁定 | `lsattr /opt/nginx/conf.d/default.conf` |
| 解锁文件 | `chattr -i /opt/nginx/conf.d/default.conf` |
| 修复前端文件权限 | `chmod -R 755 /opt/iot-frontend/CloudPlatform/` |

### 按响应类型定位故障

| 现象 | 第一条证据 | 下一步 |
|---|---|---|
| 首页正常，API 返回 200 HTML | Content-Type、正文与命中的 location | 查 API 是否落到 SPA 的 index.html 回退 |
| 404 | 上游是否收到请求，收到什么路径 | 区分刷新前端路由、静态文件不存在和后端路径错位 |
| 502 | Nginx 错误日志中的 upstream 地址和 connect 错误 | 从代理所在网络查 DNS、地址、端口、协议与进程 |
| 504 | 上游日志与响应耗时 | 查线程、连接池、依赖超时，确认瓶颈后再调代理超时 |
| WebSocket 连不上 | 浏览器握手 URL、状态和断开时间 | 对照 Upgrade、路径、鉴权与心跳 |
| 更新后还是旧页面 | 首页引用的 JS 文件名及浏览器请求 | 分辨缓存、旧挂载、旧容器与旧反代 |

分析慢请求时，把入口的总耗时与上游响应耗时放在一起。入口耗时高但上游用时短，优先考虑客户端传输、缓冲或前端重试。上游用时也高，则继续查应用和数据库。一次复盘保留时间、路径、状态、上游地址和可对齐的请求编号，记录足够复现即可。

### 用上游耗时和状态核对故障

需要把 502、504 和慢请求放到同一时间窗对比时，可在隔离环境使用以下日志格式。`log_format` 放在 `http` 层，`access_log` 绑定到实际站点。路径只记录 `$uri`，避免默认记录完整查询字符串中的临时签名。

```nginx
# 在 http 层定义。请求总耗时和上游耗时都保留，便于逐段排查。
log_format route_check '$time_iso8601 $host $request_method $uri '
                       '$status $request_time $upstream_addr '
                       '$upstream_status $upstream_response_time';
# 将下行放入需核对的站点 server 块，先确认目录存在且进程可写。
access_log /var/log/nginx/route-check.log route_check;
```

变更前确认日志存放和轮转位置。请求发生内部重定向时，`$uri` 可能和最初路径不同，需要结合实际命中规则解释。若有重试，上游字段也可能含多个值。建议先做成功请求和失败请求各一次对照，再看集中出现的变化。


---

## 6. 经验教训总结

1. **每次修改配置前先备份**，出问题时可以快速回滚。
2. **502 几乎都是 IP 变化或后端未启动**，先用 `docker exec` 测试连通性再改配置。
3. **403 先从权限和锁定排查**，再检查后端安全配置。
4. **前端缓存问题用无痕模式验证**，如果无痕正常就是浏览器缓存。
5. **只读目录挂载仍会反映宿主机修改**；配置更新后先 `nginx -t` 再 reload，静态文件还需排查缓存与发布目录。
6. **不要轻易 `chattr +i`**，除非确实需要防止误覆盖，否则增加维护成本。
7. **统一前端 API 前缀**（如 `/iot-api`），避免与已有服务路径冲突。

---

**此手册将随项目维护持续更新。**
