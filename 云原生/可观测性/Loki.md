# 《Grafana Loki 完整学习与开发速查笔记》

> **适用环境**　理解容器标准输出和 JSON 日志。以 Loki 3.x、Grafana Alloy 和 Grafana Explore 为例。
> **学习目标**　从服务与时间范围定位日志，用 LogQL 筛选结构化字段，理解标签基数和采集断点。
> **动手路线**　从第 8 节启动整套日志链路，再做查询、文件轮转和采集恢复。

---

# 第一篇　基础认知

## 1. 日志采集、存储和查询链路

```text
Spring Boot JSON 日志 → 文件或容器 stdout → Grafana Alloy
                                          ↓ 采集、加标签、发送
                                     Loki 存储与查询
                                          ↓ LogQL
                                      Grafana Explore
```

Loki 按一组标签把日志组织成 stream。查询先缩小 stream 和时间范围，再读取内容并执行过滤或解析。日志内容通常存放在压缩的数据块中。Grafana Explore 是查询入口，Alloy 是常用采集器。新练习使用 Alloy，旧项目的 Promtail 配置可以参考迁移文档。

---

## 2. Label、正文和结构化元数据

| 位置 | 适合放什么 | 示例 |
|---|---|---|
| 索引标签 | 值集合小且稳定，用于定位来源 | `service_name=catalog-api`、`env=dev`、`namespace=cloud-lab` |
| 日志正文 | 事件含义及其字段，查询时解析 | `level`、`message`、`product_id`、`trace_id` |
| 结构化元数据 | 需要随日志查询、但值变化很多的字段 | 容器 ID、Trace ID。使用前确认存储 schema 和配置支持 |

> [!warning]
> **易混淆**　每个新的标签组合都会增加一个 stream。给每次请求的 `trace_id` 建索引标签会制造大量 stream。先用服务、环境和时间窗口缩小范围，再按正文或结构化元数据查 Trace ID。

业务日志至少考虑时间、级别、服务、事件名和少量必要上下文。例子中的 `trace_id` 只是教学值。实际值来自追踪上下文。采集前去除凭据、Authorization 头、完整 Cookie 等敏感字段。

---

# 第二篇　最小练习与 LogQL

## 3. 写入一条 JSON 日志

按官方 Loki 快速开始启动本地 Loki 与 Grafana，假设本机可以访问 `127.0.0.1:3100`，本地示例未开启多租户鉴权。先用 `/ready` 确认服务就绪。下面的 Bash 示例直接调用写入 API，验证存储和查询，再用 Alloy 接入实际日志文件。

```bash
curl -fsS http://127.0.0.1:3100/ready
ts="$(date +%s)000000000" # Unix 纳秒时间戳，以 JSON 字符串传入
curl -fsS -w '%{http_code}\n' -X POST http://127.0.0.1:3100/loki/api/v1/push \
  -H 'Content-Type: application/json' \
  --data-binary @- <<EOF
{
  "streams": [{
    "stream": {"service_name": "catalog-api", "env": "dev"},
    "values": [["${ts}", "{\"level\":\"ERROR\",\"trace_id\":\"demo-42\",\"message\":\"catalog lookup timeout\"}"]]
  }]
}
EOF
```

写入成功预期返回 HTTP 204。添加 Loki 数据源，打开 Explore，时间范围选最近 15 分钟，执行 `{service_name="catalog-api", env="dev"}`，预期能看到刚写入的日志。如果 Grafana 和 Loki 是 Compose 中的两个容器，数据源 URL 通常指向 Loki 的 Compose 服务名，具体以 Compose 文件为准。

---

## 4. 从选流到过滤字段

```logql
# 先按索引标签和时间缩小范围，再按原始正文筛选
{service_name="catalog-api", env="dev"} |= "timeout"
```

```logql
# 解析 JSON 字段，再找指定请求
{service_name="catalog-api", env="dev"} | json | level="ERROR" | trace_id="demo-42"
```

```logql
# 按服务统计过去 5 分钟的 ERROR 日志，剔除 JSON 解析错误
sum by (service_name) (
  count_over_time({env="dev", service_name="catalog-api"} | json | level="ERROR" | __error__="" [5m])
)
```

查询顺序可以记成 `stream selector → 文本过滤 → 解析 → 字段过滤 → 聚合`。`|=` 表示包含字符串，`!=` 表示排除字符串，`|~` 使用正则表达式。字段名与已存在标签重名时，解析产生的字段可能带 `_extracted` 后缀。遇到查不到时，先拿掉字段过滤，展开一条原始日志核对。

---

## 5. 用 Alloy 采集实际服务日志

