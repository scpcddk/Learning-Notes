# Spring6 Core(AOP + IOC) 精简学习笔记

> **目标**：应试 + 开发实用，剔除 XML，纯注解，适配 Spring6 / SpringBoot3

---

## 一、**IOC 核心思想与容器基础**

### 1. 核心思想

- **IOC**：对象创建、依赖管理的控制权从**应用程序**转移到 **Spring 容器**
- **容器**：`ApplicationContext`（如 `AnnotationConfigApplicationContext`）
- **Bean**：由 Spring 管理的对象

> ⚠️ **理解**：你不再 `new` 对象，而是向容器"要"对象

---

### 2. BeanFactory vs ApplicationContext（面试常问）

| 特性 | BeanFactory | ApplicationContext |
| ------ | ------------- | ------------------- |
| 加载时机 | **懒加载**（用时才创建） | **预加载**（启动时创建所有单例） |
| 功能 | 基础 IOC（Bean 创建、依赖注入） | 继承 BeanFactory + AOP、事件、国际化、资源加载 |
| 典型实现 | `XmlBeanFactory`（已废弃） | `AnnotationConfigApplicationContext` |
| 适用场景 | 资源受限环境（如嵌入式设备） | **绝大多数企业级应用** |

> [!TIP]
> **面试一句话**：ApplicationContext 是 BeanFactory 的**超集**，功能更完整，启动时预初始化，开发中几乎只用 ApplicationContext

---

### 3. **IOC 管理 Bean 的两种实现方式**

- 核心对比:

| 实现方式 | 技术核心 | 适用场景 |
| --------- | ---------- | ---------- |
| **方式一：包扫描 + 注解** | `@ComponentScan` + `@Component`及其派生注解 | **自己编写的类**（Service / DAO / Controller） → **开发最常用** 🔥🔥🔥 |
| **方式二：配置类 + @Bean** | `@Configuration` + `@Bean`方法 | **第三方类、需要复杂初始化、或者不能加注解的类**（如 `DataSource`, `RestTemplate`） 🔥🔥 |

---

#### (1)**方式一：包扫描 + 注解**（推荐自己写的类）

- **步骤**：
  - 在**配置类**或**启动类**上添加`@ComponentScan`（SpringBoot 中  `@SpringBootApplication`已隐含）
    - **启动类**:启动类是一个普通的 Java 类，内部包含`public static void main  (String[] args)`方法，该方法作为应用程序的**入口**,本身也是一个配置类
    - **配置类**:定义和注册 Spring 容器中的 Bean，或提供额外的**配置**（如数据源、拦截器、第三方库的初始化）
      - 将相关的一组 Bean 放在同一个配置类中，提高代码的可维护性
  - 在**类**上使用 `@Component` / `@Service` / `@Repository` / `@Controller` 标记
- **示例**：

```java
// 启动类（已包含包扫描）
@SpringBootApplication   // 默认扫描当前包及子包
public class App { ... }

// 业务类
@Service                 // 自动注册为 Bean
public class UserService { ... }
```

- **适用场景**：
  - ✅ **所有自己编写的 Service、DAO、Controller 组件**
  - ✅ **绝大多数业务类**
  - ✅ **无侵入、开发效率最高**

> 📌 **注意**：派生注解本质就是 `@Component`，只是增加了语义层（`@Service` 标识业务层，`@Repository` 标识数据层）

- **`@ComponentScan`自定义过滤**：有时需要排除某些类或包，避免冲突：

```java
@ComponentScan(basePackages = "com.example",
               excludeFilters = @ComponentScan.Filter(type = FilterType.REGEX,
                                                      pattern = "com.example.test.*"))
```

> 可通过`includeFilters`精确控制**只扫描**某些注解，面试偶尔会考"如何选择性不注册某个 Bean"

---

#### 🔥🔥 方式二：配置类 + @Bean（推荐第三方类 / 复杂初始化）

- **步骤**：
  1. **创建`@Configuration`类**
  2. 在**方法**上使用`@Bean`，方法返回**需要注册的对象**
  3. 容器启动时会自动调用该方法注册 Bean
