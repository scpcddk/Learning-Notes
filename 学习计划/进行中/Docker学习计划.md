# Docker 系统学习路线计划书

> **学习方向：Docker 基础原理 → 容器管理 → 镜像构建 → 网络 → 存储 → Compose → 工程化部署 → 安全与排障**
>
> **适用场景：Java Spring Boot 后端、Python/FastAPI、AI Agent 项目、Linux 服务器部署**
>
> **计划性质：长期学习计划，不设置时间限制，以阶段验收作为推进依据。**

---

# 一、学习定位

## 1. 最终目标

能够独立完成以下任务：

1. 理解 Docker 镜像、容器、网络、存储的工作机制。
2. 熟练使用 Docker CLI 管理容器及镜像。
3. 独立编写、优化和调试 Dockerfile。
4. 理解容器网络隔离、DNS、端口映射和容器间通信。
5. 正确使用 Bind Mount、Volume 管理持久化数据。
6. 使用 Docker Compose 管理多容器应用。
7. 独立将 Spring Boot、Python/FastAPI 项目容器化。
8. 解决容器启动失败、网络异常、端口冲突、权限问题、数据丢失和资源限制等常见故障。
9. 理解 Docker 在实际软件开发、部署与 CI/CD 中的作用。
10. 具备为 AI Agent 项目设计和交付 Docker 运行环境的能力。

**最终定位：熟练的 Docker 应用开发与部署使用者，具备必要的容器底层原理知识和独立排障能力。**

不以深入研究 Docker Engine 源码、容器运行时开发或 Kubernetes 运维作为本计划的必修目标。

## 2. 学习原则

- **内容驱动**：按照知识依赖关系推进，不按日期推进。
- **理论与实践结合**：先理解，再操作，最后验证。
- **不能只背命令**：必须理解命令执行后 Docker 实际发生了什么。
- **以独立完成为准**：看过示例不等于能独立应用。
- **维护错题与故障记录**：将理解错误和实操问题保留在个人笔记中。
- **优先工程实际**：重点学习开发、部署、调试和交付中常用的能力。
- **不重复学习中间件本身**：Nginx、Redis、EMQX、MinIO 等只作为 Docker 部署案例，其内部原理另行学习。

## 3. 进度标记规范

- `[ ]` 未完成验收。
- `[x]` 已完成验收。
- `已接触`：之前学过或使用过，但尚未完成本计划对应验收。
- `学习中`：正在系统学习。
- `已掌握`：能够独立解释、操作、排障，且通过阶段验收。

**注意：本计划中未勾选的项目不代表你完全不会，只表示还没有按照本计划完成验收。**

---

# 二、总体学习路线

| 阶段 | 学习主题 | 核心能力 | 优先级 |
|---|---|---|---|
| 阶段 0 | Docker 环境与整体认识 | 理解 Docker 体系 | 必修 |
| 阶段 1 | 镜像与容器基础 | 熟练使用基本命令 | 必修 |
| 阶段 2 | 容器生命周期与运行机制 | 理解容器运行和退出 | 必修 |
| 阶段 3 | Dockerfile 与镜像构建 | 独立制作镜像 | 必修 |
| 阶段 4 | Docker 网络 | 理解并解决网络通信问题 | 必修 |
| 阶段 5 | Docker 存储与数据持久化 | 正确管理容器数据 | 必修 |
| 阶段 6 | Docker Compose | 编排和管理多容器应用 | 必修 |
| 阶段 7 | Docker 工程化部署 | 部署 Spring Boot / Python 项目 | 必修 |
| 阶段 8 | 日志、监控、排障与资源管理 | 独立定位常见故障 | 必修 |
| 阶段 9 | Docker 安全与构建优化 | 提高安全性和可维护性 | 进阶 |
| 阶段 10 | 综合项目与持续交付 | 形成完整工程能力 | 进阶 |

推荐顺序：**0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10**。

阶段之间可以适度交叉复习，但必须分别完成验收。

---

# 三、阶段 0：Docker 环境与整体认识

## 阶段目标

理解 Docker 是什么、为什么使用 Docker，以及 Docker 的基本架构。

### 1. Docker 基础

- [ ] 什么是容器化技术
- [ ] Docker 解决了哪些问题
- [ ] 传统部署与容器化部署的区别
- [ ] Docker 与虚拟机的区别
- [ ] Docker 的典型使用场景
- [ ] 容器与宿主机之间的关系

### 2. Docker 基本架构

- [ ] Docker Client
- [ ] Docker Daemon（dockerd）
- [ ] Docker Engine
- [ ] Docker Image
- [ ] Docker Container
- [ ] Docker Registry
- [ ] Docker Hub
- [ ] Docker CLI 与守护进程之间的关系

### 3. Docker 运行环境

- [ ] Docker Desktop 与 Linux Docker Engine 的区别
- [ ] Windows + WSL2 中 Docker 的运行方式
- [ ] Docker Engine 与 Docker Compose V2
- [ ] Docker 服务的启动与停止
- [ ] 查看 Docker 版本与系统信息
- [ ] Docker 基本目录与数据存放位置

