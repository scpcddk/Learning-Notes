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
| `docker-compose up` | 启动多容器应用（从 docker-compose.yml 文件） | `docker-compose up` |
| `docker-compose down` | 停止并删除由 docker-compose 启动的容器、网络等 | `docker-compose down` |
| `docker info` | 显示 Docker 系统的详细信息 | `docker info` |
| `docker version` | 显示 Docker 客户端和守护进程的版本信息 | `docker version` |
| `docker stats` | 显示容器的实时资源使用情况 | `docker stats` |
| `docker login` | 登录 Docker 仓库 | `docker login` |
| `docker logout` | 登出 Docker 仓库 | `docker logout` |
| `docker export` | 导出容器 | `docker export` |
| `docker import` | 导入容器快照 | `$ cat docker/ubuntu.tar \| docker import - test/ubuntu:v1` 将快照文件 ubuntu.tar 导入到镜像 test/ubuntu:v1 |

- `-t`: 在新容器内指定一个伪终端或终端
- `-i`: 允许你对容器内的标准输入 (STDIN) 进行交互

**常用 `docker run` 选项**：

- `-d`：后台运行
- `-p 宿主机端口:容器端口`：端口映射
- `--name`：指定容器名称
- `-v 宿主机目录:容器目录`：挂载数据卷（持久化）
- `--restart=always`：自动重启

---

## 3. Dockerfile 模板（Spring Boot 项目）

```dockerfile
# 基础镜像（轻量级 JDK 21）
FROM eclipse-temurin:21-jre-alpine

# 指定工作目录
WORKDIR /app

# 复制 jar 包（需要先执行 mvn clean package）
COPY target/*.jar app.jar

# 暴露端口（Spring Boot 默认 8080）
EXPOSE 8080

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**构建镜像**：

```bash
docker build -t clash-royale-server .
```

**运行容器**：

```bash
docker run -d -p 8080:8080 --name game-server clash-royale-server
```

---

## 4. docker-compose 模板（多服务编排，可选）

```yaml
version: '3.8'
services:
  game:
    build: .
    ports:
      - "8080:8080"
    restart: always
  # 可添加其他服务，如 redis、向量数据库等
```

启动：`docker-compose up -d`  
停止：`docker-compose down`

---

## 5.注意事项

- 每次修改代码后，需要重新打包（`mvn clean package`）并重新构建镜像
- 容器内的 `localhost` 指向容器自身，要访问宿主机服务时需用 `host.docker.internal`（Windows/Mac）或宿主机 IP
- 如果端口映射冲突，换一个宿主机端口即可
- 查看容器详细信息：`docker inspect <容器名>`

---

参考链接：[https://www.runoob.com/docker/docker-tutorial.html]
