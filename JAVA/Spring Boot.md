# Spring Boot 学习笔记

> 一份快速上手的核心知识总结，适合日常开发查阅。

---

## 1. 什么是 Spring Boot

- 基于 Spring 的快速开发框架，**简化 Spring 应用的搭建和配置**。
- 核心思想：**约定大于配置**，开箱即用。
- 内置 Tomcat / Jetty / Undertow，无需部署 war 包。

---

## 2. 核心特性

| 特性 | 说明 |
| ------ | ------ |
| **自动配置** | 根据依赖自动配置 Spring 及第三方库（如数据源、MyBatis） |
| **起步依赖** | 一个依赖整合一套功能（如 `spring-boot-starter-web`） |
| **内嵌服务器** | 直接运行 `main` 方法，`java -jar` 启动 |
| **Actuator** | 生产级监控端点（健康检查、指标、环境信息等） |
| **外部化配置** | 通过 `application.yml` / 环境变量 / 命令行参数统一管理配置 |

---

## 3. 快速开始

### 3.1 创建项目

使用 [Spring Initializr](https://start.spring.io) 或在 IDE 中新建 Spring Boot 项目。

### 3.2 主启动类

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

- `@SpringBootApplication` 包含：
  - `@SpringBootConfiguration`：配置类
  - `@EnableAutoConfiguration`：开启自动配置
  - `@ComponentScan`：扫描当前包及子包的组件

### 3.3 第一个 REST 接口

```java
@RestController
@RequestMapping("/api")
public class HelloController {

    @GetMapping("/hello")
    public String hello(@RequestParam(defaultValue = "World") String name) {
        return "Hello " + name;
    }
}
```

---

## 4. 配置文件

### 4.1 优先级

`application.yml`（或 `.properties`）可放在以下位置，优先级从高到低：

1. jar 包外部的 `config` 子目录
2. jar 包外部的当前目录
3. 类路径 `config` 包
4. 类路径根目录

### 4.2 基本写法（YAML）

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/test
    username: root
    password: 123456

my:
  custom:
    name: myApp
    version: 1.0
```

读取自定义配置：

```java
@Value("${my.custom.name}")
private String appName;
```

或者用 `@ConfigurationProperties` 绑定到 Bean。

---

## 5. 多环境配置（Profile）

### 5.1 配置文件命名

- `application-dev.yml`   → 开发环境
- `application-prod.yml`  → 生产环境
- 公共配置仍在 `application.yml` 中

### 5.2 激活指定环境

- 配置文件：`spring.profiles.active=dev`
- 启动参数：`--spring.profiles.active=prod`
- 环境变量：`SPRING_PROFILES_ACTIVE=prod`

### 5.3 条件 Bean

```java
@Bean
@Profile("dev")
public DataSource devDataSource() {
    // 仅 dev 环境生效
}
```

---

## 6. 常用注解速查

| 注解 | 作用 |
| ------ | ------ |
| `@SpringBootApplication` | 启动类复合注解 |
| `@RestController` | = `@Controller` + `@ResponseBody` |
| `@RequestMapping` | 映射请求路径，可放在类或方法上 |
| `@GetMapping / @PostMapping` | REST 风格请求映射 |
| `@RequestParam` | 获取请求参数 |
| `@PathVariable` | 获取路径变量（如 `/user/{id}`） |
| `@Autowired` | 按类型自动注入 |
| `@Qualifier` | 配合 `@Autowired` 按名称注入 |
| `@Value` | 读取配置文件值 |
| `@ConfigurationProperties` | 批量绑定配置到 Bean |
| `@Component / @Service / @Repository` | 声明 Spring 管理的 Bean |
| `@Transactional` | 声明事务 |
| `@PostMapping` | 处理 POST 请求 |
| `@RequestBody` | 接收 JSON 自动转成 Java 对象 |

---

## 7. 自动配置原理（简要）

- `@EnableAutoConfiguration` 通过 `spring-boot-autoconfigure` jar 包中的 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（Spring Boot 3.x）加载大量自动配置类。
- 每个自动配置类都用 `@ConditionalOnClass`、`@ConditionalOnMissingBean` 等条件注解，**按需生效**。
- 想查看当前生效的配置：启动时加 `--debug`，日志会打印自动配置报告。

---

## 8. 起步依赖（Starter）

常见 Starter：

- `spring-boot-starter-web`：Web 支持（Spring MVC + Tomcat）
- `spring-boot-starter-data-jpa`：JPA + Hibernate
- `spring-boot-starter-data-redis`：Redis
- `spring-boot-starter-test`：测试（JUnit5, Mockito）
- `spring-boot-starter-actuator`：监控端点

---

## 9. 启动后执行初始化代码

### 9.1 CommandLineRunner

应用启动完毕、所有 Bean 初始化后执行，接受原始命令行参数 `String... args`。

```java
@Component
@Order(1)  // 数值越小越先执行
public class MyStartupRunner implements CommandLineRunner {
    @Override
    public void run(String... args) throws Exception {
        System.out.println("=== CommandLineRunner 启动后执行 ===");
    }
}
```

### 9.2 ApplicationRunner

与 `CommandLineRunner` 类似，但参数是 `ApplicationArguments`，可以方便解析 `--key=value` 格式。

```java
@Component
@Order(2)
public class MyAppRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) throws Exception {
        System.out.println("非选项参数: " + args.getNonOptionArgs());
        System.out.println("选项参数名: " + args.getOptionNames());
    }
}
```

- 若启动时传入 `java -jar app.jar --debug --name=Spring`，`ApplicationRunner` 能直接拿到 `name` 的值。

> **注意**：`run` 方法内抛异常会导致启动失败；长时间阻塞会拖慢启动，建议异步处理。

### 9.3 与 `@PostConstruct` 区别

- `@PostConstruct`：**当前 Bean 初始化完成后立即执行**，此时其他依赖可能尚未就绪。
- `CommandLineRunner / ApplicationRunner`：**整个 Spring 容器完全启动后执行**，所有依赖就绪，适合需要数据库连接的初始化。

### 9.4 关于 `@Override`

- 实现接口方法时，建议**始终加上** `@Override` 注解。
- 它让编译器检查你是否真的正确重写了父类/接口方法，避免因拼写错误导致逻辑失效。

---

## 10. Actuator 监控

添加依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

默认暴露端点（Spring Boot 3.x）：

- `GET /actuator/health`      健康检查
- `GET /actuator/info`        应用信息（需配置）
- 其他端点如 `metrics`、`env`、`beans` 需手动开启：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env
```

