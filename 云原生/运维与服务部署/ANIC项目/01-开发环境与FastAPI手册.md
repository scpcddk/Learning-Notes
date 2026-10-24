# ANIC 开发环境与 FastAPI 入门手册

> **项目：** ANIC 赛题二——惜字如金：黑盒弱网语义通信  
> **阶段：** 第一阶段——开发环境、官方基础镜像检查与最小 HTTP 服务  
> **开发环境：** Windows + VS Code + WSL Ubuntu 24.04 + Docker Desktop  
> **当前状态：** WSL 环境及 FastAPI 服务已验收；官方基础镜像已加载，部分关键字段已检查  
> **维护原则：** 只把实际执行、确认或验证过的内容标记为已完成。

---

## 一、阶段目标与完成情况

本阶段的目标是建立能够运行 ANIC HTTP 服务的 Python 开发环境，了解官方基础镜像的关键配置，并完成最小 FastAPI 服务的验证。

| 任务 | 状态 |
|---|---|
| 配置 WSL Python 环境 | 已完成 |
| 创建并激活 `.venv` | 已完成 |
| 安装 FastAPI、Uvicorn | 已完成 |
| 编写最小 FastAPI 服务 | 已完成 |
| 启动服务并验证 `/health` | 已完成 |
| 使用 Swagger UI 实际调用接口 | 已完成 |
| 加载 ANIC 官方基础镜像 | 已完成 |
| 检查官方镜像关键元信息 | 已检查部分字段 |
| 构建自定义 Docker 镜像 | 待完成 |
| 使用 Docker Compose 启动服务 | 待完成 |

## 二、开发环境与项目目录

### 2.1 工具及作用

| 工具 | 用途 |
|---|---|
| Windows | 宿主操作系统 |
| VS Code | 编写、查看和调试代码 |
| WSL Ubuntu 24.04 | Linux 开发环境 |
| Python 3.12.3 | 当前 WSL Python 解释器 |
| `.venv` | 项目独立的 Python 虚拟环境 |
| FastAPI | 定义 HTTP API |
| Uvicorn | 运行 ASGI 应用服务器 |
| Docker Desktop | 管理 Docker 镜像和容器 |

### 2.2 项目路径

Windows 项目路径：

`D:\东北大学大作业\ANIC\project`

**对应的 WSL 路径**：

`/mnt/d/东北大学大作业/ANIC/project`

官方基础镜像文件：

`D:\东北大学大作业\ANIC\materials\agenthack-base-1.1.1.tar`

### 2.3 项目目录结构

```text
project/
├── app/
│   └── main.py
├── .venv/
├── requirements.txt
└── Dockerfile
```

- `app/main.py`：FastAPI 应用代码。
- `requirements.txt`：Python 依赖清单。
- `.venv/`：虚拟环境目录。
- `Dockerfile`：后续构建项目镜像的配置文件。

`.venv` 通常不需要提交到 Git 仓库。

## 三、创建 Python 虚拟环境

### 3.1 进入项目目录

在 VS Code 的 WSL 终端中执行：

```bash
cd "/mnt/d/东北大学大作业/ANIC/project"
```

检查当前目录：

```bash
pwd
```

预期输出：

```text
/mnt/d/东北大学大作业/ANIC/project
```

### 3.2 检查 Python 版本

```bash
python3 --version
```

本次实际输出：

```text
Python 3.12.3
```

### 3.3 安装虚拟环境支持

首次创建虚拟环境时，系统缺少 `venv` 支持组件，执行：

```bash
sudo apt update
sudo apt install python3.12-venv
```

创建虚拟环境：

```bash
python3 -m venv .venv
```

### 3.4 激活虚拟环境

```bash
source .venv/bin/activate
```

激活成功后，终端提示符通常会出现：

```text
(.venv)
```

检查当前 Python 路径：

```bash
which python
```

预期路径应指向项目虚拟环境，例如：

```text
/mnt/d/东北大学大作业/ANIC/project/.venv/bin/python
```

### 3.5 关键命令速查

| 命令 | 作用 |
|---|---|
| `python3 -m venv .venv` | 创建虚拟环境 |
| `source .venv/bin/activate` | 激活虚拟环境 |
| `which python` | 查看当前 Python 路径 |
| `deactivate` | 退出虚拟环境 |

