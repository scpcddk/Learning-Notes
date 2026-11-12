# 《Apache Kafka 完整学习与开发速查笔记》

> **适用环境**　理解生产者、消费者与 Docker 基础。命令采用 Apache Kafka 4.1 的单节点练习镜像。Kafka 4.x 使用 KRaft 管理元数据。
> **学习目标**　理解 Topic、Partition、Offset 和消费组，完成带 Key 的事件发布与消费，能判断顺序、可靠性和积压的边界。
> **动手路线**　先用第 3 节看分区和消费组，再按第 8～10 节部署双 Listener、接入 Java 并练习回放。

---

# 第一篇　基础认知

## 1. Kafka 是可回放的分区日志

生产者把事件追加到 Topic 的某个 Partition。Broker 按配置保留数据，消费者按自己的进度读取。订单事件可以由读模型更新组和统计组分别处理。消费者读完后，事件仍可在保留期内由其他组读取或重放。

```text
订单服务 → Topic orders.events.v1
                    ├─ Partition 0  ... offset 35, 36, 37
                    └─ Partition 1  ... offset 18, 19, 20
                                   ↓
                        读模型组和统计组各自维护进度
```

| 术语 | 含义 | 常见误区 |
|---|---|---|
| Topic | 事件类别或数据流的名字 | 一个 Topic 可以有多个 Partition |
| Partition | 独立追加的日志，也是常规消费组分配单位 | 顺序以分区为单位 |
| Offset | 记录在某分区内的位置 | 不同分区不能按 Offset 比较先后。部分 Offset 可能没有可读记录 |
| Consumer Group | 一组协作处理同一份事件的消费者 | 常规组中同一分区同一时刻由组内一个成员负责。不同组可独立消费 |
| Leader / Replica / ISR | Leader 提供分区读写的主要入口，副本复制日志，ISR 是同步副本集合 | 复制因子 3 与当前仍同步的副本数是两个指标 |

---

## 2. Key、顺序与并行度

同一主题内，用稳定序列化的 `orderId` 作 Key，常规按 Key 分区时，同一订单的事件通常落到同一分区。业务还要保证生产端的发送顺序，并避免消费者并行任务把副作用顺序打乱。扩大分区数可能改变后续 Key 的分配，应规划重分区期间的顺序。

3 个分区、同组 5 个消费者，最多 3 个成员同时拿到分区。若积压集中在一个订单 Key 所在的分区，增加消费者也不能平分这个分区。先检查分区分布、事件速率和单条处理时间。

---

# 第二篇　动手操作与可靠消费

## 3. 发布与消费三条订单事件

```bash
# 单节点练习，CLI 在容器内部访问 Broker
docker run --rm --name kafka-lab -d apache/kafka:4.1.2
docker logs kafka-lab
docker exec kafka-lab /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders.events.v1 --partitions 3 --replication-factor 1
docker exec -it kafka-lab /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders.events.v1 --property parse.key=true --property key.separator=:
```

看到生产者提示符后，输入下面三行，每行回车发送，然后 `Ctrl+C` 退出生产者。分隔符前是 Key，后面是消息值。