### 4. 基础原理入门

- [ ] 理解容器并不是一台完整虚拟机
- [ ] 容器共享宿主机内核的基本含义
- [ ] Linux Namespace 的作用
- [ ] Linux cgroups 的作用
- [ ] 容器文件系统隔离的基本概念

此阶段只要求理解作用，不要求深入 Linux 内核实现。

## 实操任务

- [ ] 检查 Docker Engine 是否可用
- [ ] 查看 Docker 版本与运行信息
- [ ] 拉取并运行 `hello-world`
- [ ] 观察 Docker Desktop 与 CLI 的对应关系
- [ ] 解释 Windows + WSL2 环境下容器实际运行在哪里

## 阶段验收

- [ ] 能解释 Docker、镜像、容器、仓库的关系
- [ ] 能描述一条 Docker 命令如何交给 Docker Engine 执行
- [ ] 能解释 Docker 与虚拟机的主要区别
- [ ] 能独立确认 Docker 环境正常工作

---

# 四、阶段 1：镜像与容器基础

## 阶段目标

熟练掌握镜像和容器的基本操作，理解两者关系。

### 1. 镜像管理

- [ ] 镜像是什么
- [ ] 镜像与容器的关系
- [ ] 镜像名称和 Tag
- [ ] `latest` 的真实含义
- [ ] 镜像 ID 与镜像名称
- [ ] 镜像拉取与查看
- [ ] 镜像删除
- [ ] 镜像重命名与打标签
- [ ] 镜像仓库基本概念

重点命令：

```bash
docker pull
docker images
docker image ls
docker rmi
docker image inspect
docker tag
```

### 2. 容器基础操作

- [ ] 创建并启动容器
- [ ] 查看运行中的容器
- [ ] 查看全部容器
- [ ] 启动已有容器
- [ ] 停止容器
- [ ] 重启容器
- [ ] 删除容器
- [ ] 强制删除容器
- [ ] 查看容器详细信息
- [ ] 查看容器日志

重点命令：

```bash
docker run
docker ps
docker ps -a
docker start
docker stop
docker restart
docker rm
docker inspect
docker logs
```

### 3. docker run 常用参数

- [x] `-d`
- [ ] `-i`
- [ ] `-t`
- [ ] `-it`
- [x] `--name`
- [ ] `--rm`
- [x] `-p`
- [x] `-e`
- [ ] `--env-file`
- [x] `-v`
- [ ] `--mount`
- [x] `--network`
- [ ] `--restart`
- [ ] `--memory`
- [ ] `--cpus`

理解不同命令中相同短参数可能有不同含义，例如 `docker build -t` 与 `docker run -t`。

### 4. 容器内部操作

- [ ] `docker exec`
- [ ] `docker attach`
- [ ] `docker cp`
- [ ] `docker top`
- [ ] `docker stats`
- [ ] 容器内 Shell 的使用
- [ ] `bash` 和 `sh` 的区别
- [ ] 容器与宿主机文件的复制

## 实操任务

- [ ] 拉取 Ubuntu 或 Alpine 镜像
- [ ] 创建一个有名称的容器
- [ ] 进入容器执行命令
- [ ] 从宿主机复制文件到容器
- [ ] 从容器复制文件到宿主机
- [ ] 查看容器信息和日志
- [ ] 删除容器并验证镜像是否还存在

## 阶段验收

- [ ] 不查笔记完成镜像和容器基本操作
- [ ] 正确区分 `run`、`start`、`restart`
- [ ] 正确区分 `rm` 与 `rmi`
- [ ] 能解释 `docker run` 常用参数的实际作用
- [ ] 能根据需求独立写出完整 `docker run` 命令

---

# 五、阶段 2：容器生命周期与运行机制

## 阶段目标

理解容器为什么运行、为什么退出以及如何控制运行状态。

### 1. 容器生命周期

- [ ] Created
- [ ] Running
- [ ] Paused
- [ ] Exited
- [ ] Restarting
- [ ] Dead 状态的基本认识
- [ ] 容器状态之间的转换
- [ ] 已停止容器与已删除容器的区别

### 2. 容器主进程

- [ ] 容器启动与主进程的关系
- [ ] PID 1 的基本概念
- [ ] 主进程结束为什么会导致容器退出
- [ ] 前台与后台运行
- [ ] `-d` 为什么不保证容器持续运行
- [ ] `docker exec` 与容器主进程的区别

### 3. 退出码与信号

- [ ] 退出码 `0`
- [ ] 退出码 `1`
- [ ] 退出码 `137`
- [ ] 退出码 `143`
- [ ] 退出码的适用范围与常见误解
- [ ] SIGTERM 与 SIGKILL
- [ ] `docker stop` 与 `docker kill`
- [ ] 优雅停止的基本原理
- [ ] 停止超时后的强制终止

### 4. 自动重启策略

