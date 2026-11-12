# EMQX 使用笔记（换热站项目 · Docker 部署）

---

## 1. 环境与快速安装

### 1.1 场景说明

每个换热站有 PLC / RTU 设备，通过 MQTT 协议上报温度、压力、流量等数据到中心服务器。使用 EMQX 作为消息中间件，接收数据并桥接到后端数据库和告警系统。

### 1.2 Docker 安装 EMQX

服务器已安装 Docker，直接拉取镜像运行。**生产环境建议锁定小版本号（如 `emqx/emqx:5.7.2`），避免 `latest` 自动升级引入兼容性问题。**

```bash
# 拉取指定版本（推荐）
docker pull emqx/emqx:5.7.2

# 启动单节点（测试用）
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 8084:8084 \
  -p 8883:8883 \
  -p 18083:18083 \
  emqx/emqx:5.7.2
```

端口说明：
- `1883`：MQTT TCP 端口
- `8883`：MQTT SSL 端口
- `8083`：WebSocket 端口
- `8084`：WebSocket SSL 端口
- `18083`：Dashboard 管理控制台

启动后访问 `http://服务器IP:18083`，默认账号 `admin` / 密码 `public`，**务必登录后立即修改密码**

---

## 2. 核心概念理解

[参考课件](<MQTT 协议详解（EMQX）讲义.pptx>)

**感性认识：传输层与应用层的关系**

MQTT 是**应用层**协议，依赖 TCP（**传输层**）提供可靠的双向字节流。TCP 在连接有效时提供有序可靠的字节流，但不能保证断连后消息或业务处理一定成功，MQTT 在此基础上定义“主题”“服务质量”“遗嘱”等语义。可以把 TCP 看作“电话线路”，MQTT 就是通话时的“语言规则”——线路通了，双方才能按规则对话。

- **MQTT 客户端**：每个换热站控制器是一个客户端，有唯一 Client ID
- **主题（Topic）**：如 `station/1/temperature`，用 `/` 分层，可用通配符订阅：
  - **单层** `+`：`station/+/temperature` 匹配所有站温度
  - **多层** `#`：`station/#` 匹配所有站所有数据
- **会话（Session）**：客户端断开后，若设置了 `Clean Session = false`，EMQX 会保留未接收的 QoS 1/2 消息，重连后推送。
- **保留消息（Retained Message）**：主题最后一条消息会被存储，新订阅者立即获得当前值，适合获取设备最新状态。
- **遗嘱消息（Will Message）**：客户端异常断开时，EMQX 自动发布一条消息，可用来检测设备离线。

### 2.1 主题设计深化（换热站最佳实践）

建议将主题分为四个维度，清晰划分职责：

| 类型     | 主题格式                     | 说明                     |
| -------- | ---------------------------- | ------------------------ |
| 数据上报 | `data/{station_id}/{param}`  | 如 `data/1/temperature`  |
| 设备状态 | `status/{station_id}`        | 遗嘱消息自动更新         |
| 控制指令 | `cmd/{station_id}/setpoint`  | 后端下发阀门开度等       |
| 指令应答 | `cmd/{station_id}/setpoint/ack` | 设备回执，保证指令送达 |

- **QoS 选用**：数据上报和指令建议用 **QoS 1**（至少一次），状态消息可用 QoS 0 降低开销。
- **Payload 格式**：统一使用 JSON，方便规则引擎解析。

#### 用隔离报文核对主题与字段

原笔记已经给出了换热站主题分层和规则引擎的方向。联调时先对齐设备侧实际发布的 Topic、QoS、保留标志、消息格式，以及后端订阅和权限。一个主题应能判断属于哪个站点与用途。采集消息最好携带能追查和去重的事件编号、设备标识、采集时间、数据单位与格式版本。新增字段先让下游能读旧格式，再安排设备升级。不要把显示名称、整段图片或账户凭据塞进 Topic。

下面是**隔离测试**的报文结构，用来说明如何把业务编号带过 MQTT、规则和数据库。主题可用 `heat/lab/42/telemetry`，实际字段与主题按原设备协议选择。

