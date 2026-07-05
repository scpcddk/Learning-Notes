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
  docker build -t 我的应用名 .   # 打包成镜像
  docker run -p 8080:8080 我的应用名  # 运行
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
  | **depends_on** | “启动顺序” | 数据库必须先开，后端代码才能连上去，否则报错 |

- **`docker-compose.yml`示例**（注意后缀是 `.yml`）：

  ```yaml
  # 1. 版本号，基本固定写 3
  version: '3'
  
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
        POSTGRES_PASSWORD: 123456
      ports:
        - "5432:5432"         # 把数据库端口暴露出来
  ```

> [!IMPORTANT]
> **重点来了**：在 Compose 文件里，`web` 服务想连接 `db` 服务，**直接在代码里写主机名 `db` 就行**（比如 `postgresql://db:5432`）。Compose 会自动帮你们配好网络，你完全不用管 IP 地址！

- **使用**：在 `docker-compose.yml` 文件所在的目录，打开终端，敲：

  ```bash
  # 一键启动所有服务（-d 代表后台运行，像开机一样）
  docker-compose up -d
  
  # 一键停止所有服务
  docker-compose down
  
  # 查看所有服务的运行日志（看哪里报错）
  docker-compose logs -f
  ```

- **什么时候用**：你的项目需要多个容器配合工作（比如后端要连数据库、缓存、AI模型等）

---

### 0.3 **它俩到底啥关系？**

| 对比项 | **Dockerfile** | **Docker Compose** |
| :--- | :--- | :--- |
| **管什么** | 管 **“怎么做”**（如何打包一个镜像） | 管 **“怎么跑”**（如何启动一堆镜像） |
| **文件类型** | 无后缀名，叫 `Dockerfile` | 叫 `docker-compose.yml` |
| **干活的** | 只负责造出 1 个容器 | 负责同时管理和连接 N 个容器 |
| **是否必须** | **必须**（你要自定义环境就得写） | **非必须**（但项目一复杂就是神器） |

> [!TIP]
> **“Dockerfile 负责把代码装进箱子（镜像），Compose 负责把箱子和数据库、Redis 一起通上电、插上网线（运行）”**

---

### 0.4 **菜鸟救急命令**（复制即用）

| 场景 | 命令 |
| :--- | :--- |
| 把 Dockerfile 打包成镜像 | `docker build -t 我的应用名 .` |
| 运行镜像 | `docker run -p 8080:8080 我的应用名` |
| 启动 compose 全家桶 | `docker-compose up -d` |
| 关停 compose 全家桶 | `docker-compose down` |
| 查看容器日志（找报错） | `docker logs 容器名 --tail 50` |
| 查看容器退出码 | `docker inspect 容器名 --format='{{.State.ExitCode}}'` |

---

## 1. **核心概念**

- **镜像（Image）**：一个只读的**模板**，包含运行环境（如 JDK + 应用 jar）
- **容器（Container）**：镜像的**运行实例**，可启动、停止、删除，相互隔离
- **仓库（Repository）**：**存放镜像**的地方，如`Docker Hub`

---

## 2. 常用命令

### 2.1 **基础命令**

