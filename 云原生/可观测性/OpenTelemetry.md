# 《OpenTelemetry 完整学习与开发速查笔记》

> **适用环境**　以 Java 17+、Spring Boot、OpenTelemetry Java Agent 2.x 和本地 Collector 为例。理解一次 HTTP 调用的请求与响应。
> **学习目标**　看懂 Trace 和 Span，通过 OTLP 导出一条调用链，能定位链路中断、采样缺失和导出失败。
> **动手路线**　先按第 4 节启动 Collector，再用第 8 节的两个 Java 进程复现超时和链路中断。

---

# 第一篇　基础认知

## 1. Metrics、Logs 与 Traces

| 信号 | 回答的问题 | 服务调用示例 |
|---|---|---|
| Metrics 指标 | 故障何时开始，影响多少请求 | 订单 API 的错误率和 p95 延迟 |
| Logs 日志 | 某个事件发生时记录了什么 | 订单查询超时、库存检查失败 |
| Traces 追踪 | 一次请求经过哪些组件，各用了多久 | Gateway → 订单 API → MySQL 与库存接口 |

OpenTelemetry 约定如何产生、关联和导出遥测数据。应用经 SDK 或 Agent 产生信号，Collector 接收、处理和转发，后端负责存储与查询。只启动 Collector 的 `debug` exporter 可以看见数据经过，长期查询要接入对应后端。

---

## 2. Trace、Span 与 Context

```text
Trace 5f...  GET /orders/{id}                420 ms
              ├─ MySQL SELECT orders         25 ms
              └─ HTTP inventory-api            360 ms
                    └─ MySQL SELECT stock  320 ms
```

- **Trace ID** 标识一次分布式请求。**Span ID** 标识其中一个操作。父子关系解释调用来源，时间线显示操作是否并行。
- **Span** 记录操作名称、时长、状态、属性和事件。服务名、环境等描述遥测来源的信息通常放在 Resource。
- **Context** 保存当前操作的上下文。跨 HTTP 时，传播器注入并提取 W3C `traceparent` 等头部。下游从它创建子 Span，保持 Trace ID 一致。
- **Baggage** 可携带经选择的上下文键值，可能随请求传播到多个系统。限制字段和长度，禁止放凭据或敏感个人数据。

> [!warning]
> **易混淆**　父 Span 的耗时可包含子 Span。上例 420 ms 已包含库存查询耗时，直接把所有 Span 的耗时相加会重复计算。并行子 Span 也会互相重叠。

---

## 3. 接入方式与 Collector 组件

| 组件 | 职责 |
|---|---|
| Java Agent | 自动给支持的 Web、HTTP 客户端、JDBC 等库加观测能力 |
| SDK / API | SDK 管采样、处理和导出。API 可创建需要的业务 Span 或属性 |
| Receiver | 接收 OTLP 等协议的数据 |
| Processor | 做批处理、内存限制、采样或属性处理 |
| Exporter | 把数据输出到调试日志或远程后端 |
| Pipeline | 按信号把接收、处理、导出串起来。组件定义后还需要被 pipeline 引用 |

---

# 第二篇　接通一条 Trace

## 4. 本地 Collector 与 Java Agent

下载官方 Collector 和 Java Agent，准备可运行的 Spring Boot JAR。应用和 Collector 都直接在同一台机器运行。保存以下配置为 `otel-collector.yaml`。

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:4318 # 仅本地，接收 HTTP/protobuf
processors:
  batch: {}
exporters:
  debug:
    verbosity: detailed # 练习时方便查看 Trace ID 和属性
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
```

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
otelcol --config=otel-collector.yaml
```

另开终端，使用以下 Bash 命令启动应用。`order-api.jar` 和 `opentelemetry-javaagent.jar` 换成实际路径。

```bash
export OTEL_SERVICE_NAME=order-api
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
export OTEL_TRACES_SAMPLER=always_on # 仅用来验证本地链路
export OTEL_METRICS_EXPORTER=none
export OTEL_LOGS_EXPORTER=none
java -javaagent:opentelemetry-javaagent.jar -jar order-api.jar
```