```json
{
  "schema_version": 1,
  "event_id": "lab-42-0001",
  "device_id": "lab-42",
  "sampled_at": "2026-01-01T08:00:00+08:00",
  "temperature_c": 66.5
}
```


### 2.2 遗嘱消息与保留消息的组合应用

- **遗嘱消息**：每个 PLC 连接时在 CONNECT 报文中设置：
  
  ```
  Will Topic: status/{station_id}
  Will Payload: {"status": "offline", "timestamp": ...}
  Will QoS: 1
  Will Retain: true
  ```

  设备异常断开时，该消息自动发布并保留，所有订阅方立刻感知离线。

- **保留消息**：每次数据上报时，可以将关键参数（如温度、压力）发布为保留消息：
  
  ```
  Topic: data/1/temperature, Payload: 23.5, Retain: true
  ```

  新上线的 SCADA/HMI 订阅 `data/+/temperature` 后立即获得所有站点的最新温度值，无需等待下次上报周期。

### 2.3 MQTT协议报文格式与交互流程详解

#### 2.3.1 报文总览与分组

MQTT v5.0（EMQX 5.x 同时支持 v3.1.1）定义的控制报文可分为以下几组：

- **连接与断开**：CONNECT, CONNACK, DISCONNECT
- **心跳保活**：PINGREQ, PINGRESP
- **增强认证（仅 v5.0）**：AUTH
- **主题订阅/取消**：SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK
- **消息发布**：PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP

所有报文由 **固定报头**（必选）、**可变报头**（可选）和 **有效载荷**（可选）构成。固定报头第一个字节包含报文类型和标志位，随后是“剩余长度”（Remaining Length）。

#### 2.3.2 剩余长度（Remaining Length）的编码与解码

**概念**：剩余长度表示当前报文从“可变报头+有效载荷”的总字节数，不包括固定报头本身。该值采用变长编码（最多 4 字节），每字节最高位（bit 7）表示是否还有后续字节，低 7 位为数据。

**编码规则**：

- 将数值反复除以 128，每次取余数作为当前字节的低 7 位，若商仍大于 0 则当前字节最高位置 1，否则置 0。
- **示例**：数值 321 的编码过程：
  - 先取 321 & 0x7F = 65 (0x41)，321 >> 7 = 2，因为 2 > 0，所以第一个字节最高位置 1 → 0xC1；再取 2 & 0x7F = 2，无需继续 → 0x02。最终编码为 `C1 02`。

**解码规则**：

- 从第一个字节开始，读取低 7 位，检查最高位：若为 1，则继续读取下一个字节，将低 7 位左移相应位数（第一个字节移 0，第二个移 7，第三个移 14，第四个移 21）再累加；若最高位为 0，则结束。
- 最大有效值为 268,435,455 字节（256 MiB − 1），超出则为协议错误。

#### 2.3.3 连接与断连报文（CONNECT / CONNACK / DISCONNECT）

- **CONNECT**：客户端发起的第一个报文，包含协议名、版本、ClientID、Clean Start（v5）或 Clean Session（v3.1.1）、心跳间隔（Keep Alive）、遗嘱（Will）字段、用户名/密码等。EMQX 收到后触发认证流程。
- **CONNACK**：服务端响应连接请求，返回连接确认标志（Session Present）和原因码（0x00 表示成功）。Session Present 指示当前是否存在之前保存的会话。
- **DISCONNECT**：客户端或服务端主动断开连接前的通知报文，v5.0 可携带原因码。

#### 2.3.4 心跳报文（PINGREQ / PINGRESP）

- **PINGREQ**：客户端在 Keep Alive 周期内无其他报文时发送，用于检测网络存活。
- **PINGRESP**：服务端收到 PINGREQ 后返回响应。Keep Alive 非零时，若服务端在 1.5 倍 Keep Alive 内未收到任何 MQTT 控制报文，应断开连接；不要求周期内必须有 PINGREQ。客户端未在合理时间内收到 PINGRESP 时应断开。

#### 2.3.5 订阅/取消订阅报文（SUBSCRIBE / SUBACK / UNSUBSCRIBE / UNSUBACK）

