# EMQX 使用笔记（换热站项目 · Docker 部署）

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

MQTT 是**应用层**协议，依赖 TCP（**传输层**）提供可靠的双向字节流。TCP 保证数据不丢失、顺序到达，MQTT 在此基础上定义“主题”“服务质量”“遗嘱”等语义。可以把 TCP 看作“电话线路”，MQTT 就是通话时的“语言规则”——线路通了，双方才能按规则对话。

- **MQTT 客户端**：每个换热站控制器是一个客户端，有唯一 Client ID
- **主题（Topic）**：如 `station/1/temperature`，用 `/` 分层，可用通配符订阅：
  - **单层** `+`：`station/+/temperature` 匹配所有站温度
  - **多层** `#`：`station/#` 匹配所有站所有数据
- **会话（Session）**：客户端断开后，若设置了 Clean Session = false，EMQX 会保留未接收的 QoS 1/2 消息，重连后推送。
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

MQTT v5.0（EMQX 5.x 同时支持 v3.1.1）定义的控制报文分为三大类：

- **连接与断开**：CONNECT, CONNACK, DISCONNECT
- **心跳保活**：PINGREQ, PINGRESP
- **主题订阅/取消**：SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK
- **消息发布**：PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP

所有报文由 **固定报头**（必选）、**可变报头**（可选）和 **有效载荷**（可选）构成。固定报头第一个字节包含报文类型和标志位，随后是“剩余长度”（Remaining Length）。

#### 2.3.2 剩余长度（Remaining Length）的编码与解码

**概念**：剩余长度表示当前报文从“可变报头+有效载荷”的总字节数，不包括固定报头本身。该值采用变长编码（最多 4 字节），每字节最高位（bit 7）表示是否还有后续字节，低 7 位为数据。

**编码规则**：

- 将数值反复除以 128，每次取余数作为当前字节的低 7 位，若还有除尽则当前字节最高位置 1，否则置 0。
- **示例**：数值 321 → 321 / 128 = 2 余 65 → 第一个字节 0x41 (bit7=0? 实际需继续) 正确过程：
  - 先取 321 & 0x7F = 65 (0x41)，321 >> 7 = 2，因为 2 > 0，所以第一个字节最高位置 1 → 0xC1；再取 2 & 0x7F = 2，无需继续 → 0x02。最终编码为 `C1 02`。

**解码规则**：

- 从第一个字节开始，读取低 7 位，检查最高位：若为 1，则继续读取下一个字节，将低 7 位左移相应位数（第一个字节移 0，第二个移 7，第三个移 14，第四个移 21）再累加；若最高位为 0，则结束。
- 最大有效值为 268,435,455 (256MB)，超出则为协议错误。

#### 2.3.3 连接与断连报文（CONNECT / CONNACK / DISCONNECT）

- **CONNECT**：客户端发起的第一个报文，包含协议名、版本、ClientID、Clean Start（v5）或 Clean Session（v3.1.1）、心跳间隔（Keep Alive）、遗嘱（Will）字段、用户名/密码等。EMQX 收到后触发认证流程。
- **CONNACK**：服务端响应连接请求，返回连接确认标志（Session Present）和原因码（0x00 表示成功）。Session Present 指示当前是否存在之前保存的会话。
- **DISCONNECT**：客户端或服务端主动断开连接前的通知报文，v5.0 可携带原因码。

#### 2.3.4 心跳报文（PINGREQ / PINGRESP）

- **PINGREQ**：客户端在 Keep Alive 周期内无其他报文时发送，用于检测网络存活。
- **PINGRESP**：服务端必须立即回复，确认连接有效。若服务端未收到 PINGREQ 或客户端未收到 PINGRESP，将关闭连接。

#### 2.3.5 订阅/取消订阅报文（SUBSCRIBE / SUBACK / UNSUBSCRIBE / UNSUBACK）

- **SUBSCRIBE**：客户端发送（QoS 必须为 1 或 2），携带一个或多个主题过滤器及其请求的最大 QoS。服务端根据 ACL 规则授权。
- **SUBACK**：服务端返回每个订阅请求的授予 QoS（可能被降级），以及原因码。
- **UNSUBSCRIBE**：取消订阅指定主题，UNSUBACK 为确认。

