# 《Python 后端长期学习计划 完整学习与开发速查笔记》

> **适用环境**：Python 3.11+、FastAPI 0.110+、Pydantic v2、SQLAlchemy 2.0、MySQL 8、Redis 7、Celery 5、Docker Compose、RabbitMQ（可选）。
>
> **标记说明**：【核心】= Python 语言/标准库能力；【整合】= 需配合框架/客户端使用的工程能力；【第三方扩展】= 外部中间件或社区方案，如 Redis、Celery、Docker、LLM API。
>
> ⚠️ **易混淆总说明**：FastAPI 是 Web 框架，Uvicorn 是 ASGI 服务器；`async def` 不等于自动多线程；`BackgroundTasks` 不是可靠分布式任务队列；SQLAlchemy `Session` 不是数据库连接本身；认证 ≠ 授权；日志 ≠ 指标 ≠ 链路追踪；JWT 无状态，Session 有状态。

---

# 第一篇：基础认知

## 1. 是什么

一句话：这份计划的目标不是“学完 Python”，而是让你具备**独立开发、调试、测试、部署 AI 应用后端**的 Python 工程能力。

核心定位：

| 维度 | 说明 |
|---|---|
| 主线 | Python 后端 + FastAPI + 异步 + 数据库 + Redis + Docker + LLM API |
| 辅助 | Java 后端继续作为基本功；AI 路线负责算法与模型认知 |
| 交付物 | 可运行、可测试、可部署、可讲解的后端项目 |
| 验收方式 | 能完成小任务、解释机制、处理常见错误，而不是“看过教程” |

> [!tip] 一句话点破核心
> 你要学的是“用 Python 把 AI 能力封装成稳定服务”，不是把 Python 所有语法重新学一遍。

## 2. 整体工作流程

```text
需求/接口设计
   ↓
FastAPI 路由 + Pydantic 模型
   ↓
依赖注入（DB Session、配置、鉴权）
   ↓
业务逻辑
   ↓
数据库 / Redis / LLM API / 任务队列
   ↓
统一异常 + 日志 + 响应
   ↓
Docker 部署 + 健康检查 + 监控
```

## 3. 整体学习路线

| 阶段 | 主题 | 目标 | 验收信号 |
|---|---|---|---|
| 0 | Python 基础查漏补缺 | 能读写调试常见 Python 代码 | 能定位报错到具体行 |
| 1 | Python 工程基础 | 项目结构、虚拟环境、依赖 | 干净环境能复现运行 |
| 2 | HTTP、REST、FastAPI | 开发基本 HTTP 服务 | 能写 GET/POST 并测试 |
| 3 | 校验、异常、接口设计 | API 稳定清晰可调试 | 能区分 4xx/5xx |
| 4 | 异步与后台任务 | 处理 I/O 密集与长任务 | 能写异步请求、任务状态接口 |
| 5 | 数据库与 ORM | 持久化 CRUD | 能处理事务与连接泄漏 |
| 6 | 测试、日志、配置 | 可验证、可交付 | 能写接口测试与配置隔离 |
| 7 | Redis、缓存、任务队列 | 服务协作机制 | 能判断缓存 vs 队列 |
| 8 | Docker、Linux、部署 | 可复现运行环境 | 能构建镜像并排查日志 |
| 9 | AI 应用后端专项 | 集成 LLM 能力 | 能封装流式/非流式 API |
| 10 | 综合项目 | 独立交付 | 能演示并解释取舍 |

## 4. 核心组件关系

```mermaid
flowchart LR
    C[Client] --> U[Uvicorn ASGI Server]
    U --> F[FastAPI App]
    F --> R[Router]
    R --> D[Depends 依赖注入]
    D --> P[Pydantic 校验]
    P --> S[Service 业务逻辑]
    S --> DB[(MySQL)]
    S --> RD[(Redis)]
    S --> LLM[LLM API]
    S --> Q[Celery/RQ 任务队列]
    Q --> RD
    S --> L[Logging]
```

## 5. 与 Java 后端的关系

| 对比项 | Java 后端 | Python 后端 | 结论 |
|---|---|---|---|
| 强项 | 工程规范、生态成熟、求职 | AI 集成、快速开发、脚本自动化 | 两条线并行 |
| Web 框架 | Spring Boot | FastAPI | 不重复深挖 MVC |
| ORM | MyBatis/JPA | SQLAlchemy | 重点学 Python 访问方式 |
| 并发 | 线程池、JUC | asyncio、协程 | 先理解 I/O 模型 |
| 部署 | JVM + 容器 | Python + 容器 | Docker/Linux 共用 |

> [!important] 必须记住的规则
> 已有 Java/MySQL/MyBatis 基础，就不要重新系统学 SQL；把时间花在 Python 工程、异步、FastAPI、LLM 集成和部署上。

**口诀：基础先行、项目驱动、验收为准。**

---

# 第二篇：项目搭建

## 6. Python 基础查漏补缺（阶段 0）

一句话：只补薄弱点，不重复学已掌握内容。

