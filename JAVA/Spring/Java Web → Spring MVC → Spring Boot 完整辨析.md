# Java Web → Spring MVC → Spring Boot 完整辨析

---

## 一、**演进总览**

```java
Java Web (Servlet/JSP)
    ↓  引入 Spring 框架，解耦层间依赖
Spring MVC (Spring Framework + MVC)
    ↓  约定优于配置，自动装配，内嵌容器
Spring Boot (Spring Framework + 自动配置)
```

> [!IMPORTANT]
> 三者是**层层封装、逐步简化**的关系。Spring Boot 底层仍是 Spring MVC，Spring MVC 底层仍是 Servlet

---

## 二、分阶段详解

### 1. Java Web（Servlet/JSP 时代）

[Java Web](<Spring MVC/JavaWeb.md>)

- **核心构成**：Servlet + JSP + JDBC + Tomcat + `web.xml`
- **特点**：基于 Servlet 规范，直接操作`HttpServletRequest/Response`；JSP 负责视图渲染
- **优点**：
  - **学习价值高**：深入理解 HTTP 请求处理、生命周期、线程模型
  - **无额外依赖**：仅依赖 Servlet 容器
  - **完全可控**：每个环节手动实现，无黑盒
- **缺点**：
  - **配置繁琐**：每个 Servlet 都要在 `web.xml` 注册，大量样板代码
  - **耦合严重**：业务逻辑、数据访问、视图渲染混杂
  - **重复劳动**：手动管理数据库连接、事务、JSON 解析
  - **测试困难**：强依赖容器，单元测试成本高

---

### 2. Spring MVC（Spring Framework 模块）

[Java MVC](<Spring MVC/Spring MVC.md>)

- **核心构成**：`DispatcherServlet` + Controller + `ModelAndView` + IoC 容器 + XML/注解配置
- **特点**：
  - **前端控制器模式**：`DispatcherServlet`统一接收请求，分发到`@Controller`
  - **IoC/DI**：通过 XML 或注解管理 Bean 生命周期，层间解耦
  - **AOP 支持**：声明式事务、日志、权限等横切关注点
  - **视图解析**：支持 JSP、Thymeleaf、FreeMarker 等
- **关键架构细节：父子容器机制**
  - **Root WebApplicationContext**（父容器）：管理 Service、Repository 等业务 Bean
  - **Servlet WebApplicationContext**（子容器）：管理 Controller、HandlerMapping 等 Web Bean
  - 子容器可访问父容器 Bean，反之不行。Spring Boot 通过自动配置统一了该行为，但结构依然存在
- **优点**：
  - **分层清晰**：MVC 三层架构，职责分离
  - **解耦彻底**：依赖注入降低组件耦合
  - **生态丰富**：Spring JDBC、Security、Transaction 等
  - **测试友好**：支持 Mock 对象，脱离容器单元测试
- **缺点**：
  - **配置冗长**：数据源、事务、视图解析器、组件扫描等仍需大量配置
  - **依赖管理复杂**：手动协调 Spring 各模块及第三方库版本（"Jar Hell"）
  - **部署依赖外部容器**：需将 WAR 包部署到独立 Tomcat/Jetty
  - **起步门槛高**：需理解 IoC、AOP、Bean 生命周期等

---

### 3. Spring Boot（快速开发框架）

[Spring Boot](<Spring Boot/Spring Boot.md>)

- **核心构成**：Spring Framework + 自动配置 + Starter 依赖 + 内嵌容器 + Actuator
- **特点**：
  - **约定优于配置**：自动推断并配置所需 Bean
  - **Starter 依赖**：如`spring-boot-starter-web`一键引入 Web 开发全套依赖（含 Spring MVC、Tomcat、Jackson）
  - **内嵌服务器**：Tomcat/Jetty/Undertow 内嵌，直接运行 JAR 包
  - **Actuator 监控**：内置健康检查、指标监控端点
- **自动配置核心原理**：
  `@EnableAutoConfiguration` → `AutoConfigurationImportSelector` → 扫描`META-INF/spring.factories`（Spring Boot 3.x 后为`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`）中的 `EnableAutoConfiguration` 实现类 → 组合条件注解（`@ConditionalOnClass`、`@ConditionalOnMissingBean` 等）
- **内嵌容器的根基**：Servlet 3.0 规范提供的 `ServletContainerInitializer` SPI。Spring 的 `SpringServletContainerInitializer` 在容器启动时回调，通过 `WebApplicationInitializer` 以代码方式注册 `DispatcherServlet`，从而彻底摆脱 `web.xml`
- **优点**：
  - **极速启动**：几分钟内搭建可运行项目，专注业务逻辑
  - **零配置开箱即用**：自动配置覆盖 80% 场景，剩余 20% 通过`application.properties/yaml`覆盖
  - **依赖版本托管**：Starter 自动管理兼容版本，告别 Jar Hell
  - **微服务原生**：配合 Spring Cloud 快速构建分布式系统
  - **独立运行**：`java -jar`直接启动，适合容器化（Docker/K8s）
- **缺点**：
  - **黑盒风险**：自动配置隐藏大量细节，出现问题时排查困难
  - **灵活性受限**：过度封装导致某些深度定制场景受限（需了解条件注解才能精准控制）
  - **启动速度相对慢**：自动扫描和配置过程在大型项目中可能耗时数秒
  - **内存占用较高**：内嵌容器 + 自动装载的 Bean 导致内存开销大于精简 Servlet 应用
  - **知识断层**：开发者可能只懂使用，不懂底层原理