- **示例**：

```java
@Configuration
public class AppConfig {

    // 注册第三方类（无法直接加 @Component）
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://localhost:3306/test");
        ds.setUsername("root");
        ds.setPassword("123456");
        return ds;
    }

    // 需要复杂初始化逻辑的对象
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate rt = new RestTemplate();
        // 可以设置超时、拦截器等复杂配置
        rt.setRequestFactory(new SimpleClientHttpRequestFactory());
        return rt;
    }
}
```

- **适用场景**：
  - ✅ **第三方 jar 包中的类**（如 `DataSource`, `RestTemplate`,   `RedisTemplate`）
  - ✅ **需要调用静态工厂方法、建造者模式创建的对象**
  - ✅ **需要复杂初始化（设置多个属性、条件判断）的 Bean**
  - ✅ **需要动态决定是否注册 Bean 的条件注册**（配合 `@Conditional`）

> 📌 **提示**：在 SpringBoot 中，很多第三方组件已通过 `AutoConfiguration` 自动配置，一般无需手动写 `@Bean`。但当默认配置不满足时，**可以用 `@Bean` 覆盖默认 Bean**

- **`@Configuration` 的 CGLIB 代理机制**
  - `@Configuration`类会被 CGLIB 代理，确保`@Bean`方法间的互相调用仍返回**容器中的单例**
  - 如果在普通`@Component`类中写`@Bean`，内部调用不会走代理，会产生多个实例。**因此只要涉及`@Bean`互相依赖，必须用`@Configuration`**

---

### 4. **常用注解汇总**（方式一专用）

| 优先级 | 注解 | 作用 | 示例 |
| :------: | ------ | ------ | ------ |
| 🔥🔥🔥 | `@Component` | 通用 Bean 标记 | `@Component` |
| 🔥🔥🔥 | `@Autowired` | **按类型注入**依赖 | `@Autowired`<br>`private UserService userService;` |
| 🔥🔥🔥 | `@Service` | **Service 层**（语义化）:实现业务逻辑，事务控制，调用 Repository | `@Service` |
| 🔥🔥 | `@Repository` | **DAO/Repository层**:封装数据库增删改查，转换异常 | `@Repository` |
| 🔥🔥 | `@Controller` / `@RestController` | **Web层**:接收 HTTP 请求，调用 Service，返回响应 | `@RestController` |
| 🔥 | `@Qualifier` | 配合 `@Autowired` 按**名称**注入 | `@Qualifier("userDaoImpl")` |
| 🔥 | `@Value` | 注入配置值 | `@Value("${jdbc.url}")` |
| 🔥 | `@Scope` | 指定作用域（`singleton` / `prototype`） | `@Scope("prototype")` |
| 🔥 | `@PostConstruct` / `@PreDestroy` | 初始化/销毁回调 | `@PostConstruct void init(){}` |
| 🔥 | `@Primary` | 声明同类型 Bean 的首选 | `@Primary` |
| 🔥 | `@ConfigurationProperties` | 绑定配置前缀到类 | `@ConfigurationProperties(prefix = "app")` |
| 🔥 | `@Resource` | JSR-250 标准，按**名称**注入 | `@Resource(name = "userDao")` |

- 💡 **方式二`@Bean`中也支持`@Autowired`注入参数**，方法参数会自动从容器中获取

---

#### (1)**辅助理解**:`@Autowired`注入原理

> [!NOTE]
> Spring 在 Bean 创建的属性填充阶段，通过一个特殊的 BeanPostProcessor 扫描带有注解的字段/方法，利用反射和依赖查找规则，将匹配的 Bean 注入进去