- **SUBSCRIBE**：客户端发送（固定报头标志必须为 `0010`，按 QoS 1 交互；订阅请求的最大消息 QoS 可为 0/1/2），携带一个或多个主题过滤器及其请求的最大 QoS。服务端根据 ACL 规则授权。
- **SUBACK**：服务端返回每个订阅请求的授予 QoS（可能被降级），以及原因码。
- **UNSUBSCRIBE**：取消订阅指定主题，UNSUBACK 为确认。

#### 2.3.6 发布报文（PUBLISH）与服务质量等级

**数据传输方向**：发布端向服务端发送 PUBLISH，服务端也向匹配的订阅客户端发送 PUBLISH；两段 QoS 交互彼此独立（跨节点转发由 EMQX 内部路由处理）。

**QoS 等级**：

- **QoS 0（最多一次）**：只发一次，不重试，不确认，适合高频传感器数据（少量丢失可容忍）。
- **QoS 1（至少一次）**：接收方响应 PUBACK，可能产生重复消息，需业务侧去重。MQTT 5.0 的未确认消息在恢复会话重连时重发，不能简单描述为连接内按超时重发。
- **QoS 2（恰好一次）**：四次握手（PUBLISH → PUBREC → PUBREL → PUBCOMP），保证一次协议交付中的重复消除，开销最大；不能保证端到端业务副作用恰好执行一次，关键指令仍需幂等、回执与重试机制。

**各等级报文详解**：

- **等级0 PUBLISH**：无 Packet ID，不要求确认；离线 QoS 0 消息可按服务端实现选择丢弃或排队。
- **等级1 PUBLISH + PUBACK**：发送方保存 Packet ID 并等待 PUBACK，恢复会话时重发未确认消息；服务端收到后存储并转发给订阅者，返回 PUBACK。
- **等级2 PUBLISH / PUBREC / PUBREL / PUBCOMP**：

  1. 发布者发送 PUBLISH（QoS=2, Packet ID = N）。
  2. 服务端回复 PUBREC（N），表示已接收。
  3. 发布者收到 PUBREC 后回复 PUBREL（N），表示可以分发。
  4. 服务端回复 PUBCOMP（N），这一段 QoS 2 交互结束；不代表订阅端已完成业务处理。

**从协议确认追到业务落库**

| 判断 | 能说明什么 | 还要检查什么 |
|---|---|---|
| 设备端收到 QoS 1 PUBACK | 发布已经被这一跳的对端确认 | 消费端是否收到，业务处理是否落库 |
| 后端收到两条相同 event_id | 可能有重发、重连或规则重复投递 | 唯一键、处理日志与实际影响行数 |
| 新订阅端立即收到旧状态 | 可能是保留消息 | 发布时刻、retain 标志和事件编号 |
| 离线回来没有收到旧采集 | 可能是会话或订阅状态不同 | MQTT 版本、会话过期、QoS、订阅和队列配置 |
| 页面出现站点数据但时间旧 | 数据可能来自缓存或旧事件 | 采集时间、入库时间和查询窗口 |

QoS 是协议传递语义，业务落库要自己做幂等。尤其是 QoS 1，短时断连恢复后可能有重复。订阅允许的 QoS 和发布时的 QoS 一起影响投递等级。保留消息用于表达当前可见状态，持久会话用于维护连接中断后的订阅及相关消息，二者用途不同。报警历史和趋势分析仍应保存到业务存储。设备使用独立 Client ID，避免误把两个客户端配置成同一标识而反复被踢下线。


#### 2.3.7 保留消息功能详解

当 PUBLISH 报文设置 Retain = true 时，服务端会为该主题**保留最后一条消息**（每个主题仅保留最新一条）。新订阅者订阅该主题时，服务端**立即推送**保留消息（可设置保留消息是否过期）。EMQX 支持通过 Dashboard 或 API 清除保留消息。

#### 2.3.8 会话的清理与保留

- **MQTT 3.1.1 Clean Session**：false 时使用持久会话，重连使用相同 ClientID 才能恢复。
- **MQTT 5.0 Clean Start**：只决定连接开始时是否清理旧会话；断连后的保留时间由 Session Expiry Interval 决定，缺省为 0。要跨连接保留会话，需设置大于 0 的过期间隔。
- **会话保留与 ClientID 的关系**：服务端以 ClientID 为键存储会话数据。同一 ClientID 重连时，若 Clean Session = false，则恢复会话；若使用不同的 ClientID，则无法恢复。**生产环境中每个设备必须使用固定且唯一的 ClientID**。

