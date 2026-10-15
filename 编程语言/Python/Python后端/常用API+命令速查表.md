# 常用 API/命令速查表（详尽版）

> 说明：下表在原速查表基础上，增加 **作用**、**关键说明/示例** 两列，方便开发时直接查、面试前快速过。
>
> 一句话：**API 记住名字不够，必须知道它解决什么问题、什么时候用。**

---

## 1. FastAPI 路由与请求

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 定义 GET 路由 | `@app.get("/path")` | 注册 GET 接口，用于查询 | 幂等，浏览器可直接访问 |
| 定义 POST 路由 | `@app.post("/path")` | 注册 POST 接口，用于创建/提交 | 常用于提交 JSON，返回 201 |
| 定义 PUT/PATCH | `@app.put` / `@app.patch` | 全量/部分更新 | PUT 幂等，PATCH 不一定 |
| 定义 DELETE | `@app.delete("/path")` | 删除资源 | 常返回 204 |
| 路径参数 | `@app.get("/users/{uid}")` | 从 URL 路径取参数 | `uid: int` 自动转类型 |
| 查询参数 | `def f(q: str = "x")` | 从 `?q=` 取值 | 非路径声明的普通参数 |
| 请求体 | `def f(user: UserIn)` | 用 Pydantic 模型接收 JSON | 自动校验 + 文档 |
| 请求头 | `Header(...)` | 读取 HTTP 头 | 如 `Authorization` |
| Cookie | `Cookie(...)` | 读取 Cookie | 登录态常用 |
| 上传文件 | `UploadFile = File(...)` | 接收文件 | 大文件建议流式 |
| 路由前缀 | `APIRouter(prefix="/api")` | 拆分路由模块 | 项目模块化必备 |
| 状态码 | `status_code=201` | 指定响应码 | 创建成功用 201 |
| 响应模型 | `response_model=UserOut` | 声明响应结构 | 自动过滤敏感字段 |
| 依赖注入 | `Depends(get_db)` | 注入 DB、配置、鉴权 | 请求级资源管理 |
| 中间件 | `@app.middleware("http")` | 全局请求/响应处理 | 请求 ID、耗时统计 |
| CORS | `CORSMiddleware` | 跨域支持 | 生产用白名单 |
| 健康检查 | `@app.get("/health")` | 探活 | K8s/负载均衡依赖 |
| 挂载子应用 | `app.mount` | 挂载静态目录/子应用 | 如 `/static` |

> [!tip] 一句话
> 路由是“入口”，Depends 是“装配”，Pydantic 是“门卫”。

---

## 2. Pydantic 校验

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 请求模型 | `class UserIn(BaseModel)` | 声明入参结构 | 自动校验并生成文档 |
| 响应模型 | `class UserOut(BaseModel)` | 声明出参结构 | 可隐藏密码字段 |
| 字段约束 | `Field(min_length=1)` | 长度/范围/正则约束 | `Field(gt=0, le=150)` |
| 必填字段 | `name: str` | 不传报 422 | 必填 |
| 可选字段 | `name: str | None = None` | 可不传 | 默认 None |
| 默认值 | `age: int = 0` | 不传用默认 | 与可选区别：有默认 |
| 嵌套模型 | `class A(BaseModel): b: B` | 结构化复杂 JSON | 自动递归校验 |
| 列表模型 | `list[UserOut]` | 返回数组 | 文档友好 |
| 别名 | `Field(alias="userName")` | 兼容外部字段名 | `populate_by_name=True` |
| 枚举 | `class Role(str, Enum)` | 限定取值 | 只允许固定值 |
| 自定义校验 | `@field_validator` | 复杂业务校验 | Pydantic v2 语法 |
| 模型转换 | `model_dump()` / `model_dump_json()` | 转 dict/JSON | v2 替代 `dict()` |
| 从 ORM 转换 | `model_config = ConfigDict(from_attributes=True)` | 直接从 ORM 对象序列化 | 替代 v1 `orm_mode` |

> [!warning] ⚠️ 易混淆：422 vs 400
> 422 是 **Pydantic 校验失败**（框架自动）；400 是 **业务主动抛**（如参数语义不合法）。

---