- **执行流程简化**
  1. **时机**  
     Bean 实例化之后，调用`populateBean()`填充属性时触发
  2. **处理器**  
    `AutowiredAnnotationBeanPostProcessor`介入，它已由`Spring`自动注册
  3. **缓存与扫描**  
    首次处理某个类时，扫描所有`@Autowired`字段和方法，包装成`InjectionMetadata`缓存起来，避免重复解析
  4. **逐个注入**  
      - **字段注入**：解析出依赖对象，直接用`Field.set()`暴力赋值  
      - **方法注入**：解析出所有参数依赖，反射调用`Method.invoke()`传入

- **依赖解析的核心匹配规则**
  - **按类型**查找所有兼容的候选 Bean
  - 若**多个候选**：  
    1. `@Primary` 优先  
    2. `@Priority`(值越小优先级越高)
    3. 均无，则**按名称匹配**（字段名或参数名）  
  - `@Qualifier` 可在任何阶段参与限定，实现精确注入
  - 支持 `required=false`、`Optional`、集合/Map 注入

- **特别之处**
  - **构造器注入**：发生在实例化阶段，更早，参数解析规则相同，但**无法解决循环依赖**(构造器注入要求在创建对象的同时就必须提供所有依赖)
  - **循环依赖**：字段和 setter 注入可利用三级缓存(先创建壳，后填充属性)**提前暴露半成品引用**来解决，构造器注入不行

> [!TIP]
> `@Autowired`：给字段或方法贴个标签，`Spring`在创建对象时会自动从容器里找到匹配的 `Bean`，然后用反射装上去。多个同类`Bean`时优先选`@Primary`或用名字匹配，找不到可设为非必须。本质就是**标记 → 自动装配**

---

#### (2)`@Autowired`vs`@Resource`vs`@Inject`对比

| 注解 | 来源 | 注入规则 | 是否支持 `required` |
| ------ | ------ | ---------- | --------------------- |
| `@Autowired` | Spring | **按类型** → 按名称 | ✅ `required = false` |
| `@Resource` | JSR-250 (Java) | **按名称** → 按类型 | ❌ 无 `required`，找不到抛异常 |
| `@Inject` | JSR-330 (Java) | 同 `@Autowired`（按类型） | ❌ 无 `required`，但支持 `Optional` |

> **开发建议**：Spring 项目用`@Autowired`；追求标准兼容性用`@Resource`（如需要与 Java EE 兼容）

- **注入集合/Map + `@Order` 排序**  
  - 当有多个同接口实现时，可直接注入`List<Interface>`或`Map<String, Interface>`（key 为 bean 名称）
  - 配合 `@Order(1)` 可控制 List 中的顺序（或 `jakarta.annotation.Priority`），常用于策略模式组装

---

## 二、**Bean 生命周期与作用域**

### 1. Bean 生命周期（完整阶段，面试高频）

- **简化流程**：

> 实例化 → 属性注入 → `BeanNameAware` / `ApplicationContextAware`  
> → `BeanPostProcessor` 前置处理 → `@PostConstruct` / `InitializingBean`  
> → 自定义 `init-method` → `BeanPostProcessor` 后置处理  
> → **Bean 就绪** → 容器关闭时 `@PreDestroy` / `DisposableBean` / 自定义 `destroy-method`

- **记忆关键**：**两个 PostProcessor 夹住初始化步骤**，销毁时也有回调

---

#### (1) 循环依赖三级缓存机制（面试必问）

Spring 通过**三级缓存**解决单例 Bean 的循环依赖（仅限字段注入和 Setter 注入）：

```java
一级缓存（singletonObjects）：成品 Bean（已完成初始化）
二级缓存（earlySingletonObjects）：半成品 Bean（已实例化，未注入属性）
三级缓存（singletonFactories）：Bean 工厂（用于生成代理对象）
```

**解决流程**：

1. A 实例化 → 放入**三级缓存**
2. A 属性注入发现需要 B
3. B 实例化 → 属性注入发现需要 A
4. 从**三级缓存**取 A 的工厂，生成半成品 A 注入 B
5. B 完成初始化 → 放入**一级缓存**
6. A 继续注入 B（已完成）→ A 完成初始化 → 放入**一级缓存**

