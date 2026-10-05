# MyBatis进阶篇

> 以下内容针对评价中提到的“原理深度偏浅”“批量与性能建议不足”“进阶主题未覆盖”等方向进行补充。所有内容仍以 **Java 17+、Spring Boot 3.x、MyBatis 3.5.x、mybatis-spring-boot-starter 3.x、MySQL 8.x** 为基准。

---

# 补充篇一：版本兼容性与依赖管理

## 1.1 mybatis-spring-boot-starter 版本矩阵

根据官方仓库的说明，各版本要求如下：

| Starter 版本 | MyBatis | MyBatis-Spring | Spring Boot | Java |
|---|---|---|---|---|
| 4.0.x | 3.5 | 4.0 | 4.0 | 17+ |
| 3.0.x | 3.5 | 3.0 | 3.2 – 3.5 | 17+ |
| 2.3.x | 3.5 | 2.1 | 2.5 – 2.7 | 8+ |

> ⚠️ 版本兼容性以官方兼容矩阵为准，生产项目建议通过父工程或 BOM 统一管理版本，避免在子模块中写死过旧版本。Spring Boot 3.x 必须使用 starter 3.x，底层要求 Java 17 和 Jakarta EE 9+。

## 1.2 MyBatis-Plus 与 Spring Boot 3.x 的版本匹配

从 Spring Boot 3.x 开始，推荐使用 MyBatis 3.5.x 系列。MyBatis-Plus 3.5.x 是与 Spring Boot 3.x 系列兼容的最佳选择。在实际项目中，需确保 MyBatis-Plus 依赖的 MyBatis 版本与 mybatis-spring-boot-starter 引入的 MyBatis 版本一致，否则可能报 `NoSuchMethodError`。

## 1.3 各进阶功能所需额外依赖

| 功能 | 需额外引入的依赖 | 说明 |
|---|---|---|
| Redis 二级缓存 | `org.mybatis.caches:mybatis-redis` | 兼容 MyBatis 3.4+ |
| `@MybatisTest` 切片测试 | `org.mybatis.spring.boot:mybatis-spring-boot-starter-test` | 提供 `mybatis-spring-boot-test-autoconfigure` |
| ShardingSphere 分库分表 | `org.apache.shardingsphere:shardingsphere-jdbc-core-spring-boot-starter` | 5.x 版本，支持 JDK17 |
| dynamic-datasource | `com.baomidou:dynamic-datasource-spring-boot-starter` | 提供 `@DS` 注解切换数据源 |

---

# 补充篇二：参数传递的精确边界

上一轮评价指出“单参数时 `#{}` 内名称可以任意”需要限定前提。精确结论如下：

| 参数类型 | `#{}` 内如何写 | 示例 |
|---|---|---|
| 单个简单类型（String、Integer、Long 等） | 任意名称，MyBatis 忽略 | `selectById(Long id)` → `#{anything}` |
| 单个对象（POJO / Map） | 必须写属性名或 Map key | `selectByStudent(Student s)` → `#{name}`、`#{age}` |
| 多参数（无 `@Param`） | `arg0/arg1`、`param1/param2`，或开启 `-parameters` 后用真实参数名 | `#{param1}`、`#{param2}` |
| 多参数（有 `@Param`） | 使用 `@Param` 指定的名称 | `@Param("name")` → `#{name}` |

核心原则：**多参数一律加 `@Param`**，不依赖编译器行为和隐式命名规则。

---

# 补充篇三：Executor 三种类型源码级区别

## 3.1 三种 Executor 对比

| 类型 | 触发方式 | Statement 策略 | 适用场景 |
|---|---|---|---|
| `SIMPLE`（默认） | `openSession()` | 每次执行新建 PreparedStatement，用完关闭 | 常规查询 |
| `REUSE` | `openSession(ExecutorType.REUSE)` | 以 SQL 为 key 缓存 Statement，复用同一 SQL 的 Statement | 同一 SQL 反复执行 |
| `BATCH` | `openSession(ExecutorType.BATCH)` | 攒批，调用 JDBC `addBatch`，直到 commit 或触发查询才批量执行 | 大批量写操作 |

