---
markmap:
  initialExpandLevel: 3
---

# Spring Boot 学习笔记

> **定位**：初学者快速上手，进阶者速查。基础部分够用，进阶部分深挖

---

## 1. 一句话理解 Spring Boot

Spring Boot 是 **"约定大于配置"** 的快速开发框架

| 传统 Spring | Spring Boot |
| ------------- | ------------- |
| 写大量 XML 配置 | 几乎零配置，开箱即用 |
| 手动部署 Tomcat | 内置 Tomcat，`java -jar` 直接跑 |
| 依赖版本冲突 | Starter 一键引入兼容版本 |

**核心思想**：你只管写业务代码，配置交给框架猜

**核心特性**：

| 特性 | 说明 |
| ------ | ------ |
| **自动配置** | 根据依赖自动配置 Spring 及第三方库（如数据源、MyBatis） |
| **起步依赖** | 一个依赖整合一套功能（如 `spring-boot-starter-web`） |
| **内嵌服务器** | 直接运行 `main` 方法，`java -jar` 启动 |
| **Actuator** | 生产级监控端点（健康检查、指标、环境信息等） |
| **外部化配置** | 通过 `application.yml` / 环境变量 / 命令行参数统一管理配置 |

---

## 2. 5分钟跑起来

### 2.1 创建项目

去 [https://start.spring.io](https://start.spring.io)，勾选 **Web**，下载导入 IDE

### 2.2 主启动类

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

📌 **`@SpringBootApplication` = 配置类 + 自动配置 + 组件扫描**。把它放在根包（如 `com.example.demo`），Spring 会自动扫描它的子包

---

## 3. 写第一个接口

### 3.1 基础版

```java
@RestController              // 📌 声明：这是 REST 接口，返回数据不是页面
@RequestMapping("/api")      // 类前缀：所有方法路径前加 /api
public class HelloController {

    @GetMapping("/hello")
    public String hello(@RequestParam(defaultValue = "World") String name) {
        return "Hello " + name;
    }
}
```

**测试**：

```bash
curl http://localhost:8080/api/hello
curl http://localhost:8080/api/hello?name=Spring
```

### 3.2 **返回 JSON**（实际开发方式）

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // 📌 查：GET /api/users/123
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return new User(id, "Tom");
    }

    // 📌 增：POST /api/users（接收 JSON 自动转对象）
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }

    // 📌 改（全量更新）：PUT /api/users/123
    @PutMapping("/{id}")  //传完整对象，覆盖原有数据
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        return userService.save(user);
    }

    // 📌 改（局部更新）：PATCH /api/users/123
    @PatchMapping("/{id}")  //只传要改的字段，其余保留
    public User patchUser(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
        return userService.patch(id, updates);
    }

    // 📌 删：DELETE /api/users/123
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### 3.3 `@Controller` vs `@RestController`

| 注解 | 返回 `String` 时 | 适用场景 |
| ------ | ------------------ | ---------- |
| `@Controller` | 解析为**页面名**（如 `index.html`） | 服务端渲染（Thymeleaf） |
| `@RestController` | 直接作为**文本**返回 | REST API / 前后端分离 |

> 💡 **初学者记住**：写 API 用 `@RestController`，写页面用 `@Controller`

---

## 4. ==常用注解速查==

### **4.1 请求映射**

| 注解 | 作用 | 示例 |
| ------ | ------ | ------ |
| `@GetMapping` | 处理 GET | `@GetMapping("/users")` |
| `@PostMapping` | 处理 POST | `@PostMapping("/users")` |
| `@PutMapping` | 全量更新 | `@PutMapping("/users/{id}")` |
| `@PatchMapping` | 局部更新 | `@PatchMapping("/users/{id}")` |
| `@DeleteMapping` | 删除 | `@DeleteMapping("/users/{id}")` |
| `@RequestMapping` | 通用（可指定 method） | `@RequestMapping(value = "/api", method = GET)` |

### **4.2 参数获取**

| 注解 | 来源 | 示例 |
| ------ | ------ | ------ |
| `@RequestParam` | URL `?` 参数 | `@RequestParam String name` |
| `@PathVariable` | 路径 `/` 参数 | `@PathVariable Long id` |
| `@RequestBody` | 请求体 JSON | `@RequestBody User user` |
| `@RequestHeader` | 请求头 | `@RequestHeader("Authorization") String token` |

### **4.3 Bean 注入**

| 注解 | 说明 |
| ------ | ------ |
| `@Autowired` | 按类型注入（Spring 专属） |
| `@Resource` | 按名称注入（JDK 标准，推荐） |
| `@Qualifier` | 配合 `@Autowired` 指定名称 |

### **4.4 其他核心**

| 注解 | 作用 |
| ------ | ------ |
| `@Service` | 业务层 |
| `@Repository` | 数据层（自动转异常） |
| `@Component` | 通用组件 |
| `@Configuration` | 配置类 |
| `@Bean` | 在配置类中手动注册 Bean |
| `@Value` | 读取配置文件值 |
| `@Transactional` | 事务 |
| `@Valid` | 开启参数校验 |