```text
order-42:{"eventId":"evt-1","seq":1,"state":"CREATED"}
order-10:{"eventId":"evt-2","seq":1,"state":"CREATED"}
order-42:{"eventId":"evt-3","seq":2,"state":"PAID"}
```

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker exec -it kafka-lab /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders.events.v1 --group orders-view-lab --from-beginning --max-messages 3 --property print.key=true --property print.partition=true --property print.offset=true
docker exec kafka-lab /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group orders-view-lab
```

新组预期收到三条记录。观察两条 `order-42` 的分区相同，分区内 Offset 递增。`order-10` 可能碰巧也落在同一分区。将组名换成 `statistics-lab`，再用 `--from-beginning`，可观察另一个组独立读取同一批数据。已有提交位置的组通常从其提交位置继续，`--from-beginning` 用于没有有效位置时选择最早可读记录。

---

## 4. 发送确认与持久性

| 配置 | 作用 | 实践关注点 |
|---|---|---|
| `acks=all` | 等待当前同步副本确认 | 与 `min.insync.replicas` 配合。同步副本不足时发送可以失败 |
| `replication.factor` | Topic 每个分区的副本数 | 练习单节点用 1。生产按故障容忍度规划 |
| `min.insync.replicas` | `acks=all` 成功所需的最小 ISR 数 | 常见起点是 3 副本、最小 ISR 2，根据可用性目标调整 |
| `enable.idempotence=true` | 抑制同一个幂等生产者发送流程因重试产生的重复 | 应用重新调用 `send` 发出同一业务事件仍需业务去重 |
| `retention.ms` / `cleanup.policy` | 决定保留时间与删除或压缩策略 | 估算允许积压、回放窗口和磁盘容量 |

---

## 5. 提交 Offset 与业务幂等

消费者读到 Offset 42，处理成功后提交的下一位置通常是 43。业务提交前先提交 Offset，可能导致重启后跳过未处理事件。业务提交后再提交 Offset，若进程在两次提交之间崩溃，重启后可能再次处理同一条消息。

```text
poll → 解析并校验 → 本地事务中记录 eventId 并更新业务 → 提交消费进度
                          ↑
               重复 eventId 走已处理分支
```

> [!warning]
> **易混淆**　生产者幂等、Kafka 事务和数据库写入是不同边界。Kafka 事务可把 Kafka 输出记录与 Kafka 消费进度一起提交，消费者通过 `read_committed` 读取已提交记录。写 MySQL 或调用外部 API 时，仍要为业务副作用设计幂等。

批量处理时，提交位置不能越过同一分区中尚未完成的记录。遇到反复解析失败的事件，应明确停止、记录后跳过或转入隔离 Topic 的策略，同时保留原位置和事件 ID。使用 Spring Kafka 时，先明确监听容器的确认模式、错误处理和重试策略，避免把框架的确认时机与业务成功混在一起。

---

# 第三篇　排障与速查

## 6. 从消费积压找瓶颈

命令行中的 `LAG` 通常是 `LOG-END-OFFSET` 与 `CURRENT-OFFSET` 的差值，表示消费进度相对日志末尾的位置差。压缩、事务控制记录等可能让 Offset 不连续。观察 Lag 趋势时，也看最新处理事件的时间和每秒消费量。

| 现象 | 第一条证据 | 下一步 |
|---|---|---|
| 所有分区 Lag 增大 | `kafka-consumer-groups.sh --describe` | 比较每秒生产与消费量，检查数据库或 HTTP 依赖 |
| 单个分区 Lag 居高 | 分区 Lag 和 Key 分布 | 排查热点 Key、慢消息或头部阻塞 |
| 反复 Rebalance | 消费者日志和处理耗时 | 核对 `max.poll.interval.ms`、单批处理时间和实例重启 |
| 能连 bootstrap，随后超时 | 客户端日志的 Broker 地址 | 检查 `advertised.listeners` 返回的地址能否从客户端访问 |
| 拉取旧记录失败 | 最早可读 Offset 与组提交位置 | 确认保留窗口及 `auto.offset.reset` 策略 |
| 发送超时或失败 | Producer 异常、Broker ISR 和磁盘 | 看副本健康、路由、权限、消息大小与发送预算 |

---

## 7. 学习分级与问题索引

**L1** 解释分区、组与 Offset。**L2** 用两个组消费同一批事件。**L3** 模拟业务成功后提交 Offset 前重启，验证业务幂等。**L4** 用积压、吞吐与复制指标推导分区、保留与故障恢复方案。

**记忆口诀**　分区定顺序，组内分任务，业务先落地，进度后提交。

---

# 第四篇　独立部署、应用接入与恢复实战

## 8. 双 Listener 的 Docker Compose 环境

第 3 节的 CLI 都在容器内运行。这一节让宿主 Java 应用和 Compose 内服务同时连接同一个 Broker，验证 Kafka 元数据中的地址选择。另建目录 `kafka-lab/`，保存以下 `compose.yaml`。使用单节点 KRaft，事务内部主题副本数设为 1，仅供本地练习。

```yaml
services:
  broker:
    image: apache/kafka:4.1.2
    ports:
      - "127.0.0.1:19092:9092"
    environment:
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
      KAFKA_NODE_ID: "1"
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_LISTENERS: "HOST://:9092,INTERNAL://:29092,CONTROLLER://:29093"
      # 返回给客户端的地址，必须分别从宿主机和 Compose 网络可达。
      KAFKA_ADVERTISED_LISTENERS: "HOST://127.0.0.1:19092,INTERNAL://broker:29092"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "HOST:PLAINTEXT,INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT"
      KAFKA_INTER_BROKER_LISTENER_NAME: "INTERNAL"
      KAFKA_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@broker:29093"
      KAFKA_LOG_DIRS: "/tmp/kraft-combined-logs"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "1"
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: "1"
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: "1"
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
    volumes:
      - kafka-data:/tmp/kraft-combined-logs