本项目当前使用 Python 自带的 `venv`，不是 Miniconda 环境。

## 四、安装与验证 Python 依赖

### 4.1 `requirements.txt`

当前文件内容：

```text
fastapi
uvicorn
```

- FastAPI：定义路由、处理请求、返回响应并生成接口文档。
- Uvicorn：运行 ASGI 应用服务器，监听 HTTP 请求。

### 4.2 安装依赖

确保位于项目目录且已激活 `.venv`，然后执行：

```bash
python -m pip install -r requirements.txt
```

本次安装成功。

### 4.3 验证依赖

```bash
python -c "import fastapi, uvicorn; print('FastAPI:', fastapi.__version__); print('Uvicorn:', uvicorn.__version__)"
```

本次实际输出：

```text
FastAPI: 0.143.1
Uvicorn: 0.54.0
```

使用 `python -m pip` 可以减少依赖被安装到错误 Python 环境的风险。

## 五、编写最小 FastAPI 服务

文件位置：

`app/main.py`

代码：

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "role": "sender"}
```

### 5.1 逐行理解

**导入 FastAPI：**

```python
from fastapi import FastAPI
```

导入用于创建应用的 `FastAPI` 类。

**创建应用对象：**

```python
app = FastAPI()
```

创建 FastAPI 应用实例。

**注册路由：**

```python
@app.get("/health")
def health():
    return {"status": "ok", "role": "sender"}
```

`@app.get("/health")` 将 `health()` 注册为处理 `/health` 路径 GET 请求的函数。

收到匹配的请求后，FastAPI 调用该函数，并将返回的 Python 字典转换为 JSON 响应。

预期响应：

```json
{
  "status": "ok",
  "role": "sender"
}
```

此时只是最小验证服务，还没有实现 Sender 的压缩、分片、UDP 发送等业务逻辑。

## 六、启动 HTTP 服务

### 6.1 启动命令

在项目根目录执行：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 6.2 命令拆解

| 命令部分 | 含义 |
|---|---|
| `python -m uvicorn` | 使用当前 Python 环境运行 Uvicorn |
| `app.main:app` | 从 `app/main.py` 加载名为 `app` 的应用对象 |
| `--host 0.0.0.0` | 监听所有 IPv4 网络接口 |
| `--port 8080` | 监听 8080 端口 |

这里的 `app.main:app` 中：

- `app.main`：Python 模块路径，对应 `app/main.py`。
- 最后的 `app`：模块中创建的 FastAPI 应用对象。

服务启动后，终端会持续运行，这是正常现象。需要停止服务时，在该终端按 `Ctrl+C`。

## 七、验证 HTTP 接口与 Swagger

### 7.1 验证 `/health`

浏览器访问：

`http://localhost:8080/health`

本次实际返回：

```json
{
  "status": "ok",
  "role": "sender"
}
```

验证通过。

### 7.2 验证 `/docs`

浏览器访问：

`http://localhost:8080/docs`

本次已确认页面可以打开，并通过 Swagger UI 实际调用 `GET /health`，获得预期结果。

操作步骤：

1. 找到 `GET /health`。
2. 点击 `Try it out`。
3. 点击 `Execute`。
4. 检查响应状态码和响应内容。

### 7.3 请求处理流程

```text
浏览器 / Swagger UI
        |
        | HTTP GET /health
        v
Uvicorn
        |
        v
FastAPI 路由匹配
        |
        v
调用 health() 函数
        |
        v
返回 Python 字典
        |
        v
FastAPI 转换为 JSON
        |
        v
浏览器显示响应
```

Swagger UI 不会直接调用 Python 函数，而是通过 HTTP 与服务通信。这与 Java 后端的基本请求处理机制相同。

## 八、ANIC 官方基础镜像检查

### 8.1 检查目的

官方基础镜像：

`agenthack/base:1.1.1`

镜像文件：

`D:\东北大学大作业\ANIC\materials\agenthack-base-1.1.1.tar`

本次已经使用 Docker 加载该镜像，并通过 `docker image inspect` 查看元信息。

