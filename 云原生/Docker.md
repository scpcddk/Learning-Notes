# 🐳 Docker 学习笔记（面向 Spring Boot 项目）

## 1. 核心概念

- **镜像（Image）**：一个只读的模板，包含运行环境（如 JDK + 应用 jar）
- **容器（Container）**：镜像的运行实例，可启动、停止、删除，相互隔离
- **仓库（Repository）**：存放镜像的地方，如 Docker Hub

---

## 2. ==常用命令==

| 命令 | 功能 | 示例 |
| --------------------- | -------------------------------- | ------------------------------------------ |
| `docker run` | **启动**一个新的容器**并运行**命令 | `docker run -d ubuntu` |
| `docker ps` | **列出**当前正在运行的容器 | `docker ps` |
| `docker ps -a` | 列出所有容器（包括已停止的容器） | `docker ps -a` |
| `docker build` | 使用 Dockerfile 构建镜像 | `docker build -t my-image .` |
| `docker images` | **列出**本地存储的所有**镜像** | `docker images` |
| `docker pull` | 从 Docker 仓库**拉取镜像** | `docker pull ubuntu` |
| `docker push` | 将**镜像推送**到 Docker 仓库 | `docker push my-image` |
| `docker exec` | 在运行的容器中**执行命令** | `docker exec -it container_name bash` |
| `docker stop` | **停止**一个或多个容器 | `docker stop container_name` |
| `docker start` | **启动**已停止的容器 | `docker start container_name` |
| `docker restart` | 重启一个容器 | `docker restart container_name` |
| `docker rm` | **删除**一个或多个**容器** | `docker rm container_name` |
| `docker rmi` | **删除**一个或多个**镜像** | `docker rmi my-image` |
| `docker logs` | **查看容器的日志** | `docker logs container_name` |
| `docker inspect` | 获取容器或镜像的详细信息 | `docker inspect container_name` |
| `docker exec -it` | 进入容器的交互式终端 | `docker exec -it container_name /bin/bash` |
| `docker network ls` | 列出所有 Docker 网络 | `docker network ls` |
| `docker volume ls` | 列出所有 Docker 卷 | `docker volume ls` |
| `docker-compose up -d` | 后台启动多容器应用（从 docker-compose.yml 文件） | `docker-compose up -d` |
| `docker-compose down` | 停止并删除由 docker-compose 启动的容器、网络等 | `docker-compose down` |
| `docker-compose logs -f` | 实时查看 compose 服务日志 | `docker-compose logs -f backend` |
| `docker-compose restart` | 重启 compose 中的某个服务 | `docker-compose restart backend` |
| `docker-compose ps` | 列出 compose 管理的容器状态 | `docker-compose ps` |
| `docker info` | 显示 Docker 系统的详细信息 | `docker info` |
| `docker version` | 显示 Docker 客户端和守护进程的版本信息 | `docker version` |
| `docker stats` | 显示容器的实时资源使用情况 | `docker stats` |
| `docker login` | 登录 Docker 仓库 | `docker login` |
| `docker logout` | 登出 Docker 仓库 | `docker logout` |
| `docker system prune -a` | 清理未使用的镜像、容器、网络（慎用） | `docker system prune -a` |

- `-t`：在新容器内指定一个伪终端或终端
- `-i`：允许你对容器内的标准输入 (STDIN) 进行交互

**常用 `docker run` 选项**：

- `-d`：后台运行
- `-p 宿主机端口:容器端口`：端口映射
- `--name`：指定容器名称
- `-v 宿主机目录:容器目录`：挂载数据卷（持久化）
- `--restart=always`：自动重启

---

## 3. Dockerfile 模板（Spring Boot 项目 + AI 扩展）

### 3.1 **常用指令详解**

| 指令 | 作用 | 示例 |
| ------ | ------ | ------ |
| **FROM** | 指定**基础镜像** | `FROM eclipse-temurin:21-jre-alpine` |
| **WORKDIR** | 设置**工作目录**，后续指令在此目录下执行 | `WORKDIR /app` |
| **COPY** | 从宿主机**复制**文件到镜像（推荐用 COPY，不用 ADD） | `COPY target/*.jar app.jar` |
| **RUN** | 构建时**执行命令**（安装依赖、配置） | `RUN apk add --no-cache curl` |
| **ENV** | **设置环境变量**，运行时可用 `-e` 覆盖 | `ENV JAVA_OPTS="-Xmx512m"` |
| **EXPOSE** | 声明容器内**服务端口**（仅文档作用） | `EXPOSE 8080` |
| **CMD** | 容器启动时的**默认命令**，可被 `docker run` 后面的命令覆盖 | `CMD ["java", "-jar", "app.jar"]` |
| **ENTRYPOINT** | 容器启动时的**入口命令**，不会被覆盖，但可追加参数 | `ENTRYPOINT ["java", "-jar", "app.jar"]` |

#### CMD vs ENTRYPOINT

- **CMD**：适合可有可无的默认参数，运行 `docker run image command` 会直接替换 CMD
- **ENTRYPOINT**：固定启动命令，后面传参会追加到 ENTRYPOINT 之后。
- **组合**：`ENTRYPOINT ["java", "-jar", "app.jar"]` + `CMD ["--server.port=8080"]`，运行 `docker run my-image --server.port=9090` 可覆盖 CMD

> Spring Boot 容器推荐：**只用 ENTRYPOINT**，避免误覆盖启动命令

### 3.2 多阶段构建（Java 项目瘦身必用）

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

效果：镜像体积可从 600MB+ 降至 200MB 以内

### 3.3 实战模板 1：Spring Boot 生产级 Dockerfile

