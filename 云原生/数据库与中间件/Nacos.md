# 《Nacos 完整学习与开发速查笔记》

> **适用环境**　已有 Spring Boot 基础。端口与控制台示例采用 Nacos 3.x，Spring 配置按 Spring Cloud Alibaba 2025.x 的 `spring.config.import` 方式说明。
> **学习目标**　会区分服务发现和配置管理，能定位注册失败、发现不到实例和配置不刷新的原因。
> **动手路线**　从第 7 节部署带认证的服务端，接第 3～4 节配置和第 8 节 Java 应用，再做故障演练。

---

# 第一篇　基础认知

## 1. 一个 Nacos，两种能力

| 能力 | 解决的问题 | 服务示例 |
|---|---|---|
| 服务注册与发现 | 实例 IP 和数量变化时，客户端如何找到它们 | 根据服务名查到两个 `catalog-api` 实例，再选择可用地址发请求 |
| 配置管理 | 环境配置如何集中发布、查询、监听和回滚 | 发布 `catalog-api.yaml`，控制商品列表的分页上限 |

```text
服务提供方 → 注册 IP、端口、元数据 → Nacos
服务调用方 ← 查询或订阅实例列表 ← Nacos
服务调用方 → 选择实例 → 直接访问服务提供方

管理员 → 发布配置 → Nacos → SDK 加载或接收变化 → 应用按支持方式生效
```

Nacos 提供实例列表。客户端负载均衡或调用框架负责选择实例、发送请求、设置超时。Kubernetes 内部已有 Service 和 DNS 时，可以先验证它们能否满足发现需求，再决定是否引入额外注册中心。

---

## 2. 命名空间、分组和标识

| 用途 | 资源定位 | 示例 |
|---|---|---|
| 配置 | `namespaceId + groupName + dataId` | 练习命名空间 ID / `CATALOG_LAB` / `catalog-api.yaml` |
| 服务 | `namespaceId + groupName + serviceName` | 练习命名空间 ID / `CATALOG_LAB` / `catalog-api` |
| 服务实例 | 服务下的集群、IP、端口等信息 | `catalog-api` 下两个不同的实例 |

> [!warning]
> **易混淆**　控制台里的命名空间名称用于显示，客户端通常填命名空间 ID。配置分组和发现分组分别设置，即使都写 `CATALOG_LAB`，仍是两条配置路径。

实例的健康、启用状态和权重可影响调用方拿到或选到哪些地址。临时实例适合随应用生命周期注册，持久实例适合由运营方管理的资源，健康检测和下线方式应按服务模型核对。

---

# 第二篇　动手配置与注册

## 3. 发布并读取一项配置

1. 按官方 Nacos 3.x 快速开始启动练习实例，登录管理控制台，创建名为 `catalog-dev` 的命名空间，记下其 ID。
2. 在这个命名空间创建 `CATALOG_LAB` 分组的 `catalog-api.yaml`，内容如下。用阈值模拟业务配置，凭据使用专门的密钥管理渠道。

```yaml
# Nacos 里的 Data ID 为 catalog-api.yaml
catalog:
  pagination:
    max-size: 50
```

3. Spring 项目使用与 Spring Boot、Spring Cloud 版本匹配的 Spring Cloud Alibaba BOM，引入 `spring-cloud-starter-alibaba-nacos-config`。把下面内容放进应用的 `application.yaml`，在本地设置 `NACOS_NAMESPACE_ID`。启用客户端鉴权的实例还需要提供相应凭据。

```yaml
spring:
  application:
    name: catalog-api
  config:
    import:
      - "nacos:catalog-api.yaml?group=CATALOG_LAB&refreshEnabled=true"
  cloud:
    nacos:
      config:
        server-addr: "${NACOS_ADDR:127.0.0.1:8848}"
        # 使用控制台显示的命名空间 ID，而非名称。
        namespace: "${NACOS_NAMESPACE_ID}"
```

启动后用测试断言 `Environment.getProperty("catalog.pagination.max-size", Integer.class)` 为 `75`，再把值改成 `78`，分别验证 Spring 环境和业务对象是否使用新值。配置发布成功、客户端收到变化、业务对象完成重绑是三个环节。对需要运行时更新的组件，明确使用框架支持的刷新方式，例如适用时的 `@RefreshScope`，并验证线程安全和重绑行为。