官方基础镜像是后续构建参赛服务镜像的基础。需要先确认它的架构、默认运行用户、工作目录、端口、启动命令和健康检查配置。

### 8.2 加载镜像

在 PowerShell 的 `materials` 目录中执行：

```powershell
docker load -i ".\agenthack-base-1.1.1.tar"
```

本次已成功加载。

### 8.3 查看镜像列表

```powershell
docker image ls
```

只查看目标镜像：

```powershell
docker image ls agenthack/base:1.1.1
```

终端常见字段：

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `REPOSITORY` | 镜像仓库名 | 确认 `agenthack/base` |
| `TAG` | 镜像标签 | 确认 `1.1.1` |
| `IMAGE ID` | 镜像 ID | 辅助识别镜像 |
| `CREATED` | 创建时间信息 | 了解镜像元数据 |
| `SIZE` | 镜像显示大小 | 了解镜像体积 |

注意：`docker image ls` 显示的大小是镜像及其父层的累计大小；不同镜像可能共享底层镜像层，因此不能直接将各镜像显示大小相加，作为实际磁盘新增占用。

### 8.4 查看完整镜像元信息

执行：

```powershell
docker image inspect agenthack/base:1.1.1
```

本次输出中的镜像 ID：

```text
sha256:2d1023efe3e6a8dc7465326bab40d70408a579991fe60bff626145b0d29241b0
```

`docker image inspect` 返回 JSON。最重要的是学会识别原始字段，而不是只看中文解释。

### 8.5 推荐重点检查的字段

#### ① 镜像身份、操作系统与架构

完整 JSON 中通常会看到：

```json
{
  "Id": "sha256:...",
  "RepoTags": [
    "agenthack/base:1.1.1"
  ],
  "Os": "linux",
  "Architecture": "amd64"
}
```

以上是字段结构示例；镜像 ID 应以实际输出为准。

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{.Id}}'
docker image inspect agenthack/base:1.1.1 --format '{{json .RepoTags}}'
docker image inspect agenthack/base:1.1.1 --format '{{.Os}}/{{.Architecture}}'
```

| 原始字段 | 示例值 | 含义 | 检查目的 |
|---|---|---|---|
| `Id` | `sha256:...` | 镜像内容标识 | 确认镜像身份 |
| `RepoTags` | `["agenthack/base:1.1.1"]` | 镜像名称和标签 | 确认使用的版本 |
| `Os` | `linux` | 操作系统类型 | 确认容器运行平台 |
| `Architecture` | `amd64` | CPU 架构 | 检查架构是否匹配 |

本次已知架构为 `linux/amd64`。

#### ② 默认工作目录：`Config.WorkingDir`

完整 JSON 中的典型结构：

```json
{
  "Config": {
    "WorkingDir": "/app"
  }
}
```

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{.Config.WorkingDir}}'
```

本次已知结果：

```text
/app
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config` | 镜像运行时配置对象 | 查看容器默认配置 |
| `Config.WorkingDir` | 默认工作目录 | 确认应用文件和相对路径的位置 |

如果 Dockerfile 后续使用相对路径复制文件、执行脚本或启动应用，就需要理解工作目录的影响。

#### ③ 默认运行用户：`Config.User`

典型 JSON 结构：

```json
{
  "Config": {
    "User": "agent"
  }
}
```

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{.Config.User}}'
```

本次已知结果：

```text
agent
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.User` | 默认运行用户 | 确认进程使用哪个用户身份运行 |

这意味着不能假设容器内应用拥有 root 权限。后续需要留意文件权限、目录所有权和可写路径。

#### ④ 声明端口：`Config.ExposedPorts`

典型 JSON 结构：

```json
{
  "Config": {
    "ExposedPorts": {
      "8080/tcp": {}
    }
  }
}
```

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.ExposedPorts}}'
```

本次已知镜像声明包含：

```text
8080/tcp
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.ExposedPorts` | 镜像声明的端口集合 | 了解镜像预期使用的端口 |
| `8080/tcp` | TCP 8080 端口声明 | 对照 HTTP 服务端口配置 |