#### 2.3.9 遗嘱功能详解

遗嘱在 CONNECT 报文中指定（Will Topic, Will Payload, Will QoS, Will Retain）。当服务端检测到**客户端异常断开**（如 TCP 连接异常、心跳超时），按协议和配置发布遗嘱；MQTT 5.0 的 Will Delay Interval 可延迟发布。正常 DISCONNECT 通常不发布遗嘱，但 v5 原因码 `0x04` 明确请求发布遗嘱。该功能常与保留消息配合，实现设备状态自动更新（参见 2.2 节）。

> **注**：理解上述报文交互后，可使用 Wireshark 抓包或 MQTTX 的“调试”模式观察报文细节，辅助排障。

---

## 3. 认证与授权（快速配置）

设备连接需要鉴权，避免非法接入。

### 3.1 简单测试：用 Dashboard 添加用户名密码

在 Dashboard → 访问控制 → 认证 → 创建内置数据库认证，添加用户 `station1` 密码 `mypassword`。客户端连接时填写即可。

### 3.2 生产推荐：使用 HTTP 回调认证

如果已有用户系统，配置 HTTP 认证：

```bash
# Dashboard → 访问控制 → 认证 → 创建 HTTP 认证
```

填写认证 URL：

```
http://your-backend:8080/mqtt/auth
```

EMQX 在客户端连接时 POST 请求该接口，按 EMQX 5.x 的 HTTP 认证响应协议判定：例如 HTTP 200 配合 JSON `{"result":"allow","is_superuser":false}` 放行，`{"result":"deny"}` 拒绝。不能沿用 4.x 只看 200/403 的规则。

授权（ACL）同理，可限制哪些客户端能发布/订阅哪些主题。

### 3.3 安全增强

- **强制 TLS 加密**：为 `8883` 端口配置证书，关闭公网 `1883` 明文端口或仅限内网使用。先通过卷挂载证书，再用环境变量指定容器内路径：
  
  ```bash
  # 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
  -e EMQX_LISTENERS__SSL__DEFAULT__SSL_OPTIONS__KEYFILE=/etc/certs/key.pem
  -e EMQX_LISTENERS__SSL__DEFAULT__SSL_OPTIONS__CERTFILE=/etc/certs/cert.pem
  ```

- **客户端证书认证**：在 PLC/RTU 无法输入密码时，可启用 X.509 证书认证，EMQX 支持基于客户端证书的主题白名单。
- **Dashboard 保护**：修改默认管理员密码后，在前端 Nginx 添加 IP 白名单或 Basic Auth 二次认证。

#### 分别验证连接、登录和主题授权

先确认客户端所在网络。设备可用原生 MQTT，浏览器需要 MQTT over WebSocket。网页使用 HTTPS 时，应在可达入口验证 WSS 和证书。若代理改变了路径，浏览器打开的 URL、反代命中的 location 和 Broker 监听路径要逐一对应。HTTP 101 之后还要等 MQTT CONNACK，握手成功不等于账号登录成功。能登录也不能说明能发所有 Topic。

测试账号只授权隔离主题。操作顺序如下：

1. 使用唯一 Client ID 连接，观察 Broker 日志和控制台中实际命中的 Listener。
2. 用独立消费端订阅已授权主题，记录 SUBACK。再对专用的未授权测试主题验证拒绝。
3. 发布一个带唯一编号且不设 retain 的报文。记录发布端确认、订阅端收到的 payload 及时间。
4. 关闭并重连消费端，对照相同 Client ID 与新 Client ID 的会话表现。仅在隔离范围改变会话参数。
5. 经浏览器入口再做一次，对照 TCP 路径和 WebSocket 路径。两个结果不同就分开查代理、TLS、路径和 MQTT 层。

只需要保存脱敏后的标识、连接时间、失败层和样本编号。不使用真实设备的 Client ID 做测试。命令行和截图中避免留下密码。容器部署时可先查看 Broker 端口和持久化配置目录，确认看到的是当前节点。

