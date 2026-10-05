# MyBatis深度篇：源码级原理补充

> 以下内容针对评价中“源码深度仍有限”的反馈，补充 MyBatis 核心组件的源码级调用流程。目标是理解“为什么能工作”，而非逐行分析源码。

---

# 深度篇一：MapperProxy 源码调用流程

## 1.1 getMapper 的调用链

调用 `sqlSession.getMapper(StudentMapper.class)` 时，源码流程如下：

```text
SqlSession.getMapper(Class<T> type)
  → Configuration.getMapper(type, this)
    → MapperRegistry.getMapper(type, sqlSession)
      → knownMappers.get(type)        // 获取 MapperProxyFactory
        → mapperProxyFactory.newInstance(sqlSession)
          → MapperProxy 实例（JDK 动态代理）
```

`MapperRegistry` 内部维护了一个 `Map<Class<?>, MapperProxyFactory<?>> knownMappers`，在 MyBatis 初始化时，通过 `XMLConfigBuilder.parseConfiguration()` 解析 `<mappers>` 节点，将 Mapper 接口和对应的 `MapperProxyFactory` 注册进去。

## 1.2 MapperProxy.invoke() 的执行逻辑

`MapperProxy` 实现了 `InvocationHandler` 接口，核心方法 `invoke()` 的关键逻辑：

```java
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    // 1. 如果方法是 Object 的默认方法（如 toString、equals），直接执行
    if (Object.class.equals(method.getDeclaringClass())) {
        return method.invoke(this, args);
    }
    // 2. 获取或创建 MapperMethod 缓存
    MapperMethod mapperMethod = cachedMapperMethod(method);
    // 3. 执行 MapperMethod
    return mapperMethod.execute(sqlSession, args);
}
```

`MapperMethod` 是核心执行类，内部持有 `SqlCommand`（封装了 `namespace + id`）和 `MethodSignature`（封装了方法参数、返回值等信息）。`MapperMethod.execute()` 根据方法返回类型和 SQL 命令类型，最终调用 `sqlSession.selectOne()`、`sqlSession.insert()` 等方法。

## 1.3 Mapper 接口与 XML 的绑定时机

Mapper 接口与 XML 的绑定发生在 MyBatis 初始化阶段：

```text
SqlSessionFactoryBuilder.build(InputStream)
  → XMLConfigBuilder.parse()
    → XMLConfigBuilder.parseConfiguration()
      → mapperElement(XNode)           // 解析 <mappers> 节点
        → XMLMapperBuilder.parse()
          → XMLMapperBuilder.configurationElement()
            → XMLMapperBuilder.bindMapperForNamespace()
              → MapperRegistry.addMapper(type)
                → knownMappers.put(type, new MapperProxyFactory<>(type))
```

`XMLMapperBuilder.bindMapperForNamespace()` 的关键逻辑是：如果 `namespace` 对应的接口存在且尚未注册，则将其注册到 `MapperRegistry` 中。同时，`XMLStatementBuilder` 解析每个 `<select>`、`<insert>` 等标签，生成 `MappedStatement` 对象，存入 `Configuration.mappedStatements`。

---

# 深度篇二：Configuration 解析 XML 的过程

## 2.1 解析入口

MyBatis 通过 `XMLConfigBuilder` 解析全局配置文件，通过 `XMLMapperBuilder` 解析 Mapper XML 文件：

```text
XMLConfigBuilder.parse()
  → Configuration 实例创建
  → parseConfiguration(XNode root)
    → propertiesElement()          // <properties>
    → settingsAsProperties()       // <settings>
    → typeAliasesElement()         // <typeAliases>
    → pluginsElement()             // <plugins>
    → objectFactoryElement()       // <objectFactory>
    → environmentsElement()        // <environments>
    → typeHandlerElement()         // <typeHandlers>
    → mapperElement()              // <mappers>
```

## 2.2 Mapper XML 的解析过程

`XMLMapperBuilder.configurationElement()` 解析 `<mapper>` 节点的核心流程：