## 3.2 执行器在调用链中的位置

```text
MapperProxy.invoke()
  → SqlSession.selectOne/insert/update
    → CachingExecutor.query/update   （二级缓存包装层）
      → SimpleExecutor / ReuseExecutor / BatchExecutor
        → StatementHandler
          → ParameterHandler + JDBC PreparedStatement
```

`CachingExecutor` 是所有 Executor 的外层包装，负责二级缓存查询和写入，内部委托给真正的 Executor。

---

# 补充篇四：MyBatis 插件（Interceptor）机制

## 4.1 可拦截的四大组件

| 拦截目标 | 接口 | 典型用途 |
|---|---|---|
| Executor | `org.apache.ibatis.executor.Executor` | 分页、读写分离、SQL 重写、执行时间统计 |
| StatementHandler | `org.apache.ibatis.executor.statement.StatementHandler` | SQL 改写、参数加工 |
| ParameterHandler | `org.apache.ibatis.executor.parameter.ParameterHandler` | 参数加密、参数校验 |
| ResultSetHandler | `org.apache.ibatis.executor.resultset.ResultSetHandler` | 结果集脱敏、字段填充 |

## 4.2 自定义 SQL 执行时间统计拦截器

```java
@Intercepts({
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class,
                       org.apache.ibatis.session.RowBounds.class,
                       org.apache.ibatis.session.ResultHandler.class})
})
public class SqlExecuteTimeInterceptor implements Interceptor {

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
            if (elapsed > 500) { // 慢 SQL 阈值
                System.err.println("慢 SQL [" + ms.getId() + "] 耗时 " + elapsed + "ms");
            }
        }
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        // 可从配置读取阈值
    }
}
```

注册方式（Spring Boot）：

```java
@Configuration
public class MyBatisPluginConfig {

    @Bean
    public SqlExecuteTimeInterceptor sqlExecuteTimeInterceptor() {
        return new SqlExecuteTimeInterceptor();
    }
}
```

MyBatis 的插件基于 JDK 动态代理实现：`Plugin.wrap(target, interceptor)` 为目标对象生成代理，调用链经过 `InterceptorChain` 时依次执行 `intercept()`。`@Intercepts` 中的 `@Signature` 精确指定拦截哪个类的哪个方法。

---

# 补充篇五：批量操作性能优化

## 5.1 两种批量插入方式对比

| 方式 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| `<foreach>` 拼多值 INSERT | 一条 SQL 插入多行 | 简单，无额外配置 | 数据量大时 SQL 极长，受 `max_allowed_packet` 限制 |
| `ExecutorType.BATCH` | 攒批，JDBC `addBatch` | 分批可控，内存友好 | 需手动管理 SqlSession 和分批提交 |

```java
// ExecutorType.BATCH 方式
try (SqlSession session = sqlSessionFactory.openSession(ExecutorType.BATCH)) {
    StudentMapper mapper = session.getMapper(StudentMapper.class);
    int batchSize = 500;
    for (int i = 0; i < list.size(); i++) {
        mapper.insert(list.get(i));
        if ((i + 1) % batchSize == 0) {
            session.flushStatements();
        }
    }
    session.commit();
}
```

## 5.2 关键性能参数

在 JDBC URL 中添加：

```text
jdbc:mysql://localhost:3306/db?rewriteBatchedStatements=true
```

`rewriteBatchedStatements=true` 让 MySQL 驱动将多条 INSERT 合并为一条高效的多值 INSERT。不配这个参数时，`ExecutorType.BATCH` 的性能通常远低于理论值，可能差一个数量级。配合 `ExecutorType.BATCH` 使用效果最明显。

## 5.3 大批量写入的推荐策略

```text
数据量 < 1000 条：  <foreach> 多值 INSERT 即可
数据量 1000 – 1万： ExecutorType.BATCH + rewriteBatchedStatements=true，分批 flush
数据量 > 1万：      生成 CSV 后 LOAD DATA INFILE，或分片写入
```

同时注意：增大 MySQL `max_allowed_packet`；批量插入期间可临时关闭非必要索引，插入后重建；设置 `flushCache=true` 避免一级缓存干扰。

---