> ⚠️ **构造器注入无法解决循环依赖**：因为构造器在实例化阶段就需要依赖，此时三级缓存还未放入
> ⚠️ **prototype 作用域无法解决循环依赖**：Spring 不缓存 prototype Bean

---

### 2. Bean 作用域详解

| 作用域 | 说明 | 适用场景 |
| -------- | ------ | ---------- |
| `singleton` | **整个容器共享一个实例**（默认） | 无状态 Service、DAO |
| `prototype` | **每次获取都创建新实例** | 有状态的 Bean（如用户会话临时对象） |
| `request` | **每个 HTTP 请求一个实例** | Web 环境下的一次请求处理 |
| `session` | **每个 HTTP Session 一个实例** | 购物车、用户登录信息 |
| `application` | **全局 ServletContext 一个实例** | 全局配置、共享缓存 |
| `websocket` | **每个 WebSocket 会话一个实例** | WebSocket 场景 |

> ⚠️ **prototype 的坑**：Spring 只负责创建，**不管理完整生命周期**（`@PreDestroy` 不会自动调用）
> ⚠️ **单例注入 prototype**：需要在 `@Scope` 上加 `proxyMode = ScopedProxyMode.TARGET_CLASS`，否则单例中的 prototype 永远只会有一个实例

- **示例**：

```java
@Component
@Scope(value = "prototype", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class TokenService {
    private String token;

    public String getToken() {
        if (token == null) {
            token = UUID.randomUUID().toString();
        }
        return token;
    }
}
```

---

## 三、**依赖注入**

### 1. **依赖注入三种方式**

#### 🔥🔥🔥(1) 字段注入（最简洁，开发常用）

```java
@Service
public class UserService {
    @Autowired
    private UserDao userDao;
}
```

#### 🔥🔥(2) 构造器注入（推荐不可变、单元测试友好）

```java
@Service
public class UserService {
    private final UserDao userDao;

    @Autowired   // Spring4.3+ 可省略（单构造器）
    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

#### 🔥(3) Setter 注入（可选依赖）

```java
@Service
public class UserService {
    private UserDao userDao;

    @Autowired
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

> [!TIP]
> ✅ **开发结论**：字段注入最方便；**构造器注入**最规范（推荐用于 `final` 字段）

---

### 2. 🔥 `@Profile`多环境配置

`@Profile`是 Spring 提供的一个环境切换注解，用来指定某个 **Bean 或配置类在特定环境下才生效**，不同环境注册不同的 Bean

```java
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean
    public DataSource dataSource() {
        // 开发环境：H2 内存数据库
        return new EmbeddedDatabaseBuilder().build();
    }
}

@Configuration
@Profile("prod")
public class ProdConfig {
    @Bean
    public DataSource dataSource() {
        // 生产环境：连接池
        return new HikariDataSource();
    }
}
```

**激活方式**：

- `spring.profiles.active=dev`（配置文件）(在 application.properties 或 application.yml 中设置)
- `-Dspring.profiles.active=prod`（JVM 参数）

> **使用场景**：不同环境（开发/测试/生产）使用不同的数据源、缓存、中间件配置

---

## 四、配置文件与条件装配

### 1. 配置文件绑定：`@ConfigurationProperties`

相比`@Value`，更适合结构化、可校验的配置：

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private int timeout;
    // getter/setter
}
```

配合 `@EnableConfigurationProperties` 或在 Boot 中自动支持，支持**松散绑定**、JSR303 校验。开发微服务时非常实用

---

### 2. 条件装配常用注解

Spring Boot 自动配置的基础，自己写 Starter 时必用：

| 注解 | 作用 |
| ------ | ------ |
| `@ConditionalOnClass` | **类存在**时生效 |
| `@ConditionalOnMissingBean` | 容器中**缺少指定 Bean** 时生效 |
| `@ConditionalOnProperty` | 配置文件中**有某项属性**时生效 |
| `@ConditionalOnExpression` | **SpEL 表达式为 true** 时生效 |
| `@ConditionalOnWebApplication` | **是 Web 应用**时生效 |

示例：只有存在`DataSource`类时才加载数据源配置

---

### 3. 🔥 Spring Boot 自动配置原理

`@SpringBootApplication` 拆解：

```java
@SpringBootApplication = 
    @Configuration //说明这个类本身是一个配置类
    + @EnableAutoConfiguration //导入了一个关键类：AutoConfigurationImportSelector
    + @ComponentScan //扫描当前包及子包，把@Service、@Controller 等注册为 Bean
