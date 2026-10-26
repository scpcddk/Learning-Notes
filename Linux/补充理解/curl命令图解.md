# curl 命令详解

> 命令行网络工具 · 下载文件 · 调试 API · 自动化脚本
>
> 示例采用 Bash 语法，`example.com` 及其子域名、`url`、代理地址和认证信息都是占位示例，使用时需替换。`/dev/null` 适用于 Linux 等类 Unix 环境。

## 一、curl 是什么？

curl 是用于通过 URL 传输数据的命令行工具，常用于发送 HTTP 请求、下载文件和调试接口。它不会像图形浏览器那样渲染页面或运行页面 JavaScript。

核心特点：

- 支持 HTTP、HTTPS、FTP、SFTP 等多种协议；实际可用协议取决于版本和构建选项，可用 `curl --version` 查看。
- 纯命令行，适合脚本自动化。
- 跨平台，可用于 Linux、macOS 和 Windows。
- 基于 libcurl 库，支持上传下载、认证和 Cookie 等功能。

| 用途 | 示例场景 |
| --- | --- |
| 下载文件 | 获取图片、安装包或归档文件 |
| 调试 API | 测试 GET、POST、PUT、DELETE 等请求 |
| 发送数据 | 提交表单、JSON 或文件 |
| 认证登录 | Basic Auth、Bearer Token、Cookie 会话 |
| 网络诊断 | 查看响应头、连接过程和请求耗时 |

## 二、基本语法

```bash
curl [选项] [URL...]

# 获取网页内容并打印到终端
curl https://www.example.com

# 保存为指定名称
curl -o myfile.html https://www.example.com

# 使用 URL 路径末尾的文件名保存
curl -O https://www.example.com/file.zip
```

## 三、请求控制

| 选项 | 全称 | 作用 | 典型用法 |
| --- | --- | --- | --- |
| `-X` | `--request` | 指定 HTTP 方法字符串 | `curl -X DELETE url` |
| `-d` | `--data` | 发送数据，HTTP 下默认使用 POST | `curl -d 'name=John' url` |
| `-H` | `--header` | 添加或替换请求头 | `curl -H 'Content-Type: application/json' url` |
| `-G` | `--get` | 将 `-d` 等提供的数据放入 GET 查询串 | `curl -G -d 'q=keyword' url` |
| `-F` | `--form` | 提交 multipart/form-data，可上传文件 | `curl -F 'file=@local.txt' url` |
| `-u` | `--user` | 提供用户名和可选密码；仅给用户名时可交互输入密码 | `curl -u admin url` |
| `-L` | `--location` | 跟随 HTTP 重定向 | `curl -L url` |
| `-I` | `--head` | HTTP 下发送 HEAD 请求，获取响应头 | `curl -I url` |

记忆：X 方法、d 数据、H 头部、G 查询参数、F 表单、u 认证、L 重定向、I HEAD。

- `-d` 默认使用 `application/x-www-form-urlencoded`；发送 JSON 时应设置对应的 `Content-Type`。
- `-d` 和 `-F` 通常已使 HTTP 请求使用 POST，无需再加 `-X POST`。
- `-X` 只改变方法字符串，不自动配置请求行为。例如 HEAD 应使用 `-I`，不应仅用 `-X HEAD` 代替。
- `-I` 的 HEAD 响应不一定与 GET 完全相同；若需观察实际 GET 响应头，可用 `curl -D - -o /dev/null url`。

## 四、输出控制

| 选项 | 作用 | 示例 |
| --- | --- | --- |
| `-o` | 保存到指定文件名 | `curl -o backup.zip url` |
| `-O` | 使用 URL 路径末尾的文件名保存 | `curl -O https://example.com/file.zip` |
| `-s` | 不显示进度和错误消息，响应体仍会输出 | `curl -s url` |
| `-S` | 配合 `-s` 恢复错误消息显示 | `curl -sS url` |
| `-v` | 将详细通信信息输出到标准错误 | `curl -v url` |
| `-w` | 传输后按指定格式输出统计信息 | `curl -w '%{http_code}\n' url` |
| `-f` | HTTP 错误状态通常使传输失败，并抑制错误响应体 | `curl -fL -o file.zip url` |

**`-o` 与 `-O`**：前者由你指定本地文件名，后者默认取 URL 路径中的文件名，并不自动使用 `Content-Disposition` 中的名称。需要使用该响应头建议的名称时，可在信任来源并注意覆盖风险的前提下使用 `-OJ`。

**HTTP 状态与退出码**：默认情况下，收到 404 或 500 响应不一定使 curl 返回非零退出码；脚本需要将 HTTP 错误视为失败时，可使用 `-f`。需要保留错误响应体时，可在支持该选项的版本中使用 `--fail-with-body`。

## 五、实战场景

### 场景 1：GET 请求获取数据

```bash
# 普通 GET
curl https://api.example.com/users

# GET 带查询参数
curl -G -d 'page=1' -d 'size=10' \
  https://api.example.com/users

# 等价 URL：https://api.example.com/users?page=1&size=10

# 含空格、中文等字符的参数使用 URL 编码
curl -G --data-urlencode 'q=Linux 学习' \
  https://api.example.com/search
```

### 场景 2：POST 提交 JSON

```bash
# 发送 JSON，-d 默认使 HTTP 请求使用 POST
curl -H 'Content-Type: application/json' \
  -d '{"name":"Alice","age":30}' \
  https://api.example.com/users

# 从文件读取 JSON，--data-binary 保留文件中的换行等字节
curl -H 'Content-Type: application/json' \
  --data-binary @data.json \
  https://api.example.com/users
```