# 补充篇六：缓存生产实践深化

## 6.1 二级缓存一致性挑战

MyBatis 二级缓存以 **Mapper namespace** 为单位。当多表关联查询时，跨 namespace 更新会导致脏读：

```text
OrderMapper 缓存了包含用户信息的订单
UserMapper 更新了用户信息
→ OrderMapper 缓存不会自动失效 → 脏读
```

解决方案：使用 `<cache-ref>` 让关联 Mapper 共享缓存刷新：

```xml
<!-- OrderMapper.xml -->
<cache/>
<cache-ref namespace="com.example.mapper.UserMapper"/>
```

这样 UserMapper 的任何写操作都会同时刷新 OrderMapper 的缓存。但需注意：`cache-ref` 共享缓存虽然能解决跨 namespace 脏读，也会让缓存依赖更复杂，需谨慎使用。

## 6.2 分布式场景：Redis 二级缓存

MyBatis 原生二级缓存基于 JVM 本地内存，集群环境下各节点缓存不共享。集成 Redis 需要额外引入依赖：

```xml
<dependency>
    <groupId>org.mybatis.caches</groupId>
    <artifactId>mybatis-redis</artifactId>
    <version>1.0.0-beta2</version>
</dependency>
```

然后在 Mapper 上配置：

```java
@CacheNamespace(implementation = RedisCache.class)
public interface IUserMapper { ... }
```

同时需要在 `resources` 根目录添加 `redis.properties` 配置文件：

```properties
host=localhost
port=6379
password=
database=0
```

实体类必须实现 `Serializable`。Redis 缓存使所有节点共享同一缓存区域，解决分布式一致性问题。

## 6.3 缓存副作用防控

| 风险 | 场景 | 对策 |
|---|---|---|
| 长会话脏读 | 一级缓存中 SqlSession 生命周期过长 | 设置 `local-cache-scope: statement` |
| 批量处理读到过期数据 | 循环中重复查询相同数据 | `@Options(flushCache = TRUE)` |
| 缓存击穿 | 热点 key 失效瞬间大量请求打到数据库 | 互斥锁重建缓存 |
| 缓存雪崩 | 大量 key 同时过期 | 过期时间加随机偏移 |

```yaml
mybatis:
  configuration:
    local-cache-scope: statement   # 每次查询后清空一级缓存
```

## 6.4 生产环境建议

**不要盲目开启二级缓存。** 数据更新频繁、多表关联复杂、分布式环境下，二级缓存带来的不一致风险往往大于收益。如果确实需要缓存，优先考虑在 Service 层使用 Spring Cache + Redis，控制粒度更精细，与业务逻辑耦合更清晰。

---

# 补充篇七：事务生产细节

## 7.1 传播行为速查

| 传播行为 | 含义 | 典型场景 |
|---|---|---|
| `REQUIRED`（默认） | 有事务加入，无则新建 | 绝大多数业务方法 |
| `REQUIRES_NEW` | 总是新建事务，挂起当前 | 日志记录、审计 |
| `NESTED` | 嵌套事务，可独立回滚 | 批量操作中单条失败不影响其他 |
| `SUPPORTS` | 有则加入，无则非事务执行 | 只读查询 |
| `NOT_SUPPORTED` | 非事务执行，挂起当前 | 耗时操作不占用事务 |

> ⚠️ `NESTED` 传播行为依赖 JDBC savepoint，不是所有数据库/驱动都支持，使用前需确认数据库兼容性。

## 7.2 隔离级别与只读事务

```java
@Transactional(
    isolation = Isolation.READ_COMMITTED,
    readOnly = true,
    timeout = 30
)
public Student getById(Long id) {
    return studentMapper.selectById(id);
}
```

`readOnly = true` 对 MySQL InnoDB 本身不改变读行为，但可作为语义提示，且某些连接池会据此优化。生产环境一般使用数据库默认隔离级别（MySQL 为 `REPEATABLE READ`）。

## 7.3 自调用失效与解决方案

```java
@Service
public class OrderService {

    public void createOrder() {
        this.deductStock();  // ❌ 自调用，@Transactional 失效
    }

    @Transactional
    public void deductStock() { ... }
}
```