---

## 三、**横向对比**

| 维度 | Java Web | Spring MVC | Spring Boot |
| ------ | ---------- | ------------ | ------------- |
| **配置方式** | `web.xml`手动配置 | XML + 注解，半自动 | 自动配置 + YAML/Properties |
| **依赖管理** | 手动引入 | 手动协调版本 | Starter 一键引入，版本托管 |
| **部署方式** | WAR → 外部 Tomcat | WAR → 外部 Tomcat | 内嵌容器，JAR 独立运行 |
| **开发效率** | 低（大量样板代码） | 中（需配置基础设施） | 高（专注业务） |
| **学习曲线** | 平缓（但后期复杂） | 陡峭（需理解 Spring 生态） | 平缓（入门快，深入难） |
| **可控性** | 完全可控 | 中等可控 | 封装较深，需专门学习 |
| **适用场景** | 教学、极轻量应用 | 中大型传统单体应用 | 微服务、云原生、快速原型 |

---

## 四、常见误区

| 误区 | 纠正 |
| ------ | ------ |
| **"Spring Boot = Spring MVC 的升级版"** | Spring Boot 是对**整个 Spring 生态的集成和自动化**。可排除 Web Starter，改用 WebFlux 做响应式开发，此时底层已不是 Spring MVC |
| **"Spring Boot 启动慢、内存大"** | Spring Boot 3 + AOT 编译 + GraalVM Native Image 可将启动时间压缩至毫秒级，内存大幅下降。但**开发模式**（热部署）与**生产模式**（Native）是两条线 |
| **"Spring Boot 完全零配置"** | 更准确的说法是 **"合理默认值 + 显式覆盖"**。一旦偏离默认约定（如自定义过滤器顺序、多数据源路由），仍需编写配置类。Starter 之间的自动配置冲突（如两个 DataSource 同时生效）反而更难排查 |

---

## 五、实践要点

### 1. Filter vs Interceptor

| 特性 | Filter（Servlet 层） | HandlerInterceptor（Spring MVC 层） |
| ------ | ---------------------- | ----------------------------------- |
| 管理方 | Servlet 容器 | Spring IoC 容器 |
| 拦截范围 | 所有请求（含静态资源） | 仅 Spring MVC 处理的请求 |
| 可获取信息 | `HttpServletRequest/Response` | HandlerMethod、ModelAndView |
| 适用场景 | 编码、安全校验、日志 | 权限细粒度控制、性能监控 |
| Spring Boot 配置 | `@Bean` 或 `@WebFilter` + `@ServletComponentScan` | 实现 `HandlerInterceptor` + 注册 `InterceptorRegistry` |

> [!WARNING]
> Filter 由 Servlet 容器管理，早于 Spring 容器启动，因此**Filter 中不能直接使用 `@Autowired`**。Spring Boot 中通过 `FilterRegistrationBean` 方式注册可解决此问题。

---

### 2. 异常处理演进

| 阶段 | 机制 |
| ------ | ------ |
| Java Web | `<error-page>` 在 `web.xml` 配置 |
| Spring MVC | `@ExceptionHandler`、`@ControllerAdvice` |
| Spring Boot | 在 MVC 基础上增添 `ErrorAttributes`、`BasicErrorController`，通过 `server.error.*` 属性定制错误页。`/error` 端点可被自定义 `ErrorController` 接管，实现统一 API 响应格式。 |

---

### 3. Fat JAR 的部署与陷阱

- **优势**：内嵌容器带来"一次构建、随处运行"，配合 Docker 实现不可变基础设施。
- **陷阱**：`LaunchedURLClassLoader` 的"嵌套 JAR"机制导致某些库（如 Swagger 静态资源扫描、MyBatis XML 映射文件扫描）在 Fat JAR 模式下失效。
- **解决**：使用 `ClassPathResource` 而非 `FileSystemResource`，或采用 Spring Boot 2.3+ 的**分层 JAR**（`layertools`）。

---

## 六、未来趋势

| 趋势 | 对应技术栈 | 适用场景 |
| ------ | ----------- | ---------- |
| **响应式/非阻塞** | Spring WebFlux（Spring Boot） | 高并发、流式数据、网关 |
| **云原生编译** | Spring Boot 3 + GraalVM Native | Serverless、边缘节点 |
| **轻量化运行时** | Quarkus、Micronaut | 对冷启动/内存极度敏感 |
| **虚拟线程革命** | Spring Boot 3.2+ + Java 21 Loom | 传统 MVC 高并发平滑迁移，无需改代码即可获得接近 WebFlux 的并发能力 |

---

## 七、**总结**

> [!IMPORTANT]
> **Java Web 是手动挡，Spring MVC 是自动挡，Spring Boot 是智能驾驶——但自动驾驶的底层仍是那套传动系统和道路规则。想上赛道竞速，你终究要打开引擎盖**

---

### 选择建议

- **学习阶段**：从 **Java Web（Servlet）** 入手，理解请求-响应本质，再过渡到 Spring Boot
- **传统/遗留项目**：若已基于 **Spring MVC**，无需强行迁移，可逐步引入 Spring Boot 简化配置
- **新项目/微服务**：直接选择 **Spring Boot**，配合 Spring Cloud 构建现代分布式系统
- **极致性能/边缘计算**：三者都可能过重，考虑 Quarkus 或 Spring Boot 3 + GraalVM Native

---