```

> [!NOTE]
> `AutoConfigurationImportSelector`作用是去类路径下找一个配置文件，里面写满了“候选配置类”的名字，然后**根据条件决定用不用它们**

**自动配置流程**：

1. `@EnableAutoConfiguration` 导入 `AutoConfigurationImportSelector`
2. 读取`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（SpringBoot3）或`spring.factories`（旧版）
3. 通过`@ConditionalOnClass`、`@ConditionalOnMissingBean`等条件过滤
4. 满足条件的配置类生效，注册其中的`@Bean`

> **开发启示**：自定义 Starter 时，在`META-INF/spring/`下配置自己的自动配置类路径

---

## 五、AOP（面向切面编程）

### 1. 核心原理

- **动态代理**：
  - **有接口** → **JDK 动态代理**
    - **基于接口**，运行时生成实现相同接口的代理类（$Proxy），通过反射调用
    - **必须有接口**，代理对象和目标对象实现同一接口，不是继承关系
      - 目标类如果没有接口，JDK代理无法生成代理类
      - 代理对象**只能调用**接口中声明的方法，不能调用目标类的非接口方法
  - **无接口** → **CGLIB 字节码代理**
    - **基于继承**，运行时生成目标类的**子类**（EnhancerByCGLIB），通过字节码重写父类方法来加入增强逻辑
      - 非`final`类 + 非`final`方法 → ✅ 可以代理，可以增强
      - `final`方法 → 无法重写，❌ 不能增强
      - `final`类 → 无法被继承，❌ 根本不能代理
- **切面（Aspect）**：横切关注点（日志、事务、权限）的模块化
- **连接点（JoinPoint）**：**方法执行**
- **通知（Advice）**：切面在连接点执行的动作
- **切点（Pointcut）**：匹配连接点的表达式

> ⚠️ **记忆**：在**方法执行前后**插入代码，不侵入业务逻辑

---

### 2. **五大通知注解**（按执行顺序）

| 注解 | 时机 | 常用场景 |
| ------ | ------ | ---------- |
| `@Before` | 目标方法**执行前** | 参数校验、权限检查 |
| `@After` | 目标方法**执行后**（finally） | 资源清理、日志记录 |
| `@AfterReturning` | 目标方法**正常返回后** | 返回值增强、日志 |
| `@AfterThrowing` | 目标方法**抛异常后** | 异常处理、报警 |
| `@Around` | **环绕**（最强，可控制是否执行目标） | 性能监控、事务、缓存 |

**示例**：

```java
@Aspect
@Component
public class LogAspect {

    @Before("execution(* com.example.service.*.*(..))")
    public void logStart(JoinPoint jp) {
        System.out.println("方法执行前：" + jp.getSignature());
    }

    @Around("execution(* com.example.service.*.*(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();      // 执行目标方法
        long time = System.currentTimeMillis() - start;
        System.out.println("耗时：" + time + "ms");
        return result;
    }
}
```

---

### 3. **切点表达式最简写法**

```java
// 格式：execution(修饰符? 返回值类型 包名.类名.方法名(参数) 异常?)

// 1️⃣ 任意公共方法
execution(public * *(..))

// 2️⃣ com.example.service 包下任意类的任意方法
execution(* com.example.service.*.*(..))

// 3️⃣ 带一个 String 参数的方法
execution(* com.example.service.*.*(String))

// 4️⃣ 无参方法
execution(* com.example.service.*.*())

// 5️⃣ 返回值类型为 void 的方法
execution(void com.example..*.*(..))

// 6️⃣ 包及子包下所有方法（.. 匹配子包）
execution(* com.example..*.*(..))
```

