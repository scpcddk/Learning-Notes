# 《Helm 完整学习与开发速查笔记》

> **适用环境**　已会使用 Deployment、Service 和 `kubectl`。通用命令覆盖 Helm 3/4，失败回滚选项按大版本区分。
> **学习目标**　把应用清单做成可复用 Chart，用配置区分环境，能解释模板输出与发布历史。
> **动手路线**　先完成第 3～4 节的最小 Chart，再做第 8～10 节的校验、测试、失败回滚和打包。

---

# 第一篇　基础认知

## 1. Chart、Values 与 Release

Helm 读取 Chart 和输入值，渲染成 Kubernetes 资源清单，再创建或升级一份有名字的发布记录。应用副本和流量仍由 Kubernetes 管理。

| 名称 | 作用 | 部署例子 |
|---|---|---|
| Chart | 安装包，由元数据、默认值和模板组成 | `web-api` 的 Deployment 与 Service |
| Values | 渲染模板用的参数 | 镜像、端口、开发和生产的副本数 |
| Release | Chart 在某个命名空间中的安装实例 | `web-dev`、`web-staging` |
| Revision | 同一 Release 的一次变更记录 | 升级后增加，回滚也会生成新 revision |
| OCI Registry | 用 OCI 格式存放打包 Chart 的仓库 | CI 打包后推送，部署时引用固定版本 |

> [!note]
> `Chart.yaml` 的 `version` 是 Chart 包版本，`appVersion` 描述应用版本。容器最终使用哪个镜像取决于渲染出的 `image` 字段。

---

## 2. 参数优先级

```text
Chart 的 values.yaml → 命令中的 -f 文件（后者覆盖前者）→ --set 系列覆盖
                                            ↓
                           templates/ 中的模板生成资源清单
```

映射通常按键合并，列表通常由覆盖值整体替换。环境差异适合写到 `values-dev.yaml` 等可审查的文件中。`--set-string image.tag=20261112` 可避免纯数字标签被解析成数字。升级时，显式传入完整的环境覆盖文件可以减少对旧 release values 的隐式依赖。

---

# 第二篇　做一个最小 Chart

## 3. 文件结构和默认值

新建 `web-api/`，包含下面三个文件。服务使用 Nginx 模拟，并为不同 release 分配不同的 Pod selector。

```yaml
# web-api/Chart.yaml
apiVersion: v2
name: web-api
description: HTTP service lab
type: application
version: 0.1.0
appVersion: "1.28"
```

```yaml
# web-api/values.yaml
replicaCount: 1
image:
  repository: nginx
  tag: "1.28-alpine"
service:
  port: 8080
```

```yaml
# web-api/templates/workload.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/instance: {{ .Release.Name | quote }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    # 发布名用来区分同一命名空间的多个 Release，升级时保持 selector 稳定。
    matchLabels:
      app.kubernetes.io/instance: {{ .Release.Name | quote }}
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: {{ .Release.Name | quote }}
    spec:
      containers:
        - name: web
          image: {{ printf "%s:%s" .Values.image.repository .Values.image.tag | quote }}
          ports:
            - name: http
              containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: http
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/instance: {{ .Release.Name | quote }}
spec:
  selector:
    app.kubernetes.io/instance: {{ .Release.Name | quote }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
```

---

## 4. 渲染、安装与验证

在 Chart 的上一级目录执行。新建 `values-dev.yaml`，内容为 `replicaCount: 2`。先渲染并核对镜像、selector 和端口，再部署到练习命名空间。

```bash
# 在练习集群中核对对象、命名空间和实际运行状态。
helm lint ./web-api -f values-dev.yaml
helm template web-dev ./web-api -n cloud-lab -f values-dev.yaml
helm upgrade --install web-dev ./web-api -n cloud-lab --create-namespace -f values-dev.yaml --wait --timeout 3m
helm status web-dev -n cloud-lab
kubectl -n cloud-lab get deployment,service -l app.kubernetes.io/instance=web-dev
```

预期 Deployment 有两个就绪副本。运行 `kubectl -n cloud-lab port-forward service/web-dev 18080:8080` 后，在另一终端用 `curl http://127.0.0.1:18080/` 验证 HTTP。`helm template` 适合检查模板结构，集群 API 兼容性、权限和准入规则还需用目标集群验证。

---

## 5. 升级、回滚和打包

```bash
helm history web-dev -n cloud-lab
helm get values web-dev -n cloud-lab --all
helm get manifest web-dev -n cloud-lab
# 确认历史里第 1 版存在且可用后，在练习环境执行
helm rollback web-dev 1 -n cloud-lab --wait --timeout 3m
helm package ./web-api
```

