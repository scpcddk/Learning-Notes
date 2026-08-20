# 云原生 + AIOps 四阶段演进路线图（最终完备版）

> **核心理念**：**先单体闭环 → 再微服务解耦 → 后云原生编排 → 最后叠加 AIOps**  
> 不跳级，每一阶段都是下一阶段的底座；时间线对齐大厂暑期实习与秋招节奏。

---

## 总览架构流向

```
阶段1：单体业务闭环
  Spring Boot 3.x + MySQL 8.0 + Redis + MinIO + EMQX + SRS + Nginx
    │
    ▼
阶段2：微服务化与异步解耦
  Spring Cloud Alibaba (Nacos/Gateway/Sentinel) + OpenFeign + Kafka/RocketMQ + SkyWalking
    │
    ▼
阶段3：云原生底座（无状态服务上云）
  Docker 多阶段镜像 → Kubernetes 集群编排 (Deployment/Service/Ingress) + Helm + CI/CD
    │
    ▼
阶段4：AIOps 智能运维（可观测性 + AI）
  Prometheus + Grafana + Loki + OpenTelemetry → Kafka 数据管道 → Python/大模型 (异常检测与 RCA)
```

---

## 阶段 1：单体业务闭环

### 核心目标

用 Java/Spring Boot 将全部已有中间件调通，形成完整业务闭环。**数据库锁定 MySQL 8.0**，吃透 InnoDB、索引、MVCC、锁机制。

### 核心技术栈

- **语言/框架**：Java 17/21、Spring Boot 3.x
- **数据库/缓存**：MySQL 8.0、Redis
- **物联网消息**：EMQX
- **对象存储**：MinIO
- **流媒体**：SRS（可选）
- **反向代理**：Nginx
- **ORM**：MyBatis-Plus

### 实战落地任务

1. **设备数据链路**  
   EMQX 接收换热站设备上报数据 → Spring Boot 订阅并解析 → 写入 MySQL 持久化 → 更新 Redis 热点状态/缓存。
2. **文件与图片上传**  
   图片/文件通过 MinIO 预签名 URL 直传。
3. **流媒体拉流**  
   如需要视频监控，接入 SRS 实现摄像头实时拉流。
4. **统一入口**  
   配置 Nginx 反向代理、SSL 证书卸载、静态资源托管。

### 验收标准

- 设备数据实时经过 EMQX → Spring Boot → MySQL/Redis。
- 图片可通过预签名 URL 直传 MinIO。
- Nginx 统一代理后端服务并支持 HTTPS。
- 能用 Java 代码熟练操作上述中间件，业务闭环。

---

## 阶段 2：微服务架构拆分与异步解耦

### 核心目标

理解单体拆微服务的原因，解决服务发现、网关、调用、熔断、链路追踪，**并引入 Kafka/RocketMQ 实现异步解耦与削峰填谷**。

### 核心技术栈

- **微服务框架**：Spring Cloud Alibaba
- **注册/配置中心**：Nacos
- **网关**：Spring Cloud Gateway
- **服务调用**：OpenFeign
- **熔断限流**：Sentinel
- **分布式锁**：Redis + Redisson
- **链路追踪**：SkyWalking / Zipkin
- **消息队列**：Kafka / RocketMQ

### 实战落地任务

1. **服务拆分**  
   将单体工程拆分为：
   - `auth-service`：认证服务
   - `device-service`：设备/物联网接入服务
   - `media-service`：流媒体/文件服务
   - `alarm-service`：告警服务
2. **服务治理**  
   - Nacos 作为注册中心与配置中心。
   - Spring Cloud Gateway 作为统一流量入口，完成鉴权、限流、路由。
3. **服务调用与容错**  
   - OpenFeign 完成服务间 HTTP 调用。
   - Sentinel 实现熔断降级、限流。
4. **异步解耦**  
   - `device-service` 收到设备数据后，通过 Kafka/RocketMQ 异步通知 `alarm-service` 触发告警，避免 HTTP 同步阻塞。
   - 日志数据也可通过 Kafka 进行缓冲，为后续 AIOps 数据管道打基础。
5. **分布式痛点解决**  
   - Redisson 实现分布式锁。
   - SkyWalking 收集全链路调用追踪。

### 验收标准

- 单体工程拆分为多个微服务，独立部署、独立调用。
- 服务间通过 Nacos 发现，Gateway 统一路由。
- 服务宕机时 Sentinel 触发熔断降级。
- Kafka 消息异步流转正常，削峰填谷效果可见。
- SkyWalking 展示完整调用链路。

---

## 阶段 3：拥抱云原生底座（无状态服务上云）

### 核心目标

从单机 Docker 升维到 Kubernetes 集群编排，实现自动部署、弹性扩缩容、自愈。  
**关键原则：无状态服务上 K8s，有状态服务外置。**

### 核心技术栈

- **容器化**：Docker、多阶段构建 Dockerfile
- **容器编排**：Kubernetes（Pod、Deployment、Service、Ingress、ConfigMap、Secret）
- **包管理**：Helm
- **入口控制器**：Ingress-Nginx
- **CI/CD**：GitLab CI / GitHub Actions

### 部署原则（避坑提示）

- **无状态服务（Stateless）**：Java 微服务（auth-service、device-service、media-service、alarm-service）全部通过 K8s Deployment 部署，利用 HPA 弹性扩缩容。
- **有状态服务（Stateful）**：MySQL、Redis、EMQX、MinIO 初学阶段建议放在 K8s 集群外部（或 Docker 独立运行），通过 IP/域名供 K8s 内部微服务连接。  
  避免在 K8s 中处理 PV/PVC、数据持久化等复杂问题，先聚焦业务代码云原生化。

