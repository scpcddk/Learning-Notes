# 《Prometheus 与 Grafana 完整学习与开发速查笔记》

> **适用环境**　以 Spring Boot 3.x、Micrometer、Prometheus 和 Grafana 为例。知道 HTTP 状态码和接口响应时间。
> **学习目标**　接通指标采集，读懂请求量、错误率和延迟分位数，能做一个仪表盘并验证一条告警。
> **动手路线**　第 8～11 节可独立搭建，覆盖指标、Grafana、告警规则测试与通知恢复。

---

# 第一篇　基础认知

## 1. 指标从应用走到图表

```text
Spring Boot + Micrometer → /actuator/prometheus 暴露指标
                                    ↑ 定期抓取
                               Prometheus 存储时间序列
                                    ↓ PromQL
                              Grafana 查询并展示

Prometheus 告警规则 → Alertmanager 路由、分组与发送通知
```

Prometheus 的时间序列由指标名和完整标签集合标识。`http_server_requests_seconds_count{method="GET",status="200",uri="/products/{id}"}` 与相同路由的 `status="500"` 是两条时间序列。Grafana 管展示和探索，也有自己的告警功能。练习先用 Prometheus 评估规则，避免对同一故障设置两套重复通知。

---

## 2. 指标类型与标签

| 类型 | 表达什么 | 常见操作 | 例子 |
|---|---|---|---|
| Counter | 累计值，进程重启可归零 | `rate` 看每秒变化，`increase` 看窗口内增量 | HTTP 请求数、错误数 |
| Gauge | 可上升也可下降的当前值 | 当前值、`avg_over_time` | 堆内存、队列积压 |
| Histogram | 按区间累计的观测次数与总量 | `histogram_quantile` 估算分位数 | 接口响应时间 |
| Summary | 客户端统计观测值，可暴露配置的分位数 | 由每个实例计算的分位数通常不能直接聚合 | 单实例延迟统计 |

> [!warning]
> **易混淆**　`p95=0.4s` 表示估算约 95% 的请求在 0.4 秒以内完成。平均延迟可能掩盖少量慢请求。也不能用各实例的 p95 取平均来得到全服务 p95。

标签优先用服务、环境、路由模板、方法和状态。`productId`、完整 URL、用户 ID、Trace ID 会产生大量不同的组合，适合放在日志或追踪中。实际影响可通过 series 数量和采集端资源观察。

---

# 第二篇　接入与查询

## 3. 让 Spring Boot 暴露指标

在使用 Spring Boot 依赖管理的 Maven 项目中添加 Actuator 与 Micrometer Prometheus Registry。

```xml
<!-- 由 Spring Boot BOM 管理版本 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus
  metrics:
    distribution:
      percentiles-histogram:
        http.server.requests: true # 让示例可查询经典直方图 bucket
```

先访问业务接口产生数据，再请求 `curl http://127.0.0.1:8080/actuator/prometheus`。检查是否出现 `http_server_requests_seconds_count` 和 `_bucket`，实际名称和标签以暴露内容为准。生产环境把管理端点限制在受控网络和权限范围内。

---

## 4. 让 Prometheus 抓取应用

示例假设 Prometheus 和 Spring Boot 都直接运行在同一台机器。把以下内容保存为 `prometheus.yml`。

```yaml
# 抓取目标的地址必须从 Prometheus 所在网络可达，路径以应用实际暴露值为准。
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: catalog-api
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['127.0.0.1:8080']
```

```bash
# 在对应终端执行，先替换示例路径或参数，再核对当前目录和退出状态。
promtool check config prometheus.yml
prometheus --config.file=prometheus.yml
```

打开 `http://127.0.0.1:9090/targets`，预期 `catalog-api` 为 `UP`。如果 Prometheus 在容器里，`127.0.0.1` 指向 Prometheus 容器本身，按环境改成可达的服务名或宿主地址。Grafana 添加 Prometheus 数据源时，URL 同样从 Grafana 所在环境出发选择。

---

## 5. 三张面板先回答三个问题

```promql
# 请求速率，每条路由每秒多少次
sum by (uri) (rate(http_server_requests_seconds_count{job="catalog-api"}[5m]))
```