- [ ] `no`
- [ ] `on-failure`
- [ ] `always`
- [ ] `unless-stopped`
- [ ] 正常退出与异常退出时的区别
- [ ] 手动停止对重启策略的影响
- [ ] Docker 守护进程重启后的恢复行为
- [ ] 重启循环及其排查

### 5. 环境变量

- [ ] 环境变量的用途
- [ ] `docker run -e`
- [ ] `--env-file`
- [ ] 容器环境变量与宿主机环境变量
- [ ] Linux 环境变量名称大小写
- [ ] Python `os.getenv()`
- [ ] Java Spring Boot 读取环境变量
- [ ] `docker exec ... printenv`

## 实操任务

- [ ] 编写一个执行完就退出的 Python 容器
- [ ] 编写一个持续运行的 Python 容器
- [ ] 模拟正常退出和异常退出
- [ ] 查看容器退出码
- [ ] 对比 `stop` 和 `kill`
- [ ] 分别测试四种重启策略
- [ ] 通过环境变量传入程序配置
- [ ] 排查容器不断重启的问题

## 阶段验收

- [ ] 能根据程序主进程判断容器是否会继续运行
- [ ] 能解释常见退出码及其局限
- [ ] 能正确选择重启策略
- [ ] 能独立分析容器异常退出
- [ ] 能使用环境变量配置容器程序

---

# 六、阶段 3：Dockerfile 与镜像构建

## 阶段目标

能够独立编写 Dockerfile，理解镜像构建过程，并优化构建结果。

### 1. Dockerfile 基础

- [ ] Dockerfile 的作用
- [ ] Dockerfile 与镜像的关系
- [ ] 构建上下文（Build Context）
- [ ] `docker build`
- [ ] `-t` 标签参数
- [ ] Dockerfile 的执行顺序
- [ ] `.dockerignore`

### 2. Dockerfile 核心指令

- [ ] `FROM`
- [ ] `WORKDIR`
- [ ] `COPY`
- [ ] `ADD`
- [ ] `RUN`
- [ ] `CMD`
- [ ] `ENTRYPOINT`
- [ ] `ENV`
- [ ] `ARG`
- [ ] `EXPOSE`
- [ ] `USER`
- [ ] `HEALTHCHECK`
- [ ] `LABEL`

### 3. 重点机制

- [ ] `RUN` 与 `CMD` 的区别
- [ ] `CMD` 与 `ENTRYPOINT` 的区别
- [ ] `COPY` 与 `ADD` 的区别
- [ ] `ARG` 与 `ENV` 的区别
- [ ] Shell Form 与 Exec Form
- [ ] `ENTRYPOINT` 和 `CMD` 组合
- [ ] Dockerfile 中环境变量的作用
- [ ] `EXPOSE` 为什么不等于端口发布
- [ ] `USER` 如何影响程序权限

### 4. 镜像分层与构建缓存

- [ ] 镜像层的概念
- [ ] 只读层与容器可写层
- [ ] 构建缓存的作用
- [ ] 缓存失效的原因
- [ ] Dockerfile 指令顺序的影响
- [ ] `docker history`
- [ ] `docker build --no-cache`
- [ ] BuildKit 基础
- [ ] BuildKit 缓存挂载
- [ ] 构建日志的阅读

### 5. 多阶段构建

- [ ] 多阶段构建的目的
- [ ] 构建阶段与运行阶段
- [ ] `FROM ... AS builder`
- [ ] `COPY --from=builder`
- [ ] JDK 构建与 JRE 运行分离
- [ ] Python 项目依赖管理与镜像瘦身
- [ ] 多阶段构建和普通构建的区别

### 6. 镜像管理扩展

- [ ] `docker save` / `docker load`
- [ ] `docker export` / `docker import`
- [ ] `docker commit`
- [ ] `docker push`
- [ ] 镜像离线迁移
- [ ] 镜像标签与版本管理
- [ ] 镜像架构：amd64 与 arm64
- [ ] 多架构镜像基本概念

## 实操任务

- [ ] 编写 Python 项目的 Dockerfile
- [ ] 编写 Spring Boot 项目的 Dockerfile
- [ ] 构建并启动自定义镜像
- [ ] 修改代码并观察构建缓存
- [ ] 编写 `.dockerignore`
- [ ] 使用多阶段构建 Java 项目
- [ ] 对比构建前后镜像大小
- [ ] 导出镜像为 tar 文件并重新导入
- [ ] 验证镜像能在目标架构运行

## 阶段验收

- [ ] 不依赖现成模板编写 Dockerfile
- [ ] 能解释镜像构建与容器运行的区别
- [ ] 能理解镜像层和缓存机制
- [ ] 能独立优化镜像构建过程
- [ ] 能将 Spring Boot 或 Python 项目制作为可运行镜像

---

# 七、阶段 4：Docker 网络

## 阶段目标

掌握 Docker 网络通信机制，并能独立定位常见网络故障。

### 1. 网络基础回顾

- [ ] IPv4 与 IPv6 基础
- [ ] IP 地址与端口
- [ ] `localhost`
- [ ] `127.0.0.1` 与 `::1`
- [ ] `0.0.0.0` 的含义
- [ ] DNS 的基本作用
- [ ] TCP 与 UDP 基础
- [ ] 网络接口与端口监听
- [ ] NAT 的基本概念