```bash
# 使用实际容器名。仅查看映射和近期日志，定位连接落到哪个实例。
: "${EMQX_CONTAINER:?请设置 EMQX 容器名}"
docker port "$EMQX_CONTAINER"
docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$EMQX_CONTAINER"
docker logs --since 10m "$EMQX_CONTAINER"
```


---

## 4. 规则引擎与数据集成

这是**核心部分**：把设备数据自动写入时序数据库或消息队列。

### 4.1 规则引擎基本流程

1. 创建**规则**，用 SQL 语句从消息流中提取数据
2. 添加**动作**，将处理后的数据发送到目标（数据库、Kafka、HTTP 服务等）

### 4.2 示例：提取所有换热站温度并发送到 InfluxDB

假设设备上报 JSON 格式：`{"temperature": 55.2, "pressure": 1.2, "flow": 30}`

**SQL 示例**（假定 payload 是合法 JSON；解码失败会导致规则执行失败，需在设备端校验并监控失败日志）：

```sql
-- 读取样例数据用于对照，留意投影列与实际返回的值。
SELECT
  json_decode(payload) as data,
  topic,
  clientid
FROM
  "data/#"
```

动作选择“数据转发到 InfluxDB”，填写连接信息，数据写入指令：

```
temperature,station=${clientid} value=${data.temperature},pressure=${data.pressure}
```

#### 先验证规则 SQL，再检查动作

规则的输入、SQL 匹配与字段提取、动作执行、目的端写入是四个环节。规则测试页面先用隔离主题和第 2.1 节的测试 JSON。动作接 HTTP 或时序库之前，确认提取的类型、空值和单位符合接收方约定。下面展示规则 SQL 的字段提取方式，测试时按实际 EMQX 版本核对编辑器中的可用字段。

```sql
-- 只匹配实验主题，避免业务采集也触发测试动作。
SELECT
  clientid AS client_id,
  topic,
  payload.event_id AS event_id,
  payload.sampled_at AS sampled_at,
  payload.temperature_c AS temperature_c
FROM "heat/lab/+/telemetry"
```

先保存一条正例与一条错误结构。若主题没命中，查发布主题、大小写与通配符。命中但字段为空，查原始 JSON 是否含对应键，温度是数值还是字符串。规则结果正确而目的端无数据时，查动作配置、连接状态、权限、超时和目的端日志。先用测试动作验证，避免一开始让原始设备的数据流进演练库。

如果 MQTT 使用隔离网络，EMQX 到动作目标的可达性也要从 Broker 所在网络确认。应用收到重复或乱序数据时，以采集时间与事件编号判断，保留到达时间用于测链路延迟。消息从设备到 Broker、规则到目的端和业务存储各有缓冲，单看 Broker 接入速率无法判断末端是否跟上。


### 4.3 桥接到 HTTP 服务

动作选“发送数据到 Web 服务”，填写后端 API 地址，将数据 POST 过去进行业务处理。可携带实时告警逻辑。

### 4.4 持久化存储与 MinIO 集成（冷数据归档）

在规则引擎中添加**条件动作**：当检测到告警或定时批量转存时，将原始消息保存为 JSON 文件并上传到对象存储。

- 创建 MinIO 的 Bucket `heat-station-archive`
- 在 EMQX 规则动作中调用后端 Webhook，由后端使用 MinIO SDK 签名上传（普通 Webhook 不会自动生成 S3 签名），或使用当前版本支持的 S3 数据集成，把消息保存为 `archive/2025/03/station1_161200.json`
- 后端也可定期从 InfluxDB 导出历史数据转存 MinIO，利用对象存储低成本存放冷数据。

**效果**：热数据在 InfluxDB 供实时查询，冷数据在 MinIO 里可供审计和模型训练，降低时序数据库存储压力。

---

## 5. 高可用与集群运维（Docker Compose）

以下用单机 Compose 的两节点演示集群通信，不能提供宿主机故障容错。生产需多主机部署并验证节点数、故障模型和负载均衡。

### 5.1 目录结构

```
emqx-cluster/
├── docker-compose.yml
└── emqx1/
    └── data/  (挂载的数据目录)
    └── log/   (日志持久化)
```