在已经运行的本地 Loki 旁启动 Alloy。以下最小配置假设 Alloy 直接在 Linux 或 WSL 中运行，并有权限读取 `/tmp/catalog-logs/*.log`，Loki 也能从该环境访问。容器部署时，要把日志目录挂载到采集器，并换成容器内可达的 Loki 地址。

```alloy
// 先发现日志文件，再通过 source 转发到写入组件。地址按 Alloy 所在网络配置。
local.file_match "heat" {
  path_targets = [
    {
      "__path__"     = "/tmp/catalog-logs/*.log",
      "service_name" = "catalog-api",
      "env"          = "dev",
    },
  ]
}

loki.source.file "heat" {
  targets    = local.file_match.heat.targets
  forward_to = [loki.write.local.receiver]
}

loki.write "local" {
  endpoint {
    url = "http://127.0.0.1:3100/loki/api/v1/push"
  }
}
```

配置启用后，在匹配目录追加一行 `{"level":"INFO","message":"alloy lab event"}`，用选择器和 `|= "alloy lab event"` 验证。生产接入还需要确认采集器的读取位置持久化、文件轮转行为、时间戳解析和失败重试。文件采集和容器 stdout 采集同时启用时，要避免同一份日志被发送两次。

---

# 第三篇　排障与速查

## 6. 用日志验证一次告警排查

1. 从 [Prometheus 与 Grafana](../数据库与中间件/Prometheus+Grafana.md) 的错误率面板找到异常时间窗和路由。
2. 在 Loki 按相同环境和服务筛选日志，按 `level` 或错误关键字查典型错误。
3. 从日志拿到 Trace ID，到追踪后端看是哪一步耗时或失败，再回查相邻服务日志。若 Trace 因采样而缺失，记录已有日志证据。
4. 修复后比较同窗口的错误率与日志计数，保留失败样例和恢复证据。

---

## 7. 问题索引与 Cheat Sheet

| 现象 | 第一条证据 | 下一步 |
|---|---|---|
| Loki 查询不到日志 | Loki `/ready`、Alloy 目标与写入错误 | 检查文件路径、权限、网络、租户和时间范围 |
| 只有旧日志 | 采集器读取位置、文件轮转、时间戳 | 追加唯一文本，检查是否被采集并成功发送 |
| 一查就很慢 | 选择器、时间窗口和 stream 数量 | 缩短时间，补稳定标签，先做文本筛选 |
| 解析无结果 | 展开原始日志，检查 `__error__` | 确认正文为单行 JSON，核对字段名和字段值 |
| 频繁写入限流 | Loki 写入拒绝、采集端重试、日志速率 | 控制高频日志，检查吞吐、缓冲和资源配额 |

**L1** 会区分标签与正文。**L2** 用 API 和 Alloy 分别写入并查询。**L3** 通过日志字段和 Trace ID 排查一个故障。**L4** 说明标签基数、采集可靠性、保留策略和成本取舍。

**记忆口诀**　先选服务与时间，再搜内容和字段。稳定值做标签，变化值留正文。

---

# 第四篇　日志平台部署与采集演练

## 8. 从 Compose 启动 Loki、Alloy 和 Grafana

在新的 `logging-lab/` 目录中创建以下文件，并建好 `logs/`。示例用单进程 Loki 和本地卷，适合在自己的机器练习。Loki HTTP 只映射到回环地址。同网络的 Grafana 和 Alloy 使用服务名访问。

```yaml
# compose.yaml
services:
  loki:
    image: grafana/loki:3.5.0
    command: ["-config.file=/etc/loki/lab.yml"]
    ports:
      - "127.0.0.1:13100:3100"
    volumes:
      - ./loki.yml:/etc/loki/lab.yml:ro
      - loki-data:/loki
  alloy:
    image: grafana/alloy:v1.10.0
    command:
      - run
      - --server.http.listen-addr=0.0.0.0:12345
      - --storage.path=/var/lib/alloy/data
      - /etc/alloy/config.alloy
    ports:
      - "127.0.0.1:12345:12345"
    volumes:
      - ./config.alloy:/etc/alloy/config.alloy:ro
      - ./logs:/var/log/catalog:ro
      - alloy-data:/var/lib/alloy/data
  grafana:
    image: grafana/grafana:12.0.2
    ports:
      - "127.0.0.1:13001:3000"
    volumes:
      - ./loki-datasource.yml:/etc/grafana/provisioning/datasources/lab.yml:ro
      - grafana-data:/var/lib/grafana
volumes:
  loki-data:
  alloy-data:
  grafana-data:
```