---

## 5. 配置文件

### 5.1 基础写法（YAML）

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/test
    username: root
    password: 123456

# 自定义配置
my:
  app:
    name: demo
```

### 5.2 读取配置

**方式一：简单属性**（适合单个值）

```java
@Value("${my.app.name}")
private String appName;

@Value("${server.port:8080}")  // 📌 冒号后面是默认值
private int port;
```

**方式二：批量绑定**（适合对象）

```java
@Data
@Component
@ConfigurationProperties(prefix = "my.app")
public class MyAppProperties {
    private String name;
    private String version;
}
```

### 5.3 多环境配置

创建文件：

```java
application.yml        # 公共配置
application-dev.yml    # 开发环境
application-prod.yml   # 生产环境
```

激活方式（三选一）：

```yaml
# application.yml 中
spring:
  profiles:
    active: dev
```

```bash
# 启动时
java -jar app.jar --spring.profiles.active=prod
```

🔧 **进阶**：Spring Boot 2.4+ 支持 `spring.profiles.group` 分组配置

---

## 6. 数据访问（极简）

### 6.1 Spring Data JPA（一句话：定义接口，自动生成 SQL）

```java
// 1. 实体
@Entity
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String username;
}

// 2. 仓库（只需接口，零实现）
public interface UserRepository extends JpaRepository<User, Long> {
    // 方法名即查询：findBy + 字段名
    Optional<User> findByUsername(String username);
}

// 3. 使用
@Service
@RequiredArgsConstructor  // 📌 Lombok 生成带 final 字段的构造器
public class UserService {
    private final UserRepository userRepository;

    @Transactional
    public User create(User user) {
        return userRepository.save(user);
    }
}
```

### 6.2 MyBatis-Plus（国内常用）

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 内置 CRUD，无需写 SQL
}
```

🔧 **进阶**：复杂查询用 `@Select` 注解或 XML 文件

---

## 7. 统一响应与异常处理

### 7.1 统一响应体（前端友好）

```java
@Data
public class Result<T> {
    private Integer code;
    private String msg;
    private T data;
    private Long time = System.currentTimeMillis();

    public static <T> Result<T> ok(T data) {
        return new Result<>(200, "success", data);
    }
    public static <T> Result<T> error(String msg) {
        return new Result<>(500, msg, null);
    }
}
```

**Controller 返回**：

```java
@GetMapping("/{id}")
public Result<User> getUser(@PathVariable Long id) {
    return Result.ok(userService.findById(id));
}
```

### 7.2 全局异常处理（一处定义，全局生效）

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 参数校验失败（如 @NotBlank 触发）
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValid(MethodArgumentNotValidException e) {
        String msg = e.getFieldErrors().stream()
            .map(error -> error.getField() + ":" + error.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return Result.error(msg);
    }

    // 业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusiness(BusinessException e) {
        return Result.error(e.getMessage());
    }

    // 兜底
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        return Result.error("系统繁忙");
    }
}
```

### 7.3 参数校验

添加依赖：`spring-boot-starter-validation`

```java
@Data
public class UserDTO {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "长度 2-20")
    private String username;

    @Email(message = "邮箱格式错误")
    private String email;
}

// 使用
@PostMapping
public Result<User> create(@RequestBody @Valid UserDTO dto) {
    // 如果校验失败，自动抛异常，被上面的 GlobalExceptionHandler 捕获
}
```

---

## 8. 启动时执行代码

### 8.1 简单方式

```java
@Component
public class StartupRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("应用启动完成，执行初始化...");
    }
}
```

### 8.2 与 `@PostConstruct` 的区别

| 方式 | 执行时机 | 适用场景 |
| ------ | ---------- | ---------- |
| `@PostConstruct` | 当前 Bean 创建完 | Bean 内部初始化 |
| `CommandLineRunner` | **整个应用启动完** | 需要数据库连接等全局初始化 |

> 💡 **初学者**：需要预热缓存、加载字典数据 → 用 `CommandLineRunner`

---

## 9. 测试

### 9.1 接口测试（不用启动整个应用）

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldGetUser() throws Exception {
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.username").value("Tom"));
    }

    @Test
    void shouldCreateUser() throws Exception {
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{"username":"Tom"}"))
            .andExpect(status().isOk());
    }
}
```

### 9.2 单元测试（只测 Service 层）

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock private UserRepository repo;
    @InjectMocks private UserService service;

    @Test
    void shouldFindUser() {
        when(repo.findById(1L)).thenReturn(Optional.of(new User("Tom")));
        assertEquals("Tom", service.findById(1L).getUsername());
    }
}
```

---

## 10. 打包与部署

```bash
# 打包
mvn clean package -DskipTests

# 运行
java -jar target/demo.jar

# 指定配置运行
java -jar demo.jar --spring.profiles.active=prod --server.port=8080
```

**Docker 极简版**：
\
```dockerfile
FROM eclipse-temurin:17-jre-alpine
COPY target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

# 🔧 进阶专题

> 以下内容为高阶用法，初学者可先跳过，遇到实际问题再回来查

---

## A. 自动配置原理