| **命令** | **功能** | **示例** |
| --------------------- | -------------------------------- | ------------------------------------------ |
| `docker run` | **启动**一个新的容器**并运行**命令 | `docker run -d ubuntu` |
| `docker ps` | **列出**当前正在运行的容器 | `docker ps` |
| `docker ps -a` | 列出所有容器（包括已停止的容器） | `docker ps -a` |
| `docker build` | 使用`Dockerfile`**构建镜像** | `docker build -t my-image .` |
| `docker images` | **列出**本地存储的所有**镜像** | `docker images` |
| `docker pull` | 从 Docker 仓库**拉取镜像** | `docker pull ubuntu` |
| `docker push` | 将**镜像推送**到 Docker 仓库 | `docker push my-image` |
| `docker exec` | 在运行的容器中**执行命令** | `docker exec -it container_name bash` |
| `docker stop` | **停止**一个或多个容器 | `docker stop container_name` |
| `docker start` | **启动**已停止的容器 | `docker start container_name` |
| `docker restart` | **重启**一个容器 | `docker restart container_name` |
| `docker rm` | **删除**一个或多个**容器** | `docker rm container_name` |
| `docker rmi` | **删除**一个或多个**镜像** | `docker rmi my-image` |
| `docker logs` | **查看容器的日志** | `docker logs container_name` |
| `docker inspect` | 获取容器或镜像的详细信息 | `docker inspect container_name` |
| `docker exec -it` | 进入容器的交互式终端 | `docker exec -it container_name /bin/bash` |
| `docker network ls` | 列出所有`Docker`**网络** | `docker network ls` |
| `docker volume ls` | 列出所有`Docker`**卷** | `docker volume ls` |
| `docker-compose up -d` | 后台启动多容器应用（从 docker-compose.yml 文件） | `docker-compose up -d` |
| `docker-compose down` | 停止并删除由`docker-compose`启动的容器、网络等 | `docker-compose down` |
| `docker-compose logs -f` | 实时查看`compose`服务日志 | `docker-compose logs -f backend` |
| `docker-compose restart` | 重启`compose`中的某个服务 | `docker-compose restart backend` |
| `docker-compose ps` | 列出`compose`管理的容器状态 | `docker-compose ps` |
| `docker info` | 显示`Docker`系统的**详细信息** | `docker info` |
| `docker version` | 显示`Docker`客户端和守护进程的**版本信息** | `docker version` |
| `docker stats` | 显示容器的实时资源使用情况 | `docker stats` |
| `docker login` | 登录`Docker`仓库 | `docker login` |
| `docker logout` | 登出`Docker`仓库 | `docker logout` |
| `docker system prune -a` | 清理未使用的镜像、容器、网络（慎用） | `docker system prune -a` |

- `-t`：在新容器内指定一个伪终端或终端
- `-i`：允许你对容器内的标准输入 (STDIN) 进行交互

**常用`docker run`选项**：

- `-d`：后台运行
- `-p 宿主机端口:容器端口`：端口映射
- `--name`：指定容器名称
- `-v 宿主机目录:容器目录`：挂载数据卷（持久化）
- `--restart=always`：自动重启
- `-m 512m`：内存硬限制
- `--cpus="1.5"`：CPU 配额限制

---

### 2.2 **调试排障命令**

| 场景 | 命令 |
| ------ | ------ |
| 查看容器实时资源 | `docker stats 容器名` |
| 查看容器进程 | `docker top 容器名` |
| 查看容器详细配置 | `docker inspect 容器名` |
| 查看容器内文件系统变化 | `docker diff 容器名` |
| 复制容器内文件到宿主机 | `docker cp 容器名:/app/logs .` |
| 进入已停止的容器 | `docker commit 容器名 临时镜像 && docker run -it 临时镜像 bash` |
| 查看容器退出码 | `docker inspect 容器名 --format='{{.State.ExitCode}}'` |

---

### 2.3 🚑 **排障三板斧**（容器起不来时别慌）

遇到容器启动失败或崩溃，按这个顺序查，**能解决 95% 的问题**：

1. **看日志（第一板斧）**：
   ```bash
   docker logs 容器名 --tail 100
   ```
   - 看到 `Exception` 或 `Error` 直接定位代码报错
   - 如果啥都没有，加 `-f` 实时盯着