```dockerfile
# ========== 构建阶段 ==========
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn clean package -DskipTests -B

# ========== 运行阶段 ==========
FROM eclipse-temurin:21-jre-alpine

# 安装 curl（健康检查用）并设置时区
RUN apk add --no-cache curl tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# 创建非 root 用户
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app

# 从构建阶段复制 jar，重命名为 app.jar
COPY --from=builder /build/target/*.jar app.jar
RUN chown -R app:app /app
USER app

# JVM 参数可通过环境变量覆盖
ENV JAVA_OPTS="-Xms256m -Xmx512m"
EXPOSE 8080

# 健康检查（需引入 spring-boot-starter-actuator）
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

**构建与运行**：

```bash
# 构建镜像
docker build -t my-spring-app .
# 运行容器
docker run -d -p 8080:8080 --name spring-app my-spring-app
```

> 若未使用多阶段构建，可直接 `mvn clean package -DskipTests` 后在 Dockerfile 中用 `COPY target/*.jar app.jar`（需确保目录下只有一个 jar）。

### 3.4 实战模板 2：Python AI 推理服务 Dockerfile

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

> 生产环境建议用 Gunicorn 替换 `python app.py`，稳定性更好。

### 3.5 镜像优化技巧速查

- **选对基础镜像**：优先用 `alpine` 或 `slim` 版本，避免 `latest` 完整版
- **多阶段构建**：Java/Go 项目必备，编译与运行分离
- **合并 RUN 命令**：减少层数，及时清理缓存和临时文件
  
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends 包名 \
    && rm -rf /var/lib/apt/lists/*
```

- **添加 `.dockerignore`**：排除 `.git`、`target`（若外部构建）、`node_modules` 等无关内容
- **固定依赖版本**：Python 用 `requirements.txt` 锁定版本，Maven 在 `pom.xml` 中明确版本号

---

## 4. docker-compose 模板（多服务编排）

### 4.1 核心字段说明

| 字段 | 作用 | 示例 |
| ------ | ------ | ------ |
| **services** | **定义所有服务** | 见下方完整示例 |
| **ports** | 端口**映射**，`宿主机端口:容器端口` | `"8080:8080"` |
| **volumes** | 数据挂载，**持久化存储** | `./logs:/app/logs` |
| **networks** | 自定义**网络**，容器间通过服务名互访 | `networks: - app-net` |
| **depends_on** | **控制启动顺序**（不保证内部服务就绪） | `depends_on: - inference` |
| **restart** | **重启**策略，推荐 `unless-stopped` | `restart: unless-stopped` |
| **environment** | 注入**环境变量** | `SPRING_PROFILES_ACTIVE=docker` |

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

### 4.4 完整编排模板：Spring Boot + AI 推理服务

```yaml
services:
  backend:                        # Spring Boot 后端
    build: ./backend              # Dockerfile 所在目录
    container_name: spring-backend
    ports:
      - "8080:8080"
    environment:
      - JAVA_OPTS=-Xms256m -Xmx512m
      - SPRING_PROFILES_ACTIVE=docker
      - AI_SERVICE_URL=http://inference:5000/predict
    volumes:
      - ./logs/backend:/app/logs   # 日志持久化
    networks:
      - app-net
    restart: unless-stopped
    depends_on:
      - inference

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

networks:
  app-net:
    driver: bridge
```

### 4.5 Compose 常用运维命令

| 命令 | 作用 |
| ------ | ------ |
| `docker-compose up -d` | 后台启动所有服务 |
| `docker-compose down` | 停止并删除容器、网络 |
| `docker-compose logs -f [服务名]` | 实时查看日志 |
| `docker-compose restart [服务名]` | 重启指定服务 |
| `docker-compose ps` | 查看所有服务状态 |
| `docker-compose up -d --build` | 重新构建镜像并启动 |
| `docker-compose build` | 只构建镜像，不启动 |

---

## 5. 注意事项（落地必看）

| 注意事项 | 说明 |
| ---------- | ------ |
| **jar 名称固定** | 在 `pom.xml` 中设置 `<finalName>app</finalName>`，避免 `COPY target/*.jar` 多文件报错。 |
| **多阶段构建优先** | 编译与运行分离，最终镜像不含 Maven 和源码，更小更安全。 |
| **非 root 用户运行** | 务必创建普通用户并 `USER` 切换，降低安全风险。 |
| **健康检查** | 配合 Actuator 接口，让编排工具感知服务状态，实现自愈。 |
| **时区设置** | Alpine 默认 UTC，需手动设置为 `Asia/Shanghai` 或其他时区。 |
| **日志与模型持久化** | 使用 volumes 挂载到宿主机，容器删除数据不丢。 |
| **网络互联** | 自定义网络下用**服务名**互访，如 `inference:5000`，不要硬编码 IP。 |
| **资源限制** | 生产环境通过 `-m` 或 Compose 的 `deploy.resources` 限制 CPU/内存。 |
| **访问宿主机** | 容器内 `localhost` 指向自身；Windows/Mac 可用 `host.docker.internal`；Linux 需在 Compose 中加 `extra_hosts: - "host.docker.internal:host-gateway"`。 |
| **优雅停机** | Spring Boot 可配置 `server.shutdown=graceful`，配合 `SIGTERM` 保证请求处理完毕。 |
| **镜像安全更新** | 定期执行 `docker build --pull .` 拉取最新基础镜像。 |
| **Compose 版本字段** | Docker Compose V2 不再需要 `version`，写上可能报警告，可移除。 |

---

参考链接：[https://www.runoob.com/docker/docker-tutorial.html](https://www.runoob.com/docker/docker-tutorial.html)