### 2. Docker 网络模式

- [ ] bridge 网络
- [ ] host 网络
- [ ] none 网络
- [ ] container 网络模式
- [ ] 自定义 bridge 网络
- [ ] 默认 bridge 与自定义 bridge 的区别
- [ ] Docker Desktop 和 Linux 网络环境的差异

### 3. Docker 网络管理

- [ ] `docker network ls`
- [ ] `docker network create`
- [ ] `docker network inspect`
- [ ] `docker network connect`
- [ ] `docker network disconnect`
- [ ] `docker network rm`

### 4. 容器之间的通信

- [ ] 同一 Docker 网络中的通信
- [ ] 不同 Docker 网络中的隔离
- [ ] 自定义网络中的容器名称解析
- [ ] 使用容器名连接其他容器
- [ ] 使用服务名连接 Compose 服务
- [ ] 为什么不建议硬编码容器 IP
- [ ] 容器间通信为什么通常不需要 `-p`

### 5. 端口映射

- [ ] `-p 宿主机端口:容器端口`
- [ ] `-P` 自动端口发布
- [ ] 宿主机端口与容器端口
- [ ] `127.0.0.1:8081:8080`
- [ ] 端口绑定地址与访问范围
- [ ] TCP 与 UDP 端口发布
- [ ] `EXPOSE` 与 `-p` 的区别
- [ ] 端口冲突的原因
- [ ] 服务监听 `127.0.0.1` 与 `0.0.0.0` 的区别

### 6. 容器访问宿主机

- [ ] 容器内 `localhost` 指向哪里
- [ ] Docker Desktop 的 `host.docker.internal`
- [ ] Linux 中的 `host-gateway`
- [ ] 宿主机访问容器
- [ ] 容器访问宿主机 MySQL 的场景
- [ ] 宿主机防火墙、监听地址和访问权限的影响

### 7. 网络排障

- [ ] 容器无法访问外网
- [ ] 容器间无法通信
- [ ] 容器名称无法解析
- [ ] 连接被拒绝（Connection refused）
- [ ] 连接超时（Timeout）
- [ ] 宿主机无法访问发布端口
- [ ] DNS 解析异常
- [ ] 使用 `curl`、`ip`、`ss` 等工具排查
- [ ] 查看容器网络配置

## 实操任务

- [ ] 创建自定义 bridge 网络
- [ ] 创建两个容器并连接同一网络
- [ ] 使用容器名完成通信
- [ ] 将容器连接到第二个网络
- [ ] 验证不同网络之间的隔离
- [ ] 测试端口发布
- [ ] 测试宿主机访问容器
- [ ] 测试容器访问宿主机
- [ ] 模拟并排查端口冲突
- [ ] 模拟并排查服务监听地址错误
- [ ] 完成至少一次 TCP/UDP 端口映射实验

## 阶段验收

- [ ] 能解释 Docker 的基本网络模式
- [ ] 能正确区分三个地址：localhost、容器名、host.docker.internal
- [ ] 能正确理解 `-p`
- [ ] 能独立创建并管理 Docker 网络
- [ ] 能排查常见容器网络不通的问题

---

# 八、阶段 5：Docker 存储与数据持久化

## 阶段目标

理解容器文件系统及数据存储方式，防止容器重建导致数据丢失。

### 1. 容器文件系统

- [ ] 镜像只读层
- [ ] 容器可写层
- [ ] 容器可写层的生命周期
- [ ] 容器删除与数据丢失的关系
- [ ] 容器重启与容器重建的区别
- [ ] 镜像更新对容器数据的影响

### 2. Docker 数据存储方式

- [ ] Bind Mount
- [ ] Named Volume
- [ ] Anonymous Volume
- [ ] tmpfs Mount
- [ ] 各种存储方式的区别
- [ ] 什么情况下使用哪一种方式

### 3. Bind Mount

- [ ] 宿主机路径与容器路径
- [ ] `-v`
- [ ] `--mount type=bind`
- [ ] 文件挂载与目录挂载
- [ ] 只读挂载
- [ ] 权限问题
- [ ] 宿主机文件变化对容器的影响
- [ ] Windows 与 Linux 路径差异

### 4. Volume

- [ ] `docker volume create`
- [ ] `docker volume ls`
- [ ] `docker volume inspect`
- [ ] `docker volume rm`
- [ ] 命名卷的生命周期
- [ ] 数据卷复用
- [ ] 数据卷备份与恢复
- [ ] 容器删除后卷是否保留
- [ ] 卷与容器内已有文件的关系

### 5. 常见存储问题

- [ ] 数据未持久化
- [ ] 挂载路径错误
- [ ] 挂载覆盖了镜像内原有文件
- [ ] 文件读写权限不足
- [ ] 数据卷无法删除
- [ ] 宿主机与容器文件内容不一致
- [ ] Docker 磁盘空间不足