`docker-compose.yml` 示例（增加资源限制与健康检查）：

```yaml
# ports 左侧是宿主入口，右侧是容器端口。数据卷独立于容器重建。
version: '3.7'
services:
  emqx1:
    image: emqx/emqx:5.7.2
    container_name: emqx1
    environment:
      - EMQX_NODE__NAME=emqx@emqx1
      - EMQX_CLUSTER__DISCOVERY_STRATEGY=static
      - EMQX_CLUSTER__STATIC__SEEDS=[emqx@emqx1,emqx@emqx2]
    ports:
      - 1883:1883
      - 18083:18083
    volumes:
      - ./emqx1/data:/opt/emqx/data
      - ./emqx1/log:/opt/emqx/log
    networks:
      - emqx-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    healthcheck:
      test: ["CMD", "emqx", "ping"]
      interval: 30s
      timeout: 5s
      retries: 3

  emqx2:
    image: emqx/emqx:5.7.2
    container_name: emqx2
    environment:
      - EMQX_NODE__NAME=emqx@emqx2
      - EMQX_CLUSTER__DISCOVERY_STRATEGY=static
      - EMQX_CLUSTER__STATIC__SEEDS=[emqx@emqx1,emqx@emqx2]
    ports:
      - 1884:1883
      - 18084:18083
    volumes:
      - ./emqx2/data:/opt/emqx/data
      - ./emqx2/log:/opt/emqx/log
    networks:
      - emqx-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

networks:
  emqx-net:
    driver: bridge
```

执行 `docker-compose up -d`，访问任一 Dashboard 节点，左侧“集群”可查看节点状态。

### 5.2 负载均衡

设备连接地址不宜直接写节点 IP，可在前面挂 Nginx/HAProxy 或使用云服务商负载均衡，配置 TCP 转发到 `1883` 端口。若使用 Nginx 流模块：

```nginx
# 根据 location 选择代理路径，核对 proxy_pass 的 URI、上游地址和转发头。
stream {
    upstream mqtt_backend {
        server emqx1:1883;
        server emqx2:1883;
    }
    server {
        listen 1883;
        proxy_pass mqtt_backend;
    }
}
```

### 5.3 运维备忘

- 备份 `data/` 目录和 `etc/` 配置
- 升级时逐个节点替换：先更新镜像标签，再用 `docker compose up -d --no-deps emqx1` 重建单节点；需验证升级路径、剩余容量和客户端重连，不能保证现有 TCP 连接不中断
- 监控 Dashboard 或 API 获得连接数、消息速率
- 日志持久化到宿主并配合 `logrotate` 切割，防止磁盘写满

**重启与升级后的验证顺序**

部署和升级前保留正在运行的镜像版本、持久化目录、Listener、认证方式、授权范围和规则列表。配置恢复后先用隔离账号测登录、允许主题和拒绝主题，再验证规则动作和一条业务样本。Broker 的配置、消息状态、下游数据库与对象存储不能互相替代备份。集群节点或版本变动时按对应版本的备份恢复路径操作，先在测试节点验证兼容性。


---

## 6. 性能调优与监控

### 6.1 系统层面

- 增加文件描述符限制：`ulimit -n 1048576`
- 调整内核参数 `tcp_tw_reuse`、`tcp_fin_timeout` 等
- 对于 Docker，可在宿主机调整，容器继承部分设置

### 6.2 EMQX 配置调整

通过 Dashboard 或 `etc/emqx.conf` 修改（挂载配置卷）：

- 最大连接数：`listeners.tcp.default.max_connections`（5.x 格式）
- 节点间通信缓冲区：`rpc.tcp_buffer_size`
- 开启共享订阅以实现消息派发负载均衡

### 6.3 内置监控

Dashboard → 监控 提供节点状态、收发字节、消息速率、连接数、规则引擎执行情况。可设置告警（Webhook 通知）。

### 6.4 集成 Prometheus

EMQX 5.7 可由 Prometheus 拉取 `/api/v5/prometheus/stats`，按实例配置提供认证；不需要用不适用的 `EMQX_PROMETHEUS__ENABLE` 开关开启拉取端点。若使用 Pushgateway，则单独配置该版本的推送参数。