---

## 11. 异常处理

### 11.1 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(RuntimeException.class)
    public Result handleRuntimeException(RuntimeException e) {
        return Result.error(e.getMessage());
    }
}
```

- `@RestControllerAdvice` = `@ControllerAdvice` + `@ResponseBody`

### 11.2 自定义错误页面

在 `src/main/resources/static/error/` 下放置 `404.html`、`500.html` 等，Spring Boot 会自动渲染。

---

## 12. 数据访问（简略）

- 加入 Starter，配置数据源，Spring Boot 会自动配置 `JdbcTemplate` 或 `DataSource`。
- 使用 JPA：只需定义接口 `JpaRepository<User, Long>`，无需实现类。
- MyBatis：引入 `mybatis-spring-boot-starter`，配置 mapper 位置即可。

---

## 13. 打包与部署

```bash
mvn clean package        # 或 gradle build
java -jar target/demo.jar
```

- 可将外部配置文件与 jar 同目录放置，以覆盖 jar 内配置。
- 支持注册为 Linux 服务（Systemd）或容器化部署。

---

## 14. 开发技巧与常见问题

- **热部署**：添加 `spring-boot-devtools` 依赖，修改代码后自动重启。
- **查看自动配置报告**：启动参数加 `--debug`。
- **日志级别**：`logging.level.root=info`，包级别：`logging.level.com.example=debug`。
- **排除自动配置类**：`@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})`
- **多个 Runner 顺序**：用 `@Order` 控制，数字小先执行。
- **不要忘记**：`ApplicationRunner` 和 `CommandLineRunner` 都会执行，但最好不要在同一个项目中混用太多，保持风格统一。

---