```promql
# 全服务 5xx 占比。没有产生过 5xx 序列时，分子按 0 展示。
(sum(rate(http_server_requests_seconds_count{job="catalog-api",status=~"5.."}[5m])) or vector(0))
/
sum(rate(http_server_requests_seconds_count{job="catalog-api"}[5m]))
```

```promql
# 经典直方图估算每条路由的 p95，保留桶边界 le
histogram_quantile(
  0.95,
  sum by (uri, le) (rate(http_server_requests_seconds_bucket{job="catalog-api"}[5m]))
)
```

先对 Counter 做 `rate`，再跨实例聚合，便于识别各实例重启。5 分钟窗口适合本练习的 15 秒采样周期。流量为零时错误率没有可解释的分母。检查采集状态、请求量和绝对错误数，再解释比例面板。

在 Grafana 新建 Dashboard，为每条查询添加一张 Time series 面板。给三个面板分别选择每秒请求数、百分比（输入范围 0～1）、秒作为单位。生成几分钟有间隔的请求后，核对查询结果与预期。用 `uri` 区分速率与延迟曲线，并让不同面板共享时间范围。

---

## 6. 加一条可解释的告警

把规则保存为 `catalog-alerts.yml`，在 `prometheus.yml` 顶层添加 `rule_files: ['catalog-alerts.yml']` 后重新加载配置。先用 `promtool check rules catalog-alerts.yml` 检查规则文件。

```yaml
# 规则按评估周期计算，核对表达式、标签和持续时间是否符合告警预期。
groups:
  - name: catalog-api
    rules:
      - alert: CatalogApiTargetDown
        expr: up{job="catalog-api"} == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: '无法抓取 catalog-api 指标'
          description: '检查目标 {{ $labels.instance }} 的网络和 Actuator 路径。'
```

保持抓取目标配置不变，停止练习应用。在 Prometheus 的 Alerts 页面观察 `pending`，条件持续超过 `for` 后进入 `firing`。恢复应用后确认状态解除。若目标配置被移除，`up` 可能没有该序列，应另用 `absent(up{job="catalog-api"})` 等方式处理「应有目标全部消失」的需求。

---

# 第三篇　排障与速查

## 7. 面板、采集和告警常见问题

| 现象 | 优先检查 | 下一步 |
|---|---|---|
| Targets 为 `DOWN` | Target 错误、地址、路径、鉴权 | 从 Prometheus 所在网络直接请求指标端点 |
| `UP` 但没有业务指标 | 应用是否已收到业务流量 | 查抓取内容、指标名、标签和 Grafana 时间范围 |
| p95 没有结果 | `_bucket` 是否存在，聚合是否保留 `le` | 开启 Histogram，确认至少有足够样本 |
| 错误率尖峰 | 同一窗口的请求量和绝对错误数 | 告警结合最小流量，避免一次低流量错误放大 |
| 告警触发但未收到通知 | `pending` / `firing` 状态、Alertmanager 路由 | 核对匹配标签、抑制规则、接收器配置 |

**L1** 会判断 Counter、Gauge 和 Histogram。**L2** 接通抓取与三张面板。**L3** 演练应用停止与恢复，区分空序列、零值和抓取失败。**L4** 按业务延迟目标设计直方图桶、告警条件和排障手册。

**记忆口诀**　应用暴露，Prometheus 抓取，Grafana 展示。看分位数保留桶，告警同时看流量。

---

# 第四篇　从零构建监控与告警实验

## 8. 一个可控错误率和延迟的 HTTP 服务

这套练习可独立运行，不依赖已有的 Spring Boot 项目。用 Python 构造 HTTP 应用，在同一个 Compose 网络中启动 Prometheus、Grafana 和 Alertmanager。独立的 webhook 进程负责接收通知，业务应用停止时也可以验收告警。

```text
metrics-lab/
├── compose.yaml
├── Dockerfile
├── app.py
├── grafana-datasource.yml
├── alertmanager.yml
└── prometheus/
    ├── prometheus.yml
    ├── rules.yml
    └── rules-test.yml
```

```dockerfile
# FROM 选择基础环境，RUN 在构建时执行，CMD 或 ENTRYPOINT 决定容器启动方式。
FROM python:3.12-slim
WORKDIR /lab
RUN pip install --no-cache-dir prometheus-client==0.22.1
COPY app.py .
CMD ["python", "-u", "app.py"]
```