> 💡 **开发口诀**：`*` 表示任意类型/方法名；`..` 表示任意参数或子包

---

### 4. 🔥 `@Pointcut` 复用最佳实践

实际开发建议将切点表达式抽离，集中管理：

```java
@Aspect
@Component
public class LogAspect {

    // 复用切点
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}

    @Pointcut("@annotation(com.example.aop.Loggable)")
    public void loggableMethods() {}

    // 组合使用
    @Around("serviceLayer() && loggableMethods()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        // ...
    }

    @Before("serviceLayer()")
    public void before() {
        // ...
    }
}
```

> **好处**：切点集中管理，修改一处全局生效，避免表达式散落在各个通知中。

---

### 5. 切点表达式进阶——常用指示符组合

除了 `execution`，还有：

| 指示符 | 含义 | 示例 |
|--------|------|------|
| `within` | 限定包/类 | `within(com.example.service.*)` |
| `this` | 代理对象为指定类型 | `this(com.example.service.UserService)` |
| `target` | 目标对象为指定类型 | `target(com.example.dao.UserDao)` |
| `args` | 匹配方法参数类型 | `args(java.lang.String)` |
| `@annotation` | 方法上有某注解 | `@annotation(com.example.log.Loggable)` |
| `@within` | 目标类上有某注解 | `@within(org.springframework.stereotype.Service)` |

**组合技巧**：`&&`（且）、`||`（或）、`!`（非），可实现复杂匹配。  
例如排除某个包：`execution(* com.example..*.*(..)) && !within(com.example.internal..*)`

---

### 6. AOP 自调用失效与解决

**问题**：同类内方法调用不会走代理，切面不生效。  
```java
public void methodA() {
    this.methodB(); // 直接调用，AOP 失效
}
```

**解决方案一**：通过 `AopContext.currentProxy()` 获取当前代理对象（需开启 `exposeProxy`）  
```java
((UserService) AopContext.currentProxy()).methodB();
```

**解决方案二**：注入自身代理对象  
```java
@Autowired
private UserService self;
public void methodA() {
    self.methodB();   // 走代理
}
```

---

### 7. 强制使用 CGLIB 代理

Spring Boot 默认对**有接口的类**使用 JDK 代理，无接口才用 CGLIB。  
但可以在 `application.properties` 中统一强制 CGLIB（常用在需要代理非接口方法或内部调用时）：

```properties
spring.aop.proxy-target-class=true
```

> ⚠️ 注意：CGLIB 无法代理 `final` 方法，不能被 `final` 修饰。

---

### 8. 🔥 Spring 事件机制（`ApplicationEvent`）

Spring 内置**发布-订阅**事件模型，用于解耦业务逻辑：

```java
// 1. 定义事件
public class OrderCreatedEvent extends ApplicationEvent {
    private Long orderId;
    public OrderCreatedEvent(Object source, Long orderId) {
        super(source);
        this.orderId = orderId;
    }
}

// 2. 发布事件
@Service
public class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;

    public void createOrder() {
        // 业务逻辑...
        publisher.publishEvent(new OrderCreatedEvent(this, 1001L));
    }
}

// 3. 监听事件
@Component
public class OrderEventListener {
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 发送短信、邮件等异步操作
    }
}
```

> **使用场景**：解耦业务逻辑（如订单创建后发送通知、更新统计），配合 `@Async` 实现异步处理。

---

## 六、声明式事务

### 1. 基础使用

```java
@Service
@Transactional
public class OrderService {
    public void createOrder() {
        // 数据库操作
    }
}
```

核心规则：

- 只需要运行时异常（`RuntimeException`）才自动回滚
- 可指定 `rollbackFor = Exception.class` 让所有异常回滚
- 默认传播行为是 `REQUIRED`（加入已有事务或新建）

---

#### 🔥 事务传播行为详解（7种）