## 实操任务

- [ ] 使用 Bind Mount 挂载配置文件
- [ ] 使用 Bind Mount 挂载日志目录
- [ ] 创建并挂载命名卷
- [ ] 删除容器并重新创建，验证数据保留
- [ ] 实验只读挂载
- [ ] 测试文件权限问题
- [ ] 完成 Volume 备份与恢复
- [ ] 使用 `docker system df` 查看磁盘使用

## 阶段验收

- [ ] 能解释三类常用存储挂载方式
- [ ] 能判断哪些数据会随着容器删除而丢失
- [ ] 能正确挂载文件与目录
- [ ] 能独立进行数据持久化和恢复
- [ ] 能排查常见挂载与权限错误

---

# 九、阶段 6：Docker Compose 多容器编排

## 阶段目标

使用 Docker Compose 管理多个相互依赖的容器服务。

### 1. Compose 基础

- [ ] Docker Compose 的作用
- [ ] Dockerfile 与 Compose 的区别
- [ ] Compose Project
- [ ] Compose Service
- [ ] Service 与 Container 的关系
- [ ] `compose.yaml` 文件
- [ ] YAML 基本语法
- [ ] Docker Compose V2 与旧版 `docker-compose` 的区别

### 2. Compose 核心字段

- [ ] `services`
- [ ] `image`
- [ ] `build`
- [ ] `container_name`
- [ ] `ports`
- [ ] `expose`
- [ ] `environment`
- [ ] `env_file`
- [ ] `volumes`
- [ ] `networks`
- [ ] `depends_on`
- [ ] `restart`
- [ ] `healthcheck`
- [ ] `command`
- [ ] `entrypoint`
- [ ] `profiles`
- [ ] `secrets` 基础概念

### 3. Compose 命令

- [ ] `docker compose up`
- [ ] `docker compose up -d`
- [ ] `docker compose up -d --build`
- [ ] `docker compose down`
- [ ] `docker compose stop`
- [ ] `docker compose start`
- [ ] `docker compose restart`
- [ ] `docker compose ps`
- [ ] `docker compose logs`
- [ ] `docker compose exec`
- [ ] `docker compose run`
- [ ] `docker compose build`
- [ ] `docker compose pull`
- [ ] `docker compose config`

### 4. Compose 网络与存储

- [ ] Compose 默认网络
- [ ] 服务名解析
- [ ] 多服务之间的通信
- [ ] 自定义网络
- [ ] 网络隔离
- [ ] 命名卷
- [ ] Bind Mount
- [ ] 服务重建与数据持久化

### 5. 服务依赖与健康检查

- [ ] `depends_on` 的真实作用
- [ ] 容器启动不等于服务就绪
- [ ] `healthcheck`
- [ ] `service_healthy`
- [ ] 服务启动顺序
- [ ] 依赖服务异常后的处理
- [ ] Compose 重建与重启的区别

### 6. 配置管理

- [ ] `.env` 文件
- [ ] 变量插值
- [ ] `environment` 与 `env_file`
- [ ] 开发环境与部署环境配置
- [ ] Compose 多文件配置
- [ ] 配置验证
- [ ] 敏感信息管理基础

## 实操任务

- [ ] 编写双服务 Compose 文件
- [ ] 完成 Spring Boot 与数据库容器的连接
- [ ] 配置自定义网络
- [ ] 为数据库配置命名卷
- [ ] 为后端配置环境变量
- [ ] 为服务添加健康检查
- [ ] 验证服务启动顺序和就绪状态
- [ ] 修改镜像并重建服务
- [ ] 对比 `stop`、`down`、`up` 的效果

## 阶段验收

- [ ] 不看模板编写基本 Compose 配置
- [ ] 理解 Service、Container、Network、Volume 的关系
- [ ] 能正确使用环境变量
- [ ] 能处理服务依赖与健康检查
- [ ] 能独立管理多容器项目

---

# 十、阶段 7：Docker 工程化部署

## 阶段目标

将已有后端与 AI 应用转换为可部署、可维护的 Docker 服务。

### 1. Spring Boot 容器化

- [ ] Maven 项目打包
- [ ] JAR 与 Docker 镜像的关系
- [ ] Java 21 运行环境
- [ ] Spring Boot Dockerfile
- [ ] 多阶段构建
- [ ] `application.yml` 配置
- [ ] Spring Profiles
- [ ] 环境变量注入
- [ ] 数据库连接配置
- [ ] 容器端口映射
- [ ] Java 进程与容器主进程
- [ ] JVM 内存与容器内存限制
- [ ] Spring Boot 健康检查
- [ ] Spring Boot 优雅停止

### 2. Python/FastAPI 容器化

- [ ] Python 基础镜像选择
- [ ] `requirements.txt`
- [ ] Python 依赖安装
- [ ] Dockerfile 编写
- [ ] Uvicorn 启动
- [ ] `0.0.0.0` 监听地址
- [ ] FastAPI 接口发布
- [ ] API Key 等敏感配置的传递
- [ ] 非 root 用户运行
- [ ] 健康检查
- [ ] 异常日志与容器退出