```text
<mapper namespace="...">
  → cacheElement()                 // <cache> 二级缓存
  → cacheRefElement()              // <cache-ref>
  → resultMapElements()            // <resultMap>
  → sqlElement()                   // <sql> 可复用片段
  → buildStatementFromContext()    // <select>/<insert>/<update>/<delete>
    → XMLStatementBuilder.parseStatementNode()
      → MappedStatement 构建
        → Configuration.addMappedStatement()
```

每个 `<select>` 标签最终被解析为一个 `MappedStatement` 对象，存入 `Configuration.mappedStatements`（一个 `StrictMap<String, MappedStatement>`，key 为 `namespace + "." + id`）。

## 2.3 Configuration 的核心数据结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `mappedStatements` | `Map<String, MappedStatement>` | 所有 SQL 映射，key = namespace + id |
| `resultMaps` | `Map<String, ResultMap>` | 所有结果映射 |
| `parameterMaps` | `Map<String, ParameterMap>` | 所有参数映射 |
| `caches` | `Map<String, Cache>` | 所有二级缓存 |
| `interceptorChain` | `InterceptorChain` | 插件链 |
| `typeHandlerRegistry` | `TypeHandlerRegistry` | 类型处理器注册表 |
| `languageRegistry` | `LanguageDriverRegistry` | 语言驱动注册表 |

---

# 深度篇三：一级缓存与二级缓存源码

## 3.1 一级缓存：PerpetualCache

一级缓存实现在 `BaseExecutor` 中，使用 `PerpetualCache` 作为底层存储。`PerpetualCache` 的默认实现极其简单，内部就是一个 `HashMap`：

```java
public class PerpetualCache implements Cache {
    private final String id;
    private final Map<Object, Object> cache = new HashMap<>();
    // putObject / getObject / removeObject 直接委托给 HashMap
}
```

`BaseExecutor.query()` 中一级缓存的查询逻辑：

```java
public <E> List<E> query(MappedStatement ms, Object parameter, ...) {
    if (queryStack == 0 && ms.isFlushCacheRequired()) {
        clearLocalCache();  // flushCache = true 时清空
    }
    List<E> list;
    try {
        queryStack++;
        list = resultHandler == null ? (List<E>) localCache.getObject(key) : null;
        if (list != null) {
            handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
        } else {
            list = queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
        }
    } finally {
        queryStack--;
    }
    return list;
}
```

## 3.2 二级缓存：CachingExecutor 与 TransactionalCacheManager

二级缓存通过 `CachingExecutor` 装饰 `BaseExecutor` 实现。`CachingExecutor` 内部持有 `TransactionalCacheManager`，管理事务提交/回滚时的缓存写入：

```java
public class CachingExecutor implements Executor {
    private final Executor delegate;
    private final TransactionalCacheManager tcm = new TransactionalCacheManager();

    public <E> List<E> query(MappedStatement ms, Object parameter, ...) {
        Cache cache = ms.getCache();
        if (cache != null) {
            flushCacheIfRequired(ms);
            if (ms.isUseCache() && resultHandler == null) {
                List<E> list = (List<E>) tcm.getObject(cache, key);
                if (list == null) {
                    list = delegate.query(ms, parameter, rowBounds, resultHandler, key, boundSql);
                    tcm.putObject(cache, key, list);
                }
                return list;
            }
        }
        return delegate.query(ms, parameter, rowBounds, resultHandler, key, boundSql);
    }
}
```

`TransactionalCacheManager` 内部维护 `Map<Cache, TransactionalCache>`，`TransactionalCache` 的核心机制是：查询结果先暂存在 `entriesToAddOnCommit` 中，只有事务提交时才批量写入真正的二级缓存；如果事务回滚，则清空暂存区。

## 3.3 二级缓存的装饰器链

二级缓存默认使用 `PerpetualCache`，但可以通过装饰器叠加功能：

```text
PerpetualCache（基础 HashMap）
  → LruCache（LRU 淘汰策略）
    → SerializedCache（序列化/反序列化）
      → LoggingCache（日志统计）
        → SynchronizedCache（线程安全）
```

装饰顺序由 `<cache>` 标签的 `eviction` 属性决定，默认是 `LRU`。

---

# 深度篇四：Plugin 代理链与 InterceptorChain 源码

## 4.1 Plugin.wrap 的代理逻辑

`Plugin` 类实现了 `InvocationHandler`，`wrap()` 方法的核心逻辑：