### 场景 3：提交表单与上传文件

```bash
# 表单数据；示例值需要替换
curl --data-urlencode 'username=alice' \
  --data-urlencode 'password=示例密码' \
  https://api.example.com/login

# 文件上传（multipart/form-data）
curl -F 'file=@/path/to/report.pdf' \
  -F 'description=季度报告' \
  https://api.example.com/upload
```

`-F` 会自动生成含 boundary 的 `Content-Type`，通常不要手动覆盖该请求头。表单示例中的明文密码仅用于说明语法，实际使用时应妥善提供凭据。

### 场景 4：认证与授权

```bash
# Basic Auth：交互输入密码，使用 HTTPS
curl -u admin https://api.example.com/admin

# Bearer Token：先通过合适的方式设置 TOKEN
curl -H "Authorization: Bearer ${TOKEN}" \
  https://api.example.com/protected

# Cookie 会话：用已设置的 LOGIN_USER 和 LOGIN_PASSWORD 登录
# 接口字段及认证方式需按实际 API 调整
curl -c cookies.txt \
  --data-urlencode "user=${LOGIN_USER}" \
  --data-urlencode "pass=${LOGIN_PASSWORD}" \
  https://example.com/login

# 后续请求携带 Cookie
curl -b cookies.txt https://example.com/dashboard
```

Cookie 文件可能包含会话凭据，应限制访问并在不需要时删除。环境变量可避免将凭据硬编码进脚本，但展开后放入命令参数仍可能暴露给进程检查工具；它不等于完整的秘密管理方案。

### 场景 5：下载文件

```bash
# 跟随重定向，将 HTTP 错误视为失败，并指定文件名
curl -fL -o package.tar.gz \
  https://example.com/package.tar.gz

# 断点续传，需要服务器支持，且远端文件内容未改变
curl -fL -C - -O https://example.com/large.iso

# 限制传输速度
curl --limit-rate 500K -fLO https://example.com/large.iso
```

### 场景 6：调试与诊断

```bash
# HTTP HEAD 请求
curl -I https://api.example.com/status

# 显示详细通信过程
curl -v https://api.example.com/users

# 丢弃响应体，只输出 HTTP 状态码；保留传输错误消息
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://api.example.com/health

# 输出各阶段的时间点，单位为秒
curl -sS -o /dev/null \
  -w 'DNS:%{time_namelookup}\nConnect:%{time_connect}\nTTFB:%{time_starttransfer}\nTotal:%{time_total}\n' \
  https://example.com
```

`time_connect`、`time_starttransfer` 等是从请求开始算起的累计时间点，不能直接当作各阶段独立耗时。`-v` 输出可能包含认证头、Cookie 等信息，分享前应检查并脱敏。

## 六、安全与代理

| 选项 | 作用 | 注意 |
| --- | --- | --- |
| `-k` / `--insecure` | HTTPS 下跳过服务器证书验证 | 仅用于明确知道风险的临时排障；正常连接应修复信任链或证书问题 |
| `--cacert` | 指定用于验证服务端证书的 CA 文件 | CA 必须可信，证书域名等校验仍需通过 |
| `-x` / `--proxy` | 指定代理地址，两者是同一选项的短、长写法 | 如 `curl -x http://proxy:8080 url`，也支持 SOCKS 代理 |

凭据优先通过交互输入、权限受限的 `.netrc` 或秘密管理工具提供；使用 `.netrc` 时可将权限设为 `600`。不要将真实密码或 Token 提交到笔记、代码仓库或共享日志。

## 七、常见问题速查

| 问题 | 现象 | 排查与处理 |
| --- | --- | --- |
| 证书验证失败 | `curl: (60) SSL certificate problem` | 检查系统时间、域名、证书链和 CA；必要时通过 `--cacert` 指定可信 CA |
| 301/302 重定向 | 收到跳转状态及 `Location` 响应头 | 使用 `-L` 跟随；返回 HTML 也可能由登录页或其他错误引起 |
| 415 错误 | `Unsupported Media Type` | 按接口要求设置 `Content-Type` 和实际请求体；仅在提交 JSON 时使用 `application/json` |
| 401 错误 | `Unauthorized` | 检查认证方式、凭据有效期和 `Authorization` 头 |
| 中文乱码 | 响应显示异常 | 核对响应实际编码和终端编码；确有编码差异时用 `iconv` 转码 |
| 下载中断 | 文件只下载了一部分 | 检查网络及服务端续传支持，再尝试 `-C -`；不要拼接不同版本的远端文件 |
| 脚本把 404 当成功 | curl 退出码为 0，但状态码是 404 | 使用 `-f` 或 `--fail-with-body`，并检查退出码 |

## 八、curl 与 wget 怎么选？

| 维度 | curl | wget |
| --- | --- | --- |
| 常见用途 | API 调试、请求控制、上传和下载 | 文件下载、递归抓取、网站镜像 |
| 请求能力 | 多种方法、自定义请求头、认证和数据提交 | 也支持部分请求头、认证和提交功能，具体以版本为准 |
| 下载能力 | 支持续传和限速，方便与脚本组合 | 支持续传、递归下载和后台下载 |
| 选择依据 | 需要精细控制请求或调试 API 时常用 | 需要递归获取资源或镜像网站时常用 |

## 参考资料

- [curl 官方手册](https://curl.se/docs/manpage.html)
- [curl HTTP 脚本指南](https://curl.se/docs/httpscripting.html)
