# 《Apache RocketMQ 完整学习与开发速查笔记》

> **适用环境**　已理解 Topic、生产者和消费者。正文采用 RocketMQ 5.x 的消息类型与客户端概念，旧版 SDK 的端口、API 和重试策略需按对应版本核对。
> **学习目标**　按业务语义选择普通、顺序、延时、事务消息，掌握确认、重试、死信和幂等的边界。
> **动手路线**　从第 9 节启动 Broker 与 Proxy，第 10～12 节练发送、确认、重试和故障恢复。

---

# 第一篇　基础认知

## 1. 消息从哪里发到哪里

订单提交后，把 `OrderCreated` 发给消息服务。通知组消费该事件，决定是否发短信。统计组也可独立消费该事件更新汇总。业务 API 可在自身工作完成后返回，通知处理随后进行。

```text
Producer → RocketMQ Topic / Message Queue → Consumer Group
                    ↓                              ↓
               Broker 存储                  ACK / 重试 / 死信
```

| 组件 | 职责 | 常见误区 |
|---|---|---|
| NameServer | 保存和提供 Broker 路由信息 | 消息数据由 Broker 存储 |
| Broker | 存储、投递消息，维护消费与重试状态 | 发送成功与消费成功是两个阶段 |
| Proxy | RocketMQ 5.x 新版 gRPC SDK 可通过 Proxy 访问服务 | 5.x gRPC SDK 的接入点与老 Remoting SDK 的 NameServer 地址需要分别配置 |
| Topic / Queue | 按主题组织消息，底层按队列存取 | 单个主题可有多个队列 |
| Consumer Group | 一组具有同样订阅和处理逻辑的消费者 | 同组实例应使用一致的订阅、消息类型和处理规则 |

---

## 2. 四种消息怎么选

| 类型 | 提供的能力 | 订单场景 | 边界 |
|---|---|---|---|
| 普通 | 异步分发 | 订单已创建，通知和统计各自消费 | 消费失败和重复仍要处理 |
| FIFO | 同一 Message Group 内按顺序处理 | 同一订单的创建、支付、发货 | 发送端按业务顺序写入，消费端保持有序。不同组没有全局顺序 |
| 延时 | 到指定投递时间后可消费 | 15 分钟后检查订单是否仍未支付 | 到期后消费者可能积压。真正执行前再查当前状态 |
| 事务 | 让本地事务结果与消息是否可见相协调 | 写入订单记录后发布订单事件 | 下游事务和外部通知仍需幂等、重试或补偿 |

> [!important]
> 5.x 按消息类型准备 Topic。FIFO 的 `messageGroup` 可以用 `orderId`。若把所有订单都放进同一组，一个慢任务可能阻塞这一组后续事件。

---

## 3. Topic、Tag、Keys 与 Event ID

- **Topic** 区分较稳定的事件域，例如 `orders-normal`。
- **Tag** 可区分同一主题内的类别，例如 `ORDER_CREATED`、`ORDER_CANCELLED`，供订阅过滤。
- **Keys** 给运营排查和消息检索使用，可填业务事件 ID。
- **Event ID** 是应用定义的稳定幂等标识，应随事件体传递。发送重试可能生成不同的 Broker 消息标识，同一次业务事件继续使用相同的 `eventId`。

---

# 第二篇　开发流程与可靠性

## 4. 普通消息练习

按官方 5.x Docker 快速开始启动 NameServer、Broker 和 Proxy。通过同版本的管理工具创建普通 Topic `orders-normal` 和消费组 `orders-notify-lab`。在 Java 项目中引入兼容的 `org.apache.rocketmq:rocketmq-client-java`，参照官方示例初始化 Producer 与 PushConsumer。`ClientConfiguration.setEndpoints` 使用可达的 Proxy 接入点，官方容器示例使用 `localhost:8081`。先启动监听器，再发送消息。

使用以下事件发送两次，模拟同一笔订单事件的重复投递。以下是事件体，消息 Tag 可设为 `ORDER_CREATED`，Keys 可设为 `order-42-created-v1`。

**阅读提示**　事件体使用稳定事件 ID 进行幂等判断，业务字段按契约版本解释。

```json
{
  "eventId": "order-42-created-v1",
  "schemaVersion": 1,
  "orderId": 42,
  "customerId": "user-10",
  "totalCents": 19900
}
```