> [!note]
> 必需配置使用 `nacos:`，拉取失败时可以尽早暴露配置问题。应用具备可用默认值且可以独立启动时才考虑 `optional:nacos:`。

---

## 4. 注册两个实例并验证调用

另加 `spring-cloud-starter-alibaba-nacos-discovery`，把以下字段合并到同一个 `spring.cloud.nacos` 节点。`spring.application.name` 作为默认服务名。

```yaml
# 配置地址从当前应用的网络出发选择，核对服务发现与配置各自的命名空间和组。
discovery:
  server-addr: "${NACOS_ADDR:127.0.0.1:8848}"
  namespace: "${NACOS_NAMESPACE_ID}"
  group: CATALOG_LAB
```

使用不同的 `server.port` 启动两个 `catalog-api` 实例。控制台应显示两个实例。停止一个实例后，观察订阅者列表如何更新，并分别验证「Nacos 能查到实例」和「调用者可以访问实例的 HTTP 端口」。容器场景中，注册 IP 必须能从调用方所在网络访问。

---

## 5. 端口、鉴权与变更流程

| Nacos 3.x 默认端口 | 用途 |
|---|---|
| `8848` | SDK 常用的配置地址基准，也用于部分 HTTP API |
| `9848` | 客户端 gRPC，默认由主端口加 1000 推导 |
| `8080` | 3.x 独立管理控制台，按部署模式启用 |

浏览器能登录管理控制台只验证了控制台链路。应用端还需要连到 SDK 对应的端口，代理要按协议转发。生产实例应启用鉴权、按最小权限授权，并限制管理面访问。调整分页上限时，先在练习环境验证，再分批发布，保留配置历史和回滚步骤。

---

# 第三篇　排障与速查

## 6. 问题索引与 Cheat Sheet

| 现象 | 先看什么 | 继续检查 |
|---|---|---|
| 应用启动时报配置找不到 | `namespaceId`、`group`、`dataId` | 文件扩展名、导入方式、鉴权、SDK 连接 |
| 能访问控制台，SDK 超时 | SDK 日志中的 `8848` / `9848` | 容器或客户端到 gRPC 端口的连通性和代理模式 |
| 已发布但业务仍用旧分页上限 | Nacos 历史、客户端监听日志 | 数据来源优先级、刷新配置、Bean 绑定方式 |
| 注册成功但调用失败 | 注册 IP、端口、健康和启用状态 | 调用方到实例的网络及 HTTP 响应 |
| 同名服务找不到 | 服务名、命名空间 ID、发现分组 | 同时核对提供方、调用方和控制台筛选条件 |

**L1** 能口述发现与配置两条链路。**L2** 发布配置并注册两个实例。**L3** 复现分组错误、地址不可达和配置未刷新，区分根因。**L4** 设计多环境隔离、配置审计和回滚演练。

**记忆口诀**　发现看服务名，配置看 Data ID，两边都核对命名空间和组。

---

# 第四篇　从独立部署到故障演练

## 7. Docker Compose 部署带认证的 Nacos

独立目录 `nacos-lab/` 下放 `compose.yaml`。这个实验使用 `nacos/nacos-server:v3.1.1`、standalone 模式和命名数据卷。将管理控制台映射到 `18080`，保留 SDK 默认的 `8848` 与 `9848`，方便直接理解 gRPC 端口计算。命令适用于 Bash 或 WSL。

```yaml
# ports 左侧是宿主入口，右侧是容器端口。数据卷独立于容器重建。
services:
  nacos:
    image: nacos/nacos-server:v3.1.1
    environment:
      MODE: standalone
      NACOS_AUTH_ENABLE: "true"
      NACOS_AUTH_TOKEN: "${NACOS_AUTH_TOKEN:?set NACOS_AUTH_TOKEN}"
      NACOS_AUTH_IDENTITY_KEY: "nacosLabIdentity"
      NACOS_AUTH_IDENTITY_VALUE: "${NACOS_IDENTITY_VALUE:?set NACOS_IDENTITY_VALUE}"
    ports:
      - "127.0.0.1:18080:8080"
      - "127.0.0.1:8848:8848"
      - "127.0.0.1:9848:9848"
    volumes:
      - nacos-data:/home/nacos/data
volumes:
  nacos-data:
```