请求一个已存在的业务端点，例如 `curl http://127.0.0.1:8080/orders/42`。在 Collector 输出中找 `service.name=order-api` 对应的资源和服务器 Span，记录 Trace ID。若应用调用另一个同样接入 Agent 的服务，核对下游 Span 与上游 Trace ID 一致，父 Span ID 对应调用链。

| OTLP 接入 | 常见端口 | 配置提示 |
|---|---|---|
| gRPC | `4317` | Collector 需启用 gRPC receiver，客户端协议填 `grpc` |
| HTTP/protobuf | `4318` | 通用 OTLP endpoint 自动使用 `/v1/traces` 等信号路径。若单独填 traces endpoint，要填写完整路径 |

---

## 5. 业务埋点与上下文关联

Agent 已能看见 HTTP 和 SQL 调用时，可为「检查库存」创建一个低基数的 `inventory.check` Span，增加规则类型和处理结果。创建时沿用当前 Context，结束时在 `finally` 调用 `span.end()`。异常时记录异常并按需要设置错误状态。

在已有 Java Agent、并引入 `opentelemetry-api` 的应用里，可以在订单服务的方法中这样包住现有规则计算。`Scope` 关闭时恢复前一个 Context，`span.end()` 则结束并提交这一段的记录。

```java
Tracer tracer = GlobalOpenTelemetry.getTracer("order-api");
Span span = tracer.spanBuilder("inventory.check").startSpan();
try (Scope scope = span.makeCurrent()) {
    span.setAttribute("inventory.check.type", "reservation");
    return inventory.check(skuId); // 已有业务逻辑
} catch (RuntimeException error) {
    span.recordException(error);
    span.setStatus(StatusCode.ERROR);
    throw error;
} finally {
    span.end();
}
```

线程池、异步任务和消息消费都可能跨越原始线程。使用受支持的自动埋点，或在提交任务时捕获并在执行时恢复 Context。HTTP 调用和消息头需要正确注入与提取。日志中的 `trace_id` 与 `span_id` 需要日志集成或明确注入，单独导出 Trace 不会为所有日志自动加字段。

---

## 6. 生产采样与资源控制

- **头部采样**在 Trace 开始时决定是否采集，开销可控。概率采样配合父级决策可保持上下游一致，低频故障可能没有样本。
- **尾部采样**在收集一段链路后再决定是否保留，例如优先保留错误和慢请求。Collector 需要缓存，同一 Trace 的 Span 要能汇聚到负责决策的实例。
- 监控 Collector 的拒收、丢弃、队列和导出失败。配置容量上限、批处理、传输鉴权和访问范围，数据过多时优先确定哪些属性和信号真正用于排障。

---

# 第三篇　排障与速查

## 7. 问题索引与 Cheat Sheet

| 现象 | 先检查 | 下一步 |
|---|---|---|
| Collector 没有任何 Trace | Agent 是否加载，有无真实请求，`4317` / `4318` 与协议是否对应 | 看启动日志和导出错误，核对监听地址及 pipeline |
| 上下游各有 Trace，但 ID 不同 | HTTP 或消息头中的上下文是否传播 | 排查网关转发、异步边界、框架支持和 Propagator 配置 |
| Collector 有数据，后端没有 | Exporter 地址、鉴权和队列指标 | 用 `debug` 临时验证入口，再分段检查出口 |
| Grafana 日志无法跳到 Trace | 日志是否带 Trace ID，数据源链接是否匹配 | 对比字段名、Trace 保留期和采样 |
| 数据量过大 | Span 生成速率、属性长度、重复埋点 | 移除无用埋点和敏感字段，评估采样和容量 |

**L1** 能区分信号和 Trace 层级。**L2** 跑通 Agent → Collector。**L3** 串起两服务并复现上下文丢失。**L4** 设计采样、容量、保留和日志跳转，能解释遗漏与丢弃的区别。