下面是已有 `provider` 和 `producer` 时的发送片段。两次发送是为练习重复投递，调用方重试真实事件时也应沿用稳定的 `eventId`。

```java
// json 为上一段事件体，Producer 已绑定 orders-normal。
Message message = provider.newMessageBuilder()
        .setTopic("orders-normal")
        .setTag("ORDER_CREATED")
        .setKeys("order-42-created-v1")
        .setBody(json.getBytes(StandardCharsets.UTF_8))
        .build();
SendReceipt receipt = producer.send(message);
System.out.println(receipt.getMessageId()); // 保存发送回执，便于核对消费日志
```

消费处理逻辑可以按下面的顺序实现。返回值对应 SDK 消费结果，数据库辅助函数是伪代码。

```text
解析事件并校验必填字段
开始本地事务
  尝试占用唯一键 (consumer_group, event_id)
  若已处理，结束事务，返回 SUCCESS
  若首次处理，写入通知任务
提交事务成功后返回 SUCCESS
临时失败时回滚，返回 FAILURE 让 Broker 按策略重试
```

预期两次投递只生成一条本地通知任务。模拟数据库暂时不可用时，应观察到失败重试。恢复后验证任务生成，并核对同一 `eventId` 的完整日志。

---

## 5. PushConsumer、SimpleConsumer 与消费重试

| 消费方式 | 处理流程 | 容易出错的地方 |
|---|---|---|
| PushConsumer | SDK 交给监听器处理，监听器返回成功或失败 | 把任务交给线程池后马上返回成功，后续失败不会按预期重试 |
| SimpleConsumer | 主动 `receive`，处理后 `ack` | 不可见时长太短可能在处理未完成时再次投递 |

消费失败或处理超时可触发重投，达到重试策略上限后进入死信队列（DLQ）。区分临时依赖故障和永久非法消息。对 DLQ 记录 `eventId`、原因、首次和最近失败时间，修复后才有选择地重放，重放时沿用业务 ID。

---

## 6. 事务消息的回查

```text
Producer 发送半消息 → Broker 暂存，消费者暂时不可见
          ↓
Producer 执行本地事务 → 根据持久化结果通知 Commit 或 Rollback
          ↓
若结果未知，Broker 回查 → Producer 从本地持久化状态判断
```

回查要查本地业务提交记录。应用刚重启时，内存变量已经丢失。回查期间若状态仍无法确认，应按 SDK 表达未知结果的方式处理，避免把短暂查询失败误判为回滚。事务消息适合允许异步一致的流程，也可与 [事务 Outbox](../微服务.md) 比较部署与维护成本。

---

# 第三篇　选型、排障与速查

## 7. Kafka 与 RocketMQ 的取舍

| 需求 | Kafka | RocketMQ |
|---|---|---|
| 日志流、回放、多组分析 | 以分区日志和组进度为核心 | 也有保留和回溯，按消息模型和运维接口评估 |
| 延时、死信、事务消息 | 往往由框架或业务补充延时与死信流程，事务以 Kafka 读写为主 | 5.x 提供对应消息类型和消费重试语义 |
| 业务顺序 | 关注分区 Key 和同一分区处理顺序 | 关注 FIFO Message Group 和发送、消费方式 |
| 业务副作用幂等 | 需要业务去重 | 同样需要业务去重 |

---

## 8. 问题索引与 Cheat Sheet

| 现象 | 从哪里查 |
|---|---|
| 生产者无法连接 | 客户端类型、Proxy 或 NameServer 接入点、Broker 路由与鉴权 |
| 发送成功但没消费 | Topic 类型、Tag 过滤、组订阅、消费进度和死信 |
| 同一订单发了两次通知 | 稳定 `eventId`、ACK 时机、数据库唯一键和外部通知幂等 |
| 单个订单的事件停住 | FIFO 组内前序消息、处理时长与重试 |
| 延时消息未按秒到达 | 投递时间、服务端时间、消费积压和消费者在线状态 |
| 事务消息一直不可见 | 半消息状态、事务回查日志、本地提交证据 |

**L1** 能按场景选消息类型。**L2** 能完成一次普通消息的发布和消费。**L3** 演练重复、重试和死信。**L4** 对比事务消息与 Outbox，用一次故障恢复说明取舍。

**记忆口诀**　发送只到 Broker，确认才算消费。顺序按组，重试靠幂等。