用 Prometheus + Grafana 可视化监控，模板 ID 可在 Grafana 官网找。

### 6.5 关键告警指标（推荐）

- **活跃连接数**：接近 licence 限制或系统上限前预警
- **消息流入/流出速率**：突降可能表示大面积设备离线
- **规则引擎执行失败率**：若突然升高，可能是后端数据库宕机或消息格式变更
- **集群节点状态**：监控心跳，及时发现脑裂或单点故障
- **系统 CPU/内存/磁盘**：尤其注意 `data` 目录所在磁盘用量

#### 用连接、积压和目的端指标排障

| 现象 | 先比较 | 动作 |
|---|---|---|
| 连接数周期性上升下降 | Client ID、断开原因、心跳与客户端日志 | 区分冲突登录、网络抖动、心跳超时和客户端重启 |
| 收到很多，处理成功变少 | 规则匹配、动作失败、缓冲与目标写入速率 | 控制测试流量，定位慢依赖和重试，避免排队无限增长 |
| 管理面正常，设备掉线 | 设备连接所在 Listener、对外端口与实际协议 | 从设备网络复测，不能用 Dashboard 登录代替 |
| 重启后策略看似丢失 | 数据卷路径、配置来源、节点名与加载日志 | 核对备份与实际挂载，在演练节点先验证恢复 |
| 日志说已发布但没有业务行 | 事件编号、动作回执、后端入库结果 | 把发布、转发与落库分别确认，查重复或失败记录 |


---

## 7. 实践流程速查

1. 安装 Docker，启动单节点 EMQX 测试连接。
2. 使用 MQTTX 客户端模拟换热站，发测试消息（主题 `data/1/temperature`）。
3. 在 Dashboard 配置认证（先试用内置数据库，再切 HTTP）。
4. 创建规则，桥接到 InfluxDB 或 Kafka，验证数据链路。
5. 设计主题结构，配置保留消息和遗嘱消息，测试设备离线告警。
6. 编写 Docker Compose，部署两节点集群，验证消息在节点间路由。
7. 前端接负载均衡，修改设备连接地址。
8. 开启 Prometheus 监控，导入 Grafana 模板，设置告警规则。
9. （可选）接入 MinIO 冷存储，将关键原始报文或历史数据归档。
10. 安全加固：启用 TLS、关闭明文端口、配置客户端证书。

### 交接时记录完整链路

交接时写清设备入口、浏览器入口、Topic 约定、测试样本、三处时间（采集、Broker、入库）和出现异常时应该查哪一层。以前的部署记录用来解释为何选择 MQTT/WS 和特定路径，实际复用以当前网络与配置为准。 [EMQX MQTT 概念](https://docs.emqx.com/en/emqx/latest/get-started/messaging/mqtt-concepts.html) · [WebSocket 接入](https://docs.emqx.com/en/emqx/latest/develop/connect-emqx/mqtt-over-websocket.html) · [EMQX 消息积压](https://docs.emqx.com/en/emqx/latest/develop/design/inflight-window-and-message-queue.html)

**验收时一次只变更一个参数**

验证断线重连、保留消息、认证或会话时，保持设备 ID、报文结构和另一端订阅不变，只改一个条件。每轮保存成功与失败的事件编号、Broker 事件和目的端结果，避免把多种改变合并解释成单一原因。


---

## 8. 系统数据流总览

```
PLC/RTU 设备
    │
    │ MQTT over TLS
    ▼
EMQX 集群 (负载均衡)
    │
    ├── 认证/授权 (HTTP回调或内置库)
    ├── 规则引擎 ──────┬──→ InfluxDB (热数据) ──→ Grafana 仪表板
    │                  ├──→ Webhook 告警 (钉钉/邮件)
    │                  └──→ MinIO 归档 (冷数据, 原始报文)
    │
    └── Prometheus 监控 ←── 运维人员
```

---

[参考网课](https://www.bilibili.com/video/BV1VDdoYhEYh/?spm_id_from=333.1391.0.0&p=4&vd_source=e0c0ad2a316e90d4078b1131e8182407)

[MQTT-3.1.1参考文档](MQTT-3.1.1标准协议文档.pdf)

---