#### 2.3.6 发布报文（PUBLISH）与服务质量等级

**数据传输方向**：PUBLISH 始终由发布者客户端发往服务端，服务端再转发给匹配的订阅者（跨节点转发由 EMQX 内部路由处理）。

**QoS 等级**：

- **QoS 0（最多一次）**：只发一次，不重试，不确认，适合高频传感器数据（少量丢失可容忍）。
- **QoS 1（至少一次）**：服务端响应 PUBACK，若超时未收到 ACK，发送方会重发 PUBLISH，可能产生重复消息（需业务侧去重）。
- **QoS 2（恰好一次）**：四次握手（PUBLISH → PUBREC → PUBREL → PUBCOMP），保证不重不漏，开销最大，适合关键控制指令。

**各等级报文详解**：

- **等级0 PUBLISH**：无可变报头中的 Packet ID，服务端直接转发，不存储离线消息。
- **等级1 PUBLISH + PUBACK**：发布者保存 Packet ID，等待 PUBACK，超时重发；服务端收到后存储并转发给订阅者，返回 PUBACK。
- **等级2 PUBLISH / PUBREC / PUBREL / PUBCOMP**：

  1. 发布者发送 PUBLISH（QoS=2, Packet ID = N）。
  2. 服务端回复 PUBREC（N），表示已接收。
  3. 发布者收到 PUBREC 后回复 PUBREL（N），表示可以分发。
  4. 服务端分发完成后回复 PUBCOMP（N），整个流程结束。

#### 2.3.7 保留消息功能详解

当 PUBLISH 报文设置 Retain = true 时，服务端会为该主题**保留最后一条消息**（每个主题仅保留最新一条）。新订阅者订阅该主题时，服务端**立即推送**保留消息（可设置保留消息是否过期）。EMQX 支持通过 Dashboard 或 API 清除保留消息。

#### 2.3.8 会话的清理与保留（教程大纲第17、18点）

- **Clean Start (v5) / Clean Session (v3.1.1)**：若为 true，连接时丢弃之前会话；若为 false，则重用之前会话，恢复未确认的 QoS 1/2 消息和订阅关系。
- **会话保留与 ClientID 的关系**：服务端以 ClientID 为键存储会话数据。同一 ClientID 重连时，若 Clean Session = false，则恢复会话；若使用不同的 ClientID，则无法恢复。**生产环境中每个设备必须使用固定且唯一的 ClientID**。

#### 2.3.9 遗嘱功能详解（教程大纲第19点）

遗嘱在 CONNECT 报文中指定（Will Topic, Will Payload, Will QoS, Will Retain）。当服务端检测到**客户端异常断开**（如 TCP 连接异常、心跳超时），会立即发布遗嘱消息。若客户端正常 DISCONNECT，则不会触发遗嘱。该功能常与保留消息配合，实现设备状态自动更新（参见 2.2 节）。

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

EMQX 在客户端连接时 POST 请求该接口，根据返回状态码决定是否允许连接。

授权（ACL）同理，可限制哪些客户端能发布/订阅哪些主题。

### 3.3 安全增强

- **强制 TLS 加密**：为 `8883` 端口配置证书，关闭公网 `1883` 明文端口或仅限内网使用。可通过环境变量挂载证书：
  
  ```bash
  -e EMQX_LISTENERS__SSL__DEFAULT__KEYFILE=/etc/certs/key.pem
  -e EMQX_LISTENERS__SSL__DEFAULT__CERTFILE=/etc/certs/cert.pem
  ```
  
- **客户端证书认证**：在 PLC/RTU 无法输入密码时，可启用 X.509 证书认证，EMQX 支持基于客户端证书的主题白名单。
- **Dashboard 保护**：修改默认管理员密码后，在前端 Nginx 添加 IP 白名单或 Basic Auth 二次认证。

---

## 4. 规则引擎与数据集成