---

# 第四篇　独立部署、客户端接入和故障演练

## 9. 用 Compose 运行 5.x 练习环境

在新目录 `rocketmq-lab/` 准备 `compose.yaml` 与 `broker.conf`。NameServer 提供路由，Broker 保存消息，Proxy 为新版 Java SDK 提供 gRPC 接入。应用只需要访问映射到本机的 `18081`。在企业部署中，客户端入口、管理网络和 Broker 内部通信应分开设计。

```yaml
# compose.yaml
services:
  namesrv:
    image: apache/rocketmq:5.3.2
    command: ["sh", "mqnamesrv"]
  broker:
    image: apache/rocketmq:5.3.2
    command: ["sh", "mqbroker", "-c", "/home/rocketmq/broker.conf"]
    environment:
      NAMESRV_ADDR: namesrv:9876
    volumes:
      - ./broker.conf:/home/rocketmq/broker.conf:ro
      - broker-store:/home/rocketmq/store
    depends_on:
      - namesrv
  proxy:
    image: apache/rocketmq:5.3.2
    command: ["sh", "mqproxy"]
    environment:
      NAMESRV_ADDR: namesrv:9876
    ports:
      - "127.0.0.1:18081:8081"
    # depends_on 保证启动顺序，Broker 路由仍要用 clusterList 确认。
    depends_on:
      - namesrv
      - broker
volumes:
  broker-store:
```

```properties
# broker.conf。同一个 Compose 网络中的 Proxy 访问 Broker 自动探测的容器地址。
brokerClusterName=DefaultCluster
brokerName=broker-lab
brokerId=0
brokerRole=ASYNC_MASTER
flushDiskType=ASYNC_FLUSH
storePathRootDir=/home/rocketmq/store
storePathCommitLog=/home/rocketmq/store/commitlog
autoCreateTopicEnable=false
```

上面的角色和异步刷盘配置用于单节点功能练习。启动顺序由 Compose 约束，实际就绪需要查看日志和路由。如果 Proxy 找到了 Broker 但连接失败，先用 `clusterList` 检查 Broker 发布的地址是否能从 Proxy 所在网络访问。`-n` 指向 NameServer，应用的 `18081` 与这里的管理端口用途不同。

```bash
# 启动声明的服务。进程启动后继续确认容器健康和业务端口。
docker compose up -d
docker compose logs --tail=80 namesrv broker proxy

mqadmin() {
  local action="$1"
  shift
  docker compose exec -T broker sh mqadmin "$action" -n namesrv:9876 "$@"
}

mqadmin clusterList
mqadmin updateTopic -c DefaultCluster -t orders-normal -a +message.type=NORMAL
mqadmin updateSubGroup -c DefaultCluster -g orders-notify-lab
mqadmin topicRoute -t orders-normal
```

验收顺序为 NameServer 有 Broker 路由、Broker 有目标 Topic、Proxy 正常提供客户端服务、SDK 能拿到发送回执。用同一个 Compose 项目重建 Broker 前，先正常停止并确认数据卷仍存在。检查恢复后的 Topic 和消费进度。跨主机容错需要额外节点和副本方案。

---

## 10. 从发送到确认的 Java 实操

### 10.1 项目骨架

JDK 17+ 和 Maven 即可练习。在 `rocketmq-lab/` 下创建 `pom.xml` 和 `src/main/java/RocketLab.java`。程序先启动 SimpleConsumer 再发送，避免新组初始位置影响首次实验。`getBody()` 返回 ByteBuffer，使用 UTF-8 解码。

```xml
<!-- 放到 pom.xml 的对应节点，区分依赖版本管理、实际依赖与构建插件。 -->
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>lab</groupId>
    <artifactId>rocketmq-lab</artifactId>
    <version>1.0.0</version>
    <properties>
        <maven.compiler.release>17</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.apache.rocketmq</groupId>
            <artifactId>rocketmq-client-java</artifactId>
            <version>5.0.8</version>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
            </plugin>
        </plugins>
    </build>
</project>
```

