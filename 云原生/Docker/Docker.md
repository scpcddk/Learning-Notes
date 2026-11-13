# 🐳 Docker 学习笔记（面向 Spring Boot 项目）

---

## 0. 🚀 新手极简速查

> 如果你忘了 Dockerfile 和 Compose 到底是干啥的，只看这一块就够了

---

### 0.1 **Dockerfile 是什么？**

- **一句话定义**：Dockerfile 是一份 **“自动化的安装说明书”**，Docker 照着它就能自动生成一个干净的镜像
- **核心指令（记住这4个就够了）**：

  | 指令 | 作用 | 大白话 |
  | :--- | :--- | :--- |
  | **FROM** | 指定基础镜像 | “基于谁” |
  | **WORKDIR** | 设置工作目录 | “进哪个文件夹干活” |
  | **COPY** | 复制文件到镜像 | “把代码拷进去” |
  | **CMD** | 容器启动时执行的命令 | “开机后自动运行啥” |

> **注意**：`COPY` 是构建时复制文件，`CMD` 是运行时才执行

- **什么时候用**：你写了一个项目（Spring Boot / Python / Node），需要把它打包成镜像去部署

- **怎么用**：

  ```bash
  docker build -t my-app .   # 打包成镜像
  docker run -p 8080:8080 my-app  # 运行
  ```

- **示例**：

  ```dockerfile
  # 1. 基础环境：我用 Python 3.9 官方系统当底子
  FROM python:3.9
  
  # 2. 设置工作目录：进到容器里的 /app 文件夹干活
  WORKDIR /app
  
  # 3. 复制文件：把电脑里的代码复制进容器里
  COPY . .
  
  # 4. 启动命令：容器运行时，执行 python app.py
  CMD ["python", "app.py"]
  ```

---

### 0.2 **Docker Compose 是什么？**

- **一句话定义**：当你需要**同时管理多个容器**（如：后端 + MySQL + Redis）时，Compose 是一张 **“一键启动全家桶的布局图”**
- **核心字段（记住这4个就够了）**：

  | 关键词 | 大白话解释 | 举例 |
  | :--- | :--- | :--- |
  | **services** | 声明“我要开几个店” | 下面缩进的都是你要启动的容器 |
  | **build** | “现场用 Dockerfile 现做” | `build: .` 代表用当前目录的 Dockerfile 现打包 |
  | **image** | “去网上直接下载现成的” | `image: redis` 代表直接去官方仓库拽一个 Redis 过来用，连 Dockerfile 都不用写！ |
  | **depends_on** | “启动顺序” | 短语法只控制启动顺序，不等待数据库就绪；需 healthcheck 与 service_healthy，应用仍应支持重试 |

- **`docker-compose.yml`示例**（注意后缀是 `.yml`）：

  ```yaml
  # 使用当前 Compose Specification，无需 version 字段
  # 2. 核心：定义所有需要启动的“服务”
  services:
  
    # 服务A：你的 Python 后端（基于刚才的 Dockerfile）
    web:
      build: .                # 意思是：“去当前目录找 Dockerfile 来构建”
      ports:
        - "5000:5000"         # 把容器的 5000 映射到电脑的 5000
      depends_on:
        - db                  # 告诉工头：“先启动数据库，再启动我”
  
    # 服务B：数据库（不用写 Dockerfile，直接从网上下载官方现成的）
    db:
      image: postgres:15      # 意思是：“去网上下载 Postgres 15 这个成品”
      environment:            # 设置数据库的密码（环境变量）
        POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:?请先设置数据库密码}"
      ports:
        - "5432:5432"         # 把数据库端口暴露出来
  ```

> [!IMPORTANT]
> **重点来了**：在 Compose 文件里，`web` 服务想连接 `db` 服务，**直接在代码里写主机名 `db` 就行**（比如 `postgresql://db:5432`）。Compose 会自动帮你们配好网络，你完全不用管 IP 地址！

- **使用**：在 `docker-compose.yml` 文件所在的目录，打开终端，敲：

  ```bash
  # 一键启动所有服务（-d 代表后台运行，像开机一样）
  docker compose up -d
  
  # 一键停止所有服务
  docker compose down
  
  # 查看所有服务的运行日志（看哪里报错）
  docker compose logs -f
  ```

- **什么时候用**：你的项目需要多个容器配合工作（比如后端要连数据库、缓存、AI模型等）

---

### 0.3 **它俩到底啥关系？**

| 对比项 | **Dockerfile** | **Docker Compose** |
| :--- | :--- | :--- |
| **管什么** | 管 **“怎么做”**（如何打包一个镜像） | 管 **“怎么跑”**（如何启动一堆镜像） |
| **文件类型** | 无后缀名，叫 `Dockerfile` | 叫 `docker-compose.yml` |
| **干活的** | 描述镜像构建过程；镜像可启动多个容器 | 负责同时管理和连接 N 个容器 |
| **是否必须** | 通常用于自定义镜像；使用现成镜像可不写 | **非必须**（但项目一复杂就是神器） |

> [!TIP]
> **“Dockerfile 负责把代码装进箱子（镜像），Compose 负责把箱子和数据库、Redis 一起通上电、插上网线（运行）”**

---

### 0.4 **菜鸟救急命令**（复制即用）

| 场景 | 命令 |
| :--- | :--- |
| 把 Dockerfile 打包成镜像 | `docker build -t my-app .` |
| 运行镜像 | `docker run -p 8080:8080 my-app` |
| 启动 compose 全家桶 | `docker compose up -d` |
| 关停 compose 全家桶 | `docker compose down` |
| 查看容器日志（找报错） | `docker logs 容器名 --tail 50` |
| 查看容器退出码 | `docker inspect 容器名 --format='{{.State.ExitCode}}'` |

---

## 1. **核心概念**

- **镜像（Image）**：只读模板，包含应用和运行时文件（如 `app.jar`、Java 21 和相关库），也可指定默认启动命令。
- **容器（Container）**：从镜像创建的实例，可启动、停止、删除。容器启动后，应用进程在其中执行。
- **镜像仓库（Repository）**：同名镜像及其标签的集合；Docker Hub 是托管仓库的注册服务（Registry）

### 1.1 容器化技术

**容器化**把应用、运行时、依赖和可随应用分发的配置打包进镜像。部署时，从镜像创建容器来运行应用。

#### 1.1.1 Spring Boot 应用怎么交付

| 交付方式 | 交付内容 | 目标机器需要准备 |
| :--- | :--- | :--- |
| 直接交付 JAR | `app.jar` | 版本匹配的 Java 运行时及其他系统依赖 |
| 交付容器镜像 | `app.jar`、Java 运行时和相关依赖 | 兼容的容器运行环境 |

同一镜像可以减少不同机器上的依赖版本差异。同一台 Linux 服务器也可以同时运行项目 A（Java 17）和项目 B（Java 21），因为两个容器各自使用镜像里的 Java。

> [!NOTE]
> 数据库连接等配置仍需按部署环境提供。MySQL 作为独立服务运行时，应用容器需要能访问它。

#### 1.1.2 `docker run` 如何启动应用

假设镜像 `my-java-app` 包含 Java 21 和 `app.jar`，启动命令为 `java -jar app.jar`。

```bash
docker run my-java-app
```

1. **准备镜像**。Docker 管理目标机器上的镜像文件，将解包后的镜像层用于容器文件系统。
2. **创建容器**。Docker 以只读镜像层为基础，默认给新容器添加自己的可写层。
3. **启动应用**。容器内的 Java 21 执行 `app.jar`。宿主机无需单独安装 Java。