```python
# app.py。仅供本地实验，用固定范围参数产生可控流量。
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from prometheus_client import Counter, Histogram, start_http_server

REQUESTS = Counter("demo_http_requests", "Completed demo requests", ["route", "status"])
DURATION = Histogram(
    "demo_http_request_duration_seconds",
    "Request duration",
    ["route"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2),
)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path != "/work":
            self.reply(404, {"error": "unknown route"})
            return
        params = parse_qs(url.query)
        status = params.get("status", ["200"])[0]
        delay = params.get("delay", ["0"])[0]
        if status not in ("200", "500") or delay not in ("0", "0.1", "0.3", "0.8"):
            self.reply(400, {"error": "invalid lab parameters"})
            return
        with DURATION.labels("/work").time():
            time.sleep(float(delay))
            REQUESTS.labels("/work", status).inc()
            self.reply(int(status), {"status": status})

    def do_POST(self):
        if self.path != "/alert-hook":
            self.reply(404, {"error": "unknown route"})
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        print("alert webhook", body["status"], [a["labels"]["alertname"] for a in body["alerts"]])
        self.reply(200, {"received": True})


if __name__ == "__main__":
    # 预初始化零值，否则尚未出现过 5xx 时没有相应时间序列。
    for value in ("200", "500"):
        REQUESTS.labels("/work", value)
    DURATION.labels("/work")
    start_http_server(9100, addr="0.0.0.0")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
```

---

## 9. Compose、抓取与 Grafana 数据源

```yaml
# compose.yaml
services:
  app:
    build: .
    ports:
      - "127.0.0.1:18000:8000"
  webhook:
    build: .
  prometheus:
    image: prom/prometheus:v3.5.0
    command: ["--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.path=/prometheus"]
    ports:
      - "127.0.0.1:19090:9090"
    volumes:
      - ./prometheus:/etc/prometheus:ro
      - prometheus-data:/prometheus
  alertmanager:
    image: prom/alertmanager:v0.28.1
    command: ["--config.file=/etc/alertmanager/alertmanager.yml"]
    ports:
      - "127.0.0.1:19093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
  grafana:
    image: grafana/grafana:12.0.2
    ports:
      - "127.0.0.1:13000:3000"
    volumes:
      - ./grafana-datasource.yml:/etc/grafana/provisioning/datasources/lab.yml:ro
      - grafana-data:/var/lib/grafana
volumes:
  prometheus-data:
  grafana-data:
```

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 5s
  evaluation_interval: 5s
rule_files:
  - /etc/prometheus/rules.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
scrape_configs:
  - job_name: catalog-demo
    static_configs:
      - targets: ["app:9100"]
```

```yaml
# grafana-datasource.yml
apiVersion: 1
datasources:
  - name: Lab Prometheus
    uid: lab-prom
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: "5s"
```

```yaml
# alertmanager.yml
route:
  receiver: lab-webhook
  group_by: ["alertname", "job"]
  group_wait: 5s
  group_interval: 10s
  repeat_interval: 1m
receivers:
  - name: lab-webhook
    webhook_configs:
      - url: http://webhook:8000/alert-hook
        send_resolved: true
```

---

## 10. 录制规则、告警和单测

```yaml
# prometheus/rules.yml
groups:
  - name: catalog-demo
    rules:
      # 先记录请求速率，下一条规则用它作错误率的分母。
      - record: job:demo_http_requests:rate1m
        expr: sum by (job) (rate(demo_http_requests_total{job="catalog-demo"}[1m]))
      - record: job:demo_http_errors:ratio1m
        expr: |
          sum by (job) (rate(demo_http_requests_total{job="catalog-demo",status="500"}[1m]))
          /
          job:demo_http_requests:rate1m
      - alert: DemoTargetDown
        expr: up{job="catalog-demo"} == 0
        for: 20s
        labels:
          severity: warning
      - alert: DemoErrorRatioHigh
        expr: |
          (job:demo_http_errors:ratio1m > 0.20)
          and on (job) (job:demo_http_requests:rate1m >= 1)
        for: 20s
        labels:
          severity: warning