Spring Boot 启动时，会读取 jar 包中的：

```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

里面列了所有自动配置类（如 `DataSourceAutoConfiguration`）。每个类用**条件注解**判断是否生效：

| 条件注解 | 含义 |
|----------|------|
| `@ConditionalOnClass` | classpath 有某类才生效 |
| `@ConditionalOnMissingBean` | 容器里没有该 Bean 才生效 |
| `@ConditionalOnProperty` | 配置项满足条件才生效 |

**查看生效的配置**：
```bash
java -jar app.jar --debug
# 看日志里的 Positive matches / Negative matches
```

**排除不需要的自动配置**：
```java
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class
})
```

---

## B. Actuator 监控

添加依赖后，默认暴露 `/actuator/health`（健康检查）和 `/actuator/info`。

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,loggers  # 或 "*" 暴露所有
  endpoint:
    health:
      show-details: always
```

**常用端点**：

| 端点 | 功能 |
|------|------|
| `/actuator/health` | 健康状态 |
| `/actuator/metrics` | JVM、CPU、HTTP 指标 |
| `/actuator/env` | 环境变量与配置 |
| `/actuator/loggers` | 查看/修改日志级别 |
| `/actuator/beans` | 所有 Spring Bean |

🔧 **进阶**：自定义健康检查，实现 `HealthIndicator` 接口。

---

## C. 跨域与拦截器

### C.1 全局跨域

```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");  // 生产环境写具体域名
        config.addAllowedHeader("*");
        config.addAllowedMethod("*");
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
```

### C.2 拦截器

```java
@Component
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        String token = req.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            res.setStatus(401);
            return false;  // 拦截
        }
        return true;  // 放行
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired private AuthInterceptor interceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(interceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/auth/**");
    }
}
```

---

## D. 日志与调优

### D.1 日志使用

```java
@Slf4j
@Service
public class UserService {
    public void doSomething() {
        log.debug("调试: {}", variable);   // 占位符，比拼接高效
        log.info("业务: userId={}", id);
        log.error("错误: {}", e.getMessage(), e);
    }
}
```

### D.2 配置

```yaml
logging:
  level:
    root: info
    com.example.demo: debug
  file:
    name: logs/app.log
  logback:
    rollingpolicy:
      max-file-size: 10MB
      max-history: 30
```

🔧 **进阶**：通过 Actuator 实时改日志级别（无需重启）。

### D.3 性能优化速查

| 优化项 | 配置 |
|--------|------|
| HTTP 压缩 | `server.compression.enabled=true` |
| JSON 忽略 null | `spring.jackson.default-property-inclusion=non_null` |
| 连接池 | HikariCP `maximum-pool-size` = CPU × 2 |
| 懒初始化 | `spring.main.lazy-initialization=true`（开发用） |
| 优雅停机 | `server.shutdown=graceful` |

---

## E. Spring Boot 3.x 新特性

### E.1 包名变更（重要！）

Spring Boot 3.x 基于 Jakarta EE 9，所有 `javax.*` 改为 `jakarta.*`：

| 旧（2.x） | 新（3.x） |
|-----------|-----------|
| `javax.persistence.*` | `jakarta.persistence.*` |
| `javax.validation.*` | `jakarta.validation.*` |
| `javax.servlet.*` | `jakarta.servlet.*` |

### E.2 原生镜像（GraalVM）

```bash
./gradlew bootBuildImage
# 编译为原生可执行文件，启动毫秒级，内存占用极低
```

### E.3 ProblemDetail（标准化错误）

Spring Boot 3.0+ 支持 RFC 7807 错误格式：

```java
@ExceptionHandler(BusinessException.class)
public ProblemDetail handle(BusinessException e) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(400, e.getMessage());
    pd.setProperty("code", e.getCode());
    return pd;
}
```

响应：
```json
{
  "type": "about:blank",
  "status": 400,
  "detail": "用户不存在",
  "code": 10001
}
```

---

## F. 避坑指南

| 坑 | 现象 | 解决 |
|----|------|------|
| **循环依赖** | Bean A 注入 B，B 注入 A，启动报错 | 重构；或用 `@Lazy` |
| **事务不生效** | 同类方法内调用 `@Transactional` 方法 | 拆分到另一个 Service，或注入自身代理 |
| **404 但路径对** | 启动类包层级不对，没扫描到 Controller | 启动类放根包，如 `com.example.demo` |
| **时区差 8 小时** | 数据库时间不对 | JDBC URL 加 `serverTimezone=Asia/Shanghai` |
| **JSON 字段为 null** | 响应里全是 null 字段 | `spring.jackson.default-property-inclusion=non_null` |
| **文件上传失败** | 默认限制 1MB | `spring.servlet.multipart.max-file-size=10MB` |
| **端口占用** | 8080 被占用 | `server.port=8081` |
| **@Value 取不到** | 配置项拼写错误或没加载 | 检查 YAML 缩进；或用 `@ConfigurationProperties` |

---

> **版本**：Spring Boot 3.2.x + JDK 17+ | 基础部分初学者必看，🔧 进阶部分按需查阅