```bash
# 首次启动生成练习密钥。保留这些值以便同一环境重建。
export NACOS_AUTH_TOKEN="$(openssl rand -base64 48)"
export NACOS_IDENTITY_VALUE="$(openssl rand -hex 24)"
docker compose up -d
docker compose ps
docker compose logs --tail=100 nacos
```

打开 `http://127.0.0.1:18080/`。按控制台提示初始化管理员密码，之后用该账号做本地练习。生产应让应用使用专用账号和受限角色，管理员账号只用于管理。JWT 签名密钥应妥善保管，环境重建和多节点部署必须按计划管理密钥一致性与轮换。服务端数据卷也要纳入备份恢复。

| 访问方 | 正确地址 | 证据 |
|---|---|---|
| 宿主浏览器 | `http://127.0.0.1:18080/` | 可登录控制台、查看命名空间 |
| 宿主 Java SDK | `127.0.0.1:8848` | 配置导入和注册成功，SDK 会访问 `9848` |
| 同 Compose 网络中的客户端 | `nacos:8848` | 使用容器 DNS，访问对应 gRPC 端口 |
| 生产运维 | 受控管理网的控制台地址 | 管理员操作有审计，应用账号权限受限 |

> [!warning]
> 修改宿主的 SDK 基准端口后，通常还要配套暴露“新端口 + 1000”的 gRPC 入口。只把容器 `8848` 映射成 `18848`，客户端很可能会去找宿主 `19848`。使用负载均衡时，也要根据 Nacos 部署文档检查 gRPC 转发。

---

## 8. 一个 Maven 项目同时验证 Config 与 Discovery

### 8.1 固定练习版本

下面使用官方版本矩阵中的 Spring Boot `3.5.0`、Spring Cloud `2025.0.0`、Spring Cloud Alibaba `2025.0.0.0`。这是练习组合，正式部署应按组织的升级节奏重新选择兼容补丁并验证。JDK 17+，以已有 Maven 项目为起点，在 `pom.xml` 配置以下模块。

```xml
<!-- 放到 pom.xml 的对应节点，区分依赖版本管理、实际依赖与构建插件。 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.5.0</version>
    <relativePath/>
</parent>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>2025.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-alibaba-dependencies</artifactId>
            <version>2025.0.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
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

`mvn dependency:tree` 用来确认实际引入的 Nacos SDK 与 Spring 依赖版本。服务端和客户端分别有版本，控制台显示的服务端版本无法说明 Java 项目实际加载了哪个 SDK。版本不匹配时先定位异常来源与依赖树，避免随意覆盖单个依赖。

### 8.2 练习应用

先按第 3 节发布 `catalog-api.yaml`，在 `application.yaml` 保留第 3～4 节的配置和注册参数，同时加入公共认证参数。通过环境变量提供用户名、密码与命名空间 ID。

```yaml
# 配置地址从当前应用的网络出发选择，核对服务发现与配置各自的命名空间和组。
spring:
  cloud:
    nacos:
      username: "${NACOS_USERNAME}"
      password: "${NACOS_PASSWORD}"
```

在 `src/main/java/lab/CatalogApplication.java` 放置下列类。`/lab/limits` 读取当前 Spring Environment。另一个端点返回发现的实例，便于分开检查发现和真正调用。两个端点仅供本地验收。

```java
// 先看输入与依赖，再沿关键调用检查返回结果和异常分支。
package lab;

import java.util.List;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.core.env.Environment;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class CatalogApplication {
    public static void main(String[] args) {
        SpringApplication.run(CatalogApplication.class, args);
    }
}

@RestController
class LabController {
    private final Environment environment;
    private final DiscoveryClient discovery;

    LabController(Environment environment, DiscoveryClient discovery) {
        this.environment = environment;
        this.discovery = discovery;
    }

    @GetMapping("/lab/limits")
    Map<String, Integer> limits() {
        int configured = environment.getRequiredProperty(
                "catalog.pagination.max-size", Integer.class);
        return Map.of("maxSize", Math.min(Math.max(configured, 1), 500));
    }