```java
public static Object wrap(Object target, Interceptor interceptor) {
    Map<Class<?>, Set<Method>> signatureMap = getSignatureMap(interceptor);
    Class<?> type = target.getClass();
    Class<?>[] interfaces = getAllInterfaces(type, signatureMap);
    if (interfaces.length > 0) {
        return Proxy.newProxyInstance(
            type.getClassLoader(),
            interfaces,
            new Plugin(target, interceptor, signatureMap));
    }
    return target;
}
```

`getSignatureMap()` 解析 `@Intercepts` 和 `@Signature` 注解，得到“需要拦截的类 -> 需要拦截的方法集合”的映射。`getAllInterfaces()` 过滤出目标对象实现的、且在签名映射中存在的接口。

## 4.2 InterceptorChain.pluginAll()

`InterceptorChain` 维护一个 `List<Interceptor>`，在创建 Executor、StatementHandler 等核心组件时，依次应用所有拦截器：

```java
public Object pluginAll(Object target) {
    for (Interceptor interceptor : interceptors) {
        target = interceptor.plugin(target);
    }
    return target;
}
```

因此，如果有三个拦截器，最终的代理链是：

```text
Interceptor3(Interceptor2(Interceptor1(目标对象)))
```

调用时先经过 Interceptor3，再经过 Interceptor2，再经过 Interceptor1，最后到达目标对象。这就是 MyBatis 插件的“洋葱式”责任链。

## 4.3 插件在 Configuration 中的注册

插件在 `Configuration` 初始化时通过 `interceptorChain.addInterceptor()` 注册。在 Spring Boot 中，任何实现了 `Interceptor` 接口的 Spring Bean 会被 `MybatisAutoConfiguration` 自动注册到 `Configuration` 中。

---

# 深度篇五：SqlSessionTemplate 线程安全原理

## 5.1 DefaultSqlSession 为什么线程不安全

`DefaultSqlSession` 线程不安全的原因有两个：

1. **Connection 不是线程安全的**：`DefaultSqlSession` 持有 `Executor`，`Executor` 持有 `Transaction`（通常是 `JdbcTransaction`），`JdbcTransaction` 持有 `Connection`。如果多个线程共享同一个 `SqlSession`，它们将使用同一个 `Connection`，导致事务混乱。
2. **一级缓存使用 HashMap**：`BaseExecutor` 中的 `localCache` 是 `PerpetualCache`，底层是 `HashMap`，不是线程安全的。

## 5.2 SqlSessionTemplate 的 ThreadLocal 机制

`SqlSessionTemplate` 通过 JDK 动态代理和 `ThreadLocal` 实现线程安全：

```java
public class SqlSessionTemplate implements SqlSession {
    private final SqlSessionFactory sqlSessionFactory;
    private final ExecutorType executorType;
    private final SqlSession sqlSessionProxy;

    public SqlSessionTemplate(SqlSessionFactory sqlSessionFactory, ...) {
        this.sqlSessionProxy = (SqlSession) newProxyInstance(
            SqlSessionFactory.class.getClassLoader(),
            new Class[] { SqlSession.class },
            new SqlSessionInterceptor());
    }

    private class SqlSessionInterceptor implements InvocationHandler {
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            SqlSession sqlSession = getSqlSession(sqlSessionFactory, executorType, exceptionTranslator);
            try {
                Object result = method.invoke(sqlSession, args);
                if (!isSqlSessionTransactional(sqlSession, sqlSessionFactory)) {
                    sqlSession.commit(true);
                }
                return result;
            } catch (Throwable t) {
                // 异常时回滚
                throw t;
            } finally {
                if (sqlSession != null) {
                    closeSqlSession(sqlSession, sqlSessionFactory);
                }
            }
        }
    }
}
```

关键点：

- `SqlSessionTemplate` 本身是单例，但每次方法调用都通过 `SqlSessionInterceptor` 获取一个 `SqlSession`。
- `getSqlSession()` 内部使用 `TransactionSynchronizationManager` 的 `ThreadLocal<Map<Object, Object>>` 保存每个线程对应的 `SqlSession`，确保同一线程内复用同一个 `SqlSession`，不同线程之间互不干扰。
- 如果当前线程已在 Spring 事务中，`isSqlSessionTransactional()` 返回 `true`，不会自动提交，由 Spring 事务管理器统一提交/回滚。