| 主题 | 必须会 | 易错点 |
|---|---|---|
| 数据类型 | list/dict/set/tuple | 可变对象默认参数 |
| 函数 | 参数、返回值、作用域 | 闭包与 `nonlocal` |
| 异常 | try/except/finally/raise | 裸 `except` 吞异常 |
| 文件/JSON | pathlib、json | 编码与路径分隔符 |
| 类 | 继承、组合 | `self` 与类属性 |
| 类型标注 | `Optional`、`list[str]` | 运行时不强制 |

> [!warning] 易错/危险操作
> ```python
> def add_bad(item, lst=[]):  # 反例：默认参数共享，传入 [] 也会被替换
>     lst.append(item)
>     return lst
> ```
> 正例：必须用 `None` 占位，再在函数体内初始化。
> ```python
> def add_good(item, lst=None):
>     if lst is None:      # 必须加
>         lst = []
>     lst.append(item)
>     return lst
> ```

**阶段 0 最小交付物**：CLI JSON 处理小工具，能读写文件、处理异常。

## 7. Python 工程基础（阶段 1）

| 组件 | 职责 | 正确用法 |
|---|---|---|
| `venv` | 隔离依赖 | 每个项目一个 `.venv` |
| `pip` | 安装包 | 用锁定文件 |
| `.env` | 环境变量 | 不提交密钥 |
| `ruff` | 格式/静态检查 | 提交前运行 |
| Git | 版本管理 | 小步提交，分支开发 |

### 7.1 依赖管理升级

| 方案 | 适合 | 结论 |
|---|---|---|
| `pip freeze > requirements.txt` | 小项目、临时脚本 | 可用，但依赖多时易混乱 |
| `pip-tools` | 需要 `requirements.in` + 锁定 | 推荐中小项目 |
| `uv` | 追求速度、现代工作流 | 推荐新项目 |
| `poetry` | 需要完整包管理 | 可用，但学习成本高 |

```bash
# requirements.in 只写直接依赖
fastapi
uvicorn[standard]
pydantic
httpx
sqlalchemy
alembic
pytest

# 生成锁定文件
pip-compile requirements.in -o requirements.txt
pip-sync requirements.txt
```

> [!tip] 一句话点破核心
> 直接依赖手写，间接依赖锁定；不要靠 `pip freeze` 把环境里所有包都当项目依赖。

### 7.2 虚拟环境与目录

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/WSL
# .venv\Scripts\activate         # Windows
```

推荐目录：

```text
app/
  main.py
  api/
    routes.py
  core/
    config.py
    logging.py
  models/
  schemas/
  services/
  db/
tests/
.env
requirements.in
requirements.txt
Dockerfile
```

> [!tip] 一句话点破核心
> 虚拟环境解决“依赖隔离”，锁定文件解决“可复现”。

**阶段 1 最小交付物**：可复现项目模板，干净环境能跑起来。

**口诀：虚拟环境隔离，依赖清单复现。**

---

# 第三篇：核心用法

## 8. HTTP 与 REST API（阶段 2）

| 方法 | 用途 | 幂等 | 常见状态码 |
|---|---|---|---|
| GET | 查询 | 是 | 200/404 |
| POST | 创建/提交 | 否 | 201/400/422 |
| PUT | 全量更新 | 是 | 200/404 |
| PATCH | 部分更新 | 否 | 200/404 |
| DELETE | 删除 | 是 | 204/404 |

> [!note] 补充理解
> REST 不是“必须用某个框架”，而是一套用 URL 表示资源、用 HTTP 方法表示动作的风格。

---

## 9. FastAPI + Uvicorn + Pydantic【整合】

| 组件 | 是什么 | 核心职责 | 生命周期 | 线程安全 | 正确用法 |
|---|---|---|---|---|---|
| FastAPI | Web 框架 | 路由、依赖注入、校验、文档 | 应用级 | 路由函数无状态 | 业务逻辑放 Service |
| Uvicorn | ASGI 服务器 | 监听端口、解析 HTTP、驱动 ASGI | 进程级 | 多 worker 进程 | 生产用 Gunicorn + UvicornWorker |
| Pydantic | 数据校验 | 请求/响应模型校验与序列化 | 请求级 | 模型实例不共享 | 入参出参都建模 |

> [!tip]
> **一句话核心**：Java 靠“注解 + 额外依赖”，FastAPI 靠“类型提示 + 原生自带”。

| 对比项 | Java (Spring Boot) | Python (FastAPI) |
|---|---|---|
| **技术栈** | Spring Boot + Springdoc + Swagger UI | FastAPI（内置 OpenAPI） |
| **实现方式** | 注解描述接口 | 类型提示自动推导 |
| **额外依赖** | 需单独引入 | 无，开箱即用 |
| **文档路径** | `/swagger-ui.html` | `/docs`（Swagger）/ `/redoc` |

> [!tip] 一句话点破核心
> Java 的 Swagger 是“外挂”的，FastAPI 的 Swagger 是“原生”的。
> **口诀：Java 注解加依赖，Python 类型即文档。**

**最小示例**：

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class CreateUser(BaseModel):
    name: str = Field(min_length=1, max_length=50)  # 必须加约束
    age: int = Field(ge=0, le=150)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users", status_code=201)
def create_user(user: CreateUser):
    return {"id": 1, **user.model_dump()}
```