    @GetMapping("/lab/instances")
    List<String> instances() {
        return discovery.getInstances("catalog-api").stream()
                .map(instance -> instance.getUri().toString())
                .toList();
    }
}
```

业务侧限幅用于防止误配把请求压力放大。更严格的场景可以拒绝错误配置并保留上一个已验证的配置值。

```bash
export NACOS_NAMESPACE_ID='<控制台中的命名空间ID>'
export NACOS_USERNAME='nacos'
read -rs -p 'Nacos lab password: ' NACOS_PASSWORD
printf '\n'
export NACOS_PASSWORD

# 终端 A
mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=18081

# 在继承相同环境变量的终端 B 启动第二个实例
mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=18082
```

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl -fsS http://127.0.0.1:18081/lab/limits
curl -fsS http://127.0.0.1:18081/lab/instances
curl -fsS http://127.0.0.1:18082/lab/limits
```

发布 `max-size: 50` 后，预期两实例返回 50，发现列表包含两个可达实例。发布 100 后分别请求两个实例，记录哪一时刻应用读到了 100。若控制台显示两个实例但调用不通，从发现列表取出实际 IP:port 直接请求。宿主访问方式、本机 IP、容器网段和调用方所在环境都可能影响结果。

### 8.3 三层刷新证据

| 层次 | 要查什么 | 典型失败 |
|---|---|---|
| 服务端配置 | 发布历史、命名空间、Group、Data ID | 改错环境，配置发布到了同名 Data ID 的另一个 Group |
| 客户端配置源 | SDK 订阅和 Spring Environment 的当前值 | 连接中断、刷新关闭、其他更高优先级配置覆盖 |
| 业务对象 | 当前请求实际读取的阈值、线程池或路由参数 | 启动时读入普通字段，后来 Environment 更新但对象没有重建 |

一次性注入到普通 Singleton 的值一般不会自动跟随环境更新。能否使用 `@RefreshScope`、`@ConfigurationProperties` 重绑或监听事件，取决于组件生命周期与框架支持。线程池、连接池、路由表等有状态资源，应设计先创建新对象、验证后切换、等待旧对象使用结束的过程。大规模更新先小批验证，保留上一版和值班时可执行的回滚步骤。

### 8.4 用服务名发 HTTP 请求

第 8.2 节用 `DiscoveryClient` 验证实例列表。发起 HTTP 调用时，再加 `org.springframework.cloud:spring-cloud-starter-loadbalancer`，通过 Spring Cloud LoadBalancer 把 URI 中的服务名转换成实例地址。下列代码放进第 8 节的调用方配置，使用同一发现命名空间和组。

```java
@Configuration
class CatalogClientConfiguration {
    @Bean
    @LoadBalanced
    RestClient.Builder serviceRestClient() {
        var requests = new SimpleClientHttpRequestFactory();
        requests.setConnectTimeout(Duration.ofMillis(300)); // 建立连接的预算
        requests.setReadTimeout(Duration.ofMillis(700));    // 等待下游响应的预算
        return RestClient.builder().requestFactory(requests);
    }
}
```

`@LoadBalanced` 来自 `org.springframework.cloud.client.loadbalancer`。在调用方构造器上用同样的限定符注入 `RestClient.Builder`，构建并复用客户端。

```java
// URI 的主机部分是 Nacos 服务名，由负载均衡器选一个实例。
String body = client.get()
        .uri("http://catalog-api/lab/limits")
        .retrieve()
        .body(String.class);
```