## 3. 异常与响应

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 抛 HTTP 异常 | `raise HTTPException(404, "not found")` | 返回标准错误 | 客户端错误用 4xx |
| 统一错误响应 | 自定义异常处理器 | 统一格式 | `@app.exception_handler` |
| 请求校验异常 | `RequestValidationError` | 覆盖 422 格式 | 自定义返回体 |
| 服务端异常 | `Exception` 处理器 | 兜底 500 | 记日志 + 返回统一结构 |
| 自定义响应 | `JSONResponse` | 精确控制响应 | 如设置 header |
| 流式响应 | `StreamingResponse` | 分块返回 | SSE、大文件 |
| 重定向 | `RedirectResponse` | 302/301 | 登录跳转 |
| 文件响应 | `FileResponse` | 下载文件 | 自动 Content-Type |

> [!important] 必须记住
> 4xx = 客户端错；5xx = 服务端错；不要把所有失败都写成 500。

---

## 4. 异步与 HTTP 客户端

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 异步 HTTP 客户端 | `httpx.AsyncClient` | 异步发起请求 | 必须设 `timeout` |
| 同步 HTTP | `httpx.Client` / `requests` | 同步请求 | 不要在 async 中用 |
| 超时 | `timeout=30.0` | 防卡死 | 必须加 |
| 重试 | `httpx.HTTPTransport(retries=3)` | 网络抖动重试 | 只重试安全请求 |
| 并发请求 | `asyncio.gather` | 并发多个 I/O | 提高吞吐 |
| 超时取消 | `asyncio.wait_for` | 限制总耗时 | 防长尾 |
| 后台任务 | `BackgroundTasks` | 请求后执行 | 不可靠，短任务 |
| 事件循环 | `asyncio.run` | 启动协程 | 脚本入口 |
| 阻塞识别 | `time.sleep` / `requests` | 阻塞事件循环 | 用 `asyncio.sleep` / httpx |

> [!warning] ⚠️ 易混淆：`BackgroundTasks` vs Celery
> BackgroundTasks：进程内、不持久、不跨进程；Celery：分布式、可重试、可持久。

---

## 5. 数据库与 ORM（SQLAlchemy 2.0）

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 同步 Engine | `create_engine(url)` | 连接池入口 | 应用级单例 |
| 异步 Engine | `create_async_engine(url)` | 异步连接池 | MySQL 用 `aiomysql` |
| 连接池参数 | `pool_size` / `max_overflow` | 控制连接数 | 结合 DB 上限 |
| 防死连接 | `pool_pre_ping=True` | 使用前探活 | 必须加 |
| 回收连接 | `pool_recycle=3600` | 防 MySQL 断连 | < wait_timeout |
| Session 工厂 | `sessionmaker` / `async_sessionmaker` | 创建 Session | 每请求一个 |
| 请求级 Session | `Depends(get_db)` | 注入 + 自动关闭 | 防泄漏 |
| 模型基类 | `class Base(DeclarativeBase)` | ORM 基类 | 2.0 写法 |
| 表定义 | `__tablename__` / `Mapped` | 映射表 | 类型标注友好 |
| 查询 | `select(User).where(...)` | 2.0 查询 | 替代 `query()` |
| 主键查询 | `session.get(User, 1)` | 按主键取 | 简单快 |
| 新增 | `session.add(obj)` | 加入会话 | 需 commit |
| 更新 | `obj.name = "x"` | 改属性 | 需 commit |
| 删除 | `session.delete(obj)` | 删除 | 需 commit |
| 提交 | `session.commit()` | 持久化 | 事务成功 |
| 回滚 | `session.rollback()` | 撤销 | 异常时 |
| 预加载 | `selectinload` / `joinedload` | 防 N+1 | 关联查询必看 |
| 原生 SQL | `text("...")` | 复杂查询 | 参数化防注入 |

> [!important] 必须记住
> Engine 全局一个，Session 每请求一个，Connection 由连接池管理。

---

## 6. Alembic 迁移