```

错误率告警同时要求每秒至少一次请求，降低低流量时的误报。`for` 要求评估条件持续满足，指标缺失、流量下滑或条件恢复都可能中断 Pending。练习用短窗口便于观察，生产按业务目标、流量与值班策略设置。

```yaml
# prometheus/rules-test.yml
rule_files:
  - rules.yml
evaluation_interval: 5s
tests:
  - interval: 5s
    input_series:
      - series: 'up{job="catalog-demo",instance="app:9100"}'
        values: '1 0 0 0 0 0 1'
    alert_rule_test:
      - eval_time: 20s
        alertname: DemoTargetDown
        exp_alerts: []
      - eval_time: 25s
        alertname: DemoTargetDown
        exp_alerts:
          - exp_labels:
              job: catalog-demo
              instance: app:9100
              severity: warning
      - eval_time: 30s
        alertname: DemoTargetDown
        exp_alerts: []
```

```bash
# 启动声明的服务。进程启动后继续确认容器健康和业务端口。
docker compose run --rm --no-deps --entrypoint /bin/promtool \
  prometheus check config /etc/prometheus/prometheus.yml
docker compose run --rm --no-deps --entrypoint /bin/promtool \
  prometheus test rules /etc/prometheus/rules-test.yml
docker compose up -d --build
docker compose ps
curl -fsS http://127.0.0.1:18000/work
```

打开 `http://127.0.0.1:19090/targets` 与 Rules 页面，确认抓取为 UP，规则按 5 秒间隔评估。登录 Grafana 的 `http://127.0.0.1:13000/`，选择自动加载的 `Lab Prometheus`。默认管理员凭据仅用于本地，按首次登录流程修改。

---

## 11. 故障注入与面板验收

### 11.1 正常、慢、错误、停止四个阶段

每个阶段保持至少一分钟，用 `Ctrl+C` 结束连续请求。错误阶段使用 `curl -sS` 接收 500 并继续发请求。

```bash
# 首轮用正常 URL，后续分别换成两条注释中的 URL。
url='http://127.0.0.1:18000/work?status=200&delay=0'
# url='http://127.0.0.1:18000/work?status=200&delay=0.8'
# url='http://127.0.0.1:18000/work?status=500&delay=0.1'
while true; do
  curl -sS -o /dev/null "$url"
  sleep 0.25
done
```

```promql
# 把数值样本或直方图桶聚合到目标维度，再计算分位数。
job:demo_http_requests:rate1m{job="catalog-demo"}
job:demo_http_errors:ratio1m{job="catalog-demo"}
histogram_quantile(0.95, sum by (le) (rate(demo_http_request_duration_seconds_bucket[1m])))
```

分别把三行作为三个面板的查询。正常阶段看请求量，慢请求阶段看 p95 上移，错误阶段观察告警。等待 Alertmanager 的分组时间，执行 `docker compose logs --tail=30 webhook` 看 firing 通知。恢复正常请求，等待窗口更新后看 resolved。最后执行 `docker compose stop app`，确认抓取变为 DOWN，独立 webhook 仍能接收告警。恢复 `app` 后核对状态清除。

### 11.2 从业务目标计算消耗速度

30 天内成功率目标若为 99.9%，预算错误比例就是 0.001。某段时间的错误比例为 0.0144，消耗速度就是预算允许值的 14.4 倍。生产可组合长窗口与短窗口，分别确认累计消耗和异常是否仍持续。低流量、零流量、采集缺失应有各自的解释。

| 面板或规则 | 要回答的问题 | 验证证据 |
|---|---|---|
| 请求量 | 流量是否变化，比例的分母是否有意义 | 每秒速率和窗口内总数 |
| 错误率 | 异常是否持续，影响哪个接口 | 比例、绝对失败数和同窗口日志 |
| 延迟 | 尾延迟是否超过目标 | 直方图桶分布，变更前后的 p95 |
| `up` 与 `absent()` | 目标抓取失败还是目标未被发现 | Targets、服务发现和规则状态 |
| 通知 | 经过哪条路由，何时解除 | Alertmanager 与独立 webhook 日志 |

### 11.3 抓取前、入库前和远程写入前的重标记