注意：**`EXPOSE` 或 `Config.ExposedPorts` 只是端口声明，不会自动发布到宿主机**。宿主机端口映射需要通过 `docker run -p` 或 Compose 的 `ports` 配置。

#### ⑤ 默认入口点：`Config.Entrypoint`

典型 JSON 结构：

```json
{
  "Config": {
    "Entrypoint": null
  }
}
```

也可能是一个命令数组，例如：

```json
{
  "Config": {
    "Entrypoint": [
      "python"
    ]
  }
}
```

以上是结构示例，不代表本次镜像实际返回值。

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Entrypoint}}'
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.Entrypoint` | 容器入口点 | 确认容器启动时固定执行的程序 |

如果该字段是 `null`，通常表示镜像没有配置专门的入口点。最终执行行为还需要结合 `Config.Cmd` 判断。

#### ⑥ 默认命令：`Config.Cmd`

典型 JSON 结构：

```json
{
  "Config": {
    "Cmd": [
      "..."
    ]
  }
}
```

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Cmd}}'
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.Cmd` | 默认命令或默认参数 | 确认容器启动后执行什么 |

**本次已确认：** 官方基础镜像的默认 CMD 会主动以失败状态退出，并提示参赛者需要覆盖 CMD。

因此，后续必须为自己的应用配置正确的启动命令。不能把官方基础镜像加载成功误认为服务已经启动。

`Entrypoint` 和 `Cmd` 需要结合理解：两者共同影响容器最终执行的命令；具体组合规则可参考 Docker 官方文档。

#### ⑦ 健康检查：`Config.Healthcheck`

典型 JSON 结构：

```json
{
  "Config": {
    "Healthcheck": {
      "Test": [
        "CMD-SHELL",
        "..."
      ],
      "Interval": 30000000000,
      "Timeout": 3000000000,
      "Retries": 3
    }
  }
}
```

以上仅用于说明字段结构，具体数值和命令必须以实际输出为准。

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Healthcheck}}'
```

本次已知健康检查会通过 curl 访问容器内的：

`http://localhost:8080/health`

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.Healthcheck` | 健康检查配置 | 确认镜像如何检测服务健康 |
| `Test` | 实际执行的检查命令 | 确认检查目标与方式 |
| `Interval` | 检查间隔 | 了解多久执行一次检查 |
| `Timeout` | 单次检查超时时间 | 了解检查最长等待时间 |
| `Retries` | 失败重试次数 | 了解失败多少次后判定不健康 |
| `StartPeriod` | 启动宽限期（如果存在） | 了解启动初期是否有宽限时间 |

如果服务没有启动，或者 `/health` 不符合检查要求，容器可能被标记为 `unhealthy`。

`running` 与 `healthy` 是两个不同状态：容器正在运行，不一定代表应用健康。

#### ⑧ 环境变量：`Config.Env`

典型 JSON 结构：

```json
{
  "Config": {
    "Env": [
      "PATH=...",
      "PYTHON_VERSION=..."
    ]
  }
}
```

这是字段结构示例，具体变量以实际镜像为准。

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Env}}'
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.Env` | 镜像默认环境变量列表 | 了解运行环境预设 |

环境变量可能涉及 Python 路径、运行参数或其他配置。检查时注意不要把密钥等敏感信息粘贴到公开文档或提交到 Git。

#### ⑨ 卷声明：`Config.Volumes`

典型 JSON 结构：

```json
{
  "Config": {
    "Volumes": null
  }
}
```