| 场景 | 命令 | 作用 | 关键说明 |
|---|---|---|---|
| 初始化 | `alembic init -t async migrations` | 生成迁移目录 | 异步项目用 async 模板 |
| 自动生成 | `alembic revision --autogenerate -m "msg"` | 根据模型生成迁移 | 必须 review |
| 空迁移 | `alembic revision -m "msg"` | 手写迁移 | 数据迁移常用 |
| 升级 | `alembic upgrade head` | 升到最新 | 部署必跑 |
| 升级到指定 | `alembic upgrade <rev>` | 指定版本 | 分步上线 |
| 回滚一步 | `alembic downgrade -1` | 回滚 | 必须写好 downgrade |
| 查看当前 | `alembic current` | 当前版本 | 排错用 |
| 查看历史 | `alembic history` | 迁移链 | 冲突排查 |
| 生成 SQL | `alembic upgrade head --sql` | 只输出 SQL | 生产审查 |

> [!warning] ⚠️ 易混淆：Alembic vs SQLAlchemy
> SQLAlchemy 管 **ORM 映射**；Alembic 管 **数据库结构变更版本**。两者配合，不是二选一。

---

## 7. 测试

| 场景 | API/命令 | 作用 | 关键说明 |
|---|---|---|---|
| 测试框架 | `pytest` | 运行测试 | `pytest -q` 简洁 |
| 接口测试 | `TestClient(app)` | 不启服务器测接口 | 同步写法 |
| 异步测试 | `pytest-asyncio` | 跑 async 测试 | 加 `@pytest.mark.asyncio` |
| 夹具 | `@pytest.fixture` | 复用测试资源 | DB、Client |
| 参数化 | `@pytest.mark.parametrize` | 多组输入 | 边界值 |
| Mock | `unittest.mock` | 隔离外部依赖 | 不 mock 被测逻辑 |
| 测试 DB | 建表/回滚 | 隔离数据 | 每用例清空 |
| 覆盖率 | `pytest --cov` | 统计覆盖 | 关注核心逻辑 |
| 异步 DB fixture | `async_sessionmaker` | 测试用 Session | 事务回滚 |

> [!tip] 一句话
> 测试不是证明你对，是防止你以后改错。

---

## 8. Redis / 缓存 / 限流

| 场景 | API/命令 | 作用 | 关键说明/示例 |
|---|---|---|---|
| 连接 | `redis.asyncio.Redis` | 异步客户端 | 连接池复用 |
| 读写 | `get` / `set` | 缓存键值 | 设过期 |
| 过期 | `set(key, val, ex=60)` | 自动过期 | 防脏数据 |
| 计数 | `incr` | 原子自增 | 限流、计数 |
| 过期窗口 | `expire` | 设置 TTL | 配合 incr |
| 删除 | `delete` | 删缓存 | 更新 DB 后删 |
| 分布式锁 | `set(key, val, nx=True, ex=10)` | 加锁 | 释放需校验 value |
| 缓存穿透 | 空值缓存 / 布隆过滤器 | 防无效查询 | 空值短 TTL |
| 缓存击穿 | 互斥锁 / 逻辑过期 | 热点 key | 防并发打 DB |
| 缓存雪崩 | 过期加随机 | 防同时失效 | TTL 抖动 |

> [!warning] ⚠️ 易混淆：缓存 vs 队列
> 缓存存 **结果** 加速读；队列存 **任务** 异步做。都用 Redis，但目的不同。

---

## 9. Celery 任务队列

| 场景 | API/命令 | 作用 | 关键说明 |
|---|---|---|---|
| 创建应用 | `Celery("tasks", broker=..., backend=...)` | 定义 Celery | broker 存任务 |
| 定义任务 | `@celery_app.task` | 注册任务 | 可 bind |
| 异步发送 | `task.delay(args)` | 提交任务 | 立即返回 |
| 带选项发送 | `task.apply_async(args, countdown=5)` | 延迟/定时 | 更灵活 |
| 重试 | `self.retry(exc=..., countdown=5)` | 失败重试 | 需幂等 |
| 最大重试 | `max_retries=3` | 限制重试 | 防死循环 |
| 结果查询 | `AsyncResult(id).get()` | 取结果 | 别阻塞请求 |
| 定时任务 | `beat_schedule` | 周期执行 | 需 beat 进程 |
| 启动 worker | `celery -A app.tasks worker -l info` | 执行任务 | 可多 worker |
| 启动 beat | `celery -A app.tasks beat` | 定时调度 | 单实例 |
| 幂等 | 业务唯一键 + 状态机 | 防重复消费 | 关键 |
| 分库隔离 | broker/backend 分实例 | 防故障扩散 | 生产推荐 |