2. **看退出码（第二板斧）**：
   ```bash
   docker inspect 容器名 --format='{{.State.ExitCode}}'
   ```
   - **0**：正常退出（没事）
   - **1**：程序内部报错（去看日志）
   - **137**：被系统强制 Kill（**绝大多数是因为内存超了**，赶紧去调大 `mem_limit` 或检查 JVM `-Xmx`）
   - **143**：收到了 SIGTERM 正常关机（说明优雅停机生效了）

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
| **RUN** | 构建时**执行命令**（安装依赖、配置） | `RUN apk add --no-cache curl` |
| **ENV** | **设置环境变量**，运行时可用 `-e` 覆盖 | `ENV JAVA_OPTS="-Xmx512m"` |
| **EXPOSE** | 声明容器内**服务端口**（仅文档作用） | `EXPOSE 8080` |
| **CMD** | 容器启动时的**默认命令**，可被 `docker run` 后面的命令覆盖 | `CMD ["java", "-jar", "app.jar"]` |
| **ENTRYPOINT** | 容器启动时的**入口命令**，不会被覆盖，但可追加参数 | `ENTRYPOINT ["java", "-jar", "app.jar"]` |

#### CMD vs ENTRYPOINT

- **CMD**：适合可有可无的默认参数，运行`docker run image command`会直接替换`CMD`
- **ENTRYPOINT**：固定启动命令，后面传参会追加到`ENTRYPOINT`之后
- **组合**：`ENTRYPOINT ["java", "-jar", "app.jar"]` + `CMD ["--server.port=8080"]`，运行`docker run my-image --server.port=9090`可覆盖`CMD`

- Spring Boot 容器推荐：**只用 ENTRYPOINT**，避免误覆盖启动命令

---

### 3.2 镜像分层与构建缓存

- Docker 镜像采用**分层存储**（Union File System），Dockerfile 中每条指令都会创建一个新的只读层

  ```dockerfile
  FROM eclipse-temurin:21-jre-alpine    # 第1层：基础镜像层
  WORKDIR /app                          # 第2层
  COPY target/app.jar app.jar           # 第3层（若jar变化，此层及之后缓存失效）
  RUN chmod +x app.jar                  # 第4层
  ENTRYPOINT ["java", "-jar", "app.jar"] # 第5层
  ```

- **关键规则：**
  - 层是**只读**的，容器启动时在最上层添加**可写层**
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
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -Xms256m -Xmx512m"

EXPOSE 8080

# 5. 使用 exec 替换 sh 进程，让 Java 能正常接收 SIGTERM 信号（实现优雅停机）
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar app.jar"]