Helm 3 的 `helm upgrade --atomic` 会在升级失败时回滚，并启用等待。Helm 4 使用 `--rollback-on-failure` 表达该意图。先看 `helm version` 和 `helm upgrade --help`，再写入 CI 脚本。回滚可恢复 release 清单，数据库数据、外部 API 的副作用和应用自身的迁移需要独立处理。

---

# 第三篇　常见坑与速查

## 6. 模板和发布常见问题

| 现象 | 检查 | 改法 |
|---|---|---|
| YAML 解析失败 | `helm template` 的缩进、引号、条件分支 | 多行值用 `toYaml` 与 `nindent`。字符串字段用 `quote` |
| 更新时报 selector 不可变 | Deployment selector 是否包含版本、随机值等 | 保持 selector 稳定。需要改 selector 时计划替换对象 |
| Pod 镜像与预期不同 | `helm get values --all` 和渲染清单 | 固定镜像版本，核对覆盖顺序 |
| 等待超时 | `helm status`、Pod 事件、PVC 状态 | 先定位镜像、资源、探针或卷绑定，再决定是否回滚 |
| 日志里出现敏感配置 | 渲染结果、CI 输出和 release 记录 | values 中只传现有 Secret 的引用。审查输出访问权限 |

模板复杂后，可把公共标签和名字提取到 `_helpers.tpl`。在 `range` 或 `with` 内，`.` 指向当前作用域，需要全局上下文时可使用 `$`。对副本数、端口等参数，可用 `values.schema.json` 提前检查类型和范围。

---

## 7. Cheat Sheet 与学习分级

| 要做什么 | 命令或知识点 |
|---|---|
| 检查、渲染 | `helm lint` → `helm template` |
| 发布、观察 | `helm upgrade --install` → `helm status` → `kubectl get pods` |
| 看实际配置 | `helm get values --all`、`helm get manifest` |
| 看历史、恢复 | `helm history` → `helm rollback` |

**L1** 区分 Chart 与 Release。**L2** 用不同 values 部署两个实例。**L3** 模拟发布失败并恢复。**L4** 在 CI 中校验、打包和固定 Chart 版本，说明数据恢复边界。

**记忆口诀**　Chart 管模板，Values 管差异，Release 管实例，Revision 管历史。

---

# 第四篇　应用 Chart 的工程实战

## 8. 用 schema 和模板保证配置能用

延续第 3 节的 `web-api/` Chart。真实项目会把 Deployment、Service、ConfigMap、测试拆成各自的模板文件。以下练习先保留 `workload.yaml`，为输入建立类型和范围约束。把以下内容放到 `web-api/values.schema.json`。