---

## 10. JWT / 安全

| 场景 | API/命令 | 作用 | 关键说明 |
|---|---|---|---|
| 密码哈希 | `pwd.hash(raw)` | 存密码 | bcrypt/argon2 |
| 密码校验 | `pwd.verify(raw, hashed)` | 登录验证 | 不存明文 |
| 生成 token | `jwt.encode(payload, key, alg)` | 签发 | 必须设 `exp` |
| 解析 token | `jwt.decode(token, key, algorithms=[...])` | 验签 | 必须指定算法 |
| 过期 | `exp` 字段 | 自动失效 | 短期 access |
| 刷新 | refresh token | 续签 | 双 token 模式 |
| 认证依赖 | `OAuth2PasswordBearer` | 提取 Bearer | 配合 Depends |
| 授权 | 检查资源归属/角色 | 防越权 | 认证≠授权 |
| CORS | `CORSMiddleware` | 跨域 | 白名单，不用 `*` |
| 密钥管理 | 环境变量 / SecretStr | 防泄漏 | 不硬编码 |
| 限流 | `redis.incr` + `expire` | 防刷 | 按 IP/用户 |

> [!important] 必须记住
> 认证 = 你是谁；授权 = 你能干什么。两者都要做。

---

## 11. 配置 / 日志 / 可观测性

| 场景 | API/命令 | 作用 | 关键说明 |
|---|---|---|---|
| 配置类 | `pydantic-settings` | 环境变量读取 | 校验 + 类型 |
| 环境隔离 | `.env` / `.env.prod` | 开发/生产分离 | 不提交密钥 |
| 日志 | `logging.getLogger` | 记录事件 | 分级 |
| 结构化日志 | JSON 格式 | 便于检索 | 生产推荐 |
| 请求 ID | 中间件 `X-Request-ID` | 链路串联 | 必加 |
| 指标 | `prometheus-fastapi-instrumentator` | 暴露 `/metrics` | 接 Prometheus |
| 链路 | OpenTelemetry | 跨服务追踪 | 微服务必备 |
| 健康检查 | `/health` | 探活 | K8s 依赖 |
| 就绪检查 | `/ready` | 依赖就绪 | DB/Redis 检查 |

---

## 12. 部署 / Docker

| 场景 | 命令 | 作用 | 关键说明 |
|---|---|---|---|
| 构建镜像 | `docker build -t app .` | 打包 | 多阶段构建 |
| 运行 | `docker run -p 8000:8000 app` | 启动容器 | 端口映射 |
| 环境变量 | `--env-file .env` | 注入配置 | 不写进镜像 |
| 查看日志 | `docker logs <id>` | 排错 | 必会 |
| Compose 启动 | `docker compose up -d` | 多服务 | API+DB+Redis |
| 生产启动 | `gunicorn -k uvicorn.workers.UvicornWorker` | 多进程 | 不用 `--reload` |
| 优雅关闭 | `--graceful-timeout 30` | 处理 SIGTERM | 用 exec CMD |
| Nginx | `proxy_buffering off` | SSE 必须关 | 长连接 |
| CI | GitHub Actions | 自动测试 | ruff + pytest |

> [!warning] 易错
> 开发用 `--reload`，生产用 Gunicorn + UvicornWorker；不要把密钥打进镜像。

---

## 13. 一句话总结

```text
路由用 FastAPI，校验用 Pydantic，注入用 Depends；
异步用 async/await，HTTP 用 httpx，超时必须设；
DB 用 SQLAlchemy，迁移用 Alembic，Session 每请求一个；
缓存队列用 Redis/Celery，安全用 JWT + 限流；
部署用 Docker + Gunicorn + UvicornWorker，日志带请求 ID。
```

**口诀：路由校验依赖，异步超时 DB，缓存队列安全，部署日志监控。**