```java
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import org.apache.rocketmq.client.apis.ClientConfiguration;
import org.apache.rocketmq.client.apis.ClientServiceProvider;
import org.apache.rocketmq.client.apis.consumer.FilterExpression;
import org.apache.rocketmq.client.apis.consumer.FilterExpressionType;
import org.apache.rocketmq.client.apis.message.Message;

public class RocketLab {
    public static void main(String[] args) throws Exception {
        String topic = "orders-normal";
        String group = "orders-notify-lab";
        String tag = "ORDER_CREATED";
        String eventId = "order-42-created-v1";
        boolean skipAck = args.length > 0 && args[0].equals("skip-ack");
        boolean receiveOnly = args.length > 0 && args[0].equals("receive-only");

        var provider = ClientServiceProvider.loadService();
        var config = ClientConfiguration.newBuilder()
                .setEndpoints("127.0.0.1:18081").build();
        var filter = new FilterExpression(tag, FilterExpressionType.TAG);
        try (var consumer = provider.newSimpleConsumerBuilder()
                     .setClientConfiguration(config)
                     .setConsumerGroup(group)
                     .setAwaitDuration(Duration.ofSeconds(5))
                     .setSubscriptionExpressions(Map.of(topic, filter))
                     .build();
             var producer = provider.newProducerBuilder()
                     .setClientConfiguration(config)
                     .setTopics(topic)
                     .build()) {
            if (!receiveOnly) {
                String body = """
                        {"eventId":"order-42-created-v1","orderId":42,"totalCents":19900}
                        """;
                Message message = provider.newMessageBuilder()
                        .setTopic(topic).setTag(tag).setKeys(eventId)
                        .setBody(body.getBytes(StandardCharsets.UTF_8))
                        .build();
                var receipt = producer.send(message);
                System.out.println("sent messageId=" + receipt.getMessageId());
            }

            // 最多拉取数次，每次只处理一条，便于查看日志和 ACK。
            for (int attempt = 0; attempt < 4; attempt++) {
                var messages = consumer.receive(1, Duration.ofSeconds(20));
                if (messages.isEmpty()) {
                    continue;
                }
                var message = messages.get(0);
                System.out.println("received " + StandardCharsets.UTF_8.decode(message.getBody()));
                // 实际应用在业务事务成功之后确认。
                if (!skipAck) {
                    consumer.ack(message);
                    System.out.println("acked messageId=" + message.getMessageId());
                }
                return;
            }
            throw new IllegalStateException("No matching message received");
        }
    }
}
```

```bash
# 使用配置好的 Maven 项目。首次运行需要可访问 Maven 仓库。
mvn -q compile org.codehaus.mojo:exec-maven-plugin:3.5.0:java -Dexec.mainClass=RocketLab

# 发出新一条练习消息并故意不确认，等待不可见期结束后只接收。
mvn -q compile org.codehaus.mojo:exec-maven-plugin:3.5.0:java -Dexec.mainClass=RocketLab -Dexec.args=skip-ack
mvn -q compile org.codehaus.mojo:exec-maven-plugin:3.5.0:java -Dexec.mainClass=RocketLab -Dexec.args=receive-only
```

正常模式预期打印 `sent`、`received`、`acked`。故障模式以事件体里的业务 ID 核对重新投递，投递时机由不可见期、重试和调度决定。先等 20 秒并给重试留时间。上一条练习消息未清理时，消费者也可能先拿到上一条消息，验收应核对发送回执、消息体和组进度。

### 10.2 补上真实的幂等落库

以下表用 MySQL 8.x。对同一个订单事件的通知任务只允许创建一次，通知记录本身也可以作为幂等证据。如果一次事件要分别发邮件、短信，可加 `channel` 到唯一键，分别记录状态。

```sql
-- 建表时关注字段类型、主键和约束如何限制后续写入。
CREATE TABLE notify_task (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    consumer_group VARCHAR(64) NOT NULL,
    event_id VARCHAR(96) NOT NULL,
    order_id BIGINT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    attempts INT NOT NULL DEFAULT 0,
    UNIQUE KEY uk_notify_event (consumer_group, event_id)
);
```

处理顺序为校验事件、插入任务、提交事务、ACK。重复键只说明同组已经持久化这项任务，要核对内容是否一致。数据库连接超时或事务回滚时返回失败，留给消息重试。独立发送任务还要处理第三方超时导致的“已发送但本地未记录”，优先使用第三方幂等请求键或结果查询接口。

### 10.3 PushConsumer 回调、过滤与失败分类