实际验证时，在两个商品服务实例的响应中临时加 `server.port` 或实例名。从调用方请求多次，确认结果来自可达实例。停止一个实例后，比对 Nacos 控制台、调用方列表和 HTTP 请求。负载均衡器的选择策略、实例缓存与 Nacos 的状态更新时间会影响切换。关键服务显式配置超时，写请求采用幂等键后再考虑重试。 [Spring Cloud Commons 负载均衡客户端](https://docs.spring.io/spring-cloud-commons/reference/spring-cloud-commons/common-abstractions.html)

---

## 9. 配置与发现故障演练

### 9.1 配置读不到

1. 启动参数临时把配置分组改为 `WRONG_GROUP`，保持 `nacos:` 为必需导入，观察启动日志。对照正确的 `CATALOG_LAB`，保存数据标识和报错。
2. 恢复分组，再试错口令。鉴权失败与配置资源不存在是两个不同结论。检查应用配置、用户权限和服务端鉴权日志。
3. 把 `refreshEnabled=true` 临时改为 `false`。重启后记录初始值，再发布新值并观察端点。恢复启用刷新后重做，确认能区分“启动读取”与“运行时订阅”。
4. 保留命名空间隔离，用配置历史恢复已验证的值。重新访问两个实例，核对配置在所有副本上的效果。

### 9.2 查到实例但 HTTP 连接失败

在两个端口都健康时查看发现列表。停止第二个实例，观察正常注销或健康状态变化。再用隔离环境模拟异常退出，比较实例不再可用的时间。Nacos 列表、调用方缓存和实际 TCP 状态会在不同时间更新。

| 症状 | 首选动作 | 继续查 |
|---|---|---|
| `connection refused` | 从调用方网络请求实际实例 IP 和端口 | 应用监听、容器端口、Service 路由 |
| SDK 日志报 gRPC 不通 | 检查客户端所用主端口与 gRPC 偏移 | 映射、代理协议、访问策略 |
| 控制台显示注册但分组查询为空 | 比较发现组、命名空间 ID 和服务名 | 客户端缓存、过滤条件和健康状态 |
| 只有新启动的实例使用新配置 | 对比刷新事件与业务实际读取 | 是否禁用了刷新，Bean 生命周期，配置优先级 |
| 访问压力随变更波动 | 比较重连数、发布频率、实例变动 | 分批发布、更新速率、应用重建成本 |

对生产故障，记录实例名、实际目标地址、客户端版本、配置标识和时间范围。应用调用仍需设置合理超时与重试策略。即使发现列表存在可用实例，业务端口也可能临时不可达。

---

## 10. 从单机到可维护的生产部署

- **隔离**　环境和业务命名空间需要明确 ID、所有者和发布权限。配置权限与服务注册权限按用途设置。尽量避免开发配置和生产配置共用同一个可写组。
- **存储与集群**　单机嵌入式数据用于练习。正式集群按所选版本的指南部署节点和外部存储，核对内网端口、持久化、备份、数据库初始化和访问策略。高可用要验证节点重启、网络隔离以及应用已有连接的行为。
- **发布**　配置进入代码评审或有审计的管理流程。记录变更前值、发布人、目标范围、生效证据和恢复步骤。仅对确有必要的字段启用动态刷新。
- **观测**　关注实例数、健康状态、注册和推送错误、gRPC 连接、配置查询时延、数据库和 JVM 资源。结合应用错误率和超时，判断是发现、配置还是业务调用故障。
- **对比选型**　只在 Kubernetes 内调用少量服务时，Service/DNS 常能提供稳定发现能力。若需要跨环境发现、兼容已有 Spring Cloud 部署或单独管理动态配置，再评估引入 Nacos 的维护成本。

**实战验收**　自己部署一个有认证的 Nacos，接入两个 Java 实例，成功发布并回滚一个业务参数，复现并修复分组、鉴权、gRPC 或注册地址中的至少两类问题。每次保留配置版本、日志、实际 HTTP 响应和恢复证据。

官方实操　[Spring Cloud Alibaba 版本矩阵](https://sca.aliyun.com/en/docs/2025.x/overview/version-explain/) · [Nacos Docker 快速开始](https://www.nacos.io/en/docs/v3.2/quickstart/quick-start-docker/) · [服务端鉴权](https://nacos.io/en/docs/v3.2/manual/admin/auth/)

延伸阅读　[微服务](../微服务.md) · [Nacos 3.x Docker 快速开始](https://www.nacos.io/en/docs/v3.2/quickstart/quick-start-docker/) · [Nacos 配置管理](https://www.nacos.io/en/docs/v3.2/manual/user/config/overview/) · [服务发现](https://www.nacos.io/en/docs/v3.2/manual/user/naming/overview/) · [Nacos 部署与端口](https://www.nacos.io/en/docs/v3.2/manual/admin/deployment/deployment-overview/) · [Spring Cloud Alibaba Nacos 配置](https://sca.aliyun.com/en/docs/2025.x/user-guide/nacos/advanced-guide/)