| 传播行为 | 含义 | 使用场景 |
|----------|------|----------|
| `REQUIRED`（默认） | 有事务则加入，无则新建 | **最常用**，普通业务方法 |
| `REQUIRES_NEW` | 挂起当前事务，新建独立事务 | 日志记录、审计，**必须成功** |
| `SUPPORTS` | 有事务则加入，无则以非事务执行 | 查询方法 |
| `NOT_SUPPORTED` | 挂起当前事务，以非事务执行 | 发送通知、邮件 |
| `MANDATORY` | 必须有事务，否则抛异常 | 强制事务上下文 |
| `NEVER` | 必须无事务，否则抛异常 | 纯查询，禁止事务 |
| `NESTED` | 在当前事务中创建**嵌套事务**（savepoint） | 部分回滚场景 |

> **面试重点**：`REQUIRED` vs `REQUIRES_NEW` 的区别？前者共用事务（同回同滚），后者独立事务（互不影响）。

---

#### 🔥 事务隔离级别

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
```

| 隔离级别 | 解决问题 | 说明 |
|----------|----------|------|
| `DEFAULT` | - | 使用数据库默认级别（MySQL 默认 RC，Oracle 默认 RC） |
| `READ_UNCOMMITTED` | - | 最低级别，允许脏读 |
| `READ_COMMITTED` | 脏读 | 只能读到已提交数据（**Oracle/SQL Server 默认**） |
| `REPEATABLE_READ` | 脏读、不可重复读 | 同一事务内多次读取结果一致（**MySQL InnoDB 默认**） |
| `SERIALIZABLE` | 脏读、不可重复读、幻读 | 最高级别，串行执行，性能最差 |

> **面试关联**：Spring 的隔离级别只是"建议"，最终由数据库实现。

---

### 2. 事务失效清单（面试必问）

| 失效场景 | 原因 | 解决方案 |
|----------|------|----------|
| 方法非 `public` | Spring 代理只能拦截 public 方法 | 改为 public，或开启 AspectJ 模式 |
| 同类自调用 | `this.method()` 绕过代理 | 注入自身 `@Autowired` 或 `AopContext.currentProxy()` |
| 异常被 catch 未抛出 | 事务需感知到异常才会回滚 | 在 catch 中重新抛出，或手动 `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` |
| 异常类型非回滚异常 | 默认为 `RuntimeException` 及 `Error` | 配置 `@Transactional(rollbackFor = Exception.class)` |
| 数据库引擎不支持 | 如 MyISAM | 使用 InnoDB |
| 多线程调用 | 事务绑定线程，子线程不在事务内 | 重新设计事务边界，确保在事务线程内操作 |
| 方法被 `final` 修饰 | CGLIB 无法代理 final 方法 | 去掉 final |
| 未启用事务管理 | 缺少 `@EnableTransactionManagement`（SpringBoot 自动配置已包含，但纯 Spring 需手动） | 确认存在注解或 XML 配置 |

---

## 七、POM 核心配置（精简版）

> 仅记录 **parent**、**starter 依赖**、**打包插件** 三块，纯 SpringBoot3 项目必备

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.5</version>   <!-- SpringBoot3 → Spring6 -->
    <relativePath/>
</parent>

<dependencies>
    <!-- Web 开发（含 IOC + AOP 核心） -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- 若仅需 AOP（无 Web）可换成 -->
    <!--
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-aop</artifactId>
    </dependency>
    -->
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

> 📌 **说明**：`parent` 锁定 SpringBoot 版本；`spring-boot-starter-web` 已传递包含 `spring-context`、`spring-aop` 等；打包插件用于生成可执行 jar。

---

## 八、SpringBoot3 适配注意事项

### 1. `javax` → `jakarta` 命名空间变更

| Spring5 / SpringBoot2 | Spring6 / SpringBoot3 |
| ---------------------- | ---------------------- |
| `javax.servlet.*` | `jakarta.servlet.*` |
| `javax.persistence.*` | `jakarta.persistence.*` |
| `javax.validation.*` | `jakarta.validation.*` |
| `javax.annotation.*` | `jakarta.annotation.*` |

**修改点示例**：

```java
// 旧写法（Boot2）
import javax.annotation.PostConstruct;
import javax.servlet.http.HttpServletRequest;