查询命令：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Volumes}}'
```

| 原始字段 | 含义 | 检查目的 |
|---|---|---|
| `Config.Volumes` | 镜像声明的卷 | 了解镜像是否声明了需要挂载的目录 |

如果输出为 `null`，表示镜像配置中没有声明卷；这不代表运行容器时不能使用挂载。

#### ⑩ 镜像大小与构建历史

查看镜像列表：

```powershell
docker image ls agenthack/base:1.1.1
```

查看构建历史：

```powershell
docker image history agenthack/base:1.1.1
```

查看 Docker 磁盘使用情况：

```powershell
docker system df -v
```

| 命令或字段 | 含义 | 用途 |
|---|---|---|
| `SIZE` | 镜像显示大小 | 了解镜像体积 |
| `docker image history` | 镜像层构建历史 | 了解镜像层和构建指令摘要 |
| `SHARED SIZE` | 与其他镜像共享的层大小 | 理解镜像层共享 |
| `UNIQUE SIZE` | 镜像独有的层大小 | 了解镜像独有层占用 |

此前终端记录出现过 `224MB` 和 `58.1MB`，但缺少完整表头，不能直接确定它们分别属于哪个字段，应以当时的完整终端输出为准。

### 8.6 官方基础镜像检查结论

目前已经确认：

- [x] 镜像 `agenthack/base:1.1.1` 已加载。
- [x] 镜像 ID 已记录。
- [x] 架构为 `linux/amd64`。
- [x] `Config.WorkingDir` 为 `/app`。
- [x] `Config.User` 为 `agent`。
- [x] `Config.ExposedPorts` 声明了 `8080/tcp`。
- [x] 存在针对 `/health` 的健康检查配置。
- [x] 默认 `Config.Cmd` 需要被参赛者的应用启动命令覆盖。

这里的“已确认”只表示掌握了现有检查记录中确认的结果。若需要补齐每一个字段的准确值，应重新执行对应命令并以完整终端输出为准。

## 九、常见问题排查

### 9.1 缺少 `python3.12-venv`

```bash
sudo apt update
sudo apt install python3.12-venv
python3 -m venv .venv
```

如果 `.venv` 已创建成功，不必重复创建。

### 9.2 找不到 `requirements.txt`

```bash
cd "/mnt/d/东北大学大作业/ANIC/project"
pwd
ls
```

确认在项目根目录，并且文件存在。

### 9.3 访问 `/` 返回 404

当前代码只定义了 `/health`：

- `/`：没有定义根路由，通常返回 404。
- `/health`：返回健康检查 JSON。
- `/docs`：显示自动生成的接口文档。

根路径返回 404 不代表服务启动失败。

### 9.4 无法访问 `localhost:8080`

检查：

1. Uvicorn 是否仍在运行。
2. 启动时是否出现端口占用或导入错误。
3. 是否在正确的项目目录执行命令。
4. `app/main.py` 是否存在，应用对象是否命名为 `app`。
5. 浏览器访问端口是否为 8080。

### 9.5 Python 包安装后仍报错

```bash
which python
python -m pip --version
```

确认解释器和 pip 都指向项目的 `.venv`。如果没有，执行：

```bash
source .venv/bin/activate
```

### 9.6 Docker 镜像已加载，但容器启动失败

先检查默认启动配置：

```powershell
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Entrypoint}}'
docker image inspect agenthack/base:1.1.1 --format '{{json .Config.Cmd}}'
```

官方基础镜像默认 CMD 会主动失败退出，需要后续为应用配置启动命令。

## 十、本阶段验收清单

- [x] WSL Python 环境可用。
- [x] `.venv` 创建并激活。
- [x] FastAPI、Uvicorn 安装成功。
- [x] `app/main.py` 最小服务编写完成。
- [x] Uvicorn 在 8080 端口运行。
- [x] `/health` 返回正确 JSON。
- [x] `/docs` 页面可以打开。
- [x] Swagger UI 实际调用接口成功。
- [x] 官方基础镜像已加载。
- [x] 官方基础镜像关键运行约定已检查。

**阶段结论：** WSL 开发环境和最小 FastAPI HTTP 服务已完成验收；官方基础镜像已加载，并检查了部分关键字段。自定义 Docker 镜像构建与 Compose 部署仍属于后续工作。

## 十一、下一阶段任务

下一阶段进入 Docker 容器化交付：

1. 编写项目 Dockerfile。
2. 为 Sender、Receiver 准备镜像构建方案。
3. 配置容器启动命令、运行用户、工作目录和端口。
4. 编写 Docker Compose。
5. 启动容器并检查日志、端口和健康状态。
6. 验证容器中的 `/health` 能够正常响应。

完成后，再单独编写第二篇《ANIC Docker 镜像与容器交付手册》。

---

**维护原则：** 实际操作与验证结果优先；“已完成”“已检查”和“待验证”必须明确区分。后续环境、依赖或项目结构发生变化时，应更新对应章节。