### 实战落地任务

1. **镜像构建**  
   为每个微服务编写多阶段构建 Dockerfile，生成体积小、安全的镜像。
2. **K8s 资源定义**  
   - `Deployment`：管理副本数、滚动升级。
   - `Service`：集群内服务发现与负载均衡。
   - `ConfigMap/Secret`：环境变量与敏感信息分离。
   - `Ingress`：外部域名路由到内部服务。
3. **云原生特性实操**  
   - 配置 HPA 实现 Pod 自动弹性扩缩容。
   - 配置 Liveness/Readiness 健康检查。
   - 验证无缝滚动更新，服务不中断。

### 验收标准

- 微服务均以 Docker 镜像形式交付。
- 通过 `kubectl` 一键部署整个系统到 K8s 集群。
- 流量突增时 HPA 自动扩容；Pod 崩溃时自动重启。
- Ingress 实现域名访问，滚动更新零停机。
- 有状态服务外置连接稳定，无数据丢失。

---

## 阶段 4：顶层叠加 AIOps 智能运维

### 核心目标

构建生产级可观测性平台，利用 AI/大模型自动处理云原生系统的故障检测与根因定位。  
**补充：引入权威公开数据集验证算法；通过 Kafka 构建实时流处理管道，避免离线定时脚本。**

### 核心技术栈

- **指标监控**：Prometheus、Grafana、Spring Boot Actuator
- **日志收集**：Loki / ELK、Fluentd
- **链路追踪**：OpenTelemetry
- **消息管道**：Kafka
- **AI/算法**：Python、Pandas、PyTorch、LSTM、Prophet
- **大模型应用**：LangChain、Agent、RAG
- **权威数据集**：Loghub 日志数据集、AIOps Challenge 竞赛数据集、CloudBed

### 实战落地任务

1. **三大可观测性数据采集**  
   - **Metrics**：Prometheus 采集 K8s 节点、容器及 Spring Boot Actuator 应用指标，Grafana 可视化。
   - **Logs**：Loki 或 ELK + Fluentd 收集全集群应用与系统日志。
   - **Traces**：OpenTelemetry 统一链路标准，关联指标与日志。
2. **实时数据管道**  
   - Prometheus/Loki 采集的海量 Metrics 和 Logs 先进入 Kafka 缓冲，再由 Python Consumer 实时消费，防止后端/算法服务被高并发冲垮。
3. **AI 算法与智能决策**  
   - **指标异常检测**：  
     使用 Python 构建时序预测模型（LSTM / Prophet），针对内存泄漏、流量突增等场景提前告警。  
     使用 Loghub 或 AIOps Challenge 公开数据集训练与验证，证明模型有效性。
   - **根因定位 RCA**：  
     利用 LLM + Agent + RAG，提取微服务报错日志与 Trace 链路，自动判断故障根因并生成修复建议。
4. **可选进阶**  
   了解 Flink 实时流计算概念，为高吞吐场景做技术储备。

### 验收标准

- Prometheus + Grafana 实时展示集群与业务指标，配置告警。
- Kafka 管道稳定缓冲日志/指标数据，无积压或丢失。
- 至少一个基于公开数据集的时序异常检测 Demo，效果可量化。
- 至少一个基于大模型的日志/链路根因分析 Demo，输出可能根因与建议。

---

## 🗓️ 云原生 + AIOps 专属时间线

| 时间 | 阶段 | 核心任务 | 里程碑 |
|------|------|---------|--------|
| **大二上学期**（当下 ~ 2027年1月） | 阶段1：单体业务闭环（前置基础） | Java/Spring Boot 串联 MySQL、Redis、EMQX、MinIO、Nginx、SRS，完成换热站项目闭环。 | 手里有一个功能完整、代码质量高的单体全栈项目。 |
| **大二下学期**（2027年2月 ~ 6月） | 阶段2：微服务化（云原生前置） | 单体拆分微服务，引入 Nacos、Gateway、Kafka/RocketMQ、SkyWalking。 | 掌握完整的微服务与分布式治理体系，为容器化做好准备。 |
| **大三上学期**（2027年9月 ~ 2028年1月） | **阶段3：云原生 K8s** | 将微服务 Docker 镜像化，部署到 Kubernetes 集群，实现自动扩缩容、滚动更新、自愈。 | 微服务系统完全运行在 K8s 上，具备一键部署和弹性伸缩能力。 |
| **大三下学期**（2028年2月 ~ 5月） | **阶段4：AIOps 智能运维** | 引入 Prometheus + ELK + OpenTelemetry，通过 Kafka 管道实时采集日志/指标，用 Python/大模型做异常检测与根因定位。 | 完成可观测性平台搭建 + AIOps 亮点项目，作为秋招/暑期实习的王牌。 |

---

## 最终行动建议

1. **立即打住**：停止寻找新的中间件教程，聚焦阶段 1 业务开发。
2. **数据库锁定 MySQL 8.0**：吃透 InnoDB、B+ 树、MVCC、Undo/Redo Log。
3. **大三上学期必须攻克微服务 + 容器化**：这是暑期实习简历的硬门槛。
4. **AIOps 作为秋招差异化王牌**：用公开数据集训练模型，证明算法真实性。
5. **有状态服务外置**：K8s 部署无状态微服务，避免 MySQL/Redis 上云踩坑。

---