# 6. 配合 Spring Boot 2.3+ 的 /actuator/health/readiness
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health/readiness || exit 1
```

> **配套 Spring Boot 配置（务必在 application.yml 中开启）：**
> ```yaml
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
# 运行容器（带资源限制）
docker run -d -p 8080:8080 --name spring-app -m 512m --cpus="1.5" my-spring-app
```

---

### 3.5 实战模板 2：Python AI 推理服务 Dockerfile

```dockerfile
FROM python:3.10-slim

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
RUN apt-get update && apt-get install -y --no-install-recommends 包名 \
    && rm -rf /var/lib/apt/lists/*
```

- **添加 `.dockerignore`**：排除 `.git`、`target`（若外部构建）、`node_modules` 等无关内容（参考下方 3.8）
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

### 3.8 📁 `.dockerignore` 文件（必须创建）

在项目根目录新建 `.dockerignore`，防止把本地编译产物和 IDE 配置误拷进镜像，导致缓存失效或镜像臃肿：

```dockerignore
# 构建产物（外部 Maven 已经打好了，禁止重复复制）
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

## 4. docker-compose 模板（多服务编排）

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

---

### 4.2 数据挂载三种方式

#### ① 匿名卷（Docker 自动管理）

```yaml
volumes:
  - /app/logs        # 容器内路径
```

#### ② 命名卷（方便备份与共享）

```yaml
volumes:
  - app-logs:/app/logs

volumes:
  app-logs:          # 顶层声明
```

#### ③ 宿主机目录挂载（开发调试最常用）

```yaml
volumes:
  - ./logs:/app/logs           # 日志持久化
  - ./models:/app/model        # 模型热更新，无需重建镜像
```

---

### 4.3 自定义网络

Compose 默认创建 `bridge` 网络，同一网络内的容器可直接用**服务名**作为域名通信。

```yaml
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
| **自定义 bridge** | 用户创建的 bridge 网络，支持 DNS 自动解析（服务名互访） | docker-compose 默认使用 |

```bash
# 查看容器网络详情
docker inspect 容器名 | grep -A 20 "NetworkSettings"

# 容器间通信本质：通过 docker0 网桥（172.17.0.1/16）转发
# 自定义网络额外提供：内置 DNS，容器间可用服务名 ping 通
```

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
      - JAVA_OPTS=-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -Xms256m -Xmx512m
      - SPRING_PROFILES_ACTIVE=docker
      - AI_SERVICE_URL=http://inference:5000/predict
    volumes:
      - ./logs/backend:/app/logs   # 日志持久化
    networks:
      - app-net
    restart: unless-stopped
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

    # ⭐【新增】Linux 用户访问宿主机 MySQL/Redis 的神器（Mac/Win 默认支持 host.docker.internal）
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
| `docker-compose up -d` | **后台启动所有服务** |
| `docker-compose down` | **停止并删除容器、网络** |
| `docker-compose logs -f [服务名]` | **实时查看日志** |
| `docker-compose restart [服务名]` | 重启指定服务 |
| `docker-compose ps` | 查看所有服务状态 |
| `docker-compose up -d --build` | 重新构建镜像并启动 |
| `docker-compose build` | 只构建镜像，不启动 |

---

## 5. CI/CD 流水线示例（GitHub Actions）

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
      
      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          
      - name: Build with Maven
        run: mvn clean package -DskipTests
        
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and Push
        uses: docker/build-push-action@v5
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
| **健康检查** | 配合 Actuator 接口，让编排工具感知服务状态，实现自愈 |
| **时区设置** | Alpine 默认 UTC，需手动设置为`Asia/Shanghai`或其他时区 |
| **日志与模型持久化** | 使用 volumes 挂载到宿主机，容器删除数据不丢 |
| **网络互联** | 自定义网络下用**服务名**互访，如 `inference:5000`，不要硬编码 IP |
| **资源限制** | 生产环境通过 `-m` / `--cpus` 或 Compose 的 `deploy.resources` 限制 CPU/内存，防止雪崩 |
| **访问宿主机** | 容器内 `localhost` 指向自身；Windows/Mac 可用 `host.docker.internal`；Linux 需在 Compose 中加 `extra_hosts: - "host.docker.internal:host-gateway"`（已在本笔记模板中内置 ✅） |
| **优雅停机** | Spring Boot 可配置 `server.shutdown=graceful`，配合 `SIGTERM` 保证请求处理完毕（已在本笔记 Dockerfile 中用 `exec` 修复 ✅） |
| **镜像安全更新** | 定期执行 `docker build --pull .` 拉取最新基础镜像；使用 `docker scout` 或 `trivy` 扫描漏洞 |
| **Compose 版本字段** | Docker Compose V2 不再需要 `version`，写上可能报警告，可移除 |
| **JVM 容器感知** | Java 8u191+ / 11+ 默认开启 `-XX:+UseContainerSupport`，JVM 自动读取 cgroup 内存限制；早期版本需显式配置，否则按宿主机总内存分配导致 OOM |
| **日志轮转** | 生产必配 `logging` 的 `max-size` 和 `max-file`，防止日志撑满磁盘 |
| **`.dockerignore` 必备** | 创建 `.dockerignore` 排除 `target/`、`.git/` 等，防止构建缓存失效和镜像臃肿（已在本笔记 3.8 提供模板 ✅） |

---

## 7. 参考与扩展

- 参考链接：[https://www.runoob.com/docker/docker-tutorial.html](https://www.runoob.com/docker/docker-tutorial.html)
- 网课链接：[https://www.bilibili.com/video/BV1s54y1n7Ev/](https://www.bilibili.com/video/BV1s54y1n7Ev/?spm_id_from=333.1387.favlist.content.click&vd_source=e0c0ad2a316e90d4078b1131e8182407)

---
