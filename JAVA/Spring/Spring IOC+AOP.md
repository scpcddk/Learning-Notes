# Spring6 IOC + AOP 精简学习笔记

> **目标**：应试 + 开发实用，剔除 XML，纯注解，适配 Spring6 / SpringBoot3

---

## 一、IOC（控制反转）

### 1. 核心思想

- **IOC**：对象创建、依赖管理的控制权从**应用程序**转移到 **Spring 容器**
- **容器**：`ApplicationContext`（如 `AnnotationConfigApplicationContext`）
- **Bean**：由 Spring 管理的对象

> ⚠️ **理解**：你不再 `new` 对象，而是向容器“要”对象

---

### 2. IOC 管理 Bean 的两种实现方式（核心对比）

| 实现方式 | 技术核心 | 适用场景 |
| --------- | ---------- | ---------- |
| **方式一：包扫描 + 注解** | `@ComponentScan` + `@Component` 及其派生注解 | **自己编写的类**（Service / DAO / Controller） → **开发最常用** 🔥🔥🔥 |
| **方式二：配置类 + @Bean** | `@Configuration` + `@Bean` 方法 | **第三方类、需要复杂初始化、或者不能加注解的类**（如 `DataSource`, `RestTemplate`） 🔥🔥 |

---

#### 🔥 方式一：包扫描 + 注解（推荐自己写的类）

**步骤**：

1. 在**配置类**或**启动类**上添加 `@ComponentScan`（SpringBoot 中 `@SpringBootApplication` 已隐含）
2. 在**类**上使用 `@Component` / `@Service` / `@Repository` / `@Controller` 标记

**示例**：

```java
// 启动类（已包含包扫描）
@SpringBootApplication   // 默认扫描当前包及子包
public class App { ... }

// 业务类
@Service                 // 自动注册为 Bean
public class UserService { ... }
```

**适用场景**：

- ✅ **所有自己编写的 Service、DAO、Controller 组件**
- ✅ **绝大多数业务类**
- ✅ **无侵入、开发效率最高**

> 📌 **注意**：派生注解本质就是 `@Component`，只是增加了语义层（`@Service` 标识业务层，`@Repository` 标识数据层）

---

#### 🔥🔥 方式二：配置类 + @Bean（推荐第三方类 / 复杂初始化）

**步骤**：

1. **创建 `@Configuration` 类**
2. 在**方法**上使用 `@Bean`，方法返回需要注册的对象
3. 容器启动时会自动调用该方法注册 Bean

**示例**：

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

**适用场景**：

- ✅ **第三方 jar 包中的类**（如 `DataSource`, `RestTemplate`, `RedisTemplate`）
- ✅ **需要调用静态工厂方法、建造者模式创建的对象**
- ✅ **需要复杂初始化（设置多个属性、条件判断）的 Bean**
- ✅ **需要动态决定是否注册 Bean 的条件注册**（配合 `@Conditional`）

> 📌 **提示**：在 SpringBoot 中，很多第三方组件已通过 `AutoConfiguration` 自动配置，一般无需手动写 `@Bean`。但当默认配置不满足时，**可以用 `@Bean` 覆盖默认 Bean**

---

### 3. 常用注解汇总（方式一专用）

| 优先级 | 注解 | 作用 | 示例 |
| :------: | ------ | ------ | ------ |
| 🔥🔥🔥 | `@Component` | 通用 Bean 标记 | `@Component` |
| 🔥🔥🔥 | `@Autowired` | **按类型注入**依赖 | `@Autowired`<br>`private UserService userService;` |
| 🔥🔥🔥 | `@Service` | Service 层（语义化） | `@Service` |
| 🔥🔥 | `@Repository` | DAO/Repository 层 | `@Repository` |
| 🔥🔥 | `@Controller` / `@RestController` | Web 层 | `@RestController` |
| 🔥 | `@Qualifier` | 配合 `@Autowired` 按**名称**注入 | `@Qualifier("userDaoImpl")` |
| 🔥 | `@Value` | 注入配置值 | `@Value("${jdbc.url}")` |
| 🔥 | `@Scope` | 指定作用域（`singleton` / `prototype`） | `@Scope("prototype")` |
| 🔥 | `@PostConstruct` / `@PreDestroy` | 初始化/销毁回调 | `@PostConstruct void init(){}` |

> 💡 **方式二 `@Bean` 中也支持 `@Autowired` 注入参数**，方法参数会自动从容器中获取

#### 辅助理解:`@Autowired`注入原理

> [!NOTE]
> Spring 在 Bean 创建的属性填充阶段，通过一个特殊的 BeanPostProcessor 扫描带有注解的字段/方法，利用反射和依赖查找规则，将匹配的 Bean 注入进去

- **执行流程简化**
  1. **时机**  
     Bean 实例化之后，调用 `populateBean()` 填充属性时触发
  2. **处理器**  
     `AutowiredAnnotationBeanPostProcessor`介入，它已由`Spring`自动注册
  3. **缓存与扫描**  
     首次处理某个类时，扫描所有 `@Autowired` 字段和方法，包装成   `InjectionMetadata` 缓存起来，避免重复解析
  4. **逐个注入**  
      - **字段注入**：解析出依赖对象，直接用 `Field.set()` 暴力赋值  
      - **方法注入**：解析出所有参数依赖，反射调用 `Method.invoke()` 传入

- **依赖解析的核心匹配规则**
  - **按类型**查找所有兼容的候选 Bean
  - 若多个候选：  
    1. `@Primary` 优先  
    2. `@Priority`（值越小优先级越高）  
    3. 均无，则**按名称匹配**（字段名或参数名）  
  - `@Qualifier` 可在任何阶段参与限定，实现精确注入
  - 支持 `required=false`、`Optional`、集合/Map 注入

- **特别之处**
  - **构造器注入**：发生在实例化阶段，更早，参数解析规则相同，但**无法解决循环依赖**
  - **循环依赖**：字段和 setter 注入可利用三级缓存提前暴露半成品引用来解决，构造器注入不行

> [!TIP]
> `@Autowired`：给字段或方法贴个标签`Spring`在创建对象时会自动从容器里找到匹配的 `Bean`，然后用反射装上去。多个同类`Bean`时优先选`@Primary`或用名字匹配，找不到可设为非必须。本质就是**标记 → 自动装配**

---

### 4. 依赖注入三种方式（按推荐优先级）

#### 🔥🔥🔥 字段注入（最简洁，开发常用）

```java
@Service
public class UserService {
    @Autowired
    private UserDao userDao;
}
```

#### 🔥🔥 构造器注入（推荐不可变、单元测试友好）

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

#### 🔥 Setter 注入（可选依赖）

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

> ✅ **开发结论**：字段注入最方便；**构造器注入**最规范（推荐用于 `final` 字段）

---

## 二、AOP（面向切面编程）

### 1. 核心原理

- **动态代理**：
  - 有接口 → **JDK 动态代理**
  - 无接口 → **CGLIB 字节码代理**
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

## 三、POM 核心配置（精简版）

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

## 四、SpringBoot3 适配注意事项

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

## 五、**日常开发易错点（避坑指南）**

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

---

## 六、快速启动 Demo（SpringBoot3 + 注解）

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