volumes:
  kafka-data:
```

```bash
# 启动声明的服务。进程启动后继续确认容器健康和业务端口。
docker compose up -d
docker compose logs --tail=80 broker
docker compose exec -T broker /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server broker:29092
docker compose exec -T broker /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server broker:29092 --create --if-not-exists \
  --topic orders.events.v1 --partitions 3 --replication-factor 1 \
  --config retention.ms=86400000
```

| 客户端位置 | 应填地址 | 使用的通道 |
|---|---|---|
| 宿主机的 Java 项目或 Kafka 命令行工具 | `127.0.0.1:19092` | HOST，端口映射到容器 9092 |
| 同一个 Compose 网络 | `broker:29092` | INTERNAL，使用服务名 |
| KRaft 元数据控制器 | `broker:29093` | CONTROLLER，供 quorum 通信 |

首次连接 bootstrap 只是获取集群元数据。元数据里返回的是 `advertised.listeners`，客户端随后用对应地址访问分区 Leader。比如宿主客户端收到 `broker:29092`，往往会出现首次握手成功、后续请求超时。检查错误中实际连接的地址，可以比反复调超时更快定位问题。

如果服务启动后提示存储目录权限异常，先核对 `KAFKA_LOG_DIRS`、容器内进程用户和挂载目录的属主。已格式化的 Kafka 数据卷还记录 cluster ID 与节点身份。切换版本、恢复卷或更换节点时先核对元数据和官方升级路径。保留卷重建后可验证 Topic 与消费组仍存在。

---

## 9. Java 客户端的确认和消费边界

### 9.1 生产者发送回执

Maven 练习可使用 `org.apache.kafka:kafka-clients:4.1.2`，JDK 17+。以下方法一次运行写入一条事件。常驻服务把线程安全的 Producer 作为可复用对象，并在关闭应用时释放。消息格式示范用 Java 文本块。实际业务把稳定的 `eventId`、订单编号和业务版本放进契约。

```java
// 构造消息并提交发送，结合回执确认 Broker 是否接收。
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class PublishOrder {
    public static void main(String[] args) throws Exception {
        Properties settings = new Properties();
        settings.put("bootstrap.servers", "127.0.0.1:19092");
        settings.put("key.serializer", StringSerializer.class.getName());
        settings.put("value.serializer", StringSerializer.class.getName());
        settings.put("enable.idempotence", "true");
        settings.put("acks", "all");
        settings.put("delivery.timeout.ms", "15000");
        settings.put("request.timeout.ms", "5000");

        String json = """
                {"eventId":"lab-created-42","orderId":"order-42","version":1,"state":"CREATED"}
                """;
        try (var producer = new KafkaProducer<String, String>(settings)) {
            var record = new ProducerRecord<>("orders.events.v1", "order-42", json);
            var meta = producer.send(record).get(20, TimeUnit.SECONDS);
            System.out.printf("topic=%s partition=%d offset=%d%n",
                    meta.topic(), meta.partition(), meta.offset());
        }
    }
}
```

把类放到 Maven 项目的 `src/main/java/PublishOrder.java`，设置编译版本 17，并在 `<dependencies>` 加入 `org.apache.kafka:kafka-clients:4.1.2`。从空目录开始时，可复用 [RocketMQ 练习的 Maven 骨架](RocketMQ.md)，替换制品名和依赖。启动第 8 节 Broker 后运行下面命令，预期返回 Topic、Partition 和 Offset。

```bash
# 在包含 pom.xml 的项目目录运行，查看构建阶段和输出制品。
mvn -q compile org.codehaus.mojo:exec-maven-plugin:3.5.0:java -Dexec.mainClass=PublishOrder
```

发送异步时也要观察回调或返回值。发送超时可能发生在 Broker 已写入、ACK 丢失的情况下，应用重发时复用业务 ID。设置 `delivery.timeout.ms` 时要覆盖 `request.timeout.ms` 与 `linger.ms` 的预算，同时在业务层规定这一步允许等待多久。

### 9.2 消费、落库与精确提交

Consumer 由拥有它的一个线程调用。把 `enable.auto.commit` 设为 `false` 后，`poll` 返回的是已拉取数据，应用负责在业务成功后提交进度。下面是核心循环，`applyInDatabase` 为自己的持久化操作，必须在返回前完成本地事务。示例按记录提交便于观察语义，生产可按分区批量提交已连续处理的位置。

```java
consumer.subscribe(java.util.List.of("orders.events.v1"));
while (!Thread.currentThread().isInterrupted()) {
    var records = consumer.poll(java.time.Duration.ofMillis(500));
    for (var record : records) {
        // 业务抛异常时退出当前流程。未处理位置留给重试或重启。
        applyInDatabase(record.key(), record.value());
        var partition = new org.apache.kafka.common.TopicPartition(
                record.topic(), record.partition());
        var next = new org.apache.kafka.clients.consumer.OffsetAndMetadata(record.offset() + 1);
        consumer.commitSync(java.util.Map.of(partition, next));
    }
}
```

这里精确提交某个分区的处理进度。用无参 `commitSync()` 处理部分批次，可能会提交客户端已拉取但业务尚未完成的位置。开启多线程消费后仍要维护每个分区连续完成的最大位置，并处理 Rebalance 前后的归属变化。处理耗时超出 `max.poll.interval.ms` 时，应减少 `max.poll.records`、拆分单条工作或调整预算。

### 9.3 用数据库唯一键保证重放安全

订单读模型的事件应用可用一个本地事务处理。先插入去重记录，成功后更新订单视图；若已有相同记录，结束本次事务并把消息视为已应用。非重复的 SQL 错误应抛出，不能被当成重复事件跳过。可以按订阅者分隔相同事件的用途。

```sql
-- 建表时关注字段类型、主键和约束如何限制后续写入。
CREATE TABLE kafka_processed_event (
    consumer_name VARCHAR(64) NOT NULL,
    event_id VARCHAR(96) NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (consumer_name, event_id)
);