**阅读提示**　这是校验规则。required 决定必填项，properties 约束字段类型和取值范围。

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount", "image", "service"],
  "properties": {
    "replicaCount": { "type": "integer", "minimum": 1, "maximum": 10 },
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string", "minLength": 1 },
        "tag": { "type": "string", "minLength": 1 }
      }
    },
    "service": {
      "type": "object",
      "required": ["port"],
      "properties": {
        "port": { "type": "integer", "minimum": 1, "maximum": 65535 }
      }
    }
  }
}
```

```bash
# 核对 Chart、Release 与目标命名空间，结合渲染或状态输出验证结果。
helm lint ./web-api -f values-dev.yaml
helm template web-dev ./web-api -n cloud-lab -f values-dev.yaml --set replicaCount=0
helm template web-dev ./web-api -n cloud-lab -f values-dev.yaml --set image.tag=20261112
helm template web-dev ./web-api -n cloud-lab -f values-dev.yaml --set-string image.tag=20261112
```

预期正常配置通过，副本数 0 和数字类型的 image tag 被 schema 拒绝，`--set-string` 版本通过。schema 校验输入结构，镜像是否存在、资源是否允许部署仍要用仓库和目标集群验证。使用数值的字段不要盲目加引号。

### 8.1 共用标签和作用域

发布标识、应用名、版本等标签可放进 `templates/_helpers.tpl`。选择器只用稳定且能区分 Release 的标签。把应用版本、Chart 版本用作查询标签即可，放进 selector 会影响升级。

```gotemplate
{{/* 复用此模板时传入当前 Chart 和 Release 的上下文，再检查渲染结果。 */}}
{{- define "web-api.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end -}}
```

在新 Chart 中，Deployment 的 `spec.selector.matchLabels`、Pod 模板的 `metadata.labels`、Service 的 `spec.selector` 都可用 `include "web-api.selectorLabels" . | nindent N`。`N` 对应插入位置缩进，三个位置不同。对已有 Release，不能直接加新字段到 Deployment selector，应保持旧 selector 或规划迁移。测试时安装两个不同 release 并检查各自 EndpointSlice，避免跨 release 误选。

### 8.2 ConfigMap 更新自动触发 rollout

新增 `pageText: "version 1"` 到 `values.yaml`。下面是 `templates/page.yaml`，模板内容影响校验和。

```yaml
# 检查资源的 API 版本、名称与引用关系，应用前先查看渲染后的清单。
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ printf "%s-page" .Release.Name }}
data:
  index.html: |-
{{ .Values.pageText | indent 4 }}
```

在 Deployment 的 `spec.template.metadata.annotations` 增加下列注解。它位于 Pod 模板上，配置变化时使 Deployment 创建新的 ReplicaSet。

```yaml
# 按层级合并到对应配置位置，保持缩进并核对引用的服务、端口或文件。
checksum/page: {{ include (print $.Template.BasePath "/page.yaml") . | sha256sum }}
```

再把 `{{ printf "%s-page" .Release.Name }}` 作为 ConfigMap 卷挂到容器的 `/usr/share/nginx/html`，卷项和容器挂载字段参照 [Kubernetes 编排的配置练习](K8s编排.md)。升级 `pageText` 后，比较 `helm get manifest` 中的 checksum、ReplicaSet 和 HTTP 首页。敏感值用现有 Secret 引用，避免把明文带入渲染输出和发布历史。

---

## 9. Chart 测试与发布回滚

### 9.1 添加实际请求 Service 的 Helm Test

创建 `web-api/templates/tests/http.yaml`。测试镜像需要能从练习集群拉取，执行成功后删除测试 Pod，失败时保留用于定位。

```yaml
# 检查资源的 API 版本、名称与引用关系，应用前先查看渲染后的清单。
apiVersion: v1
kind: Pod
metadata:
  name: {{ printf "%s-http-test" .Release.Name }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: check
      image: busybox:1.37
      command: ["wget"]
      args:
        - "-qO-"
        - {{ printf "http://%s:%v/" .Release.Name .Values.service.port | quote }}
```

```bash
# 核对 Chart、Release 与目标命名空间，结合渲染或状态输出验证结果。
helm upgrade --install web-dev ./web-api -n cloud-lab --create-namespace \
  -f values-dev.yaml --wait --timeout 3m
helm test web-dev -n cloud-lab --logs --timeout 90s
helm get manifest web-dev -n cloud-lab
```

测试通过说明从集群内可以解析并访问该 Service。可进一步校验响应内容或实际接口返回码。不要把测试写成“只看容器起来”。在目标 namespace 有 NetworkPolicy 时，测试 Pod 也要满足访问规则。Hook 的资源生命周期由 hook 注解或控制器规则管理，不能依赖所有 hook 对象随 release 自动删除。

### 9.2 注入坏镜像并回到已验证版本

1. 执行 `helm history web-dev -n cloud-lab`，记下状态为 deployed 的 revision，并用 `helm test` 留下可用证据。
2. 创建 `values-fail.yaml`，其中 `image.tag` 填一个明确不存在的 tag。用 `-f values-dev.yaml -f values-fail.yaml --wait --timeout 60s` 执行练习升级。预期等待失败，Pod 事件提示镜像拉取失败。
3. 取 `helm status`、`kubectl describe pod` 与 `helm history`。按记录执行 `helm rollback web-dev <可用revision> -n cloud-lab --wait --timeout 3m`。
4. 再跑 `helm test`，核对镜像和 Service。确认失败覆盖文件没有进入下一次发布。
5. 重做一次升级，在 Helm 3 使用 `--atomic`，或在 Helm 4 使用 `--rollback-on-failure`，对照失败后的 release revision 和实际对象。

自动回滚可以恢复清单。若升级包含数据库迁移，应先保证前后应用能读写同一阶段的 schema，再拆开破坏兼容性的步骤。不要依赖 Pod 回滚恢复已经修改的数据。

---

## 10. 多环境、依赖和流水线

### 10.1 打包与版本

| 项目 | 版本来源 | 发布时要核对 |
|---|---|---|
| Chart | `Chart.yaml` 的 `version` | 依赖、模板和默认值变化都要管理 Chart 版本 |
| 应用镜像 | values 中的 tag 或 digest | 同一制品在各环境晋级，避免重复构建出不同内容 |
| 子 Chart | `Chart.yaml` 的 `dependencies` 与 `Chart.lock` | 需要更新时显式更新，流水线用 `helm dependency build` 按锁定版本构建 |
| 环境参数 | 审查过的 `values-*.yaml` | 参数顺序、权限、Secret 引用、资源上限 |
| 发布历史 | Helm release 与 revision | 发布人、目标集群、实际 manifest 和恢复目标 |

在 CI 分开执行 `helm lint`、`helm template`、清单检查、打包和部署。渲染时传入与实际部署同一套 values。对自定义资源，检查目标集群中 CRD 及可用版本。CRD 生命周期与普通模板不同，尤其升级和删除应按所用 Chart 的说明处理。实际环境的控制面权限和 admission 策略可用目标 namespace 的服务端 dry-run 检查。

```bash
# 在练习集群中核对对象、命名空间和实际运行状态。
helm lint ./web-api -f values-dev.yaml
helm template web-dev ./web-api -n cloud-lab -f values-dev.yaml > rendered.yaml
kubectl --context kind-cloud-lab -n cloud-lab apply --dry-run=server -f rendered.yaml
mkdir -p dist
helm package ./web-api --destination dist
```

这里的模板含 Helm Test hook。对 `rendered.yaml` 的服务端 dry-run 会校验这些对象，流水线若只检查普通工作负载，可用当前 Helm 版本支持的跳过测试模板选项。若把 Chart 发布到 OCI 仓库，应由流水线使用受限凭据，固定包版本与镜像 digest，记录目标仓库和制品校验信息。

### 10.2 发布排障表

| 症状 | 优先证据 | 恢复 |
|---|---|---|
| schema 报错 | lint 的字段路径与值类型 | 修正参数，使用一致的 values |
| 模板过了，集群拒绝 | 服务端 dry-run、API 版本和准入事件 | 改不兼容 API，先准备 CRD 或权限 |
| 同 namespace 两个 release 串流量 | Service selector、Pod labels、EndpointSlice | 让实例标签区分 release |
| 升级超时 | Helm 状态、Deployment 条件、Pod 事件 | 修复探针/镜像/存储，或回到验证过的 revision |
| 卸载后残留 Job | Hook 状态和注解 | 核对 hook 删除策略及 TTL，按对象确认后清理 |
| 回滚后接口仍失败 | 数据库兼容、依赖版本和配置 | 修复数据或运行依赖，再验证真实请求 |

### 10.3 升级时旧 values 怎么处理

设当前 Release 的 `replicaCount` 手工改成过 4，新 Chart 的默认值是 2。上线前应明确这个手工值是否继续保留。

| 方式 | 合并起点 | 适用场景 |
|---|---|---|
| `--reset-values` | 新 Chart 默认值，再覆盖本次传入的值 | 按版本库的环境配置重新部署 |
| `--reuse-values` | 上一次 Release 的值，再覆盖本次传入的值 | 短期保留旧环境配置，同时有明确迁移计划 |
| `--reset-then-reuse-values` | 新 Chart 默认值，再合并旧 Release 的值和本次覆盖 | 使用支持该选项的 Helm 版本，并明确需要继承哪些值 |

如果同时传入相互冲突的选项，Helm 按版本定义的优先级处理。生产流水线选择一个明确策略，把环境差异放在同一套版本化 values 中。验证时比较 `helm get values`、`helm get values --all` 和本次渲染结果，分别查看用户覆盖、计算结果和将要发布的清单。生产数据中可能含敏感配置，差异输出需要访问控制。

```bash
# 先检查已发布的覆盖项和最终值，再按新 Chart 加环境文件预演。
helm get values web-dev -n cloud-lab
helm get values web-dev -n cloud-lab --all
helm upgrade web-dev ./web-api -n cloud-lab --reset-values \
  -f values-dev.yaml --dry-run=client --hide-secret
```

`--hide-secret` 只隐藏渲染的 Secret 对象。若模板把敏感值放到 ConfigMap、注解或 Notes，仍可能输出。有关升级和依赖参数，以实际 CLI 大版本的文档为准。 [Helm upgrade](https://helm.sh/docs/helm/helm_upgrade/) · [Helm dependency build](https://helm.sh/docs/helm/helm_dependency_build/)

**实战验收**　从空 Chart 目录起步，部署两个 release。用 schema 拦截错误值，用 checksum 触发一次配置发布，用 Helm Test 检查 HTTP，最后完成坏镜像的诊断和回滚。

官方实操　[Chart 结构](https://helm.sh/docs/topics/charts/) · [Helm Test](https://helm.sh/docs/topics/chart_tests/) · [Chart Hooks](https://helm.sh/docs/topics/charts_hooks/) · [Helm 模板技巧](https://helm.sh/docs/howto/charts_tips_and_tricks/)

延伸阅读　[Kubernetes 编排](K8s编排.md) · [CI/CD](../DevOps/CI-CD.md) · [Helm 使用指南](https://helm.sh/docs/intro/using_helm/) · [Chart 模板](https://helm.sh/docs/chart_template_guide/) · [Helm 4 upgrade](https://helm.sh/docs/helm/helm_upgrade/) · [Helm 3 upgrade](https://helm.sh/docs/v3/helm/helm_upgrade/)
