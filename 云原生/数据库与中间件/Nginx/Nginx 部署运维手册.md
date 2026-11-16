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

排查旧的前端容器时，用 `docker ps -a` 找到候选容器，包括已停止的容器。端口映射和列表中截断的启动命令可用于初筛。再用 `docker inspect` 查看容器配置中的镜像、入口程序和启动参数，容器已停止时也可以读取这些信息。

```bash
# NGINX_CONTAINER 填待核对的容器名。
: "${NGINX_CONTAINER:?请设置容器名}"
docker inspect --format 'Image={{.Config.Image}} Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}' "$NGINX_CONTAINER"
docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$NGINX_CONTAINER"
docker exec "$NGINX_CONTAINER" nginx -t
docker logs --since 5m "$NGINX_CONTAINER"
```

例如，`Entrypoint=["/docker-entrypoint.sh"]` 和 `Cmd=["nginx","-g","daemon off;"]` 分别表示入口脚本和传给它的启动命令。官方 Nginx 镜像的入口脚本完成初始化后，用 `exec` 执行该命令。`-g` 从命令行传入全局指令，`daemon off;` 让 Nginx 主进程留在前台，作为容器内持续运行的服务进程。 [官方镜像入口脚本](https://raw.githubusercontent.com/nginx/docker-nginx/master/entrypoint/docker-entrypoint.sh) · [Nginx 命令行参数](https://nginx.org/en/docs/switches.html) · [`daemon` 指令](https://nginx.org/en/docs/ngx_core_module.html#daemon)

需要启动已停止的容器时，`docker start 容器名` 会按已有配置重新运行启动命令，沿用原容器的可写层、挂载和端口映射。用 `docker ps` 核对目标的 `STATUS`。容器处于运行状态时，可用 `docker exec` 在容器内执行 `nginx -t` 等检查命令。 [Docker start](https://docs.docker.com/reference/cli/docker/container/start/) · [Docker exec](https://docs.docker.com/reference/cli/docker/container/exec/)

宿主机部署时，在宿主机执行 `nginx -t` 并检查服务状态。排查反向代理时，分别核对入口监听端口和 `proxy_pass` 指向的上游端口。

#### 查看已停止容器的日志

容器仍存在、日志仍保留且日志驱动支持读取时，`docker logs` 可以查看已停止容器记录的标准输出和标准错误。`--tail 30` 读取末尾最多 30 行。官方 Nginx 镜像默认将访问日志和错误日志分别接到标准输出和标准错误。自定义镜像若把日志写入普通文件，应按实际的 `access_log` 和 `error_log` 配置查找。 [Docker 日志命令](https://docs.docker.com/reference/cli/docker/container/logs/) · [Docker 容器日志说明](https://docs.docker.com/engine/logging/)

```bash
docker logs --tail 30 "$NGINX_CONTAINER"
```

以下是进程日志和访问日志的两个片段。

```text
[notice] 1#1: start worker process 41
"GET / HTTP/1.1" 200 694
```

- `[notice]` 是通知级别。第一行记录 Nginx 启动了 PID 为 `41` 的工作进程。 [Nginx 进程启动日志源码](https://raw.githubusercontent.com/nginx/nginx/master/src/os/unix/ngx_process.c)
- 在默认的 `combined` 访问日志格式中，第二行记录了对根路径 `/` 的一次 GET 请求。状态码是 `200`，`694` 是发给客户端的响应体字节数。自定义格式的字段顺序以实际 `log_format` 为准。 [Nginx 访问日志格式](https://nginx.org/en/docs/http/ngx_http_log_module.html#log_format) · [Nginx 日志变量](https://nginx.org/en/docs/http/ngx_http_core_module.html#var_body_bytes_sent)

历史日志中的 `200` 只确认日志所记时间、路径和请求的响应。验证服务当前是否可用时，重新请求目标路径，并对照这次请求产生的日志。


#### 用本地镜像创建验证容器

`docker image ls nginx` 按仓库名查找镜像。自建前端镜像也可以包含 Nginx，应按实际仓库名和标签查找。下面以本地已有的 `cloud-frontend:latest` 为例。`docker run` 从镜像创建并启动新容器，`-d` 使其在后台运行，`--name` 指定容器名。端口映射把容器的 `80` 端口发布到宿主机回环地址的 `8088` 端口。新容器有自己的可写层，运行所需的挂载、环境变量和外部依赖需单独核对。 [Docker 镜像列表](https://docs.docker.com/reference/cli/docker/image/ls/) · [Docker run](https://docs.docker.com/reference/cli/docker/container/run/) · [端口映射](https://docs.docker.com/engine/network/port-publishing/)

```powershell
docker image ls cloud-frontend:latest
docker run -d --name nginx-lab -p 127.0.0.1:8088:80 cloud-frontend:latest
```

返回容器 ID 表示 Docker 已创建容器并发起启动。用 `docker ps` 核对名称和当前状态，确认显示 `Up` 后，再从宿主机验证映射端口的 HTTP 响应。若运行列表里找不到目标容器，用 `docker ps -a` 查看它是否已退出，并检查启动日志。 [Docker 容器列表](https://docs.docker.com/reference/cli/docker/container/ls/)

```powershell
docker ps --filter "name=nginx-lab"
curl.exe -I http://127.0.0.1:8088/
```

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


#### 用独立监听验证上游连接失败

在独立的 Nginx 验证容器中，如果主配置包含 `/etc/nginx/conf.d/*.conf`，可用一个新文件定义额外的 `server`。以下示例让它在容器内监听 `8081`，将 `/lab/` 转发到同一容器内的 `127.0.0.1:9999`。在 `9999` 没有进程监听时，请求到达这个代理路径后，预期会出现连接被拒和 HTTP `502`。

这里用 IP 字面量跳过上游域名解析，使失败发生在处理请求、建立上游连接时。若 `proxy_pass` 写的是配置加载时就要解析的固定域名，域名无法解析时，`nginx -t` 就可能报 `host not found in upstream`。 [Nginx 上游初始化源码](https://raw.githubusercontent.com/nginx/nginx/master/src/http/ngx_http_upstream_round_robin.c) · [Nginx 地址解析源码](https://raw.githubusercontent.com/nginx/nginx/master/src/core/ngx_inet.c)

```powershell
@'
server {
    listen 8081;
    server_name localhost;

    location /lab/ {
        proxy_pass http://127.0.0.1:9999/;
    }
}
'@ | docker exec -i nginx-lab sh -c 'cat > /etc/nginx/conf.d/lab.conf'

docker exec nginx-lab nginx -t
```

PowerShell 单引号 here-string 保留多行配置的字面内容。`docker exec -i` 把它传给容器内的标准输入，由 `sh -c` 中的 `>` 写入容器内文件。使用可写目录和新文件名，已有同名文件会被 `>` 截断。配置测试通过后还需成功重载，监听和转发规则才会用于新请求。 [PowerShell 引号规则](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_quoting_rules#here-strings) · [Docker exec](https://docs.docker.com/reference/cli/docker/container/exec/)

`listen 8081` 配置的是容器内监听。已有的 `8088:80` 只把宿主机的 `8088` 转发到容器的 `80`。从宿主机测试时，在创建验证容器时发布容器的 `8081`，再访问对应的宿主机端口。 [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)

重载后，若容器内有 `wget`，可直接在容器内向 `8081` 发 GET 请求。`-S` 显示服务器响应头，`-O /dev/null` 将下载内容写到空设备。这个请求先访问 Nginx，再由 Nginx 连接代理配置里的 `9999`。 [Wget 参数手册](https://manpages.debian.org/bookworm/wget/wget.1.en.html)

```bash
docker exec nginx-lab wget -S -O /dev/null http://127.0.0.1:8081/lab/
```

##### 关联访问日志和错误日志

```text
127.0.0.1 - - [16/Nov/2026:05:14:19 +0000] "GET /lab/ HTTP/1.1" 502 157 "-" "Wget" "-"
```

下表按 Nginx 示例配置中的 `main` 格式解读。排障时以实际 `access_log` 选用的 `log_format` 为准。默认的 `combined` 格式到 User-Agent 为止，末尾的转发地址字段由格式另行指定。 [Nginx 日志格式](https://nginx.org/en/docs/http/ngx_http_log_module.html#log_format) · [Nginx 示例配置](https://raw.githubusercontent.com/nginx/nginx/master/conf/nginx.conf)

| 片段 | 字段 | 含义 |
| --- | --- | --- |
| `127.0.0.1` | `$remote_addr` | 客户端地址。本例的请求在容器内经回环地址发出。 |
| `- -` | 固定短横线、`$remote_user` | 第一个是格式里的字面字符，第二个表示远程用户名缺省。 |
| `[16/Nov/2026:05:14:19 +0000]` | `$time_local` | `+0000` 表示 UTC。换算到北京时间为当天 `13:14:19`。 |
| `"GET /lab/ HTTP/1.1"` | `$request` | 请求行，依次为方法、请求目标和 HTTP 版本。 |
| `502` | `$status` | Nginx 返回的 HTTP 状态码。 |
| `157` | `$body_bytes_sent` | 发给客户端的响应体字节数，响应头另计。 |
| `"-"` | `$http_referer` | 本次请求未记录到 Referer。 |
| `"Wget"` | `$http_user_agent` | 请求携带的 User-Agent。 |
| 末尾的 `"-"` | `$http_x_forwarded_for` | 若格式定义了该字段，表示本次请求的 X-Forwarded-For 无值。 |

访问日志给出失败的请求和 HTTP 状态。再按同一请求的时间与路径查错误日志，用 `upstream` 字段核对实际连接的目标。若错误日志输出到标准错误，可用容器日志读取。

```bash
docker logs --tail 20 nginx-lab
```

```text
connect() failed (111: Connection refused) while connecting to upstream
```

`111` 在该 Linux 环境中对应系统错误 `ECONNREFUSED`。本例的 `GET /lab/` 已进入代理规则，失败发生在连接上游时。此时优先核对错误日志中的目标地址、端口和后端监听状态。用服务名指定上游时，还要从 Nginx 所在网络确认它解析到了预期地址。 [Linux errno 定义](https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/asm-generic/errno.h)

##### 修正上游并复测

确认同一容器的 `80` 端口正在提供静态首页后，在 `lab.conf` 的 `location /lab/` 中将上游端口改成 `80`。

```nginx
proxy_pass http://127.0.0.1:80/;
```

这里的 `proxy_pass` 带有 URI `/`，会将匹配到的 `/lab/` 前缀替换为 `/`。因此 `GET /lab/` 从容器内的 `8081` 进入，再由 Nginx 向容器内的 `80` 端口请求静态首页。 [Nginx proxy_pass 指令](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)

配置测试通过并成功重载后，用相同的 GET 请求再次访问 `127.0.0.1:8081/lab/`。预期返回 `200 OK`。若响应头里含 `Content-Length: 694`，它声明该 GET 响应的内容长度。查看同次访问日志中的 `$body_bytes_sent`，可核对 Nginx 发送了多少响应体字节。用同一入口和路径比较修复前后的状态码与日志，可以确认这条代理链路是否恢复。 [HTTP Content-Length](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6)

---

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

---

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


---

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


---

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

2. 后端 `SecurityConfig` 中放行 `/ws/**`。

---

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

---

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
`nginx -t` 检查配置语法，并尝试打开配置引用的文件。出现 `syntax is ok` 和 `test is successful` 表示本次配置测试通过，可以继续重载。上游是否可达、关键路径是否返回预期响应，要用实际请求验证。 [Nginx 命令行参数](https://nginx.org/en/docs/switches.html)

需要核对主配置及 `include` 引入的文件时，用 `nginx -T`。它执行相同的检查，并将本次读取的配置输出到标准输出。若实例启动时使用了 `-c` 或 `-p`，检查时沿用相同参数。配置文件修改后，运行中的进程会继续使用已加载的配置，直到成功重载或重新启动。 [Nginx 命令行参数](https://nginx.org/en/docs/switches.html) · [Nginx 配置重载](https://nginx.org/en/docs/control.html#reconfiguration)

```bash
docker exec docker-nginx-1 nginx -T
```

这里 `docker exec` 在运行中的容器内执行指定命令，`docker-nginx-1` 选定容器，`nginx` 是容器内要执行的程序，`-T` 是传给 `nginx` 的参数。 [Docker exec](https://docs.docker.com/reference/cli/docker/container/exec/)

按请求的容器内端口和 Host 核对 `listen` 与 `server_name`，再按 URI 找到匹配的 `location`。例如，端口映射为 `8088:80` 时，宿主机访问 `8088`，配置中查 `listen 80`。静态路径继续核对 `root` 或 `alias`，代理路径核对 `proxy_pass`。交接时只摘录相关规则和配置文件路径，遮盖凭据等敏感参数。

若 `nginx -T` 显示 `include /etc/nginx/conf.d/*.conf;`，可以列出该目录的文件名、权限和属主。配置检查读到哪些文件，以 `nginx -T` 中列出的文件路径为准。 [Nginx include 指令](https://nginx.org/en/docs/ngx_core_module.html#include)

```bash
docker exec docker-nginx-1 ls -l /etc/nginx/conf.d/
```

`-rw-r--r--` 开头的 `-` 表示普通文件，后三组分别是属主读写、属组只读、其他用户只读。属主和属组两列若显示 `root root`，表示文件归 `root` 用户及 `root` 组所有。 [GNU ls 长列表](https://www.gnu.org/software/coreutils/manual/html_node/What-information-is-listed.html)

### 4.3 重载配置

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec docker-nginx-1 nginx -s reload
```

`nginx -s reload` 向正在运行的主进程发出重载信号。主进程成功应用新配置后启动新的工作进程，旧工作进程处理完已有请求后退出。应用失败时仍使用上次成功加载的配置。 [Nginx 配置重载](https://nginx.org/en/docs/control.html#reconfiguration)

重载前后都可以用 `nginx -T` 核对磁盘上的配置。判断工作进程是否已应用新规则，要结合重载时的错误日志和一次命中新规则的实际请求。 [Nginx 命令行参数](https://nginx.org/en/docs/switches.html)

### 4.4 验证关键路径

先核对请求命中的 `location`。由 `root` 和 `index` 提供的静态首页，以及由 `return 200` 直接返回的入口响应，都由 Nginx 本地处理。验证后端时，访问一条由 `proxy_pass` 转发的已知只读接口。

```bash
# Nginx 入口，本手册配置中的精确路径 /iot-api/ 由 return 200 直接响应。
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

#### 从宿主机发送 HEAD 请求

从宿主机访问 Docker 映射后的端口。以下以容器 `nginx-web` 将宿主机的 `8080` 映射到容器的 `80` 为例，在 Windows PowerShell 中执行。

```powershell
curl.exe -I http://localhost:8080/
docker logs --tail 10 nginx-web
```

对 HTTP 地址，`-I` 发送 `HEAD` 请求并显示响应头。若访问日志记录了请求行，可按时间、方法、路径和状态码核对当次请求，例如 `"HEAD / HTTP/1.1" 200 0`。按 `combined` 格式解读，`200` 说明这次 HEAD 请求成功，末尾的 `0` 是 `$body_bytes_sent`，表示本次发送了零字节响应体。验证网页正文时，用 GET 请求同一路径。 [curl 手册](https://curl.se/docs/manpage.html) · [HTTP HEAD 语义](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.2)

配置检查通过后若实际请求返回 `502`，按请求时间查看 Nginx 错误日志中的上游地址和连接错误。配置语法有效时，`proxy_pass` 仍可能指向错误端口，上游也可能尚未监听。

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
| 检查并输出配置及包含的文件 | `docker exec docker-nginx-1 nginx -T` |
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
2. **502 先查当次请求的错误日志**。若日志显示连接被拒，从 Nginx 所在网络核对实际使用的上游地址、端口和监听状态。
3. **403 先从权限和锁定排查**，再检查后端安全配置。
4. **前端缓存问题用无痕模式验证**，如果无痕正常就是浏览器缓存。
5. **只读目录挂载仍会反映宿主机修改**；配置更新后先 `nginx -t` 再 reload，静态文件还需排查缓存与发布目录。
6. **不要轻易 `chattr +i`**，除非确实需要防止误覆盖，否则增加维护成本。
7. **统一前端 API 前缀**（如 `/iot-api`），避免与已有服务路径冲突。

---