[`docker run` 命令参考](https://docs.docker.com/reference/cli/docker/container/run/) · [镜像层与容器层](https://docs.docker.com/engine/storage/drivers/#container-and-layers)

#### 1.1.3 三种部署方式的资源开销

假设同一个 Spring Boot 应用使用相同的 Java 21 运行时、JVM 参数和负载。应用本身的 CPU 和内存用量通常相近，整机开销还取决于部署方式。

| 部署方式 | 运行环境的开销 |
| :--- | :--- |
| 在 Linux 上直接运行 | Java 进程直接使用宿主系统。 |
| 在 Docker 容器中运行 | Java 进程共享底层 Linux 内核，整机用量还包括 Docker 和容器相关开销。 |
| 在独立虚拟机中运行 | 整机用量还包括客户机内核和系统服务的开销。 |

假设 Java 应用直接运行时使用 600 MB 内存，仅凭这个数值无法推算容器中的内存用量。实际用量还受资源限制影响。把 Java 放进镜像，主要是为了隔离依赖、简化部署和复用交付产物。 [Docker 容器与虚拟机](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/#containers-versus-virtual-machines-vms)

> [!TIP]
> **共享镜像层节省的是磁盘空间。** 多个镜像可以复用相同的 Java 21 基础层。每个单独启动的 Java 应用仍有自己的 JVM 进程和堆。比较磁盘占用时，还要算上镜像里的基础系统库。 [Docker 镜像层与容器层](https://docs.docker.com/engine/storage/drivers/#container-and-layers)

在 Windows 上使用 Docker Desktop 的 WSL 2 后端时，比较整机资源占用要计入 WSL 2 和 Docker Desktop 的开销。 [Docker Desktop 的 WSL 2 后端](https://docs.docker.com/desktop/features/wsl/)

容器可以发布端口供外部访问，也可以挂载宿主机目录来读写文件。

#### 1.1.4 镜像怎么迁移

- **通过镜像仓库**。在源机器用 `docker push` 推送，再在兼容的目标机器用 `docker pull` 拉取。[镜像仓库与版本管理](镜像仓库与版本管理.md)
- **通过离线文件**。用 `docker save` 导出镜像归档，再在目标机器用 `docker load` 加载。

---

### 1.2 Docker 镜像是什么

#### 1.2.1 镜像里有哪些内容

以 Spring Boot 镜像 `my-java-app:1.0` 为例，镜像包含文件系统层和镜像配置。 [Docker 镜像基础](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)

| 组成 | 示例 |
| :--- | :--- |
| **文件系统层** | 基础系统文件和库、Java 21 可执行文件和运行库、`app.jar` |
| **镜像配置** | 工作目录 `/app`、默认启动命令 `java -jar app.jar`、环境变量默认值 |

Java 21 在镜像里以文件形式保存。容器启动时，才会按启动配置创建 Java 进程。见 [§1.1.2 `docker run` 如何启动应用](#112-docker-run-如何启动应用)。

#### 1.2.2 同一个镜像如何运行多个容器

从 `my-java-app:1.0` 可以创建多个容器。它们共享镜像的只读层，各自拥有容器可写层。每个容器启动后运行自己的 Java 进程。 [Docker 镜像层与容器层](https://docs.docker.com/engine/storage/drivers/#container-and-layers)

> [!NOTE]
> **写入发生在各自的可写层。** 假设容器 A 执行 `touch /tmp/test.txt`，并把文件写入自己的可写层，那么使用同一镜像的容器 B 不会自动看到它。需要共享文件时，可以把同一个卷挂载到两个容器中。

---

### 1.3 Docker 解决了哪些问题

#### 1.3.1 环境一致性、隔离与交付

| 问题 | Docker 的做法 |
| :--- | :--- |
| **环境一致性** | 把 Spring Boot 应用和 Java 21 一起打包。不同机器部署同一镜像时，使用镜像里相同的运行时和依赖。 |
| **环境隔离** | 让两个容器分别使用各自的 Java 17 和 Java 21。容器有各自的进程和文件系统视图，同时共享底层 Linux 内核。 |
| **部署与迁移** | 把构建好的镜像交付给另一台兼容的机器，再创建容器运行。镜像可通过仓库分发，也可通过文件迁移。 |

[§1.1.4 镜像怎么迁移](#114-镜像怎么迁移) · [Docker 容器基础](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)

#### 1.3.2 应用仍需要外部服务

Spring Boot 镜像可以包含正确的 Java 21 和 `app.jar`。如果应用启动时必须连接 MySQL，数据库也要在配置的地址和端口上提供服务，而且应用容器需要能访问它。

> [!NOTE]
> 假设应用启动日志同时出现 `Communications link failure` 和 `Connection refused`，说明这次 TCP 连接被拒绝。可以检查 MySQL 是否已启动并监听目标端口，以及 Spring Boot 使用的数据库地址、端口和容器网络是否正确。应用如果在启动时必须连上数据库，就可能因此启动失败。 [Linux `connect(2)`](https://man7.org/linux/man-pages/man2/connect.2.html)

#### 1.3.3 Spring Boot 和 MySQL 分开部署

Spring Boot 容器运行应用镜像，MySQL 容器运行官方 `mysql` 镜像。两个容器加入同一个自定义 Docker 网络。若 Compose 中的数据库服务名是 `mysql`，应用可通过 `mysql:3306` 连接数据库。 [§4.3 自定义网络](#43-自定义网络) · [MySQL 官方镜像](https://hub.docker.com/_/mysql)

- **独立更新**。发布新版 Spring Boot 时，只需替换应用容器，继续使用原有的 MySQL 容器。
- **独立扩展**。可以增加 Spring Boot 实例，让它们连接同一个 MySQL 服务。 [Docker 多容器应用](https://docs.docker.com/get-started/docker-concepts/running-containers/multi-container-applications/)
- **数据持久化**。给 MySQL 的数据目录 `/var/lib/mysql` 挂载命名卷。即使将来重建 MySQL 容器，也可以挂载原来的卷来保留数据。 [§4.2.2 命名卷](#422-命名卷方便备份与共享) · [Docker 卷的生命周期](https://docs.docker.com/engine/storage/volumes/#a-volumes-lifecycle)

> [!NOTE]
> 两个容器可以独立更新，服务之间仍有依赖。MySQL 停止后，Spring Boot 的数据库操作可能失败。

---

### 1.4 Docker 容器与虚拟机的区别

#### 1.4.1 应用使用哪个内核

| 部署方式 | 应用运行环境 | 应用使用的内核 |
| :--- | :--- | :--- |
| Ubuntu 虚拟机 | 虚拟化软件提供虚拟硬件，客户机启动自己的操作系统和系统服务 | Ubuntu 客户机的 Linux 内核 |
| Linux 上的 Docker 容器 | 应用进程使用镜像提供的用户态文件，例如命令、库和 Java 运行时 | 运行这些容器的 Linux 宿主机内核 |

多个容器共享一个内核，启动容器时只需启动配置好的应用进程及其所需进程。虚拟机还需要启动客户机操作系统。资源比较见 [§1.1.3 三种部署方式的资源开销](#113-三种部署方式的资源开销) · [Docker 容器与虚拟机](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/#containers-versus-virtual-machines-vms)。

#### 1.4.2 Ubuntu 和 Alpine 容器

> [!NOTE]
> 同一台 Linux 服务器上的 Ubuntu 容器和 Alpine 容器各自使用基础镜像提供的命令和库。两者的进程由同一个宿主 Linux 内核运行。

#### 1.4.3 Windows 上的 WSL 2 与 Docker

**系统调用**是应用程序向操作系统内核请求服务的接口，例如打开文件、读取数据或创建进程。以 Python 读取文本文件为例，Python 运行时会通过系统调用向内核发出文件操作请求。 [Linux 系统调用手册](https://man7.org/linux/man-pages/man2/syscalls.2.html)

```python
with open("test.txt", "r", encoding="utf-8") as f:
    print(f.read())
```

| 版本 | Linux 程序的请求如何处理 | 运行环境 |
| :--- | :--- | :--- |
| WSL 1 | 兼容层把 Linux 系统调用转换为 Windows 内核能够处理的操作。 | Windows 内核和兼容层 |
| WSL 2 | Linux 内核直接处理 Linux 系统调用。 | 由 Windows 管理的轻量级虚拟机 |

[Microsoft WSL 版本对比](https://learn.microsoft.com/zh-cn/windows/wsl/compare-versions)

> [!NOTE]
> **WSL 1 兼容的是系统调用。** `ls` 仍作为 Linux 程序执行。它请求读取目录时，兼容层将该请求转换为 Windows 内核能够处理的操作，再把结果返回给 `ls`。

Docker Desktop 使用 WSL 2 后端时，Docker Engine 在专用的 `docker-desktop` WSL 发行版中运行。Docker 创建的 Linux 容器共享 WSL 2 虚拟机里的 Linux 内核。 [Docker Desktop 的 WSL 2 后端](https://docs.docker.com/desktop/features/wsl/)

> [!NOTE]
> 同一个 Docker Engine 启动三个 Linux 容器时，三个容器里的应用进程共用 WSL 2 提供的 Linux 内核。虚拟化发生在 Windows 与 WSL 2 之间。

---

### 1.5 Docker 的典型使用场景

| 场景 | 示例 | Docker 提供的便利 |
| :--- | :--- | :--- |
| **本地开发** | 为 Spring Boot 项目启动指定版本的 MySQL 或 Redis | 减少宿主机上的安装步骤，按项目管理服务版本和启动配置。 |
| **应用部署** | 将 Spring Boot 和 Java 运行时打包为镜像，再部署到 Linux 服务器 | 用同一镜像交付应用及其运行环境，便于部署和迁移。 |
| **自动化测试** | 在 CI 中为集成测试启动临时数据库 | 每次测试可从指定的镜像和初始化配置开始，任务结束后清理容器。 |

> [!NOTE]
> **MySQL 运行数据需要单独迁移。** 在新服务器上使用同一镜像可以启动相同版本的 MySQL。运行后创建的 `school` 数据库保存在数据目录里。迁移时可以备份并恢复数据库，也可以通过数据卷迁移数据。 [§4.2.2 命名卷](#422-命名卷方便备份与共享) · [Docker 卷的生命周期](https://docs.docker.com/engine/storage/volumes/#a-volumes-lifecycle)

[CI/CD 笔记 §8.1 测试数据库](../DevOps/CI-CD.md#81-ci-数据库必须独立准备) · [GitHub Actions 服务容器](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)

---

### 1.6 容器与宿主机的关系

在原生 Linux 上，容器里的进程由宿主机内核调度，使用宿主机的 CPU、内存和磁盘。以一台 8 核 CPU、16 GB 内存、500 GB 磁盘的服务器为例，MySQL 和 Spring Boot 容器都从这台服务器获取资源，宿主机上的其他进程也会占用这些资源。

| 资源 | 容器如何使用 |
| :--- | :--- |
| CPU | 宿主机内核为容器进程分配 CPU 时间。 |
| 内存 | MySQL 缓冲区和 Spring Boot 的 JVM 堆都会占用宿主机内存。 |
| 磁盘 | 镜像、容器可写层和本地数据卷都会占用宿主机的磁盘空间。 |

默认情况下，容器在宿主机内核允许的范围内按需使用 CPU 和内存。部署时可以为单个容器设置上限，以减少资源竞争对其他服务的影响。 [Docker 资源限制](https://docs.docker.com/engine/containers/resource_constraints/)

---

## 2. 常用命令

### 2.1 **基础命令**

| **命令** | **功能** | **示例** |
| --------------------- | -------------------------------- | ------------------------------------------ |
| `docker run` | ==**创建并启动**一个新容器，在其中运行命令== | `docker run -d ubuntu` |
| `docker ps` | ==**列出**当前**正在运行**的容器== | `docker ps` |
| `docker ps -a` | 列出**所有**容器（包括已停止的容器） | `docker ps -a` |
| `docker build` | ==使用`Dockerfile`**构建镜像**== | `docker build -t my-image .` |
| `docker images` | **列出**本地存储的所有**镜像** | `docker images` |
| `docker pull` | 从 Docker 仓库**拉取镜像** | `docker pull ubuntu` |
| `docker push` | 将**镜像推送**到 Docker 仓库 | `docker push my-image` |
| `docker exec` | ==在运行的容器中**执行命令**== | `docker exec -it container_name bash` |
| `docker stop` | **停止**一个或多个容器 | `docker stop container_name` |
| `docker start` | **启动**已停止的容器 | `docker start container_name` |
| `docker restart` | **重启**一个容器 | `docker restart container_name` |
| `docker rm` | **删除**一个或多个**容器** | `docker rm container_name` |
| `docker rmi` | **删除**一个或多个**镜像** | `docker rmi my-image` |
| `docker logs` | ==**查看容器的日志**== | `docker logs container_name` |
| `docker inspect` | 获取容器或镜像的详细信息 | `docker inspect container_name` |
| `docker exec -it` | 进入容器的交互式终端 | `docker exec -it container_name /bin/bash` |
| `docker network ls` | 列出所有`Docker`**网络** | `docker network ls` |
| `docker volume ls` | 列出所有`Docker`**卷** | `docker volume ls` |
| `docker compose up -d` | 后台启动多容器应用（从 docker-compose.yml 文件） | `docker compose up -d` |
| `docker compose down` | 停止并删除由`docker-compose`启动的容器、网络等 | `docker compose down` |
| `docker compose logs -f` | 实时查看`compose`服务日志 | `docker compose logs -f backend` |
| `docker compose restart` | 重启`compose`中的某个服务 | `docker compose restart backend` |
| `docker compose ps` | 列出`compose`管理的容器状态 | `docker compose ps` |
| `docker info` | 显示`Docker`系统的**详细信息** | `docker info` |
| `docker version` | 显示`Docker`客户端和守护进程的**版本信息** | `docker version` |
| `docker stats` | 显示容器的实时资源使用情况 | `docker stats` |
| `docker login` | 登录`Docker`仓库 | `docker login` |
| `docker logout` | 登出`Docker`仓库 | `docker logout` |
| `docker system prune -a` | 删除已停止的容器、未使用的网络、未被容器引用的镜像和未使用的构建缓存（慎用） | `docker system prune -a` |

常用`docker run`选项:

- `-t`：在新容器内指定一个伪终端或终端
  **阅读提示**　从指定上下文构建镜像，输出标签供后续启动或发布使用。

  ```text
  docker build -t
          ↑
       tag 镜像，给镜像设置名称/标签
  
  docker run -t
          ↑
       TTY 终端
  ```
- `-i`：允许你对容器内的标准输入 (STDIN) 进行交互
- `-d`：后台运行
- **`-p 宿主机端口:容器端口`**：端口映射
- `-p 绑定IP:宿主机端口:容器端口`：指定宿主机绑定地址（三段式）
  ```bash
  # 只允许宿主机本机访问，外网/局域网连不进来
  docker run -d -p 127.0.0.1:8081:8080 myapp:1.0

  # 等价于 -p 8081:8080，绑定所有网卡
  docker run -d -p 0.0.0.0:8081:8080 myapp:1.0
  ```
- `--name`：指定容器名称
- `-v 宿主机目录:容器目录`：挂载数据卷（持久化）
- `--restart=always`：自动重启
- `-m 512m`：内存硬限制
- `--cpus="1.5"`：CPU 配额限制
- `--network`：指定容器加入哪个网络
  ```bash
  # 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
  docker run -d --name backend --network app-net myapp:1.0
  ```
  - `--network bridge`：默认桥接网络
  - `--network host`：共享宿主机网络栈（端口可能冲突）
  - `--network none`：禁用网络，只有 lo
  - `--network container:容器名`：和另一个容器共享网络栈
  - `--network 自定义网络名`：加入自定义 bridge 网络，可用容器名/服务名互访
  - `--network-alias`：给容器在自定义网络里加别名
    ```bash
    # 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
    docker run -d --network app-net --network-alias db mysql:8
    ```

---

### 2.2 🧩 镜像深度操作

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| `docker save` | ==将一个或多个镜像**导出**为归档文件（`.tar`）== | `docker save -o myapp.tar nginx:alpine` |
| **`docker load`** | ==从 `save` 导出的归档文件中**导入镜像**（离线迁移核心）== | `docker load -i myapp.tar` |
| `docker tag` | 给本地镜像打上新的**标签**（仓库名+版本） | `docker tag nginx:latest myrepo/nginx:v1.0`(`latest`本质上就是一个默认 tag，只是一个名字，不保证它真的就是最新版本) |
| `docker history` | 查看镜像的**构建历史**（分层细节与大小） | `docker history ubuntu:22.04 --no-trunc` |
| `docker import` | 从压缩包或 URL **导入**内容创建镜像（配合 `export`） | `docker import myapp.tar.gz myapp:imported` |
| `docker export` | 将**容器**当前文件系统**导出**为快照（扁平化，丢失历史） | `docker export container_id > snapshot.tar` |
| `docker commit` | 将容器的改动**提交**为新的镜像（生产环境不推荐，调试用） | `docker commit -m "fix bug" container_id newimg:v2` |

---

### 2.3 ⚙️ 容器高级控制与调试

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| `docker attach` | 连接容器主进程的标准输入/输出/错误流，不会启动新 shell | `docker attach container_name` |
| `docker pause` | **暂停**容器内所有进程（挂起状态，不占用 CPU） | `docker pause container_name` |
| `docker unpause` | 恢复被暂停的容器 | `docker unpause container_name` |
| `docker wait` | 阻塞当前终端，直到容器停止并返回退出码 | `docker wait container_name` |
| `docker rename` | 重命名一个已有的容器 | `docker rename old_name new_name` |
| `docker update` | 动态更新运行中容器的资源限制（CPU/内存） | `docker update --cpus=2 -m 4G container_name` |
| `docker kill` | **强制杀死**容器进程（发送 SIGKILL，比 `stop` 更粗暴） | `docker kill container_name` |
| `docker container prune` | 删除所有**已停止**的容器（释放磁盘空间） | `docker container prune -f` |

---

### 2.4 📂 文件与数据交互（主机↔容器）

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| **`docker cp`** | ==在**主机与容器**之间**拷贝**文件/目录== | `docker cp ./local.txt container:/app/` |
| `docker diff` | 查看容器**文件系统**相对于镜像的改动（新增/修改/删除） | `docker diff container_name` |

---

### 2.5 🌐 网络与卷（Volume）精细管理

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| `docker network create` | 创建自定义网络（如 bridge/overlay） | `docker network create --driver bridge my-net` |
| `docker network inspect` | 查看网络的详细配置与连接的容器 | `docker network inspect my-net` |
| `docker network rm` | 删除一个网络 | `docker network rm my-net` |
| `docker network prune` | 删除所有未被使用的网络 | `docker network prune` |
| `docker volume create` | 创建一个数据卷 | `docker volume create my-data` |
| `docker volume inspect` | 查看数据卷的挂载路径与元数据 | `docker volume inspect my-data` |
| `docker volume rm` | 删除一个数据卷 | `docker volume rm my-data` |
| `docker volume prune` | 默认删除未使用的匿名卷；加 `-a` 才包含未使用的命名卷 | `docker volume prune -f` |

---

### 2.6 🔍 监控、排障与系统信息

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| `docker top` | 查看容器内运行的**进程列表**（类似 Linux `top`） | `docker top container_name` |
| `docker events` | 实时打印 Docker 守护进程的**事件流**（调试利器） | `docker events --since 1h` |
| `docker port` | 查看容器**端口映射**情况 | `docker port container_name` |
| `docker system df` | 查看 Docker 磁盘占用详情（镜像/容器/卷/构建缓存） | `docker system df -v` |
| `docker system prune` | 清理停止的容器、未使用网络、悬空镜像和未使用构建缓存；`-a` 扩大镜像清理范围，卷需另加 `--volumes` | `docker system prune -f` |
| `docker system events` | （同 `docker events`，系统级事件查看） | `docker system events` |

---

### 2.7 🧩 Docker Compose 深度补充

| 命令 | 功能 | 示例 |
| :--- | :--- | :--- |
| `docker compose exec` | 在 compose 运行中的服务里执行命令（与 `run` 区分） | `docker compose exec web bash` |
| `docker compose build` | 重新构建 compose 中的服务镜像 | `docker compose build --no-cache web` |
| `docker compose pull` | 拉取 compose 服务依赖的最新镜像 | `docker compose pull backend` |
| `docker compose stop` | 停止 compose 服务（不删除容器） | `docker compose stop web` |
| `docker compose rm` | 删除 compose 已停止的服务容器 | `docker compose rm -v web` |
| `docker compose config` | 验证并查看合并后的 compose 配置（排错用） | `docker compose config` |

---

### 2.8 ⚠️ 排障口诀

- **`save` 配 `load`**：镜像迁移；**`export` 配 `import`**：文件系统快照（别混用）。
- **`stop` 优雅退出** vs **`kill` 暴力强杀**：前者给进程 SIGTERM，后者直接 SIGKILL。
- **`commit` 救急不救穷**：生产环境请用 `Dockerfile + build` 实现可复现构建。

---

### 2.9 **调试排障命令**

| 场景 | 命令 |
| ------ | ------ |
| 查看容器实时资源 | `docker stats 容器名` |
| 查看容器进程 | `docker top 容器名` |
| 查看容器详细配置 | `docker inspect 容器名` |
| 查看容器内文件系统变化 | `docker diff 容器名` |
| 复制容器内文件到宿主机 | `docker cp 容器名:/app/logs .` |
| 进入已停止的容器 | `docker commit 容器名 debug-image && docker run --rm -it --entrypoint sh debug-image` |
| 查看容器退出码 | `docker inspect 容器名 --format='{{.State.ExitCode}}'` |

---

### 2.10 🚑 **排障三板斧**（容器起不来时别慌）

遇到容器启动失败或崩溃，按这个顺序查，**能解决 95% 的问题**：

1. **看日志（第一板斧）**：
   ```bash
   # 用容器状态和近期日志确认启动进度及失败位置。
   docker logs 容器名 --tail 100
   ```
   - 看到 `Exception` 或 `Error` 直接定位代码报错
   - 如果啥都没有，加 `-f` 实时盯着

2. **看退出码（第二板斧）**：
   ```bash
   # 读取容器或镜像的实际状态，和配置中的期望值对照。
   docker inspect 容器名 --format='{{.State.ExitCode}}'
   ```
   - **0**：正常退出（没事）
   - **1**：程序内部报错（去看日志）
   - **137**：通常表示 SIGKILL；可能是 OOM、手动 kill 或停止超时。结合 `.State.OOMKilled` 和宿主机日志定位
   - **143**：通常表示因 SIGTERM 退出；是否完成优雅停机还需检查应用日志和请求结果

3. **进入容器内部（第三板斧）**：
   ```bash
   # 如果是 Alpine 系统（没有 bash），用 sh
   docker exec -it 容器名 sh
   # 进去后执行 ps aux 看进程，或者 curl localhost:端口 看通不通
   ```

---

## 3. **Dockerfile 模板**（Spring Boot 项目 + AI 扩展）

### 3.1 **常用指令详解**

| 指令 | 作用 | 示例 |
| ------ | ------ | ------ |
| **FROM** | **指定基础镜像** | `FROM eclipse-temurin:21-jre-alpine` |
| **WORKDIR** | **设置工作目录**，后续指令在此目录下执行 | `WORKDIR /app` |
| **COPY** | **从宿主机复制文件**到镜像（推荐用 COPY，不用 ADD） | `COPY target/*.jar app.jar` |
| **RUN** | 构建 ==镜像== 时**执行命令**（安装依赖、配置） | `RUN apk add --no-cache curl` |
| **ENV** | **设置环境变量**，运行时可用 `-e` 覆盖 | `ENV JAVA_OPTS="-Xmx512m"` |
| **EXPOSE** | 声明容器内**服务端口**（仅文档作用） | `EXPOSE 8080` |
| **CMD** | ==容器== 启动时的**默认命令**，可被 `docker run` 后面的命令覆盖（如果需要运行命令过多，可以创建**启动脚本**，直接运行脚本，如：CMD ["./start.sh"]） | `CMD ["java", "-jar", "app.jar"]` |
| **ENTRYPOINT** | 容器启动时的**入口命令**，可用 `--entrypoint` 覆盖；exec 形式可接收追加参数 | `ENTRYPOINT ["java", "-jar", "app.jar"]` |

#### 3.1.1 `-e`

`-e`: **把配置放在环境变量里，启动容器时再传入**

- **例如**：
  **阅读提示**　用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。

  ```
  docker run -d \
    --name backend \
    -e APP_ENV=production \
    -e DB_HOST=mysql \
    -e DB_PORT=3306 \
    myapp:1.0
  ```
- `-e` 设置的环境变量，是提供给容器内部运行的程序使用的，不是直接修改宿主的环境变量
- `os.getenv()`：根据变量名，从当前程序的环境变量中取值
  ```python
  # 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
  import os
  
  db_host = os.getenv("DB_HOST")
  print(db_host)
  ```
  - `db_host`：Python 代码里的变量名，你自己定义的，可以用小写。
  - `"DB_HOST"`：要从环境变量中查找的名称，字符串，必须和环境变量名称对应
  - **左边变量名可以自己起；右边环境变量名必须匹配**
  - 找不到对应名称时，默认返回 `None`

- 如果你想检查容器实际配置了哪些环境变量，可以使用：
  **阅读提示**　在已运行容器内执行命令，命令使用容器里的路径和网络。

  ```
  docker exec backend printenv
  ```
  - 查看指定变量：

    **阅读提示**　在已运行容器内执行命令，命令使用容器里的路径和网络。

    ```
    docker exec backend printenv DB_HOST
    ```
  - 没设置时 `printenv` 则通常不输出内容。

#### 3.1.2 CMD vs ENTRYPOINT

- **CMD**：适合可有可无的默认参数，运行`docker run image command`会直接替换`CMD`
- **ENTRYPOINT**：固定启动命令，后面传参会追加到`ENTRYPOINT`之后
- **组合**：`ENTRYPOINT ["java", "-jar", "app.jar"]` + `CMD ["--server.port=8080"]`，运行`docker run my-image --server.port=9090`可覆盖`CMD`

- Spring Boot 容器推荐：**只用 ENTRYPOINT**，避免误覆盖启动命令

---

### 3.2 镜像分层与构建缓存

- Docker 镜像采用**分层存储**（Union File System），`RUN`、`COPY`、`ADD` 等通常生成文件系统层，`ENV`、`CMD`、`ENTRYPOINT` 等主要设置镜像元数据，并非每条指令都产生文件系统层

  ```dockerfile
  FROM eclipse-temurin:21-jre-alpine    # 引入基础镜像已有的层
  WORKDIR /app                          # 设置工作目录
  COPY target/app.jar app.jar           # 复制 JAR，内容变化影响后续缓存
  ENTRYPOINT ["java", "-jar", "app.jar"] # 设置启动元数据
  ```

- **关键规则：**
  - 镜像层是**只读**的。创建容器时，Docker 默认在镜像层上添加容器自己的**可写层**。 [Docker 镜像层与容器层](https://docs.docker.com/engine/storage/drivers/#container-and-layers)
  - 某一层变化后，**该层之后的所有层缓存失效**，需重新构建
  - **优化技巧**：将变化频率低的指令放前面（如依赖安装），变化高的放后面（如代码 COPY）

- **最佳实践示例（优化前 vs 优化后）：**

  ```dockerfile
  # ❌ 优化前：每次代码改动都重新下载依赖
  COPY . .                              # 代码和 pom.xml 一起复制
  RUN mvn clean package -DskipTests     # 依赖+编译，缓存完全失效
  
  # ✅ 优化后：先复制 pom.xml 下载依赖，利用缓存
  COPY pom.xml .
  RUN mvn dependency:go-offline -B      # 依赖层缓存，pom.xml 不变就不重新下载
  COPY src ./src
  RUN mvn clean package -DskipTests -B  # 只有 src 变化时才重新编译
  ```

---

### 3.3 多阶段构建（Java 项目瘦身必用）

构建阶段用 Maven + JDK 编译，运行阶段只保留 JRE，最终镜像不包含源码和构建工具

```dockerfile
# 第一阶段：构建
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B       # 缓存依赖，加速后续构建
COPY src ./src
RUN mvn clean package -DskipTests -B

# 第二阶段：运行
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

- 效果：镜像体积可从 600MB+ 降至 200MB 以内

---

### 3.4 ⭐ 实战模板：Spring Boot 生产级 Dockerfile（已修复优雅停机）

> **相比网上多数教程，本模板特别修复了 `docker stop` 时无法优雅停机的致命缺陷。**

```dockerfile
# ========== 构建阶段 ==========
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build

# 先复制 pom，利用 Docker 缓存（就算依赖多，第一次慢，后面秒构建）
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 复制源码并打包
COPY src ./src
RUN mvn clean package -DskipTests -B

# ========== 运行阶段 ==========
FROM eclipse-temurin:21-jre-alpine

# 1. 安装 curl + 设置时区
RUN apk add --no-cache curl tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# 2. 创建非 root 用户（安全必备）
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app

# 3. 从构建阶段复制 jar
COPY --from=builder /build/target/*.jar app.jar
RUN chown -R app:app /app
USER app

# 4. JVM 参数（容器感知）
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=60.0"

EXPOSE 8080

# 5. 使用 exec 替换 sh 进程，让 Java 能正常接收 SIGTERM 信号（实现优雅停机）
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar app.jar"]

# 6. 配合 Spring Boot 2.3+ 的 /actuator/health/readiness
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health/readiness || exit 1
```

> **配套 Spring Boot 配置（务必在 application.yml 中开启）：**
> ```yaml
> # 管理端点和指标配置分开控制，暴露范围按采集或排障需要设置。
> management:
>   endpoint:
>     health:
>       probes:
>         enabled: true
>   endpoints:
>     web:
>       exposure:
>         include: health
> server:
>   shutdown: graceful
> spring:
>   lifecycle:
>     timeout-per-shutdown-phase: 30s
> ```

**构建与运行**：

```bash
# 构建镜像
docker build -t my-spring-app .
# 运行容器（停机等待时间大于 Spring 的 30s 超时）
docker run -d --stop-timeout 40 -p 8080:8080 --name spring-app -m 512m --cpus="1.5" my-spring-app
```

---

### 3.5 实战模板 2：Python AI 推理服务 Dockerfile

```dockerfile
FROM python:3.10-slim

# 健康检查与时区文件需要这些系统包
RUN apt-get update && apt-get install -y --no-install-recommends curl tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# 先复制依赖文件，利用缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制模型和代码
COPY model/ /app/model/
COPY app.py .

EXPOSE 5000

# 非 root 运行
RUN groupadd -r app && useradd -r -g app app && chown -R app:app /app
USER app

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["python", "app.py"]
```

> 生产环境建议用 Gunicorn 替换 `python app.py`，稳定性更好

---

### 3.6 镜像优化技巧速查

- **选对基础镜像**：优先用 `alpine` 或 `slim` 版本，避免 `latest` 完整版；固定具体版本号，如 `eclipse-temurin:21.0.2_13-jre-alpine`
- **多阶段构建**：`Java/Go`项目必备，编译与运行分离
- **合并 RUN 命令**：减少层数，及时清理缓存和临时文件
  
```dockerfile
# FROM 选择基础环境，RUN 在构建时执行，CMD 或 ENTRYPOINT 决定容器启动方式。
RUN apt-get update && apt-get install -y --no-install-recommends 包名 \
    && rm -rf /var/lib/apt/lists/*
```

- **添加 `.dockerignore`**：排除 `.git`、`target`（仅容器内多阶段构建时）、`node_modules` 等无关内容（参考下方 3.8）
- **固定依赖版本**：Python 用 `requirements.txt` 锁定版本，Maven 在 `pom.xml` 中明确版本号

---

### 3.7 镜像安全扫描

构建后检查漏洞：

```bash
# Docker 内置（需登录）
docker scout cves my-spring-app

# 开源工具 Trivy
trivy image my-spring-app
```

**安全加固建议：**

- 使用非 root 用户（已有 ✅）
- 最小化基础镜像（alpine/slim，已有 ✅）
- 固定基础镜像版本，避免 `latest`
- 只暴露必要的端口
- 只复制必要的文件（配合 `.dockerignore`）

---

### 3.8 📁 `.dockerignore` 文件（按构建方式选择）

在项目根目录新建 `.dockerignore`，防止把本地编译产物和 IDE 配置误拷进镜像，导致缓存失效或镜像臃肿：

```dockerignore
# 适用于容器内多阶段 Maven 构建；外部构建后 COPY JAR 时不可排除该产物
target/
*.jar
*.war

# IDE 和版本控制
.git/
.gitignore
.idea/
*.iml
.vscode/
.DS_Store

# 日志和本地配置
logs/
*.log
application-local.yml
application-dev.yml

# 系统文件
Thumbs.db
```

---

外部先运行 Maven、再 `COPY target/app.jar` 时，删除上面三条产物排除规则；也可在末尾添加 `!target/`、`!target/app.jar` 放行目标文件。

## 4. Docker Compose 模板（多服务编排）

### 4.1 **核心字段说明**

| 字段 | 作用 | 示例 |
| ------ | ------ | ------ |
| **services** | **定义所有服务** | 见下方完整示例 |
| **ports** | 端口**映射**，`宿主机端口:容器端口` | `"8080:8080"` |
| **volumes** | 数据挂载，**持久化存储** | `./logs:/app/logs` |
| **networks** | 自定义**网络**，容器间通过服务名互访 | `networks: - app-net` |
| **depends_on** | **控制启动顺序**（不保证内部服务就绪） | `depends_on: - inference` |
| **restart** | **重启**策略，推荐 `unless-stopped` | `restart: unless-stopped` |
| **environment** | 注入**环境变量** | `SPRING_PROFILES_ACTIVE=docker` |

**重启策略**：

| 策略               | 含义                                  |
| ---------------- | ----------------------------------- |
| `no`             | 默认，不自动重启                            |
| `on-failure`     | 主进程以非零退出码结束时自动重启                    |
| `always`         | 容器退出后通常自动重启                         |
| `unless-stopped` | 自动重启，但主动停止的容器不会在 Docker 守护进程重启后自动恢复 |

**阅读提示**　用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。

```
docker run -d \
  --name backend \
  --restart unless-stopped \
  myapp:1.0
```
**阅读提示**　该参数决定容器退出后的重启条件，适用于容器创建或策略更新。

```
--restart unless-stopped
```
容器退出后，Docker 通常会尝试自动重启它；如果你主动停止容器，则不会自动重新启动，直到你再次手动启动它

---

### 4.2 数据挂载三种方式

#### 4.2.1 匿名卷（Docker 自动管理）

```yaml
volumes:
  - /app/logs        # 容器内路径
```

#### 4.2.2 命名卷（方便备份与共享）

```yaml
volumes:
  - app-logs:/app/logs
# 上面的 volumes 是服务内片段；下方顶层声明需另写在 Compose 根节点：
```

```yaml
volumes:
  app-logs:          # 顶层声明
```

#### 4.2.3 宿主机目录挂载（开发调试最常用）

```yaml
volumes:
  - ./logs:/app/logs           # 日志持久化
  - ./models:/app/model        # 模型热更新，无需重建镜像
```

---

### 4.3 自定义网络

Compose 默认创建 `bridge` 网络，同一网络内的容器可直接用**服务名**作为域名通信。

```yaml
# 按服务组织容器。容器之间用服务名和容器端口访问。
networks:
  app-net:
    driver: bridge

services:
  backend:
    networks:
      - app-net
  inference:
    networks:
      - app-net
```

此时 `backend` 内可用 `http://inference:5000/predict` 访问 AI 服务。

---

### 4.4 网络模式详解

| 模式 | 说明 | 适用场景 |
| ------ | ------ | ---------- |
| **bridge** | 默认模式，容器通过 veth pair 连接 docker0 网桥，NAT 访问外网 | 大多数单机容器通信 |
| **host** | 容器共享宿主机网络栈，无 NAT 隔离 | 性能敏感（如高并发网关），但端口会冲突 |
| **none** | 禁用所有网络，仅 lo 回环 | 完全隔离场景 |
| **container** | 与另一个容器共享网络栈 | 如 Sidecar 模式（日志采集、代理） |
| **自定义 bridge** | 用户创建的 bridge 网络，支持 DNS 自动解析（服务名互访） | docker compose 默认使用 |

```bash
# 查看容器网络详情
docker inspect 容器名 | grep -A 20 "NetworkSettings"

# 默认 bridge 通常使用 docker0；自定义 bridge 使用各自网桥，网段以 inspect 为准
# 自定义网络额外提供：内置 DNS，容器间可用服务名 ping 通
```

#### 4.4.1 回环地址（loopback）与容器网络

**回环地址**就是机器跟自己通信用的地址，常见写法：

| 写法 | 说明 |
| :--- | :--- |
| `127.0.0.1` | IPv4 回环地址 |
| `localhost` | 通常解析到 `127.0.0.1`（也可能解析到 `::1`） |
| `::1` | IPv6 回环地址 |
| `lo` | Linux 回环网卡 |

特点：**只有本机自己能访问，外部机器访问不到**。

#### 4.4.2 关键：默认 bridge 网络中的容器有独立回环地址

- **宿主机**的 `127.0.0.1` = 宿主机自己
- **默认 bridge 容器内**的 `127.0.0.1` = **容器自己**，不是宿主机；host 模式或 container 模式会共享相应网络栈

所以容器里写：

```python
# 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
connect(host="localhost", port=3306)   # ❌ 连的是容器自己，不是宿主机 MySQL
```

如果 MySQL 装在宿主机上，容器内用 `localhost` 是**连不到的**，因为容器里的 `localhost` 指向容器自身。

#### 4.4.3 宿主机 MySQL 只监听 127.0.0.1 时，容器也连不上

即使改用 `host.docker.internal`，如果宿主机 MySQL 配置为：

```ini
# 把键值放到读取该配置的文件或节中，核对覆盖顺序与重启后的生效值。
bind-address = 127.0.0.1
```

它只接受**宿主机本机回环**的连接，容器通过网桥过来的流量会被拒绝。需要改成：

```ini
# 把键值放到读取该配置的文件或节中，核对覆盖顺序与重启后的生效值。
bind-address = 0.0.0.0
```

也可绑定容器可达的宿主机网卡地址。`bind-address` 接受监听地址，不接受 CIDR 网段；网段访问限制需配置防火墙及 MySQL 账号授权。以上是原生 Linux bridge 场景，Docker Desktop 的宿主机转发机制不同，应实测。

#### 4.4.4 `-p` 绑定 IP：`127.0.0.1` vs `0.0.0.0`

`-p` 除了两段式，还可以写成三段式：

```text
-p 绑定IP:宿主机端口:容器端口
```

| 写法 | 绑定地址 | 谁能访问 |
| :--- | :--- | :--- |
| `-p 8081:8080` | `0.0.0.0:8081` | 本机 + 局域网 + 外网（受防火墙影响） |
| `-p 0.0.0.0:8081:8080` | `0.0.0.0:8081` | 同上，显式写法 |
| `-p 127.0.0.1:8081:8080` | `127.0.0.1:8081` | **只有宿主机自己** |
| `-p 192.168.1.10:8081:8080` | 指定网卡 IP | 绑定该宿主机地址，来源是否可达取决于路由和防火墙 |

注意：**这里的 `127.0.0.1` 是宿主机的绑定地址**，不是容器内的回环。含义是：

> 只在宿主机回环口监听 8081，转发到容器 8080。外网和局域网都连不进来。

示例：

```bash
# 只允许宿主机本机访问，外网/局域网连不进来
docker run -d --name backend -p 127.0.0.1:8081:8080 myapp:1.0

# 等价于 -p 8081:8080，绑定所有网卡
docker run -d --name backend -p 0.0.0.0:8081:8080 myapp:1.0
```

**安全实践：**

```bash
# ❌ 数据库端口直接暴露到所有网卡，风险高
docker run -d -p 3306:3306 mysql:8

# ✅ 只允许宿主机访问数据库
docker run -d -p 127.0.0.1:3306:3306 mysql:8
```

- 后端 API 要对局域网/外网提供服务：用 `-p 8080:8080`
- 数据库、Redis、管理后台等只给本机用：用 `-p 127.0.0.1:端口:端口`

Compose 中等价写法：

```yaml
ports:
  - "127.0.0.1:3306:3306"   # 只绑回环
  - "8080:8080"             # 绑所有网卡
```

#### 4.4.5 一句话区分

| 你在哪 | `localhost` / `127.0.0.1` 指谁 |
| :--- | :--- |
| 宿主机终端 | 宿主机自己 |
| 容器内部 | 容器自己 |
| 容器想连宿主机 | 用 `host.docker.internal`（Mac/Win 默认，Linux 加 `extra_hosts`） |
| 容器想连另一个容器 | 用**容器名/服务名**，不是 `localhost` |
| `-p 127.0.0.1:8081:8080` | 宿主机只在回环口监听，**只有本机能访问** |
| `-p 8081:8080` | 宿主机绑 `0.0.0.0`，**外部也能访问** |

#### 4.4.6 容器如何访问宿主机服务（host.docker.internal）

如果 MySQL / Redis 安装在**宿主机**上，而不是 Compose 里的服务，那么容器内**不能用 `localhost` 或 `127.0.0.1`**，因为容器里的 `localhost` 指容器自己。

**此时应使用**：

```python
# 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
connect(host="host.docker.internal", port=3306)
```

**或 Spring Boot 配置**：

```yaml
# 按层级合并到对应配置位置，保持缩进并核对引用的服务、端口或文件。
spring:
  datasource:
    url: jdbc:mysql://host.docker.internal:3306/mydb
```

**说明**：

| 环境 | 是否需要额外配置 |
| :--- | :--- |
| Windows / Mac Docker Desktop | 默认支持 `host.docker.internal` |
| Linux | 需要在 Compose 服务中加 `extra_hosts` |
| 宿主机 MySQL | 原生 Linux bridge 下须监听容器可达的宿主机地址，并配置防火墙及账号权限；Docker Desktop 需按其转发机制验证 |

**Linux 下 Compose 配置**：

```yaml
# 按服务组织容器。容器之间用服务名和容器端口访问。
services:
  backend:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**单独 `docker run` 时等价写法**：

```bash
# 用指定镜像创建容器，核对启动参数、宿主端口和挂载位置。
docker run --add-host=host.docker.internal:host-gateway ...
```

> [!warning] **注意区分**：
> 
> - **连接宿主机上的 MySQL**：`host.docker.internal:3306`
> - **连接 Compose 里的 MySQL 服务**：`mysql:3306`，其中 `mysql` 是服务名
> - **容器自身**：`localhost:3306`，当前容器自己

#### 4.4.7 `docker run --network` 用法补充

`docker network create` 只是**创建网络**，容器要加入网络，需要在 `docker run` 时用 `--network` 指定。

```bash
# 1. 创建自定义 bridge 网络
docker network create app-net

# 2. 启动容器并加入该网络
docker run -d --name backend --network app-net myapp:1.0

# 3. 同一网络内的另一个容器，可直接用容器名访问
docker run -d --name mysql --network app-net \
  -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:?请先设置数据库密码}" mysql:8
```

此时 `backend` 容器内可以直接连接：

**阅读提示**　从指定客户端连接 MySQL，先核对主机、端口、账号和目标库。

```text
mysql:3306
```

因为自定义 bridge 网络自带 DNS 解析，容器名就是主机名。

> [!tip]
> **同一个自定义 Docker 网络中的容器，通常不需要通过 `-p` 就能相互访问监听中的服务**

**常见 `--network` 取值**：

| 写法 | 含义 | 注意 |
| :--- | :--- | :--- |
| `--network bridge` | 默认桥接网络 | 默认网络下容器名不能直接 DNS 解析，推荐自定义网络 |
| `--network host` | 共享宿主机网络栈 | 容器端口就是宿主机端口，容易冲突 |
| `--network none` | 无网络 | 只有回环口，完全隔离 |
| `--network container:xxx` | 与 `xxx` 容器共享网络栈 | Sidecar / 代理场景 |
| `--network app-net` | 加入自定义网络 | 同网络内容器名可互访 |

**补充命令**：

```bash
# 把已运行容器连接到另一个网络
docker network connect app-net backend

# 把容器从网络断开
docker network disconnect app-net backend
```

Compose 中等价写法不是 `--network`，而是在服务下写：

```yaml
# 按服务组织容器。容器之间用服务名和容器端口访问。
services:
  backend:
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

> [!note] 一句话区分
> 
> - `docker network create app-net`：**建网络**
> - `docker run --network app-net ...`：**让容器加入网络**
> - `docker network connect app-net 容器名`：**给已运行容器补加网络**
> - Compose 里：**用 `networks:` 字段**，不是 `--network`

---

### 4.5 ⭐ 完整编排模板：Spring Boot + AI 推理服务

- **相比网上多数模板，本模板额外兼容了新旧版本 Compose 的资源限制，并修复了 Linux 下无法访问宿主机的问题**

```yaml
services:
  backend:                        # Spring Boot 后端
    build: ./backend              # Dockerfile 所在目录
    container_name: spring-backend
    ports:
      - "8080:8080"
    environment:
      - JAVA_OPTS=-XX:+UseContainerSupport -XX:MaxRAMPercentage=60.0
      - SPRING_PROFILES_ACTIVE=docker
      - AI_SERVICE_URL=http://inference:5000/predict
    volumes:
      - ./logs/backend:/app/logs   # 日志持久化
    networks:
      - app-net
    restart: unless-stopped
    stop_grace_period: 40s
    depends_on:
      - inference
    
    # ⭐【新增】双保险资源限制（兼容新旧版本 Compose）
    mem_limit: 512m                # 老版本 Compose 靠这个
    cpus: '1.5'                    # 老版本 Compose 靠这个
    deploy:                        # 新版本 Compose 和 Swarm 模式靠这个
      resources:
        limits:
          cpus: '1.5'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

    # ⭐ 容器访问宿主机 MySQL/Redis 用：host.docker.internal:3306
    # Mac/Win 默认支持；Linux 靠下面这行映射 host-gateway
    extra_hosts:
      - "host.docker.internal:host-gateway"

    logging:                       # 日志轮转，防止撑满磁盘
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  inference:                      # AI 推理服务
    build: ./inference
    container_name: ai-inference
    ports:
      - "5000:5000"
    volumes:
      - ./models:/app/model        # 挂载模型，方便更新
      - ./logs/inference:/app/logs
    networks:
      - app-net
    restart: unless-stopped
    
    # 也给 AI 服务加个资源限制（防止它把内存吃光导致后端 OOM）
    mem_limit: 1g
    cpus: '1.0'
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  app-net:
    driver: bridge
```

---

### 4.6 生产环境配置（日志集中化）

```yaml
# 方案1：json-file 驱动 + 轮转（默认）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# 方案2：local 驱动（Docker 20.10+，性能更好）
logging:
  driver: "local"
  options:
    max-size: "10m"

# 方案3：发送到 Fluentd，再转发到 Elasticsearch
logging:
  driver: fluentd
  options:
    fluentd-address: "localhost:24224"
    tag: "docker.{{.Name}}"
```

---

### 4.7 **Compose 常用运维命令**

| 命令 | 作用 |
| ------ | ------ |
| `docker compose up -d` | **后台启动所有服务** |
| `docker compose down` | **停止并删除容器、网络** |
| `docker compose logs -f [服务名]` | **实时查看日志** |
| `docker compose restart [服务名]` | 重启指定服务 |
| `docker compose ps` | 查看所有服务状态 |
| `docker compose up -d --build` | 重新构建镜像并启动 |
| `docker compose build` | 只构建镜像，不启动 |

---

## 5. CI/CD 流水线示例（GitHub Actions）

CI/CD 的概念、GitHub Actions 基础、测试与发布条件见 [CI/CD 学习笔记](../DevOps/CI-CD.md)；镜像标签、仓库权限和版本追溯见 [镜像仓库与版本管理](镜像仓库与版本管理.md)。本节保留镜像发布模板。

```yaml
# .github/workflows/docker-build.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          
      - name: Build with Maven
        run: mvn --batch-mode --no-transfer-progress verify
        
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and Push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/my-spring-app:${{ github.sha }}
          # ⭐【新增】开启 GitHub Actions 原生缓存（第二次构建秒级完成）
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 6. 注意事项（落地必看）

| 注意事项 | 说明 |
| ---------- | ------ |
| **jar 名称固定** | 在 `pom.xml` 中设置 `<finalName>app</finalName>`，避免 `COPY target/*.jar` 多文件报错 |
| **多阶段构建优先** | 编译与运行分离，最终镜像不含 Maven 和源码，更小更安全 |
| **非 root 用户运行** | 务必创建普通用户并`USER`切换，降低安全风险 |
| **健康检查** | 先添加 spring-boot-starter-actuator 并启用 probes，让工具获取健康状态，标记健康状态；普通 Docker/Compose 不会仅因 unhealthy 自动重启 |
| **时区设置** | Alpine 默认 UTC，需手动设置为`Asia/Shanghai`或其他时区 |
| **日志与模型持久化** | 使用 volumes 挂载到宿主机，容器删除数据不丢 |
| **网络互联** | 自定义网络下用**服务名**互访，如 `inference:5000`，不要硬编码 IP |
| **资源限制** | 生产环境通过 `-m` / `--cpus` 或 Compose 的 `deploy.resources` 限制 CPU/内存，防止雪崩 |
| **访问宿主机** | 容器内 `localhost` 指向自身；连接宿主机 MySQL/Redis 用 `host.docker.internal:3306`。Windows/Mac 默认支持；Linux 需在 Compose 服务下加 `extra_hosts: - "host.docker.internal:host-gateway"`。若数据库本身是 Compose 服务，则直接用服务名，如 `mysql:3306`。 |
| **优雅停机** | Spring Boot 可配置 `server.shutdown=graceful`，配合 `SIGTERM` 保证请求处理完毕（已在本笔记 Dockerfile 中用 `exec` 修复 ✅） |
| **镜像安全更新** | 定期执行 `docker build --pull .` 拉取最新基础镜像；使用 `docker scout` 或 `trivy` 扫描漏洞 |
| **Compose 版本字段** | Docker Compose V2 不再需要 `version`，写上可能报警告，可移除 |
| **JVM 容器感知** | Java 8u191+ / 11+ 默认开启 `-XX:+UseContainerSupport`，JVM 自动读取 cgroup 内存限制；早期版本需显式配置，否则按宿主机总内存分配导致 OOM |
| **日志轮转** | 生产必配 `logging` 的 `max-size` 和 `max-file`，防止日志撑满磁盘 |
| **`.dockerignore` 必备** | 创建 `.dockerignore` 排除无关文件；多阶段构建可排除宿主机 target，外部构建再 COPY JAR 时须保留目标产物（已在本笔记 3.8 提供模板 ✅） |
| **`--network` 参数** | `docker run` 时用 `--network app-net` 加入自定义网络；同一自定义网络内容器可用**容器名**互访。`docker network connect/disconnect` 可动态连接/断开已运行容器。Compose 中用 `networks:` 字段，不是 `--network`。 |
| **回环地址** | `127.0.0.1` 和 `::1` 是回环地址，`localhost` 是主机名，`lo` 是回环接口，**只有本机自己能访问**。容器内的 `localhost` 指容器自己，不是宿主机；容器连宿主机 MySQL 要用 `host.docker.internal`，原生 Linux bridge 下宿主机 MySQL 需监听容器可达地址，并按需授权。 |

---

## 7. 参考与扩展

- 参考链接：[https://www.runoob.com/docker/docker-tutorial.html](https://www.runoob.com/docker/docker-tutorial.html)
- 网课链接：[https://www.bilibili.com/video/BV1s54y1n7Ev/](https://www.bilibili.com/video/BV1s54y1n7Ev/?spm_id_from=333.1387.favlist.content.click&vd_source=e0c0ad2a316e90d4078b1131e8182407)

---