这是核心部分：把设备数据自动写入时序数据库或消息队列。

### 4.1 规则引擎基本流程

1. 创建**规则**，用 SQL 语句从消息流中提取数据
2. 添加**动作**，将处理后的数据发送到目标（数据库、Kafka、HTTP 服务等）

### 4.2 示例：提取所有换热站温度并发送到 InfluxDB

假设设备上报 JSON 格式：`{"temperature": 55.2, "pressure": 1.2, "flow": 30}`

**更健壮的 SQL**（先解码 JSON，避免 payload 为二进制时报错）：

```sql
SELECT
  json_decode(payload) as data,
  topic,
  clientid
FROM
  "data/#"
WHERE
  is_json(payload)
```

动作选择“数据转发到 InfluxDB”，填写连接信息，数据写入指令：

```
temperature,station=${clientid} value=${data.temperature},pressure=${data.pressure}
```

### 4.3 桥接到 HTTP 服务

动作选“发送数据到 Web 服务”，填写后端 API 地址，将数据 POST 过去进行业务处理。可携带实时告警逻辑。

### 4.4 持久化存储与 MinIO 集成（冷数据归档）

在规则引擎中添加**条件动作**：当检测到告警或定时批量转存时，将原始消息保存为 JSON 文件并上传到对象存储。

- 创建 MinIO 的 Bucket `heat-station-archive`
- 在 EMQX 规则动作中，选择“发送到 WebHook”，调用 MinIO 的 S3 API 或通过后端中转，把消息保存为 `archive/2025/03/station1_161200.json`
- 后端也可定期从 InfluxDB 导出历史数据转存 MinIO，利用对象存储低成本存放冷数据。

**效果**：热数据在 InfluxDB 供实时查询，冷数据在 MinIO 里可供审计和模型训练，降低时序数据库存储压力。

---

## 5. 高可用与集群运维（Docker Compose）

生产环境单节点风险大，需要集群。使用 Docker Compose 启动两节点集群。

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
version: '3.7'
services:
  emqx1:
    image: emqx/emqx:5.7.2
    container_name: emqx1
    environment:
      - EMQX_NODE_NAME=emqx@emqx1
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
      - EMQX_NODE_NAME=emqx@emqx2
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
- 升级时逐个节点替换：`docker-compose up -d --no-deps emqx1` 滚动更新，保证集群不中断
- 监控 Dashboard 或 API 获得连接数、消息速率
- 日志持久化到宿主并配合 `logrotate` 切割，防止磁盘写满

---

## 6. 性能调优与监控

### 6.1 系统层面

- 增加文件描述符限制：`ulimit -n 1048576`
- 调整内核参数 `tcp_tw_reuse`、`tcp_fin_timeout` 等
- 对于 Docker，可在宿主机调整，容器继承部分设置

### 6.2 EMQX 配置调整

通过 Dashboard 或 `etc/emqx.conf` 修改（挂载配置卷）：
- 最大连接数：`listener.tcp.external.max_connections`
- 节点间通信缓冲区：`rpc.tcp_buffer_size`
- 开启共享订阅以实现消息派发负载均衡

### 6.3 内置监控

Dashboard → 监控 提供节点状态、收发字节、消息速率、连接数、规则引擎执行情况。可设置告警（Webhook 通知）。

### 6.4 集成 Prometheus

EMQX 提供了 Prometheus 指标端点，在 Docker 环境变量开启：

```yaml
environment:
  - EMQX_PROMETHEUS__ENABLE=true
```

用 Prometheus + Grafana 可视化监控，模板 ID 可在 Grafana 官网找。

### 6.5 关键告警指标（推荐）

- **活跃连接数**：接近 licence 限制或系统上限前预警
- **消息流入/流出速率**：突降可能表示大面积设备离线
- **规则引擎执行失败率**：若突然升高，可能是后端数据库宕机或消息格式变更
- **集群节点状态**：监控心跳，及时发现脑裂或单点故障
- **系统 CPU/内存/磁盘**：尤其注意 `data` 目录所在磁盘用量

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