CREATE TABLE order_projection (
    order_id VARCHAR(64) PRIMARY KEY,
    state VARCHAR(24) NOT NULL,
    version BIGINT NOT NULL
);
```

对快照事件可在业务事务内用版本条件更新，拒绝旧版本覆盖新状态。对扣减库存这类增量事件还要校验前序版本，缺前序时要等待、补取或修复，不能只靠“大版本覆盖小版本”。数据库去重记录的保留期应覆盖系统允许回放的窗口。

### 9.4 Spring Kafka 配置与错误处理

用 Spring Boot 管理 `org.springframework.kafka:spring-kafka` 依赖。下面配置对应记录监听器。`record` 模式在单条监听正常返回后提交其进度，数据库提交应发生在监听方法返回之前。若采用批量监听，另外明确一次失败时整批或剩余记录的处理策略。

```yaml
# 将 Kafka 组进度、反序列化和提交方式分开配置，提交时点应匹配业务处理。
spring:
  kafka:
    bootstrap-servers: 127.0.0.1:19092
    consumer:
      group-id: orders-projection-lab
      enable-auto-commit: false
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      max-poll-records: 50
    listener:
      ack-mode: record
```

| 错误类别 | 正常处置 | 实践验证 |
|---|---|---|
| 数据库短暂不可用 | 限次退避重试，监控处理耗时和 Lag | 暂停本地数据库，恢复后确认同一事件处理成功 |
| 无法解析、字段不合法 | 保留原事件、来源分区和 Offset，进入 DLT 或审核队列 | 写入一条无效 JSON，检查死信与后续正常记录 |
| 重复事件 | 通过业务唯一键返回已处理 | 两次发送相同 eventId，查数据库结果行数 |
| DLT 发布失败 | 让恢复操作报错，保留原进度供再次尝试 | 练习中暂时关掉 DLT 写权限，再恢复后验证 |

Spring Kafka 可用 `DefaultErrorHandler` 组合 `DeadLetterPublishingRecoverer` 和有限退避。若使用默认同分区路由，DLT 分区数至少覆盖原 Topic，且必须在禁止自动创建主题的集群预建。若死信成功后继续消费，强顺序业务要规定如何处理该事件的后继记录。

### 9.5 Kafka 内部的「消费 → 处理 → 生产」事务

上面的数据库例子通过本地事务和业务去重处理外部副作用。若输入和输出都在 Kafka，同一事务可以提交输出记录和输入消费进度。先创建输出 Topic `orders.projected.v1`。为 Producer 设置 `transactional.id`，保证每个仍在运行的实例 ID 不冲突，重启后用对应 ID 接管。Consumer 关闭自动提交，并按需用 `isolation.level=read_committed` 读取输入。下游也使用 `read_committed` 才能忽略已中止的输出。

```java
// 每个 Producer 实例只初始化一次，以下展示一个非空 poll 批次的处理边界。
producer.initTransactions();
var records = consumer.poll(java.time.Duration.ofMillis(500));
if (!records.isEmpty()) {
    var offsets = new java.util.HashMap<
            org.apache.kafka.common.TopicPartition,
            org.apache.kafka.clients.consumer.OffsetAndMetadata>();
    producer.beginTransaction();
    for (var record : records) {
        // transform 为业务映射。同一分区记录按顺序处理，保留最后的下一位置。
        producer.send(new org.apache.kafka.clients.producer.ProducerRecord<>(
                "orders.projected.v1", record.key(), transform(record.value())));
        var partition = new org.apache.kafka.common.TopicPartition(record.topic(), record.partition());
        offsets.put(partition, new org.apache.kafka.clients.consumer.OffsetAndMetadata(record.offset() + 1));
    }
    if (abortForLab) {
        // 在主动制造的中止场景下退出本次运行，输入组的提交位置不推进。
        producer.abortTransaction();
    } else {
        // 把输出和组进度一起提交，组元数据用于识别当前消费者身份。
        producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
        producer.commitTransaction();
    }
}
```

`abortForLab` 是由调用方设置的布尔开关。这个片段只演示一批，调用方负责关闭客户端。实现常驻循环时，应按客户端 API 区分可中止错误、可重试提交错误和需要关闭 Producer 的致命错误。只有确认事务还可中止时调用 `abortTransaction()`，再按已提交位置恢复或显式 seek。提交结果不明时先按 API 约定处理，不能直接继续下一批。事务超时与 `max.poll.interval.ms` 一起设定，避免处理慢时组成员身份失效。

**验收**　在练习中分别成功提交和显式中止一批。用两个新消费组读取输出，分别配置 `read_committed` 和 `read_uncommitted`，对比输出可见性，并确认输入组提交位置只随成功事务推进。外部 HTTP 和数据库仍使用各自的幂等机制。 [KafkaProducer 事务 API](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)

---

## 10. 消费组实战：观察、停机、回放

以下命令仅操作练习 Topic 和练习组。先在 Bash 中设置短函数，减少命令重复。用第 3 节方式发送至少 3 条消息，或运行上面的 Java 示例多次。

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
kafka_cli() {
  local tool="$1"
  shift
  docker compose exec -T broker "/opt/kafka/bin/$tool.sh" \
    --bootstrap-server broker:29092 "$@"
}

kafka_cli kafka-topics --describe --topic orders.events.v1
kafka_cli kafka-consumer-groups --describe --group orders-projection-lab
kafka_cli kafka-consumer-groups --describe --group orders-projection-lab --members --verbose
```