需要持续监听时可选 PushConsumer，应用在回调里完成处理并报告结果。下面假定 `provider`、`config` 已按第 10.1 节初始化，且另外创建了组 `orders-push-lab`。同一个消费组内的实例保持相同订阅，避免部分实例永远接不到某类消息。

```java
var filter = new org.apache.rocketmq.client.apis.consumer.FilterExpression(
        "ORDER_CREATED || ORDER_PAID",
        org.apache.rocketmq.client.apis.consumer.FilterExpressionType.TAG);

var consumer = provider.newPushConsumerBuilder()
        .setClientConfiguration(config)
        .setConsumerGroup("orders-push-lab")
        .setSubscriptionExpressions(java.util.Map.of("orders-normal", filter))
        .setMessageListener(message -> {
            try {
                // 按 eventId 幂等地提交本地任务，再通知 Broker 成功。
                saveTaskInTransaction(message);
                return org.apache.rocketmq.client.apis.consumer.ConsumeResult.SUCCESS;
            } catch (RuntimeException error) {
                // 记录事件键与失败类别，保留失败让 Broker 按组策略重试。
                logFailure(message, error);
                return org.apache.rocketmq.client.apis.consumer.ConsumeResult.FAILURE;
            }
        })
        .build();
```

`saveTaskInTransaction` 和 `logFailure` 是应用自己的方法。Consumer 应复用，并在应用关闭时释放。演练时分别发送两个匹配 Tag 和一个无关 Tag，核对订阅范围。再为一条消息注入暂时故障，记录重试后成功。对于明确的无效数据，可先持久化隔离记录再按约定确认，也可交给重试上限与死信流程。避免无上限循环，也避免忽略失败后直接成功。

```bash
# 复用第 9 节的管理函数，从业务 Key 查询消息，再看对应消费组的进度。
mqadmin queryMsgByKey -t orders-normal -k order-42-created-v1
mqadmin consumerProgress -g orders-push-lab
```