**启动**：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 生产不要 --reload
```

**调用链**：

```text
Uvicorn 接收 HTTP → ASGI 事件 → FastAPI Router 匹配 → Depends 解析 → Pydantic 校验 → 路由函数 → 响应序列化
```

> [!warning] 易错/危险操作
> FastAPI 不是服务器，Uvicorn 才是。只装 FastAPI 不能直接监听端口。

**阶段 2 最小交付物**：健康检查 + 用户 CRUD，能写 GET/POST 并测试。

---

## 10. 请求校验、异常处理与接口设计（阶段 3）

| 现象 | 原因 | 解决 |
|---|---|---|
| 422 Unprocessable Entity | Pydantic 校验失败 | 检查字段类型、必填、约束 |
| 500 Internal Server Error | 未捕获异常 | 全局异常处理器 + 日志 |
| 404 Not Found | 路由未匹配 | 检查路径、方法、前缀 |
| 400 Bad Request | 业务参数错误 | 主动抛 `HTTPException(400)` |

统一错误响应建议：

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=400,
    detail={"code": "INVALID_AGE", "message": "年龄不合法"}
)
```

> [!important] 必须记住的规则
> 客户端错误用 4xx，服务器错误用 5xx；不要把业务失败都写成 500。

**阶段 3 最小交付物**：统一错误响应 + 分页，能区分 4xx/5xx。

**口诀：路由声明参数，Pydantic 校验，异常统一。**

---

# 第四篇：高级特性

## 11. 异步编程与后台任务（阶段 4）

| 对比项 | 同步 `def` | 异步 `async def` | 线程 | 进程 |
|---|---|---|---|---|
| 适合 | CPU 轻、简单逻辑 | I/O 密集 | 阻塞 I/O 兼容 | CPU 密集 |
| 并发方式 | 线程池 | 事件循环 | OS 调度 | 多核并行 |
| 坑 | 阻塞请求 | 阻塞事件循环 | GIL 限制 | 开销大 |
| 结论 | 不确定先用同步 | 外部 I/O 用异步 | 少用 | 计算密集用 |

异步 HTTP：

```python
import httpx

async def call_llm(prompt: str):
    async with httpx.AsyncClient(timeout=30.0) as client:  # 必须设超时
        resp = await client.post("https://api.example.com/v1/chat", json={"prompt": prompt})
        resp.raise_for_status()
        return resp.json()
```

反例：

```python
import requests
async def bad():
    return requests.get("https://example.com")  # 阻塞事件循环
```

> [!warning] ⚠️ 易混淆：`BackgroundTasks` vs Celery
> `BackgroundTasks` 是 FastAPI 进程内后台任务，请求结束后执行，**不保证持久化、重试、跨进程**。Celery 是分布式任务队列，适合长任务、重试、多 worker。示例：发邮件可用 BackgroundTasks；订单超时关闭必须用 Celery/RQ。

**阶段 4 最小交付物**：异步调外部 API + 任务状态查询，能提交任务、查状态、取结果。

**口诀：异步怕阻塞，后台分轻重。**

## 12. 数据库与 ORM（阶段 5）

| 组件 | 职责 | 生命周期 | 线程安全 | 正确用法 |
|---|---|---|---|---|
| Engine | 连接池入口 | 应用级 | 线程安全 | 全局一个 |
| Session | 工作单元 | 请求级 | 非线程安全 | 每请求一个 |
| Connection | 数据库连接 | 事务级 | 不跨线程 | 由 Engine 管理 |
| Alembic | 迁移 | 开发/部署 | - | 版本化 DDL |

同步 Session：

```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db          # FastAPI 依赖注入
    finally:
        db.close()        # 必须关闭，防连接泄漏
```

事务：

```python
try:
    db.add(user)
    db.commit()
except Exception:
    db.rollback()
    raise
```