---

# 深度篇六：MyBatis-Plus 高级用法

【第三方扩展】

## 6.1 LambdaQueryWrapper 类型安全查询

`LambdaQueryWrapper` 是 MyBatis-Plus 提供的类型安全条件构造器，通过方法引用指定字段，编译期即可校验字段是否存在：

```java
@Service
public class StudentService {

    private final StudentMapper studentMapper;

    public StudentService(StudentMapper studentMapper) {
        this.studentMapper = studentMapper;
    }

    public List<Student> query(StudentQuery query) {
        LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.hasText(query.getName()), Student::getName, query.getName())
               .eq(query.getAge() != null, Student::getAge, query.getAge())
               .ge(query.getMinScore() != null, Student::getScore, query.getMinScore())
               .orderByDesc(Student::getScore);
        return studentMapper.selectList(wrapper);
    }
}
```

相比 `QueryWrapper` 的字符串字段名，`LambdaQueryWrapper` 避免了硬编码字段名，重构时更安全。

## 6.2 代码生成器 FastAutoGenerator

MyBatis-Plus 3.5.1+ 推荐使用 `FastAutoGenerator` 替代旧的 `AutoGenerator`：

```java
public class CodeGenerator {
    public static void main(String[] args) {
        FastAutoGenerator.create(
                "jdbc:mysql://localhost:3306/order_db",
                "root", "123456")
            .globalConfig(builder -> builder
                .author("dev")
                .outputDir(System.getProperty("user.dir") + "/src/main/java")
                .disableOpenDir())
            .packageConfig(builder -> builder
                .parent("com.example")
                .moduleName("order")
                .entity("entity")
                .mapper("mapper")
                .service("service")
                .controller("controller"))
            .strategyConfig(builder -> builder
                .addInclude("order", "order_item")
                .addTablePrefix("t_", "order_")
                .entityBuilder()
                    .enableLombok()
                    .logicDeleteColumnName("deleted")
                .controllerBuilder()
                    .enableRestStyle())
            .execute();
    }
}
```

## 6.3 公共字段自动填充

通过 `MetaObjectHandler` 实现创建时间、更新时间的自动填充：

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

实体类字段标注：

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

---

# 深度篇七：分库分表实践（ShardingSphere）

【第三方扩展】

## 7.1 ShardingSphere-JDBC 与 MyBatis 的协同

ShardingSphere-JDBC 是一个 JDBC 驱动层解决方案，嵌入应用内部，无需额外部署。它拦截 SQL 并进行分库分表的路由、改写和结果归并，对业务代码几乎无侵入。MyBatis-Plus 负责 ORM 和单表操作增强，ShardingSphere-JDBC 负责 SQL 路由，两者是协同工作的关系。

## 7.2 核心依赖

```xml
<!-- ShardingSphere-JDBC -->
<dependency>
    <groupId>org.apache.shardingsphere</groupId>
    <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
    <version>5.3.2</version>
</dependency>
<!-- MyBatis-Plus -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.3.1</version>
</dependency>
```

## 7.3 分片配置示例

以电商订单系统为例：日均订单 100 万，按 `order_id` 哈希取模分 2 个库，每个库分 16 张表：

```yaml
spring:
  shardingsphere:
    datasource:
      names: order_db_0, order_db_1
      order_db_0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/order_db_0
        username: root
        password: 123456
      order_db_1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/order_db_1
        username: root
        password: 123456
    rules:
      sharding:
        tables:
          order:
            actual-data-nodes: order_db_${0..1}.order_${0..15}
            database-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: db-hash-mod
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table-hash-mod
        sharding-algorithms:
          db-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 2
          table-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 16
```

## 7.4 常见坑

- **绑定表**：订单表和订单项表使用相同的分片规则时，需配置为绑定表，避免笛卡尔积关联。
- **广播表**：字典表等小表可配置为广播表，在所有库中冗余存储。
- **分布式主键**：ShardingSphere 集成雪花算法，配置机器标识确保不同节点生成的 ID 不重复。

---