查到消息只说明 Broker 侧存在相应索引，不能证明消费者已经完成业务。把消息记录、重试日志、数据库写入和 ACK 关联起来，才能确认一次完整消费。 [RocketMQ 消费者类型](https://rocketmq.apache.org/docs/featureBehavior/06consumertype/) · [消费重试与死信](https://rocketmq.apache.org/docs/featureBehavior/10consumerretrypolicy/)

---

## 11. FIFO、延时与事务练习

### 11.1 FIFO 用订单 ID 划分 Message Group

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
mqadmin updateTopic -c DefaultCluster -t orders-fifo -a +message.type=FIFO
mqadmin updateSubGroup -c DefaultCluster -g orders-state-lab -o true
```

将生产者和消费者切换到新 Topic/Group。构造消息时加 `.setMessageGroup("order-42")`，在同一个生产线程依次发送版本 1、2、3 并确认各自发送结果。另发一组 `order-10`。消费端保证同组串行应用并验证版本顺序，避免异步任务提前返回成功。模拟版本 2 失败，观察同一订单后续事件是否等待，另一个订单仍可处理。整体到达顺序受分组和调度影响，验收按订单检查。

### 11.2 延时用绝对时间，落地前查当前状态

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
mqadmin updateTopic -c DefaultCluster -t orders-delay -a +message.type=DELAY
mqadmin updateSubGroup -c DefaultCluster -g orders-expire-lab
```

5.x Java SDK 在构造消息时使用 `.setDeliveryTimestamp(System.currentTimeMillis() + 30_000L)`，参数是 Unix 毫秒时间戳。把业务事件设置为 `OrderPaymentCheck`，记录发送时刻、预计投递时刻、实际接收时刻和处理结束时刻。提前把订单标为 PAID，消费检查应返回已支付并 ACK。未支付则用条件更新把状态从 PENDING 改为 CANCELLED，避免和支付并发时覆盖更新。

### 11.3 事务消息与本地状态回查

事务 Topic 使用 `+message.type=TRANSACTION`。生产端先发送半消息，再提交本地订单事务。回查接口按稳定业务键查询本地状态。以下是回查决策，具体代码使用当前 SDK 的事务检查接口。

| 本地证据 | 回查结果 | 理由 |
|---|---|---|
| 订单和事件标识已在同一事务持久化 | Commit | 已有可核对的提交事实 |
| 有明确终止标记，原事务已回滚 | Rollback | 对应事件不应对消费者可见 |
| 数据库暂时不可用、事务仍在进行 | Unknown | 当前没有足够证据决定提交或回滚 |
| 只看到订单 ID，但事件标识不匹配 | 依业务规则调查 | 一个订单可以有多个版本的事件 |

演练生产者在本地事务成功后、通知 Broker 前退出。应用恢复后用回查确认半消息。再演练本地失败，确认消费者看不到该事件。它协调本地事务与消息可见性。下游副作用仍按第 10.2 节实现幂等。

---

## 12. 消息积压、死信与运维

### 12.1 从五个阶段定位故障

| 问题 | 第一条证据 | 检查路径 |
|---|---|---|
| SDK 不能建立连接 | 错误中目标地址与协议 | 宿主端口 → Proxy → NameServer 路由 → Broker |
| `TOPIC_NOT_FOUND` 或类型不匹配 | `mqadmin topicRoute -t ...` | Topic 名、集群、类型、路由刷新 |
| 发送有回执、组里无数据 | Tag、组订阅和消息 Key | 查是否订阅不同 Tag，确认组是否已消费或重试 |
| 有堆积且失败率高 | `mqadmin consumerProgress -g ...`、消费者日志 | 比较生产和 ACK 速率，查处理时长、依赖、不可见期和重试 |
| 同 Key 业务重复 | eventId、任务表、外部请求记录 | 查重投、事务确认位置及第三方接口是否幂等 |
| 事务消息不可见 | Broker 回查与本地事务证据 | 检查事务监听器、状态存储和回查返回值 |

对永久失败，记录订单 ID、事件 ID、失败类别、受影响版本和原消息体的位置。修复后先重放一条验证，再按限速和范围处理。严格有序场景要决定如何补回缺失版本，盲目重发最新记录可能把业务状态推进错。死信留存、重放工具、恢复审批和重复防护一起设计。

### 12.2 持久化、容量与生产配置

- **存储**　CommitLog 存消息主体，消费队列用于按 Topic/Queue 找到消息，索引可用于检索。跟踪磁盘剩余、读写延迟和消息保留窗口。容量估算包含复制、索引、临时文件和故障余量。
- **刷盘和复制**　写入确认与刷盘、复制的关系取决于部署配置。要求较低丢失窗口时同时验证磁盘确认、复制、网络分区和恢复。实验的单 Broker 配置只用于理解功能。
- **权限**　使用所选版本支持的鉴权方式，生产者只写允许的主题，消费者只读指定组与主题。Proxy 与 Broker 的访问边界都要验证。
- **观测**　同时看发送成功率、端到端时间、消费积压、失败重试、死信、半消息回查与存储水位。发送成功率高而 ACK 速率下降时，优先查消费链路。
- **压测**　分正常、峰值、慢依赖三个阶段，记录消息大小、吞吐、P95/P99、积压峰值和追平时间。按消费者处理能力调整并发与批量，避免用无限重试掩盖持续失败。

### 12.3 实战验收

1. 使用 CLI 和 Java 分别确认路由与消息处理成功，能说明 Proxy 与 NameServer 的角色。
2. 复现不 ACK 导致再次投递。加唯一键后，数据库中同一事件只有一条任务。
3. 验证 FIFO 组内顺序、延时到期前不可见和到期后仍需检查状态。
4. 制造一条处理必失败的事件，记录重试次数和隔离路径。修复后只恢复指定事件。
5. 根据一条异常给出“发送回执 → 路由 → 消费组 → 业务事务 → ACK”的完整证据链。

官方实操　[RocketMQ Docker Compose](https://rocketmq.apache.org/docs/quickStart/03quickstartWithDockercompose/) · [Java SDK](https://github.com/apache/rocketmq-clients/tree/master/java) · [延时消息](https://rocketmq.apache.org/docs/featureBehavior/02delaymessage/) · [消费者类型](https://rocketmq.apache.org/docs/featureBehavior/06consumertype/)

延伸阅读　[Kafka](Kafka.md) · [RocketMQ Docker 与 Java SDK 快速开始](https://rocketmq.apache.org/docs/quickStart/02quickstartWithDocker/) · [顺序消息](https://rocketmq.apache.org/docs/featureBehavior/03fifomessage/) · [事务消息](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/) · [消费重试](https://rocketmq.apache.org/docs/featureBehavior/10consumerretrypolicy/)