// 新写法（Boot3）
import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
```

> ⚠️ **升级迁移**：所有 `javax.*` 必须替换为 `jakarta.*`，否则启动报错

---

### 2. 其他兼容性检查

- **JDK**：Spring6 + Boot3 需要 **JDK17+**（必选）
- **Tomcat**：需用 Tomcat 10+（因为支持 Jakarta EE）
- **Swagger / Knife4j**：需升级到支持 `jakarta` 的版本

---

## 九、日常开发易错点（避坑指南）

| ❌ 错误场景 | ✅ 正确做法 |
| ------------ | ------------ |
| `@Autowired` 字段为 `null` | 检查该类是否被容器管理（是否加 `@Component` 系列注解或 `@Bean`） |
| 循环依赖（A 依赖 B，B 依赖 A） | 推荐使用**构造器注入**，或使用 `@Lazy` 打破循环 |
| AOP 切面不生效（内部方法调用） | 同类内 `this.method()` 不会触发代理 → 通过代理对象调用或 `AopContext.currentProxy()` |
| `@Around` 忘记调用 `proceed()` | 必须 `pjp.proceed()`，否则目标方法不执行 |
| `@Transactional` 失效 | 检查：`@EnableTransactionManagement`、方法是否为 `public`、异常默认回滚 `RuntimeException` |
| 多实现类注入报错 | 使用 `@Primary` 或 `@Qualifier` 指定唯一依赖 |
| `@Value` 读取配置文件为 `null` | 确认类被 Spring 管理，且配置源已加载（`@PropertySource` 或 `application.yml`） |
| 切点表达式写错导致无通知 | 用 `@Pointcut` 定义切点，日志或 debug 检查切入点是否匹配 |
| 🆕 `@Configuration` 内 `@Bean` 互相调用 | 必须用 `@Configuration`，不能是 `@Component`，否则 CGLIB 代理失效 |
| 🆕 单例中注入 prototype 失效 | 在 `@Scope` 上添加 `proxyMode = ScopedProxyMode.TARGET_CLASS` |
| 🆕 `@Autowired` 注入 Map/List 时顺序异常 | 用 `@Order` 控制顺序，或使用 `@Priority` |
| 🆕 配置文件属性不生效 | 引入 `spring-boot-configuration-processor` 可选依赖，IDE 自动提示；使用 `@ConfigurationProperties` 代替 `@Value` |
| 🆕 事务方法内部调用另一事务方法，传播行为不生效 | 通过代理对象调用，或理解 `REQUIRED` vs `REQUIRES_NEW` 的区别 |

---

## 十、快速启动 Demo（SpringBoot3 + 注解）

```java
// 1. 启动类（隐含包扫描）
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}

// 2. 方式一：包扫描注册 Bean
@Service
public class UserService {
    public void save() {
        System.out.println("保存用户");
    }
}

// 3. 方式二：配置类注册第三方 Bean
@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

// 4. AOP 切面
@Aspect
@Component
public class TimeAspect {
    @Around("@annotation(com.example.annotation.TimeLog)")
    public Object logTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object ret = pjp.proceed();
        System.out.println("耗时：" + (System.currentTimeMillis() - start) + "ms");
        return ret;
    }
}
```

---

## **快速记忆口诀**

| 主题 | 口诀 |
| ------ | ------ |
| **IOC 两种注册方式** | **自己写的扫描，三方的 Bean** |
| **三种注入优先级** | **构造规范，字段方便，Setter 可选** |
| **AOP 代理选择** | **有接口 JDK，无接口 CGLIB** |
| **事务失效** | **非公、自调、吃掉、类型不对、final、多线程** |
| **生命周期** | **实例化 → 注入 → Aware → PostProcessor 前 → 初始化 → PostProcessor 后 → 销毁** |
| **循环依赖解决** | **三级缓存：成品 → 半成品 → 工厂** |

---