```yaml
# loki.yml。单实例练习，使用 TSDB 索引与本地文件系统。
auth_enabled: false
server:
  http_listen_port: 3100
common:
  instance_addr: 127.0.0.1
  # 与 Compose 的 loki-data 卷挂载点一致，重建容器后仍可访问数据。
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  # TSDB 使用 v13 schema，本地练习将日志块写入文件系统。
  configs:
    - from: "2024-01-01"
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: lab_index_
        period: 24h
```

```alloy
// config.alloy。文件内容只读，位置记录写到 --storage.path。
local.file_match "catalog" {
  path_targets = [
    {
      "__path__"     = "/var/log/catalog/*.log",
      "service_name" = "catalog-api",
      "env"          = "dev",
    },
  ]
}

loki.source.file "catalog" {
  targets    = local.file_match.catalog.targets
  forward_to = [loki.write.lab.receiver]
}

loki.write "lab" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

```yaml
# loki-datasource.yml
apiVersion: 1
datasources:
  - name: Lab Loki
    uid: lab-loki
    type: loki
    access: proxy
    url: http://loki:3100
```

```bash
mkdir -p logs
docker compose up -d
docker compose ps
docker compose logs --tail=80 loki alloy
curl -fsS http://127.0.0.1:13100/ready

# 以下文件用追加方式写入，Alloy 能跟随内容增长。
printf '%s\n' \
  '{"level":"INFO","route":"/products/{id}","status":200,"message":"query complete"}' \
  '{"level":"ERROR","route":"/products/{id}","status":500,"trace_id":"lab-abc","message":"query timeout"}' \
  >> logs/catalog.log
```

等待 `/ready` 返回成功后，打开 Grafana `http://127.0.0.1:13001/` 的 Explore，选择 `Lab Loki`。验证下列命令返回最近写入的日志。若 Alloy 配置加载异常，先在它的 UI `http://127.0.0.1:12345/` 查看组件和目标，再对照容器日志。

```bash
# 从当前网络位置访问指定端点，结合状态码和响应内容判断结果。
curl -fsS -G http://127.0.0.1:13100/loki/api/v1/query_range \
  --data-urlencode 'query={service_name="catalog-api",env="dev"} |= "query timeout"' \
  --data-urlencode 'since=10m' \
  --data-urlencode 'limit=10'
```

本例默认用采集时刻作为 Loki 时间戳。业务时间来自正文的情况下，要在 Alloy 配置中解析并统一时区，记录时间解析失败策略。出现“日志在文件中但 Explore 找不到”，先比较服务时间、正文时间、抓取时间和查询时间窗口。

---

## 9. LogQL 实战：过滤、解析和聚合

### 9.1 确定是哪一层开始查不到

1. 仅用 `{service_name="catalog-api",env="dev"}` 查最近 10 分钟。
2. 加 `|= "query"`，确认原始文本存在。
3. 加 `| json`，展开一条日志，查看 `status`、`route`、`trace_id` 和可能的 `__error__`。
4. 用 `| status >= 500 | __error__=""` 选择合法的 5xx 日志。
5. 用 Trace ID 缩小到单次调用，或按路由聚合估算影响范围。

```logql
# 在指定时间窗口估算速率或数量，再按实际需要的标签维度汇总。
sum by (route) (
  count_over_time(
    {service_name="catalog-api", env="dev"}
    | json
    | status >= 500
    | __error__=""
    [5m]
  )
)
```

数值转换失败会产生管道错误，错误过滤要在产生错误的步骤之后。日志数量与请求数量不是一一对应。一次失败请求可能打印多行错误，某些失败也可能没有错误日志。评估请求成功率优先使用请求指标，日志用于解释具体事件。

### 9.2 练习日志轮转、位置与重复

```bash
# 停止采集前先确保旧日志已在 Explore 中可查。
docker compose stop alloy
printf '%s\n' '{"level":"INFO","message":"written while collector offline"}' >> logs/catalog.log
docker compose start alloy
docker compose logs --tail=60 alloy
```

用唯一文本查询预期补采离线期间的追加内容。然后在练习目录把旧文件移到不匹配 `*.log` 的名字，再创建同名新文件写入唯一标记。验证新文件被发现，并记录实际是否存在重复或遗漏。轮转和文件句柄行为与收集器和文件系统有关。生产先评估 rename/create 与 copytruncate 的差别，确保旧文件保留时间覆盖采集落后窗口。

| 现象 | 重点证据 |
|---|---|
| 文件存在，采集目标为空 | 容器挂载、glob、读权限、目录更新时间 |
| 重启后整份日志重复 | 位置记录是否持久化，是否两个采集器读同一源 |
| 轮转后缺少一段 | 文件移动与压缩时机、老文件残留时间、句柄和位置 |
| HTTP 429 | Loki 摄取限制、流量峰值、重试与批处理 |
| HTTP 400 | 时间戳格式、是否过旧、标签数、行大小或查询语法 |
| 服务显示不同名称 | Alloy 附加标签、Loki 推断的 service_name 和实际 stream |