**记忆口诀**　指标找异常，日志看细节，Trace 串调用。上下文要传播，采集端要观察。

---

# 第四篇　两进程追踪、故障复现与 Collector 运维

## 8. 用 JDK 搭一个可验证的上下游调用

这个例子独立于已有 Spring Boot 应用。准备 JDK 17+、OpenTelemetry Java Agent 2.x 和第 4 节的 Collector。JDK 的 HTTP server 与 HTTP client 都有对应 Agent 埋点。业务应用只需要 JDK。把以下内容保存为 `TraceLab.java`。

```java
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

public class TraceLab {
    public static void main(String[] args) throws Exception {
        if (args.length != 2 || !(args[0].equals("inventory") || args[0].equals("orders"))) {
            throw new IllegalArgumentException("usage: TraceLab <inventory|orders> <port>");
        }
        String role = args[0];
        int port = Integer.parseInt(args[1]);
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(200)).build();

        if (role.equals("inventory")) {
            // 模拟慢下游。700 ms 大于上游设置的 400 ms 请求超时。
            server.createContext("/stock", exchange -> {
                if ("slow".equals(exchange.getRequestURI().getQuery())) {
                    try {
                        Thread.sleep(700);
                    } catch (InterruptedException error) {
                        Thread.currentThread().interrupt();
                        respond(exchange, 503, "inventory interrupted");
                        return;
                    }
                }
                System.out.println("inventory traceparent=" +
                        exchange.getRequestHeaders().getFirst("traceparent"));
                respond(exchange, 200, "in stock");
            });
        } else {
            // Java Agent 可在这次 HTTP 调用中注入当前 Trace 上下文。
            server.createContext("/orders", exchange -> {
                String path = "slow".equals(exchange.getRequestURI().getQuery())
                        ? "/stock?slow" : "/stock";
                HttpRequest request = HttpRequest.newBuilder(
                                URI.create("http://127.0.0.1:18082" + path))
                        .timeout(Duration.ofMillis(400)).GET().build();
                try {
                    var stock = client.send(request, HttpResponse.BodyHandlers.ofString());
                    respond(exchange, stock.statusCode() == 200 ? 200 : 502, stock.body());
                } catch (HttpTimeoutException error) {
                    respond(exchange, 504, "inventory timeout");
                } catch (InterruptedException error) {
                    Thread.currentThread().interrupt();
                    respond(exchange, 503, "orders interrupted");
                } catch (IOException error) {
                    respond(exchange, 502, "inventory unavailable");
                }
            });
        }
        server.start();
        System.out.printf("%s listening at 127.0.0.1:%d%n", role, port);
    }

    private static void respond(HttpExchange exchange, int status, String value) throws IOException {
        byte[] body = value.getBytes(StandardCharsets.UTF_8);
        try (exchange) {
            exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=UTF-8");
            exchange.sendResponseHeaders(status, body.length);
            exchange.getResponseBody().write(body);
        }
    }
}
```

### 8.1 启动和基线验证

先启动第 4 节的 Collector。运行 `javac --release 17 --add-modules jdk.httpserver TraceLab.java` 编译。沿用第 4 节的 OTLP endpoint、协议、采样和 exporter 配置，在两个分别设置环境变量的 Bash 终端启动 JVM。可设置 `OTEL_EXPORTER_OTLP_TIMEOUT=3000`，令实验导出失败更快被观察到。