### 12.1 异步 SQLAlchemy【整合】

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(
    "mysql+aiomysql://user:pass@localhost:3306/app",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # 必须加：防止死连接
    pool_recycle=3600,    # 注意：MySQL 8 小时断连
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### 12.2 Alembic 迁移

```bash
# 初始化异步模板
alembic init -t async migrations

# 生成迁移
alembic revision --autogenerate -m "add user table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 12.3 N+1 与连接池

| 问题 | 现象 | 解决 |
|---|---|---|
| N+1 | 1 次查主表，N 次查关联 | `selectinload` / `joinedload` |
| 连接泄漏 | 请求增多后卡死 | `async with` + `pool_pre_ping` |
| 慢查询 | 接口变慢 | 加索引、看执行计划 |
| 死连接 | MySQL 断连 | `pool_recycle` |

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
```

> [!important] 必须记住的规则
> Session 不是连接，Session 是连接之上的工作单元；不要全局共享 Session。

**阶段 5 最小交付物**：SQLAlchemy + Alembic 用户表，能迁移、CRUD、事务回滚。

**口诀：会话短，事务清，连接池不泄漏。**

## 13. 测试、日志、配置与工程质量（阶段 6）

| 工具 | 用途 | 关键点 |
|---|---|---|
| pytest | 单元/接口测试 | fixture 管测试资源 |
| TestClient | FastAPI 接口测试 | 不启动真实服务器 |
| Mock | 隔离外部服务 | 不 mock 被测逻辑 |
| logging | 日志 | 级别、请求 ID、结构化 |
| pydantic-settings | 配置 | 环境变量覆盖 |

### 13.1 pytest 测试数据库

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

接口测试：

```python
def test_health():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
```

> [!tip] 一句话点破核心
> 测试不是证明你对，而是防止你以后改错。

**阶段 6 最小交付物**：pytest 覆盖成功失败，接口测试 + Mock 外部服务。

**口诀：fixture 管资源，Mock 隔外部。**

---

# 第五篇：原理与源码

## 14. FastAPI/ASGI 调用链

```text
Client → Uvicorn → ASGI Scope → FastAPI Router
      → 依赖注入 Depends → Pydantic 校验
      → Endpoint → Response Model → JSON 序列化
```

FastAPI 快的原因：Starlette + Pydantic + ASGI 异步；不是“魔法”。

## 15. 异步事件循环

| 概念 | 说明 |
|---|---|
| 事件循环 | 单线程调度协程 |
| 协程 | `async def` 函数，可暂停 |
| `await` | 让出控制权，等 I/O |
| 阻塞 | 同步 I/O 会卡住整个循环 |

> [!important] 必须记住的规则
> 在 `async def` 里调用 `requests`、`time.sleep`、同步 DB 驱动，会阻塞事件循环。

## 16. SQLAlchemy Session 与连接池

```text
Engine → 连接池 → Connection → Session → 事务
```

Session 常见坑：

| 现象 | 原因 | 解决 |
|---|---|---|
| 连接泄漏 | Session 未关闭 | 依赖注入 `finally: close` |
| 数据不更新 | 未 commit | 显式提交 |
| 脏读/并发 | 事务隔离 | 合理隔离级别 |

## 17. Redis 单线程与持久化【第三方扩展】

一句话：Redis 命令执行单线程，所以命令原子；网络 I/O 在 6.0+ 可多线程。

| 持久化 | 优点 | 缺点 |
|---|---|---|
| RDB | 快、体积小 | 可能丢数据 |
| AOF | 更安全 | 文件大、恢复慢 |
| 混合 | 兼顾 | 配置复杂 |

## 18. Celery 架构

```text
Producer → Broker(Redis/RabbitMQ) → Worker → Result Backend
```

| 组件 | 职责 |
|---|---|
| Broker | 存任务消息 |
| Worker | 执行任务 |
| Backend | 存结果 |
| Beat | 定时调度 |

**口诀：Uvicorn 跑 ASGI，事件循环怕阻塞。**

---

# 第六篇：生产实践

## 19. Redis、缓存、任务队列与服务协作（阶段 7）

| 对比项 | Redis 缓存 | 任务队列 |
|---|---|---|
| 解决问题 | 加速读、降低 DB 压力 | 异步执行、削峰、重试 |
| 典型工具 | Redis | Celery / RQ |
| 关键风险 | 穿透、击穿、雪崩 | 重复消费、失败重试 |
| 结论 | 读多写少用缓存 | 长任务用队列 |

### 19.1 缓存一致性严谨化

“先更新 DB，再删除缓存”只是常用方案，不是强一致方案。

| 方案 | 做法 | 适用 | 缺点 |
|---|---|---|---|
| 先 DB 后删缓存 | 更新数据库后删除缓存 | 大多数读多写少 | 并发下仍可能短暂不一致 |
| 延迟双删 | 删缓存 → 更新 DB → 延迟再删 | 并发较高 | 延迟时间难定 |
| 版本号 | key 带版本，更新后版本递增 | 配置、商品 | 旧版本残留 |
| binlog 订阅 | Canal/Debezium 监听 DB 变更 | 大规模 | 架构复杂 |

```text
最终一致 ≠ 强一致。能接受短暂旧数据，才用缓存。
```

> [!warning] ⚠️ 易混淆：缓存删除失败 ≠ 数据一定错
> 删除失败要重试或走 binlog 补偿；不要只写一个 `delete` 就认为一致了。

### 19.2 Celery 隔离严谨化

| 方案 | 隔离级别 | 推荐场景 |
|---|---|---|
| 同 Redis 不同 DB | 逻辑隔离，共享实例故障域 | 开发、小项目 |
| 独立 Redis 实例 | 物理隔离 | 生产推荐 |
| RabbitMQ + Redis backend | broker 与 backend 分离 | 任务可靠要求高 |

```python
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="amqp://guest:guest@rabbitmq:5672//",  # 生产可用 RabbitMQ
    backend="redis://redis-backend:6379/0"
)

@celery_app.task(bind=True, max_retries=3)
def send_email(self, user_id: int):
    try:
        ...
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)  # 重试
```

> [!warning] ⚠️ 易混淆：缓存和队列都用 Redis，但目的不同
> 缓存是“存结果加速读”，队列是“存任务异步做”。不要把 Celery broker 和业务缓存混在同一个 DB，建议分库或分实例。

**阶段 7 最小交付物**：Redis 缓存 + Celery 发邮件，能缓存、能重试、能幂等。

**口诀：数据库会话短，缓存任务分。**

## 20. Docker、Linux 与云原生部署（阶段 8）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| 问题 | 原因 | 解决 |
|---|---|---|
| 容器启动失败 | 缺依赖/路径错 | `docker logs` |
| 端口访问不了 | 未映射 | `-p 8000:8000` |
| 环境变量缺失 | 未注入 | `--env-file .env` |
| 优雅关闭 | 信号未处理 | 用 exec 形式 CMD |

> [!warning] 易错/危险操作
> 不要把密钥写进镜像；不要把 `--reload` 带到生产。

### 20.1 Gunicorn + Uvicorn + Nginx

```bash
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  -b 0.0.0.0:8000 \
  --timeout 60 \
  --graceful-timeout 30
```

Nginx SSE 配置：

```nginx
location /api/ {
    proxy_pass http://api:8000;
    proxy_buffering off;          # SSE 必须关
    proxy_read_timeout 3600s;     # 长连接
    proxy_set_header X-Request-ID $request_id;
}
```

Docker Compose：

```yaml
services:
  api:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: example
  redis:
    image: redis:7
```

优雅关闭：

```dockerfile
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
# 必须用 exec 形式，保证 SIGTERM 传到进程
```

**阶段 8 最小交付物**：Docker Compose 一键启动，API + DB + Redis 可联动。

**口诀：Gunicorn 管进程，Uvicorn 跑 ASGI，Nginx 关缓冲。**

## 21. 安全与鉴权【整合】

### 21.1 是什么

一句话：认证解决“你是谁”，授权解决“你能干什么”。

| 概念 | 说明 | 常见方案 |
|---|---|---|
| 认证 | 验证身份 | JWT、Session、OAuth2 |
| 授权 | 判断权限 | RBAC、Scope、Policy |
| 密码 | 存储凭证 | bcrypt/argon2 哈希 |
| 密钥 | 签名/加密 | 环境变量、SecretStr |

### 21.2 JWT 认证流程

```text
用户登录 → 校验密码 → 生成 access_token + refresh_token
      → 客户端带 Authorization: Bearer <token>
      → 服务端验签、检查过期、解析用户
      → 授权检查 → 返回资源
```

### 21.3 常用代码

```python
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "从环境变量读取"  # 不要硬编码
ALGORITHM = "HS256"

def hash_password(raw: str) -> str:
    return pwd.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(raw, hashed)

def create_token(sub: str):
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),  # 必须加过期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "invalid token")
```

### 21.4 CORS 与限流

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # 生产不要 *
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

Redis 限流：

```python
async def rate_limit(redis, key: str, limit: int = 100, window: int = 60):
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    if current > limit:
        raise HTTPException(429, "too many requests")
```

### 21.5 常见坑

| 现象 | 原因 | 解决 |
|---|---|---|
| token 永不过期 | 未设 `exp` | 必须设置过期 |
| 密钥泄露 | 硬编码 | 环境变量 + SecretStr |
| CORS 全开 | `allow_origins=["*"]` | 白名单 |
| 密码明文 | 直接存 DB | bcrypt/argon2 |
| 越权 | 只认证不授权 | 每次检查资源归属 |

> [!warning] ⚠️ 易混淆：JWT vs Session
> JWT 无状态，服务端不存会话；Session 有状态，服务端存会话。区别：JWT 适合分布式 API，Session 适合传统 Web。示例：移动端 API 常用 JWT，后台管理系统常用 Session。

**口诀：认证授权两回事，JWT 过期刷新。**

---

## 22. 可观测性与 CI/CD【第三方扩展】

### 22.1 三大支柱

| 支柱 | 解决问题 | 常用工具 |
|---|---|---|
| 日志 Logging | 发生了什么 | structlog、JSON 日志 |
| 指标 Metrics | 趋势、告警 | Prometheus、Grafana |
| 链路 Tracing | 请求经过哪些服务 | OpenTelemetry、Jaeger |

### 22.2 请求 ID 中间件

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

日志中带请求 ID：

```python
import logging
logger = logging.getLogger(__name__)

logger.info("user_login", extra={"request_id": request.state.request_id})
```

### 22.3 Prometheus 指标

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 22.4 GitHub Actions CI

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

> [!tip] 一句话点破核心
> 没有请求 ID 的日志，在微服务里等于没有日志。

**口诀：日志指标追踪，请求 ID 串联。**

---

## 23. AI 应用后端专项（阶段 9）

| 能力 | 工具 | 关键点 |
|---|---|---|
| 调 LLM API | httpx | 超时、重试、错误分类 |
| 流式响应 | SSE | `StreamingResponse` |
| 结构化输出 | Pydantic | JSON 校验与兜底 |
| Embedding/RAG | 向量库 | 分块、召回、重排 |
| Tool Calling | 函数注册 | 参数校验、权限 |
| 成本保护 | 限流 | Token 统计、并发控制 |

### 23.1 LLM SSE 流式格式修正

`StreamingResponse` 直接转发 `aiter_bytes()` 不一定符合 SSE 格式。

```python
import json
from fastapi.responses import StreamingResponse

async def sse_stream(request, llm_stream):
    async def gen():
        try:
            yield ": connected\n\n"  # 心跳/注释帧
            async for chunk in llm_stream:
                if await request.is_disconnected():  # 必须处理断连
                    break
                data = {"delta": chunk}
                yield f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
```

> [!important] 必须记住的规则
> LLM 调用必须设超时、重试、日志、成本上限和失败兜底。SSE 必须处理：`data:` 前缀、空行分隔、心跳、客户端断连、错误帧。

**阶段 9 最小交付物**：LLM 流式接口 + 超时重试 + Token 统计，能流式返回、错误兜底。

**口诀：容器可复现，AI 调用要兜底，SSE 要包格式。**

---

## 24. 综合项目与独立交付（阶段 10）

验收清单：

- [ ] 能设计接口和模块
- [ ] 能写 CRUD + 异步任务
- [ ] 能集成 LLM / 外部 API
- [ ] 能写单元测试和接口测试
- [ ] 能 Docker 部署
- [ ] 能解释架构取舍

**阶段 10 最小交付物**：综合项目演示，能讲清架构取舍。

**口诀：阶段不交付，学习不算数。**

---

# 第七篇：常见问题与坑

## 25. 常见错误速查

| 现象 | 原因 | 解决 |
|---|---|---|
| 422 | Pydantic 校验失败 | 检查字段类型/必填 |
| 500 | 未捕获异常 | 全局异常处理 + 日志 |
| 事件循环阻塞 | `async def` 里同步 I/O | 改 `httpx.AsyncClient` |
| 连接泄漏 | Session 未关闭 | 依赖注入 `finally` |
| Celery 任务重复 | 未幂等 | 任务 ID + 去重 |
| Docker 启动失败 | 依赖/路径/端口 | 看日志、查环境变量 |
| 缓存与 DB 不一致 | 更新顺序错 | 先 DB 后删缓存 + 补偿 |
| LLM 超时 | 未设 timeout | httpx timeout + 重试 |
| token 过期 | 未刷新 | refresh token |
| 越权 | 只认证不授权 | 检查资源归属 |
| 日志找不到请求 | 无请求 ID | 中间件 + 日志字段 |
| SSE 断连 | 未检测断连 | `request.is_disconnected` |

---

## 26. 易混淆点汇总

⚠️ **易混淆：`async def` vs 多线程**
`async def` 是协程，单线程事件循环；多线程是 OS 线程。区别：协程适合 I/O，线程适合兼容阻塞库。示例：`httpx.AsyncClient` 用协程，`requests` 用线程。

⚠️ **易混淆：FastAPI vs Uvicorn**
FastAPI 是框架，Uvicorn 是服务器。区别：FastAPI 定义路由，Uvicorn 监听端口。示例：`uvicorn main:app`。

⚠️ **易混淆：BackgroundTasks vs Celery**
BackgroundTasks 进程内、不可靠；Celery 分布式、可重试。示例：发通知可用前者，订单关闭用后者。

⚠️ **易混淆：JWT vs Session**
JWT 无状态，Session 有状态。示例：移动端 API 用 JWT，后台管理用 Session。

⚠️ **易混淆：日志 vs 指标 vs 链路**
日志看单次事件，指标看趋势，链路看跨服务路径。

⚠️ **易混淆：缓存 vs 队列**
缓存存结果加速读，队列存任务异步做。

⚠️ **易混淆：Alembic vs SQLAlchemy**
Alembic 管数据库迁移，SQLAlchemy 管 ORM 映射。

---

## 27. 面试追问

| 问题 | 回答要点 |
|---|---|
| FastAPI 为什么快？ | Starlette + Pydantic + ASGI 异步 |
| ASGI vs WSGI？ | ASGI 支持异步/WebSocket，WSGI 同步 |
| Session 线程安全吗？ | 不安全，每请求一个 |
| 如何防 SQL 注入？ | 参数化查询/ORM |
| Celery 如何幂等？ | 业务唯一键 + 状态机 |
| Redis 缓存穿透？ | 空值缓存、布隆过滤器 |
| Docker 多阶段构建？ | 减小镜像体积 |
| LLM 流式怎么做？ | SSE + StreamingResponse + 断连检测 |
| JWT 如何刷新？ | access + refresh 双 token |
| 如何做限流？ | Redis 计数 + 过期窗口 |
| N+1 怎么解决？ | selectinload / joinedload |
| 如何优雅关闭？ | Gunicorn + SIGTERM + graceful timeout |

**口诀：先分类再定位，日志请求 ID。**

---

# 第八篇：速查与总结

## 28. 常用配置速查

```bash
# 环境
python -m venv .venv
source .venv/bin/activate

# 依赖
pip install fastapi "uvicorn[standard]" pydantic httpx sqlalchemy alembic pytest redis celery
pip-compile requirements.in -o requirements.txt

# 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

# 测试
pytest -q

# 迁移
alembic revision --autogenerate -m "msg"
alembic upgrade head

# Docker
docker build -t app .
docker run -p 8000:8000 --env-file .env app
docker compose up -d

# Celery
celery -A app.tasks worker -l info
```

---

## 29. 常用 API/命令速查

[常用 API/命令速查表](常用API+命令速查表.md)

> 注释约定：`# 作用` 说明用途；`# 必须加` 生产必做；`# 注意` 易错点。

1. **`@app.get` / `@app.post`**  
   作用：定义 HTTP 接口。  
   ```python
   @app.get("/health")  # 定义 GET 接口，常用于探活
   def health():
       return {"status": "ok"}  # FastAPI 自动转 JSON

   @app.post("/users", status_code=201)  # POST 创建资源，201 表示已创建
   def create_user(user: UserIn):  # UserIn 是 Pydantic 模型，自动校验请求体
       ...
   ```

2. **`Depends(get_db)`**  
   作用：依赖注入，请求级 DB Session。  
   ```python
   def get_db():
       db = SessionLocal()  # 每个请求新建一个 Session
       try:
           yield db  # 交给路由使用，请求结束回来继续执行
       finally:
           db.close()  # 必须加：关闭 Session，防连接泄漏

   @app.get("/users")
   def list_users(db=Depends(get_db)):  # Depends 自动调用 get_db 并注入
       ...
   ```

3. **`HTTPException`**  
   作用：返回标准 HTTP 错误。  
   ```python
   raise HTTPException(
       status_code=404,  # 客户端错误用 4xx
       detail="not found"  # 返回给客户端的错误信息
   )
   ```

4. **`BaseModel` / `Field`**  
   作用：声明请求/响应模型并校验。  
   ```python
   class UserIn(BaseModel):  # 请求体模型
       name: str = Field(min_length=1, max_length=50)  # 必须加约束，防脏数据
       age: int = Field(ge=0, le=150)  # ge=大于等于，le=小于等于
   ```

5. **`model_dump()`**  
   作用：Pydantic 模型转 dict。  
   ```python
   data = user.model_dump()  # Pydantic v2：模型转 dict；v1 用 .dict()
   # 注意：要 JSON 字符串用 model_dump_json()
   ```

6. **`httpx.AsyncClient(timeout=...)`**  
   作用：异步调用外部 HTTP / LLM API。  
   ```python
   async with httpx.AsyncClient(timeout=30.0) as client:  # 必须加：超时防卡死
       resp = await client.get("https://api.example.com")  # await 不阻塞事件循环
       resp.raise_for_status()  # 非 2xx 抛异常，便于统一错误处理
   ```

7. **`async def` / `await`**  
   作用：定义协程、等待 I/O，不阻塞事件循环。  
   ```python
   async def fetch():
       await asyncio.sleep(1)  # 注意：别用 time.sleep，会阻塞事件循环
   ```

8. **`create_async_engine` / `async_sessionmaker`**  
   作用：创建异步数据库引擎和 Session 工厂。  
   ```python
   engine = create_async_engine(
       "mysql+aiomysql://user:pass@localhost:3306/app",  # 异步驱动 aiomysql
       pool_pre_ping=True,  # 必须加：使用前探活，防死连接
       pool_recycle=3600,   # 注意：小于 MySQL wait_timeout，防断连
   )
   AsyncSessionLocal = async_sessionmaker(
       engine,
       expire_on_commit=False,  # 提交后不过期，避免后续访问触发额外查询
   )
   ```

9. **`select` / `session.add` / `commit` / `rollback`**  
   作用：查询、新增、提交、回滚。  
   ```python
   stmt = select(User).where(User.id == 1)  # SQLAlchemy 2.0 查询写法
   session.add(user)  # 新增对象到会话
   await session.commit()  # 提交事务，真正写库
   # 异常时：
   await session.rollback()  # 回滚，避免脏数据和连接占用
   ```

10. **`alembic upgrade head`**  
    作用：把数据库升级到最新迁移版本。  
    ```bash
    alembic revision --autogenerate -m "add user table"  # 根据模型差异生成，必须 review
    alembic upgrade head  # 升到最新版本
    ```

11. **`pytest` / `TestClient`**  
    作用：跑测试、测 FastAPI 接口。  
    ```python
    client = TestClient(app)  # 不启动真实服务器，直接测 ASGI 应用
    assert client.get("/health").status_code == 200  # 断言状态码
    # 注意：TestClient 适合接口测试，不替代真实集成测试
    ```

12. **Redis `set ex` / `get` / `incr` / `expire`**  
    作用：缓存读写、计数、限流。  
    ```python
    await redis.set("k", "v", ex=60)  # ex=60 秒过期，防脏数据长期存在
    await redis.get("k")  # 读缓存；返回类型取决于 decode_responses
    await redis.incr("cnt")  # 原子自增，限流/计数常用
    await redis.expire("cnt", 60)  # 给计数键设置窗口
    ```

13. **Celery `task.delay` / `retry`**  
    作用：异步任务提交与失败重试。  
    ```python
    @celery_app.task(bind=True, max_retries=3)  # bind=True 才能用 self.retry
    def send_email(self):
        try:
            ...
        except Exception as exc:
            raise self.retry(exc=exc, countdown=5)  # 5 秒后重试；任务必须幂等

    send_email.delay()  # 异步提交任务，立即返回
    ```

14. **`jwt.encode` / `jwt.decode`**  
    作用：签发和校验 JWT。  
    ```python
    token = jwt.encode(
        {"sub": "1", "exp": exp},  # sub 用户标识；exp 必须加过期时间
        SECRET_KEY,
        algorithm="HS256",
    )
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"],  # 必须指定算法，防算法混淆
    )
    # 注意：过期会抛 ExpiredSignatureError，要捕获
    ```

15. **`uvicorn` / `gunicorn` / `docker compose up`**  
    作用：开发启动、生产启动、容器编排。  
    ```bash
    # 开发：--reload 热重载，只用于本地
    python -m uvicorn app.main:app --reload --port 8000

    # 生产：多 worker，不要 --reload
    gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

    # 编排：后台启动多服务
    docker compose up -d
    ```

**口诀：路由依赖异常，校验序列化；HTTP 异步 DB，迁移测试缓存；队列 JWT 部署。**

---

## 30. 问题 → 知识点索引

| 问题 | 知识点 | 阶段 |
|---|---|---|
| 422 错误 | Pydantic 校验 | 3 |
| 事件循环阻塞 | 异步编程 | 4 |
| 连接泄漏 | SQLAlchemy Session | 5 |
| 接口测试 | pytest + TestClient | 6 |
| 缓存不一致 | Redis 缓存 | 7 |
| 容器启动失败 | Docker/Linux | 8 |
| LLM 超时 | httpx + 重试 | 9 |
| 任务重复 | Celery 幂等 | 7/9 |
| token 过期 | JWT + refresh | 6/21 |
| 越权 | 认证 + 授权 | 6/21 |
| 日志找不到请求 | 请求 ID 中间件 | 22 |
| 接口慢 | N+1、索引、连接池 | 5/12 |
| 迁移冲突 | Alembic 版本管理 | 12 |
| CI 怎么跑测试 | GitHub Actions | 22 |
| SSE 断连 | 流式响应 + 断连检测 | 23 |
| 容器优雅关闭 | Gunicorn + SIGTERM | 20 |

---

## 31. 学习重点分级

| 级别 | 内容 | 建议 |
|---|---|---|
| Level 1 生存 | Python 基础、venv、FastAPI、Pydantic、异常、日志、httpx、Docker | 必须掌握 |
| Level 2 项目 | SQLAlchemy、Redis、异步、pytest、Alembic | 项目需要时掌握 |
| Level 3 生产 | JWT、CORS、限流、Celery、CI/CD、可观测性、Gunicorn/Nginx | 逐步补 |
| Level 4 深入 | ASGI、CPython、分布式、元编程 | 当前可暂缓 |

---

## 32. Cheat Sheet

```text
Python 后端主线：
Python 基础 → 工程化 → FastAPI → Pydantic → 异步 → DB → Redis → Celery → Docker → LLM API → 综合项目

请求链：
Client → Uvicorn → FastAPI → Depends → Pydantic → Service → DB/Redis/LLM → Response

并发选择：
I/O 密集 → async/await
阻塞库 → 线程池
CPU 密集 → 多进程

任务选择：
短小进程内 → BackgroundTasks
可靠长任务 → Celery/RQ

缓存：
读多写少 → Redis
更新：先 DB 后删缓存 + 补偿

安全：
密码哈希 bcrypt/argon2 → JWT 带 exp → OAuth2 Bearer → CORS 白名单 → Redis 限流

可观测性：
请求 ID 中间件 → 结构化日志 → Prometheus 指标 → OpenTelemetry 链路

异步 DB：
create_async_engine → async_sessionmaker → async with → Alembic upgrade head

测试：
pytest fixture → 测试数据库 → TestClient → Mock 外部服务 → 覆盖率

部署：
Gunicorn + UvicornWorker → Nginx → Docker Compose → 优雅关闭

LLM：
httpx.AsyncClient(timeout=...) → SSE data: 格式 → 心跳 → 断连检测 → 错误帧 → Token 统计
```

---

## 33. 口诀总表

| 篇章 | 口诀 |
|---|---|
| 基础认知 | 基础先行、项目驱动、验收为准 |
| 项目搭建 | 虚拟环境隔离，依赖清单复现 |
| 核心用法 | 路由声明参数，Pydantic 校验，异常统一 |
| 高级特性 | 数据库会话短，缓存任务分 |
| 原理源码 | Uvicorn 跑 ASGI，事件循环怕阻塞 |
| 生产实践 | 容器可复现，AI 调用要兜底 |
| 常见问题 | 先分类再定位，日志请求 ID |
| 勘误 | 默认参数用 None，依赖锁定用工具 |
| 安全 | 认证授权两回事，JWT 过期刷新 |
| 可观测 | 日志指标追踪，请求 ID 串联 |
| 异步 DB | 异步 DB 会话短，Alembic 管迁移 |
| 交付 | 阶段不交付，学习不算数 |
| 部署 | Gunicorn 管进程，Uvicorn 跑 ASGI |
| LLM | SSE 要包格式，断连要检测 |
| 总原则 | 原笔记当索引，本篇当增补，项目当验收 |

---

> **结论**：这份完整笔记既是“地图”也是“生产级速查卡”。真正转化成工程能力，必须按阶段交付最小项目，并把安全、可观测性、异步 DB、测试、部署这五块补进真实代码里。  
> **一句话**：拿它做索引，拿项目做验收，拿速查表做面试复习。

---