原因：Spring AOP 代理只拦截外部调用。解决方案：注入自身代理、拆分为独立 Service、或使用 `AopContext.currentProxy()`。

---

# 补充篇八：延迟加载与 N+1 问题

## 8.1 延迟加载配置

```yaml
mybatis:
  configuration:
    lazy-loading-enabled: true
    aggressive-lazy-loading: false   # 必须关闭，否则延迟加载形同虚设
```

`aggressiveLazyLoading=true`（旧版默认）会在调用任意方法时加载所有延迟属性；设为 `false` 后，只有真正调用关联属性的 getter 时才触发加载。

## 8.2 N+1 问题

```text
1 次查询班级列表
+ N 次查询每个班级的学生列表
= N+1 次查询
```

解决方案：

| 方案 | 做法 | 效果 |
|---|---|---|
| JOIN + resultMap | 用 `<collection>` 嵌套结果映射，一次 JOIN 查出所有数据 | 彻底消除 N+1 |
| 批量查询 | 先查主表，再用 `IN` 批量查关联表 | 从 N+1 降到 2 次 |
| `fetchType="eager"` | 关联数据确定常用时立即加载 | 减少触发次数，但可能浪费 |

推荐：**关联数据确定需要时用 JOIN 嵌套结果映射**；关联数据可能不需要时用延迟加载 + 批量查询兜底。

---

# 补充篇九：多数据源与动态数据源

## 9.1 非 MyBatis-Plus 方案

Spring Boot 原生多数据源需要：

```text
1. 禁用 DataSourceAutoConfiguration
2. 手动配置多个 DataSource Bean
3. 为每个数据源配置独立的 SqlSessionFactory 和 MapperScan
4. 通过 @Qualifier 注入对应数据源
```

```java
@Configuration
@MapperScan(basePackages = "com.example.mapper.primary",
            sqlSessionFactoryRef = "primarySqlSessionFactory")
public class PrimaryDataSourceConfig { ... }

@Configuration
@MapperScan(basePackages = "com.example.mapper.secondary",
            sqlSessionFactoryRef = "secondarySqlSessionFactory")
public class SecondaryDataSourceConfig { ... }
```

## 9.2 dynamic-datasource（第三方扩展）

Baomidou 的 `dynamic-datasource-spring-boot-starter` 提供注解切换：

```java
@Service
public class UserService {

    @DS("master")
    public void write(User user) { ... }

    @DS("slave")
    public User read(Long id) { ... }
}
```

```yaml
spring:
  datasource:
    dynamic:
      primary: master
      datasource:
        master:
          url: jdbc:mysql://master-host:3306/db
        slave:
          url: jdbc:mysql://slave-host:3306/db
```

支持数据源分组、读写分离、`@DS` 方法级/类级切换、方法级优先级高于类级。

## 9.3 读写分离实现

基于 `dynamic-datasource` 的读写分离方案：

```text
1. 配置 master 和 slave 数据源
2. 写操作使用 @DS("master")，读操作使用 @DS("slave")
3. 或使用 AOP 切面根据方法前缀（select/query/get vs insert/update/delete）自动路由
4. 在事务中强制走主库，确保“写后立即读”能读到最新数据
```

> ⚠️ 读写分离下，“写后立即读”可能因主从复制延迟而读不到最新数据。解决方案：在事务中强制走主库，或使用 `@DS("master")` 显式指定。

---

# 补充篇十：SQL 审计与监控

## 10.1 基于 Interceptor 的 SQL 审计

```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class,
                       RowBounds.class, ResultHandler.class}),
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class})
})
public class SqlAuditInterceptor implements Interceptor {

    private static final Logger log = LoggerFactory.getLogger(SqlAuditInterceptor.class);

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
        Object parameter = invocation.getArgs().length > 1 ? invocation.getArgs()[1] : null;
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            log.info("SQL_AUDIT | id={} | cost={}ms | param={}",
                     ms.getId(), cost, parameter);
        }
    }
}
```

拦截器可在 `intercept` 中获取 SQL 语句、参数信息、执行时间等关键数据，实现日志审计。

## 10.2 生产配置提醒