```bash
# 终端 A，设置好第 4 节的 OTEL_* 环境变量
OTEL_SERVICE_NAME=inventory-api java --add-modules jdk.httpserver \
  -javaagent:opentelemetry-javaagent.jar -cp . TraceLab inventory 18082

# 终端 B，设置相同 exporter 参数
OTEL_SERVICE_NAME=order-api java --add-modules jdk.httpserver \
  -javaagent:opentelemetry-javaagent.jar -cp . TraceLab orders 18081
```

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl -si http://127.0.0.1:18081/orders
curl -si 'http://127.0.0.1:18081/orders?slow'
```

第一条预期 200，第二条预期 504。对于正常请求，Collector 输出应能识别订单服务的服务器 Span、订单服务的库存 HTTP 客户端 Span、库存服务的服务器 Span。核对同一个 Trace ID，库存进程的 `traceparent` 应包含上游 Client Span 的 ID。此处打印请求头是专为演练准备，生产只保留允许的关联字段。

### 8.2 三次对照实验

| 实验 | 预期业务现象 | Trace 证据 |
|---|---|---|
| 正常路径 | 订单返回 200 | 三个相关 Span，父子关系与 HTTP 链路吻合 |
| 库存变慢 | 订单在设定预算附近返回 504 | 客户端 Span 记录超时。下游可能继续执行直到完成或发现断开 |
| 库存进程停止 | 订单返回 502 | 有失败的客户端 Span，通常没有下游服务器 Span |
| 临时把两端的 `OTEL_PROPAGATORS` 设置为 `none` 后重启 | HTTP 仍可能返回 200 | 库存没有收到 `traceparent`，两边可各自产生独立 Trace |

恢复 `OTEL_PROPAGATORS=tracecontext,baggage` 后重新验证关联。HTTP 返回、接收到传播头、Telemetry 被导出、后端能查询是四个不同环节。一个环节正常不代表整条链路已通过。Trace 结束顺序也可能和请求完成顺序不同。

---

## 9. 让 Collector 有明确的处理容量和采样策略

在第 4 节 Collector 的 `processors` 中替换或增加下面两项，再把 pipeline 的 processors 改为 `[memory_limiter, batch]`。这些内存值用于本地演练，部署时根据容器上限、进程基线与并发估算。

```yaml
# 先限制 Collector 的内存开销，再批量导出以降低网络请求次数。
memory_limiter:
  check_interval: 1s
  limit_mib: 128
  spike_limit_mib: 32
batch:
  timeout: 2s
  send_batch_size: 256
```

限制内存能让过载时更容易观察到拒收，批处理减少出口请求次数。设置后应监控接收、拒绝、导出失败、队列使用率和处理延迟，避免只看 Collector 进程是否存活。下游后端停止时，重试和队列能力取决于 exporter 配置；磁盘持久队列需要额外组件和存储策略。先在隔离环境量化允许积压的时间。

### 9.1 头部与尾部采样的区别

| 策略 | 可根据什么决定 | 好处与限制 |
|---|---|---|
| 父级 + 概率头部采样 | Trace 开始时的上下文与 Trace ID | 避免上游已丢的数据继续堆积。低频错误可能未被采到 |
| 尾部采样 | 收集到的 Span、错误状态和时延 | 能优先保留错误和慢请求，增加 Collector 内存与延迟 |
| 本地 always-on | 练习的每次请求 | 容易核对调用链。生产先估算开销和数据量 |

尾部采样使用支持 `tail_sampling` 的 Collector 发行版，例如包含该处理器的 contrib 构建。多实例部署要让同 Trace 的 Span 到同一个决策节点。应用过早头部采样丢掉的 Trace，尾部采样无法补回来。

### 9.2 从调试输出切换到可查询后端

本地 `debug` exporter 适合核对字段和父子关系。正式环境使用 OTLP exporter 发送到兼容后端，明确传输协议、TLS、认证、超时和保留期。可以暂时保留一条小范围 debug 流辅助验收，但要保护日志里的属性和 URL。把服务名、环境、应用版本用于筛选和版本对比。业务标识按排障需要选取，避免带凭据、个人信息或大段请求体。

### 9.3 从 traceparent 和日志校验上下文

W3C `traceparent` 有版本、Trace ID、父 Span ID 和标记位四段。比如下列请求头中的 `01` 表示已设置 sampled 位。这个标志表达传播的采样决策，不能证明后端已存入这条 Trace。

**阅读提示**　这是 HTTP 头字段示例，字段值的分段由协议规定。

```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

