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

    # 精确匹配 /iot-api/ 根路径，直接返回 200（防止 Spring Security 403）
    location = /iot-api/ {
        return 200 '{"status":"ok"}';
        add_header Content-Type application/json;
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
- 返回 `200`：IP 未变，只需重载 Nginx 配置。
- 返回 `000` 或超时：IP 已变，需要更新配置。

**解决方法**：
```bash
# 获取当前宿主机内网 IP
NEW_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# 替换 Nginx 配置中的旧 IP
sed -i "s/172\.[0-9.]*:8080/$NEW_IP:8080/g" /opt/nginx/conf.d/default.conf
sed -i "s/172\.[0-9.]*:8081/$NEW_IP:8081/g" /opt/nginx/conf.d/default.conf

# 重载 Nginx
docker exec docker-nginx-1 nginx -s reload
```

**预防**：尽量使用 `127.0.0.1` 或 Docker 网关 `172.17.0.1`，但云环境网络复杂时宿主机真实 IP 更可靠。每次服务器重启后执行一次连通性检查。

---

### 3.2 403 Forbidden

**现象**：访问 `/iot-api/` 或前端页面返回 403。

**常见原因及解决**：

**原因 A：Spring Security 拦截根路径**
前端可能会对 `/iot-api/` 做健康检查，后端 Spring Security 未放行根路径，返回 403，导致前端误判无权限。

**解决**：在 Nginx 中精确匹配根路径，直接返回 200，不再转发给后端：
```nginx
location = /iot-api/ {
    return 200 '{"status":"ok"}';
    add_header Content-Type application/json;
}
```
或者让后端在 `SecurityConfig` 中添加 `.requestMatchers("/api/").permitAll()`。

**原因 B：静态文件权限不足**
前端 `css`、`js` 目录权限为 `700`（`drwx------`），Nginx 进程（通常为 `nginx` 用户）无法读取。

**解决**：
```bash
chmod -R 755 /opt/iot-frontend/CloudPlatform/
```

**原因 C：文件被锁定（`chattr +i`）**
之前为了防止误覆盖，对某些文件设置了不可变属性，导致 Nginx 无法读取或配置更新失败。

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

---

### 3.4 前端更新后页面不刷新

**现象**：重新上传前端文件后，浏览器访问仍是旧页面，强制刷新、无痕模式均无效。

**常见原因及解决**：

**原因 A：Nginx 容器只读挂载**
容器以 `:ro` 方式挂载宿主机目录，宿主机文件更新后容器内未同步。

**解决**：重建容器时去掉 `:ro`：
```bash
docker rm -f docker-nginx-1
docker run -d --name docker-nginx-1 \
  --restart=always \
  -p 80:80 \
  -v /opt/nginx/conf.d:/etc/nginx/conf.d \
  -v /opt/iot-frontend:/opt/iot-frontend \
  nginx:latest
```

**原因 B：浏览器顽固缓存**
即使服务器返回新文件，浏览器仍使用本地缓存。

**解决**：
1. 使用无痕模式
2. `Ctrl+Shift+Del` 清除所有时间段的缓存和 Cookie
3. 注销 Service Worker：`chrome://serviceworker-internals` → 找到站点 → Unregister
4. 在 Nginx 中添加禁用 HTML 缓存的头：
   ```nginx
   location ~* \.html$ {
       add_header Cache-Control "no-cache, no-store, must-revalidate";
       expires -1;
   }
   ```

**原因 C：`index.html` 引用的 JS 文件不存在**
同 3.3 原因 C，文件名不匹配导致加载旧缓存。

---

### 3.5 WebSocket 连接失败

**现象**：前端控制台报 `WebSocket connection to 'ws://...' failed`，返回 403、502 或 301。

**原因**：Nginx 没有正确代理 WebSocket 升级请求，或者后端 Spring Security 拦截。

**解决**：
1. 在 Nginx 配置中添加 WebSocket 升级头：
   ```nginx
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
chattr -i /opt/nginx/conf.d/default.conf
```
修改完成后可重新锁定：
```bash
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
cp /opt/nginx/conf.d/default.conf /opt/nginx/conf.d/default.conf.bak.$(date +%Y%m%d_%H%M%S)
```

### 4.2 修改后测试
```bash
docker exec docker-nginx-1 nginx -t
```
看到 `syntax is ok` 和 `test is successful` 后再重载。

### 4.3 重载配置
```bash
docker exec docker-nginx-1 nginx -s reload
```

### 4.4 验证关键路径
```bash
# 后端 API
curl -I http://localhost/iot-api/

# 前端
curl -I http://localhost/CloudPlatform/

# 流媒体
curl -I http://localhost/live/

# WebSocket
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost/ws/events
```

### 4.5 恢复备份
```bash
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

---

## 6. 经验教训总结

1. **每次修改配置前先备份**，出问题时可以快速回滚。
2. **502 几乎都是 IP 变化或后端未启动**，先用 `docker exec` 测试连通性再改配置。
3. **403 先从权限和锁定排查**，再检查后端安全配置。
4. **前端缓存问题用无痕模式验证**，如果无痕正常就是浏览器缓存。
5. **只读挂载导致配置不更新**，重构容器时务必去掉 `:ro`。
6. **不要轻易 `chattr +i`**，除非确实需要防止误覆盖，否则增加维护成本。
7. **统一前端 API 前缀**（如 `/iot-api`），避免与已有服务路径冲突。

---

**此手册将随项目维护持续更新。**