先让应用处理几条消息并正常关闭，记下每个分区的提交位置。若要在已存在的组里回放，必须先停掉该练习组所有消费者。先预览每个分区将移动到的 Offset，再在确定能重放后执行。

```bash
kafka_cli kafka-consumer-groups --group orders-projection-lab \
  --topic orders.events.v1 --reset-offsets --to-earliest --dry-run

# 只对自己创建的练习组执行。实际环境先确认副作用和审批范围。
kafka_cli kafka-consumer-groups --group orders-projection-lab \
  --topic orders.events.v1 --reset-offsets --to-earliest --execute
```

重启消费者，预期旧记录重新到达，去重表与订单视图未发生重复写入。若日志已经超过保留窗口，最早可读 Offset 会向前推进。要求保留更久的审计数据时应独立设计归档与回放流程。对只读验证，可另开新组，避免移动已有组进度。

---

## 11. 运维、性能与容量

- **Topic 生命周期**　给 Topic 设所有者、格式版本、分区数、保留期和读写权限。日志清理按段和周期进行，`retention.ms` 不是严格的逐条删除时间。压缩保留同 Key 的较新状态，期间可同时看到旧版本，删除事件需按 tombstone 语义处理。
- **容量估算**　先用平均事件大小 × 每秒事件数 × 保留秒数 × 副本数估算原始量。例子每秒 1000 条，每条 1 KiB，保留 3 天，3 副本，约 742 GiB 原始数据。再考虑压缩、索引、磁盘水位、峰值、重分配和故障余量。
- **性能**　批量发送和压缩有利于吞吐，但会改变 CPU、等待和响应大小。先量化端到端时延、生产者批量大小和请求失败率，再调整 `batch.size`、`linger.ms`、压缩、分区数和应用并发。
- **安全与发布**　生产 Listener 按网络区划分，使用 TLS/SASL 和最小 ACL。验证生产者只能写目标 Topic，消费者只能读订阅 Topic 与所属 Group。变更分区数、保留期、最小 ISR 或日志目录时先做变更影响评估。
- **监控**　跟踪未充分复制的分区、离线分区、磁盘增长、请求排队、ISR 变化、组 Lag 和消费速率。将 Lag 折算为“积压事件所需处理时间”时，要考虑每个分区吞吐和热键。
- **故障验证**　宿主地址改成错误 Listener，观察元数据地址和超时；暂停消费制造积压后恢复，记录追平用时；在本地事务成功、提交 Offset 前终止程序，验证重启不会重复落业务数据。