### 3. 部署配置

- [ ] 开发与生产配置分离
- [ ] 环境变量与配置文件
- [ ] 日志输出
- [ ] 数据持久化
- [ ] 端口暴露控制
- [ ] 重启策略选择
- [ ] 镜像版本管理
- [ ] 容器资源限制

### 4. Linux 服务器部署

- [ ] 将镜像部署到 Linux
- [ ] 镜像拉取与导入
- [ ] Linux 文件权限
- [ ] 服务器端口与防火墙
- [ ] 容器开机恢复
- [ ] 日志查看
- [ ] 服务器环境与本地环境差异
- [ ] Linux amd64/arm64 架构差异

## 实操任务

- [ ] 完成 Spring Boot 项目容器化
- [ ] 使用 Docker 部署 Spring Boot API
- [ ] 完成 Python/FastAPI 项目容器化
- [ ] 验证 `/health` 接口
- [ ] 通过环境变量切换配置
- [ ] 重建镜像并部署更新版本
- [ ] 验证容器异常退出和恢复
- [ ] 将至少一个服务部署到 Linux 环境

## 阶段验收

- [ ] 能独立将 Spring Boot 项目打包并部署
- [ ] 能独立将 FastAPI 项目容器化
- [ ] 能正确处理配置、网络、日志、权限和持久化
- [ ] 能将本地开发成果迁移到另一运行环境
- [ ] 能完成一次完整的部署与更新

---

# 十一、阶段 8：日志、监控、排障与资源管理

## 阶段目标

形成系统化的 Docker 故障排查能力。

### 1. 日志管理

- [ ] 标准输出与标准错误
- [ ] `docker logs`
- [ ] `--tail`
- [ ] `-f`
- [ ] `--since`
- [ ] Docker 日志驱动基础
- [ ] `json-file`
- [ ] `local`
- [ ] 日志轮转
- [ ] 应用日志与容器日志

### 2. 资源监控

- [ ] `docker stats`
- [ ] `docker top`
- [ ] `docker inspect`
- [ ] `docker events`
- [ ] CPU 使用情况
- [ ] 内存使用情况
- [ ] CPU 配额限制
- [ ] 内存限制
- [ ] OOM 基本概念
- [ ] OOMKilled 状态识别
- [ ] 磁盘空间使用情况

### 3. 容器故障排查

- [ ] 容器无法启动
- [ ] 容器启动后立即退出
- [ ] 容器反复重启
- [ ] 主进程异常退出
- [ ] 启动命令错误
- [ ] 镜像缺少依赖
- [ ] 文件路径错误
- [ ] 环境变量缺失
- [ ] 文件权限错误

### 4. 网络故障排查

- [ ] 端口冲突
- [ ] 端口映射错误
- [ ] 监听地址错误
- [ ] DNS 解析失败
- [ ] 容器不在同一个网络
- [ ] 容器无法连接宿主机
- [ ] Connection refused
- [ ] Connection timeout

### 5. 存储故障排查

- [ ] 数据卷挂载失败
- [ ] 挂载覆盖文件
- [ ] 数据未持久化
- [ ] 文件权限不足
- [ ] 容器磁盘空间不足
- [ ] 日志占用过大

### 6. 排障方法论

- [ ] 先确认现象
- [ ] 再检查容器状态
- [ ] 查看日志
- [ ] 查看退出码
- [ ] 检查配置
- [ ] 检查网络与挂载
- [ ] 定位根本原因
- [ ] 验证修复结果
- [ ] 整理故障记录

## 实操任务

独立设计并解决以下故障：

- [ ] Dockerfile 启动命令错误
- [ ] Python 程序异常退出
- [ ] Spring Boot 端口无法访问
- [ ] 两个容器无法互相连接
- [ ] 环境变量错误
- [ ] 数据卷挂载错误
- [ ] 文件读写权限异常
- [ ] 内存不足导致容器退出
- [ ] Compose 服务启动顺序错误
- [ ] 容器磁盘使用过高

## 阶段验收

- [ ] 能依据日志和状态判断故障类型
- [ ] 不依赖 AI 直接给答案完成基础排障
- [ ] 能解释故障产生的根本原因
- [ ] 能提出并验证修复方案
- [ ] 能形成可复用的排障记录

---

# 十二、阶段 9：Docker 安全与构建优化

## 阶段目标

理解 Docker 工程实践中的安全风险，能够优化镜像与容器配置。

### 1. 容器安全

- [ ] root 与非 root 用户
- [ ] Dockerfile `USER`
- [ ] 最小权限原则
- [ ] Linux capabilities 基础
- [ ] `--privileged` 的风险
- [ ] 容器文件系统只读配置
- [ ] 运行时权限控制
- [ ] 镜像来源可信性
- [ ] 容器隔离的安全边界

### 2. 镜像安全