开发阶段可临时使用：

```yaml
mybatis:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

**生产环境不要使用 `StdOutImpl`**，应使用 SLF4J 桥接，通过日志框架控制级别和输出目标：

```yaml
logging:
  level:
    com.example.mapper: DEBUG   # 只对指定 Mapper 包开 SQL 日志
```

生产环境建议：禁止在配置中硬编码数据库账号密码，应通过环境变量或配置中心动态注入，防止敏感信息泄露到代码仓库。

## 10.3 MyBatis 语句超时控制

MyBatis 提供了 `defaultStatementTimeout` 全局配置和 Mapper 级别的 `timeout` 属性，精准控制单条 SQL 的最大执行时长：

```yaml
mybatis:
  configuration:
    default-statement-timeout: 30   # 单位：秒
```

```xml
<select id="selectLargeData" timeout="10">
    ...
</select>
```

> ⚠️ `socketTimeout` 必须大于 MyBatis 语句超时、事务超时，避免上层提前终止而网络层还未触发。

---

# 补充篇十一：测试方案

## 11.1 分层测试策略

| 层次 | 测试内容 | 工具 |
|---|---|---|
| Mapper 接口测试 | 接口与 XML 映射是否正确 | `@MybatisTest`（切片测试） |
| SQL 映射测试 | 动态 SQL 分支是否覆盖 | `@MybatisTest` + H2 |
| 数据库集成测试 | SQL 在真实 MySQL 上的行为 | `@SpringBootTest` + Testcontainers |

## 11.2 @MybatisTest 切片测试

需要引入依赖：

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter-test</artifactId>
    <version>3.0.3</version>
    <scope>test</scope>
</dependency>
```

```java
@MybatisTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class StudentMapperTest {

    @Autowired
    private StudentMapper studentMapper;

    @Test
    void selectById_shouldReturnStudent() {
        Student student = studentMapper.selectById(1L);
        assertThat(student).isNotNull();
        assertThat(student.getName()).isEqualTo("Tom");
    }
}
```

`@MybatisTest` 只加载 MyBatis 相关配置，不启动整个 Spring 上下文，速度远快于 `@SpringBootTest`。默认情况下，它配置 MyBatis 组件、Mapper 接口和内存数据库，且测试基于事务并在结尾回滚。

---

# 补充篇十二：ExecutorType.BATCH 与 `<foreach>` 的选型决策

| 维度 | `<foreach>` 多值 INSERT | `ExecutorType.BATCH` |
|---|---|---|
| SQL 长度 | 随数据量线性增长 | 恒定 |
| 内存占用 | 需一次性构建完整 SQL | 流式，内存友好 |
| 网络交互 | 1 次 | 分批 N 次（可控） |
| 主键回填 | 支持 | 支持（需 `useGeneratedKeys`） |
| 配置复杂度 | 零 | 需管理 SqlSession |
| MySQL 优化 | 依赖 `max_allowed_packet` | 依赖 `rewriteBatchedStatements` |
| 推荐数据量 | < 1000 | 1000 – 1万 |

---

# 补充篇十三：常见生产问题速查

| 问题 | 优先检查 |
|---|---|
| 批量插入慢 | `rewriteBatchedStatements=true` 是否配置；是否用了 `ExecutorType.BATCH`；是否分批 flush |
| 内存暴增 | `aggressiveLazyLoading` 是否误开；是否在循环中触发延迟加载 |
| 缓存脏读 | 二级缓存是否跨 namespace；是否用 `<cache-ref>`；是否需要改用 Redis |
| 多数据源切换失败 | `@DS` 是否生效；方法级注解是否被类级覆盖；是否在自调用中 |
| 插件不生效 | `@Intercepts` 签名是否匹配；是否注册为 Spring Bean |
| Spring Boot 3 升级报错 | starter 是否升级到 3.x；是否使用 Jakarta 命名空间 |
| N+1 查询 | 是否在循环中调用 Mapper；是否该用 JOIN + `collection` 嵌套结果映射 |
| 慢 SQL 无法定位 | 是否配置了 SQL 审计拦截器；是否只对特定 Mapper 包开了 DEBUG 日志 |

---