### 11.1 实战验收

| 能力 | 提交证据 |
|---|---|
| 两套网络入口 | 宿主与容器分别获取元数据，说明它们连的是哪个 Listener |
| 顺序与并行度 | 同一订单的分区和版本顺序，组成员与分区分配 |
| 幂等与异常恢复 | 重复事件测试、事务断点、死信或重试结果 |
| 组进度与重放 | 停机前后的 Offset，对比 dry run 和真正回放的结果 |
| 生产评估 | 写出保留期、磁盘预算、Lag 告警和事件恢复手册 |

官方实操　[Kafka Docker Listener 示例](https://github.com/apache/kafka/blob/4.1.2/docker/examples/docker-compose-files/single-node/plaintext/docker-compose.yml) · [消费者配置](https://kafka.apache.org/41/configuration/consumer-configs/) · [Kafka 运维操作](https://kafka.apache.org/41/operations/basic-kafka-operations/) · [Spring Kafka 异常处理](https://docs.spring.io/spring-kafka/reference/kafka/annotation-error-handling.html)

延伸阅读　[RocketMQ](RocketMQ.md) · [EMQX](EMQX/EMQX.md) · [Kafka 4.1 快速开始](https://kafka.apache.org/41/getting-started/quickstart/) · [Kafka 交付语义](https://kafka.apache.org/41/design/design/) · [KafkaConsumer API](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)