### 9.3 从日志字段提取数值与连接到 Trace

若应用已稳定记录 `duration_ms`，可用 `unwrap` 将解析后的字段作为数值样本，再按路由统计 p95。先为第 8 节的练习日志追加若干条带 `route`、`duration_ms` 的 JSON。字段缺失或转换失败时，从结果中排除 `__error__`。

```logql
# 将 JSON 中的 duration_ms 转成样本，按 route 求最近 5 分钟的 p95。
quantile_over_time(
  0.95,
  {service_name="catalog-api", env="dev"}
  | json
  | unwrap duration_ms
  | __error__=""
  [5m]
) by (route)
```

如果应用只在慢请求时写该字段，这个分位数代表已记录的慢请求样本，不能与全流量指标直接比较。指标更适合常驻延迟面板，日志聚合适合补充分析。

Grafana 的 Loki 数据源可以配置 Derived Fields，从正文提取 Trace ID，并链接到 Tempo 等追踪数据源。以正文中的 JSON 为例，匹配式可用 `"trace_id"\s*:\s*"([0-9a-fA-F]{32})"`。第 8 节的 `lab-abc` 只是演示值，实际练习跳转时应使用有效 Trace ID。先验证正则捕获出的字段，再看两个数据源的时间窗口、租户和采样是否一致。

### 9.4 日志告警适合什么

对应用尚无指标、但日志中有明确且低噪声的故障事件，可用 `count_over_time` 建规则。例如统计 5 分钟内某服务的 `migration_failed` 事件数。按服务和环境保留必要维度，避免每条请求生成一条告警。规则可由 Grafana 管理，或在使用 Loki Ruler 时由它评估并通知 Alertmanager。选一条实际链路验证 firing 和 resolved，把缺数据与零条日志的预期写入规则说明。 [LogQL 指标查询](https://grafana.com/docs/loki/latest/query/metric_queries/) · [Loki 数据源配置](https://grafana.com/docs/grafana/latest/datasources/loki/configure/) · [Loki 告警](https://grafana.com/docs/loki/latest/alerting/)

---

## 10. 生产部署与成本

- **存储**　单进程文件系统用于练习。生产按保留周期、吞吐、故障模型选择部署模式和对象存储，验证备份、对象存储权限与恢复。Loki 保留策略通常由 Compactor 管理，开启前核对 schema、索引周期、删除请求存储和持久化工作目录。
- **基数**　先用少量稳定标签定位服务、环境和集群。Trace ID、请求 ID 和完整 URL 进日志正文或结构化元数据。基数异常时按最重的 stream 组合追查来源。
- **敏感信息**　尽早在业务日志或采集端删掉敏感字段。生产需要网关或平台实现认证和租户隔离，并保护后端直接访问。多租户查询与摄取时核对租户 ID。
- **查询负载**　缩小时间范围与 stream，在解析前做文本过滤。常用日志统计可评估录制规则。持续的大规模聚合应优先考虑指标。
- **容量与故障**　测每天字节数、峰值行速率、平均行长、丢弃和重试、请求延迟、并发查询。对日志暴增先识别高频重复消息，避免限流时吞掉重要事件。保留能重建故障经过的关键日志。

**实战验收**　从空目录构建整套链路，通过 API、文件和 Explore 交叉验证。模拟停采、重启、文件轮转和一条非法 JSON，分别指出哪一层出现问题。最后用服务名、环境、路由和 Trace ID 还原一次故障，并记录当前日志方案的保留和权限边界。

官方实操　[Loki HTTP API](https://grafana.com/docs/loki/latest/reference/loki-http-api/) · [Loki 保留策略](https://grafana.com/docs/loki/latest/operations/storage/retention/) · [Alloy 文件发现](https://grafana.com/docs/alloy/latest/reference/components/local/local.file_match/) · [Alloy Docker 部署](https://grafana.com/docs/alloy/latest/set-up/install/docker/)

延伸阅读　[OpenTelemetry](OpenTelemetry.md) · [Loki 快速开始](https://grafana.com/docs/loki/latest/get-started/quick-start/quick-start/) · [标签说明](https://grafana.com/docs/loki/latest/get-started/labels/) · [LogQL 日志查询](https://grafana.com/docs/loki/latest/query/log_queries/) · [Alloy 采集日志](https://grafana.com/docs/alloy/latest/tutorials/send-logs-to-loki/)