- [ ] 最小化基础镜像
- [ ] Alpine 与 Debian slim 的区别
- [ ] 固定镜像版本
- [ ] 镜像漏洞扫描
- [ ] Docker Scout
- [ ] Trivy
- [ ] 依赖安全更新
- [ ] 镜像中的敏感信息泄露
- [ ] 避免将密码写入 Dockerfile

### 3. 镜像构建优化

- [ ] 构建上下文优化
- [ ] `.dockerignore`
- [ ] 构建缓存优化
- [ ] 多阶段构建
- [ ] 基础镜像选择
- [ ] 减少无关依赖
- [ ] 缓存挂载
- [ ] 镜像大小分析
- [ ] 构建时间分析

### 4. Docker 资源与清理

- [ ] 镜像空间占用
- [ ] 构建缓存空间占用
- [ ] 容器与数据卷清理
- [ ] `docker system df`
- [ ] `docker system prune`
- [ ] `docker image prune`
- [ ] `docker container prune`
- [ ] `docker volume prune`
- [ ] 清理命令的数据风险

## 实操任务

- [ ] 将一个 root 运行的容器改为非 root
- [ ] 为项目添加合适的 `.dockerignore`
- [ ] 优化镜像体积
- [ ] 对比不同构建策略的效果
- [ ] 为镜像执行漏洞扫描
- [ ] 移除镜像中的敏感配置
- [ ] 安全清理无用容器和镜像

## 阶段验收

- [ ] 能识别常见 Docker 配置安全风险
- [ ] 能优化镜像构建
- [ ] 能解释镜像安全和容器安全的区别
- [ ] 能避免危险的权限配置和数据清理操作

---

# 十三、阶段 10：综合项目与持续交付

## 阶段目标

将前面所有知识串联起来，形成完整的 Docker 工程实践能力。

### 项目一：Spring Boot 后端容器化

**项目目标：独立完成一个后端服务的 Docker 部署。**

#### 功能要求

- [ ] 使用 Spring Boot 开发 API
- [ ] 使用 Maven 构建 JAR
- [ ] 编写 Dockerfile
- [ ] 使用多阶段构建
- [ ] 发布 HTTP 端口
- [ ] 注入运行环境变量
- [ ] 配置应用日志
- [ ] 设置健康检查
- [ ] 设置重启策略
- [ ] 使用非 root 用户
- [ ] 完成容器重新部署

#### 验收

- [ ] 完成独立构建与部署
- [ ] 接口可正常访问
- [ ] 能解释从 Dockerfile 到容器启动的整个过程
- [ ] 能定位并解决一次实际部署故障

### 项目二：Spring Boot + 数据库多容器部署

**项目目标：使用 Docker Compose 构建完整后端应用运行环境。**

#### 功能要求

- [ ] 后端独立容器
- [ ] 数据库独立容器
- [ ] 自定义 Docker 网络
- [ ] 通过服务名访问数据库
- [ ] 配置数据库数据卷
- [ ] 配置环境变量
- [ ] 编写 Compose 文件
- [ ] 配置健康检查和服务依赖
- [ ] 验证重建后的数据持久化
- [ ] 完成故障模拟与恢复

#### 验收

- [ ] 一条 Compose 命令启动所有服务
- [ ] 容器之间正常通信
- [ ] 数据库持久化有效
- [ ] 可以独立重建应用服务
- [ ] 能排查常见网络与配置故障

### 项目三：Python/FastAPI AI Agent 容器化

**项目目标：面向实际 AI 项目完成容器构建和运行。**

#### 功能要求

- [ ] 编写 FastAPI 服务
- [ ] 实现 `/health` 接口
- [ ] 编写 Dockerfile
- [ ] 管理 Python 依赖
- [ ] 使用非 root 用户
- [ ] 配置 API 环境变量
- [ ] 正确监听 `0.0.0.0`
- [ ] 发布服务端口
- [ ] 处理标准输出日志
- [ ] 验证容器退出和异常恢复
- [ ] 构建 linux/amd64 镜像
- [ ] 验证容器在目标环境中正常运行

#### ANIC 项目扩展

- [ ] 独立构建 Sender / Receiver 镜像
- [ ] 验证容器启动命令
- [ ] 验证 HTTP 接口与健康检查
- [ ] 检查 UDP 通信相关的容器网络配置
- [ ] 检查目标平台架构兼容性
- [ ] 验证非 root 运行要求
- [ ] 排查容器内外网络行为差异
- [ ] 整理最终镜像构建与运行文档

### 项目四：Docker 镜像持续交付

**项目目标：了解应用从代码提交到镜像交付的过程。**

#### 学习内容

- [ ] Docker Registry
- [ ] Docker Hub 镜像仓库
- [ ] 镜像命名与版本策略
- [ ] Git 与镜像构建
- [ ] GitHub Actions 基础
- [ ] 自动构建镜像
- [ ] 镜像推送
- [ ] 基于版本标签部署
- [ ] 镜像更新与回滚
- [ ] 基本 CI/CD 流程

#### 验收

- [ ] 能独立构建并推送镜像
- [ ] 能拉取指定版本的镜像
- [ ] 能完成一次镜像更新部署
- [ ] 能回滚到之前的可用版本
- [ ] 能解释从代码到部署的完整流程