服务把这个头提取为远程父 Context，创建新的 server span。业务再发 HTTP 时，传播的是当前出站 span 上下文。消息队列要通过消息属性或头传播；对批量消费、多来源或延迟处理场景，可根据消息语义建消费者 Span 并用 Span Links 关联多个消息的创建上下文。一个 Span 只有一个父级，可以有多个 Links。

Java Agent 和 Spring Boot Micrometer Tracing 的日志集成可能使用不同的 MDC 字段名。下面是使用 Java Agent 的 Logback MDC 集成时的模式片段，先用本地请求检查实际字段。异步和没有活跃 Span 的日志可能留空。

```xml
<!-- 只输出关联标识，方便用 Trace ID 跳转到追踪后端。 -->
<pattern>%d{ISO8601} %-5level trace_id=%X{trace_id} span_id=%X{span_id} %logger - %msg%n</pattern>
```

### 9.4 排查 Collector 自身的健康与数据丢失

Collector 自身指标常由本机 Prometheus 端点暴露，默认端口通常是 `8888`，监听范围与命名以发行版和配置为准。先确认端点，再从暴露内容挑出接收、拒绝、发送失败和队列容量的指标。不要只看 “进程 Ready”。

```bash
# 在 Collector 所在主机读取自监控指标，确认本版本的实际名称。
curl -fsS http://127.0.0.1:8888/metrics | grep -E 'receiver_(accepted|refused)|exporter_(send_failed|queue)'
```

若接收数上涨而导出失败同步上涨，优先查后端连接、认证和队列。若应用报告发送成功但接收端没变化，核对客户端端点是否指向当前 Collector。要确认丢失边界，可以在隔离环境短暂停止出口，恢复后检查队列是追平、拒收还是丢弃，并记录各自计数。 [Collector 自监控](https://opentelemetry.io/docs/collector/internal-telemetry/) · [消息 Span 语义](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/)

---

## 10. 信号关联与故障处理顺序

1. 从指标判断错误率或延迟改变的时间、服务和路由。
2. 从该窗口筛选错误 Trace，看最慢的客户端 Span、重试次数和错误边界。
3. 用同一 Trace ID 查上下游日志，核对依赖报错、实际响应和应用版本。
4. Trace 丢失时，逐段检查应用产生数据、Context 传播、Collector Receiver、Processor、Exporter、后端的索引与保留。
5. 做修复并重放同一测试请求。验证业务响应和观测数据都恢复。

| 现象 | 首要检查 |
|---|---|
| Java 启动但无 Span | Agent 参数、支持的库、是否产生真实请求和采样配置 |
| Collector HTTP 400、404 或连接拒绝 | 协议、绑定地址、端口、信号 endpoint 与 pipeline |
| 日志有 Trace ID，后端查不到 | Trace 是否采样，导出是否成功，租户或时间范围是否正确 |
| 单个请求出现两组重复 Span | Java Agent、Starter、手工埋点是否重复覆盖同一层 |
| Trace 断在异步任务或队列 | 注入和提取、线程切换、消费端新 Trace/Link 语义 |

**实战验收**　编译两个进程，拿到一条完整调用链。制造超时、下游停止和上下文断开，分别给出 HTTP 结果、上下游日志和 Trace 证据。能解释当前采样、导出和保留策略为什么足以覆盖所测故障。

官方实操　[Java Agent 支持的库](https://opentelemetry.io/docs/zero-code/java/agent/supported-libraries/) · [Collector 故障排查](https://opentelemetry.io/docs/collector/troubleshooting/) · [采样概念](https://opentelemetry.io/docs/concepts/sampling/)

延伸阅读　[Prometheus 与 Grafana](../数据库与中间件/Prometheus+Grafana.md) · [Loki](Loki.md) · [上下文传播](https://opentelemetry.io/docs/concepts/context-propagation/) · [Collector 配置](https://opentelemetry.io/docs/collector/configuration/) · [Java Agent 配置](https://opentelemetry.io/docs/zero-code/java/agent/configuration/)