| 配置 | 发生在哪一步 | 常用用途 |
|---|---|---|
| `relabel_configs` | 发现目标后、抓取前 | 选择目标，调整地址、路径与持久化目标标签 |
| `metric_relabel_configs` | 抓到样本后、本地入库前 | 筛掉高成本或不使用的指标，保留需要的标签 |
| `write_relabel_configs` | 发送到 remote write 前 | 控制远端接收的时间序列。本地入库仍按本地规则处理 |

下面的 `scrape_configs` 条目可用于第 9 节环境。它把临时标签 `__address__` 的主机部分作为稳定可读标签，只保留练习所需业务指标。`up` 是 Prometheus 自动生成的目标状态，metric relabel 不作用于它。

```yaml
- job_name: catalog-demo
  static_configs:
    - targets: ["app:9100"]
  relabel_configs:
    - source_labels: [__address__]
      regex: '([^:]+):[0-9]+'
      target_label: target_service
      replacement: '$1'   # 从 app:9100 得到 app，只匹配本实验的主机名格式
  metric_relabel_configs:
    - source_labels: [__name__]
      regex: 'demo_http_.*'
      action: keep       # 删除其他抓取样本，保留本实验的两类指标
```

验证前先用 `promtool check config`。重载后在 Targets 页面确认目标与标签，再查 `up{job="catalog-demo", target_service="app"}` 和对应业务指标。删除某个标签前，要确认剩余标签还能区分原来的时间序列。直接移除高基数字段可能合并本应不同的序列，应优先从应用指标设计修正。

### 11.4 按相同维度计算错误率

分子和分母先聚合到相同的 `job, route`，然后才相除。若分子多了 `status`、`instance` 等标签，默认匹配可能找不到对应项。此例的应用已经为两个状态初始化了计数器。

```promql
# 分子分母都保留 job 和 route，使向量匹配一一对应。
sum by (job, route) (rate(demo_http_requests_total{job="catalog-demo", status="500"}[1m]))
/
sum by (job, route) (rate(demo_http_requests_total{job="catalog-demo"}[1m]))
```

遇到空结果时，分别查询分子、分母与标签。需要跨不同维度匹配时，再用 `on(...)` 或 `ignoring(...)` 指定键。多对一要确认唯一侧，避免把错误聚合隐藏在 `group_left` 或 `group_right` 里。 [Prometheus 配置](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) · [PromQL 向量匹配](https://prometheus.io/docs/prometheus/latest/querying/operators/#vector-matching)

---

## 12. 生产排障、性能和容量

- **采集**　从 Prometheus 所在网络请求目标，核对 URL、认证、超时与格式。用专用抓取网络开放指标。动态目标要验证发现标签和重新标记结果。
- **基数**　定位时间序列增长最快的指标，找高变化标签。路由用模板，在产生指标的地方删去不必要的高基数字段。对第三方指标可用 metric relabel 控制保留范围。
- **存储**　根据样本速率、实际压缩率和保留期估算，给 WAL、压缩和查询留余量。查询高基数指标前先缩小时间范围和标签范围，重复面板优先评估录制规则。
- **告警**　按 Prometheus 条件、Alertmanager 连接、分组路由、静默抑制、接收器日志逐级定位。Grafana 管理的告警与 Prometheus 规则分工明确，避免重复通知。
- **发布和恢复**　抓取配置、告警和 Dashboard 数据源进版本管理。更新前用 `promtool check` 和规则单测。更新后检查目标与通知路径，定期恢复持久卷，验证备份的实际可用性。

**实战验收**　从空目录搭起 Compose，画出三张可解释的面板。分别用慢请求、HTTP 500、进程停止验证指标、告警和通知。对一次抓取或路由配置错误记录现象、证据、修复和复测结果。

官方实操　[Prometheus 配置](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) · [规则单元测试](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/) · [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) · [Alertmanager 配置](https://prometheus.io/docs/alerting/latest/configuration/)

延伸阅读　[OpenTelemetry](../可观测性/OpenTelemetry.md) · [Loki](../可观测性/Loki.md) · [Spring Boot 指标](https://docs.spring.io/spring-boot/3.5/reference/actuator/metrics.html) · [PromQL 函数](https://prometheus.io/docs/prometheus/latest/querying/functions/) · [告警规则](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) · [Grafana Prometheus 数据源](https://grafana.com/docs/grafana/latest/datasources/prometheus/)