---

# 十四、长期复习与能力巩固

## 1. 基础命令复习

- [ ] 能快速写出常用 `docker run` 命令
- [ ] 能区分镜像命令与容器命令
- [ ] 能正确操作容器生命周期
- [ ] 能使用日志和 inspect 分析问题
- [ ] 能管理 Docker 网络
- [ ] 能管理 Docker 数据卷
- [ ] 能使用 Docker Compose

## 2. Dockerfile 复习

- [ ] 不看资料编写基础 Dockerfile
- [ ] 能解释 `RUN`、`CMD`、`ENTRYPOINT`
- [ ] 能解释镜像层与缓存机制
- [ ] 能使用多阶段构建
- [ ] 能为 Spring Boot 与 Python 选择合适镜像

## 3. 网络与存储复习

- [ ] 能区分宿主机与容器内的 localhost
- [ ] 能解释端口映射
- [ ] 能理解自定义 Docker 网络
- [ ] 能通过容器名或 Compose 服务名完成通信
- [ ] 能区分 Bind Mount 与 Volume
- [ ] 能排查常见网络和挂载故障

## 4. 工程实践复习

- [ ] 能独立部署一个 Spring Boot 项目
- [ ] 能独立部署一个 Python API 项目
- [ ] 能使用 Compose 管理多容器应用
- [ ] 能进行容器健康检查
- [ ] 能分析和修复容器启动失败
- [ ] 能安全更新镜像和容器

---

# 十五、阶段完成标准

每个阶段使用统一验收方式。

### 第一步：知识理解

能够准确解释关键概念，分清容易混淆的知识点。

### 第二步：命令与配置

能够根据需求独立编写命令、Dockerfile 或 Compose 配置。

### 第三步：独立实操

不依赖完整示例，自己完成指定任务，验证运行结果。

### 第四步：故障排查

能够判断常见错误的原因，提出修复方案并实际验证。

### 第五步：总结归档

整理以下内容：

- 本阶段掌握的知识
- 自己完成的实际操作
- 遇到的问题
- 曾经理解错误的知识点
- 后续需要复习的内容

**五项完成后，该阶段才标记为已掌握。**

---

# 十六、当前学习进度与下一步

## 1. 已有学习基础

此前已经复习过：

- 镜像和容器的基本关系
- Docker 常用命令
- Dockerfile 基础指令
- `docker run` 常用参数
- 环境变量与程序配置
- 容器生命周期
- 主进程与容器退出
- 退出码
- 自动重启策略
- Docker 网络中的 localhost
- 自定义网络下的容器名称通信
- 端口映射基础

这些属于**已有理论学习与部分练习记录**，不能直接认定为通过所有阶段的实操验收。

## 2. 当前正式学习位置

**阶段 4：Docker 网络（学习中）**

当前已讲解并练习：

- [x] 容器内 localhost 的含义（概念练习）
- [x] `host.docker.internal` 的基本用途（概念练习）
- [x] 自定义 Docker 网络中的容器名称通信（概念练习）
- [x] 容器间通信与端口发布的区别（概念练习）
- [x] 宿主机端口与容器端口的区别（概念练习）
- [x] IPv4 回环地址的端口绑定（概念练习）

尚未确认完成：

- [ ] Docker 网络命令的独立实操
- [ ] 实际创建自定义 bridge 网络
- [ ] 实际完成两个容器的网络通信
- [ ] `network connect` / `disconnect`
- [ ] Docker DNS 与网络隔离实验
- [ ] Docker 网络故障排查
- [ ] 阶段 4 综合验收

## 3. 接下来的学习任务

先从当前进度继续：

**Docker 网络创建 → 查看网络 → 容器连接网络 → 容器通信验证 → 网络隔离 → 网络故障排查。**

完成阶段 4 后，再检查阶段 0～3 中尚未验收的实操项目，并逐项补齐。

不需要为了遵循阶段编号，把已经理解的内容全部重新听一遍；但对于尚未实际验证的操作，需要通过实操确认掌握。

---

# 十七、最终能力验收

当全部阶段完成后，应能够做到：

- [ ] 从零建立 Docker 开发环境
- [ ] 理解 Docker 镜像、容器、网络与存储机制
- [ ] 独立完成 Dockerfile 编写与优化
- [ ] 独立完成 Spring Boot 容器化部署
- [ ] 独立完成 Python/FastAPI 容器化部署
- [ ] 独立使用 Docker Compose 管理项目
- [ ] 独立配置容器网络和持久化存储
- [ ] 独立处理常见容器异常
- [ ] 理解 Docker 安全、资源限制和镜像优化
- [ ] 能将镜像部署到 Linux 环境
- [ ] 能完成 AI Agent 项目的 Docker 打包与交付
- [ ] 能清晰解释 Docker 在后端开发和部署中的工作流程

**最终成果：不仅会运行 Docker 命令，而且能够独立使用 Docker 完成实际工程项目的容器化、部署、维护和排障。**