# 《Kubernetes 编排完整学习与开发速查笔记》

> **适用环境**　有 `kubectl` 和一个可访问的练习集群，已掌握 Docker 镜像、容器端口和环境变量。示例使用 `apps/v1` 与 `v1` API。
> **学习目标**　部署一个 HTTP 服务，验证流量入口，做一次滚动更新，独立定位 Pod 和 Service 常见故障。
> **动手路线**　已有 kubectl 基础可从第 8～10 节开始，完成建集群、配置发布、坏探针和流量恢复。

---

# 第一篇　基础认知

## 1. 声明式编排与控制循环

提交 Deployment 时，描述的是「需要两个运行指定镜像的副本」。API Server 接收对象，控制器持续比较期望状态和实际状态。删掉一个受管理的 Pod 后，ReplicaSet 控制器会尝试创建替代 Pod。新 Pod 通常会拿到新的名字和 IP。

**阅读提示**　在练习集群中核对对象、命名空间和实际运行状态。

```text
kubectl apply → API Server 保存对象
                   ↓
Deployment 控制器 → ReplicaSet 控制器 → 创建 Pod
                   ↓
Scheduler 为待调度 Pod 选节点 → 节点 kubelet 启动容器、执行探针
```

| 对象 | 主要职责 | 典型用途 |
|---|---|---|
| Pod | 容器运行与调度的基本单位，内部容器共享网络 | 一个 API 容器和必要的辅助容器 |
| Deployment | 管理无状态 Pod 副本和版本 | Spring Boot API、前端服务 |
| StatefulSet | 管理有稳定身份的副本，可为每个副本绑定持久卷 | 对身份与存储有要求的有状态组件 |
| DaemonSet | 在符合条件的节点运行 Pod | 日志采集器、节点监控 |
| Job / CronJob | 执行有限任务或定时创建 Job | 数据初始化、定时汇总 |
| Namespace | 提供资源命名和管理边界 | 练习环境、团队空间。网络隔离需要额外策略 |

---

## 2. 流量如何到达 Pod

Service 按标签选中 Pod。带 selector 的 Service 通常由控制面维护 EndpointSlice，记录后端地址和就绪状态。应用在集群内访问稳定的 Service DNS，例如 `web-api.cloud-lab.svc.cluster.local`，其中 `cluster.local` 是常见默认域名。

| 入口 | 访问范围与用途 |
|---|---|
| `ClusterIP` | 集群内的稳定地址，适合服务之间调用 |
| `NodePort` | 通过节点端口暴露 Service，常用于练习或作为其他入口的底层能力 |
| `LoadBalancer` | 依赖云或集群的负载均衡实现，按环境提供入口 |
| Ingress / Gateway API | 按域名、路径等路由流量，需要对应的控制器或实现 |

> [!warning]
> **易混淆**　`Service.port` 是调用者访问的端口，`targetPort` 是后端端口。`containerPort` 是容器端口声明，应用还要真正监听该端口。Ingress 资源也需要控制器才能处理流量。

---

# 第二篇　部署与发布

## 3. 练习 Deployment + Service

先确认 `kubectl config current-context` 指向练习集群。将以下内容保存为 `web-api.yaml`，用 Nginx 模拟服务。生产 API 应改用自身的业务镜像和健康端点。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api # 与 Deployment selector 一致
    spec:
      containers:
        - name: web
          image: nginx:1.28-alpine
          ports:
            - name: http
              containerPort: 80
          readinessProbe:
            # 只有就绪探针通过，常规 Service 才把流量发给此 Pod。
            httpGet:
              path: /
              port: http
            periodSeconds: 5
          resources:
            # requests 用于调度，内存 limits 约束运行时用量。
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web-api
spec:
  selector:
    app: web-api # 匹配 Pod 标签
  ports:
    - name: http
      port: 8080
      targetPort: http
```

```bash
# 在练习集群中核对对象、命名空间和实际运行状态。
kubectl create namespace cloud-lab
kubectl -n cloud-lab apply -f web-api.yaml
kubectl -n cloud-lab rollout status deployment/web-api --timeout=120s
kubectl -n cloud-lab get pods -l app=web-api -o wide
kubectl -n cloud-lab get endpointslice -l kubernetes.io/service-name=web-api
kubectl -n cloud-lab port-forward service/web-api 18080:8080
```

另开终端请求 `curl http://127.0.0.1:18080/`，预期返回 Nginx 页面。`port-forward` 主要用于确认某个后端能响应。可从同命名空间的临时 Pod 验证 Service DNS 和集群内转发。

```bash
kubectl -n cloud-lab run web-check --image=busybox:1.37 --restart=Never --rm -it -- wget -qO- http://web-api:8080/
```

---

## 4. 探针、资源和配置

| 机制 | 回答的问题 | 失败或变更时的效果 |
|---|---|---|
| `startupProbe` | 应用启动完成了吗 | 启动成功前暂缓其他探针，连续失败达到阈值会终止容器 |
| `readinessProbe` | 此刻可以接请求吗 | Pod 仍可运行，常规 Service 不再把新流量发到未就绪后端 |
| `livenessProbe` | 应用是否卡在必须重启才能恢复的状态 | 达到失败阈值会触发容器重启 |
| `requests` | 调度时需要预留多少资源 | 影响能否排到节点。`50m` 表示 0.05 个 CPU 核 |
| `limits` | 容器运行时的上限 | CPU 超出会受限，内存超限可能被 OOM kill |
| ConfigMap / Secret | 如何提供环境配置和敏感值 | 环境变量方式通常需要重建 Pod。Secret 的 base64 编码可直接解码，访问权限和静态加密需要另行配置 |

对 Java API，存活探针只检查进程能否继续工作。把共享 MySQL 直接放进存活探针，数据库短时故障可能触发所有副本反复重启。就绪探针按服务能否降级决定是否检查依赖，慢启动另加 `startupProbe`。

容器内的临时文件会随容器或 Pod 生命周期丢失。需要持久化时，应用通过 PVC 申请存储，StorageClass 可指定动态供给方式。先检查容量、访问模式、回收策略和备份，再迁移数据库数据。

ConfigMap 或 Secret 作为常规卷挂载时，投影文件通常会随对象变更逐步更新。应用需要重新读取才能使用新值。通过 `subPath` 挂载单文件时，不会跟随对象更新。发布配置时先区分环境变量、常规卷和 `subPath` 三种方式。

---

## 5. 滚动更新与回滚边界

修改清单中的 Pod 模板并再次 `apply` 会触发 Deployment 更新。`maxSurge` 控制额外副本，`maxUnavailable` 控制更新期间允许不可用的副本。发布是否平滑还依赖真实就绪探针、剩余集群资源、优雅停机和前后版本兼容。

```bash
# 将 web-api.yaml 中的镜像改为已准备好的新版本后执行
kubectl -n cloud-lab apply -f web-api.yaml
kubectl -n cloud-lab rollout status deployment/web-api --timeout=120s
kubectl -n cloud-lab rollout history deployment/web-api
# 练习环境恢复上一版本的 Pod 模板
kubectl -n cloud-lab rollout undo deployment/web-api
```

`rollout undo` 恢复 Deployment 版本，数据库迁移、外部状态和独立配置对象仍需各自的恢复方案。练习时可以临时填入不存在的镜像标签，观察 `ImagePullBackOff`，回滚后再把本地清单同步回可用版本。

---

# 第三篇　排障与速查

## 6. 先分清「跑不起来」和「访问不到」

| 现象 | 第一条证据 | 下一步 |
|---|---|---|
| Pod `Pending` | `kubectl -n cloud-lab describe pod <pod>` | 查看 Events 中的资源、节点约束、卷绑定 |
| `ImagePullBackOff` | Pod Events | 核对镜像名、架构、仓库连通和拉取凭据 |
| `CrashLoopBackOff` | `kubectl -n cloud-lab logs <pod> --previous` | 看上一次进程退出原因、探针事件、OOM 状态 |
| Pod Running 但未就绪 | Pod Conditions 和探针事件 | 核对路径、端口、启动耗时、依赖状态 |
| Service 无可用后端 | `kubectl -n cloud-lab get endpointslice -l kubernetes.io/service-name=web-api -o yaml` | 看 selector 与标签是否一致，以及 endpoint 的 `ready` 条件 |
| 集群内通、外部不通 | Service 类型、入口规则和控制器事件 | 按 DNS → 外部入口 → Service → Pod 逐段验证 |

---

## 7. 学习分级与问题索引

| 级别 | 验收 | 回看 |
|---|---|---|
| L1 | 解释 Pod、Deployment、Service 的关系 | 第 1～2 节 |
| L2 | 发布两个副本并通过 Service 访问 | 第 3 节 |
| L3 | 复现错误镜像和探针失败，分别定位并恢复 | 第 4～6 节 |
| L4 | 解释发布容量、数据迁移兼容与存储恢复 | 第 4～5 节 |

**记忆口诀**　Deployment 管副本，Service 给入口，就绪管流量，存活管重启。

---

# 第四篇　集群、配置变更和故障演练

## 8. 建一个可反复使用的练习集群

如果已有隔离的 Kubernetes 集群，可直接从第 3 节继续。否则准备 Docker、kind 和 kubectl。以下 Bash 命令创建单节点练习集群。把 context 写入命令，避免误操作当前终端默认的其他集群。

```bash
kind create cluster --name cloud-lab --wait 180s
kubectl --context kind-cloud-lab cluster-info
kubectl --context kind-cloud-lab get nodes -o wide
kubectl --context kind-cloud-lab create namespace cloud-lab

# 后续练习复用，当前 shell 内生效
labk() {
  kubectl --context kind-cloud-lab -n cloud-lab "$@"
}
labk apply -f web-api.yaml
labk rollout status deployment/web-api --timeout=120s
```

kind 的节点是容器。宿主机 Docker 中构建的镜像未必存在于节点容器的镜像存储。需要使用本地构建的镜像时，用 `kind load docker-image <image:tag> --name cloud-lab` 导入，并设置与实验匹配的 `imagePullPolicy`。给每次构建不同标签，避免同名镜像缓存混淆。生产发布使用节点可访问的仓库和明确版本，必要时固定 digest。

| 环境差异 | 要额外确认 |
|---|---|
| 本地 kind | 镜像导入、端口转发、有限节点资源 |
| 云托管集群 | 负载均衡器、身份、区域、存储与网络策略 |
| 自建集群 | 控制面与节点运维、CNI、存储、证书和升级 |
| 多命名空间 | context、名称、权限和调用地址 |

---

## 9. 配置更新使用声明式清单

### 9.1 用 Kustomize 生成带哈希的 ConfigMap

在 `web-api.yaml` 同级新建 `index.html` 与 `kustomization.yaml`。`index.html` 只需写一行 `<h1>web-api config v1</h1>`。保留第 3 节的 Deployment 和 Service。下面把 ConfigMap 挂到 Nginx 的网页目录。挂载会遮住镜像原有目录内容，确保配置中提供 `index.html`。

```yaml
# Deployment 管 Pod 副本。Service 通过 selector 选 Pod，命名端口需匹配。
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - web-api.yaml
configMapGenerator:
  - name: web-page
    files:
      - index.html
patches:
  - target:
      kind: Deployment
      name: web-api
    patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: web-api
      spec:
        template:
          spec:
            volumes:
              - name: page
                configMap:
                  name: web-page
            containers:
              - name: web
                volumeMounts:
                  - name: page
                    mountPath: /usr/share/nginx/html
                    readOnly: true
```

```bash
# 预览生成的 ConfigMap 名与 Deployment 实际引用
kubectl kustomize .
labk apply -k .
labk rollout status deployment/web-api --timeout=120s
labk get configmap
labk get rs -l app=web-api
labk port-forward service/web-api 18080:8080
```

另一终端请求首页，应看到 v1。将 HTML 改成 v2，重新生成并应用，预期 ConfigMap 名的后缀变化，Deployment 的引用随之改变并触发滚动替换。检查旧的 ConfigMap 仍存在。清理前核对是否有历史 ReplicaSet 依赖它，避免回滚时找不到资源。端口转发绑定的 Pod 在发布后可能退出，应重新启动转发再验证。

### 9.2 配置的三种交付方式

| 方式 | 生效机制 | 选择理由 |
|---|---|---|
| 环境变量 | 进程启动时读取。变更后重新创建 Pod | 少量、只在启动时生效的配置 |
| 普通 ConfigMap 卷 | kubelet 按周期同步投影，应用需要重新读文件 | 文件配置，应用能安全 reload |
| 带哈希的新对象 | 引用进入 Pod 模板，变更触发发布 | 保留发布证据与配置对应关系 |

Secret 使用受限权限、加密存储或外部密钥系统。应用账号只应能读取必需资源。若 Pod 不调用 Kubernetes API，可禁用自动挂载 ServiceAccount token。不要用 ConfigMap 存业务凭据。

---

## 10. 演练坏发布与流量故障

### 10.1 Readiness 阻止坏副本接流量

在练习环境把 Deployment 的策略临时设为允许一个额外副本、不允许现有副本减少。随后把就绪路径改为不存在的 `/missing`。以下补丁针对第 3 节的 `web` 容器。

```bash
# 在练习集群中核对对象、命名空间和实际运行状态。
labk patch deployment web-api --type=strategic -p \
  '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":0}},"template":{"spec":{"containers":[{"name":"web","readinessProbe":{"httpGet":{"path":"/missing","port":"http"}}}]}}}}'
labk rollout status deployment/web-api --timeout=40s
labk get pods -l app=web-api
labk get endpointslice -l kubernetes.io/service-name=web-api -o yaml
```

预期新 Pod 能运行但不就绪，rollout 等待超时，旧的就绪副本继续提供流量。查看新 Pod 的 `describe`，应能找到 HTTP 404 的探针事件。再用原声明恢复：若做过第 9 节，执行 `labk apply -k .`，否则 `labk apply -f web-api.yaml`。验证 rollout 成功及访问恢复。手工 patch 修改的策略如需恢复也要在声明中显式指定。

### 10.2 Service selector 配错时的证据

```bash
labk patch service web-api --type=merge -p '{"spec":{"selector":{"app":"wrong-app"}}}'
labk get pods -l app=web-api --show-labels
labk get endpointslice -l kubernetes.io/service-name=web-api -o yaml

# 恢复练习 Service
labk patch service web-api --type=merge -p '{"spec":{"selector":{"app":"web-api"}}}'
labk get endpointslice -l kubernetes.io/service-name=web-api -o yaml
```

Pod 仍可健康运行，但 Service 无匹配后端。DNS 可能仍能解析 Service 名，单纯 ping 或查 DNS 无法证明 HTTP 可达。恢复后再用临时 Pod 请求服务，形成标签、端点和 HTTP 响应三条证据。

---

## 11. 资源、扩缩容与可用性

### 11.1 HPA 从指标到副本数

以下 HPA 需要集群提供资源指标 API，例如正确安装的 Metrics Server。先确认 `kubectl top pods` 有结果，Deployment 容器设置了 CPU requests。示例的利用率是实际 CPU 使用相对于请求值的比率。

```yaml
# Deployment 管 Pod 副本。Service 通过 selector 选 Pod，命名端口需匹配。
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 180
```

简单估算为当前副本数乘以当前指标与目标指标之比，再向上取整。实际控制器还考虑容差、缺失样本、未就绪 Pod、上下限和稳定窗口。使用有持续 CPU 负载的练习应用验证扩缩容，静态 Nginx 对少量请求可能达不到触发条件。HPA 管副本数时，避免另一套持续发布流程反复把 Deployment 的 `replicas` 改回固定值。

### 11.2 可用性需要多个机制配合

- **PDB** 用于限制自愿驱逐，可在节点维护时保护最少就绪副本。它不能阻止故障节点退出，也不控制 Deployment 自己的滚动替换。
- **拓扑分布** 用 `topologySpreadConstraints` 或亲和规则让副本分散到节点或可用区。只有一个节点的练习集群不能验证节点级容错。
- **CPU 与内存** 请求值用于调度。内存上限过低会被 OOM kill，CPU 上限过低可能产生 throttling 和延迟。对 Java 服务同时考虑堆、元空间、线程栈和 native memory。
- **网络策略** 使用支持 NetworkPolicy 的 CNI 才会执行。启用默认拒绝后要列出明确的入口、内部调用、监控抓取和 DNS 出站。根据双方所在命名空间验证允许和禁止场景。
- **有状态工作负载** StatefulSet 给身份和存储绑定。数据库的主从、备份、数据恢复仍由应用或 Operator 处理。练习 PVC 时核对 StorageClass、访问模式和 reclaim policy。

### 11.3 ServiceAccount 与最小权限 RBAC

ServiceAccount 是 Pod 使用的集群身份。Role 定义命名空间中的允许操作，RoleBinding 把 Role 绑定给身份。下面只允许 `config-reader` 读取一个命名 ConfigMap。另存为 `rbac-demo.yaml`，沿用第 8 节的 `labk` 函数应用。RoleBinding 的 subject 命名空间要和实验 namespace 一致。

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: config-reader
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
rules:
  - apiGroups: [""]            # ConfigMap 属于核心 API 组
    resources: ["configmaps"]
    resourceNames: ["rbac-demo"] # 只授权按名称读取这一个对象
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: config-reader
subjects:
  - kind: ServiceAccount
    name: config-reader
    namespace: cloud-lab
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: config-reader
```

```bash
# 验证授权规则。当前操作者需要有权限模拟该 ServiceAccount。
labk apply -f rbac-demo.yaml
identity=system:serviceaccount:cloud-lab:config-reader
labk auth can-i get configmap/rbac-demo --as="$identity"   # 预期 yes
labk auth can-i list configmaps --as="$identity"          # 预期 no
labk auth can-i get secret/example --as="$identity"       # 预期 no
```

`can-i` 检查权限，对象本身不必已经存在。工作负载通过 `spec.serviceAccountName` 选身份。若只通过环境变量或卷读取已经声明的 ConfigMap，应用通常无需直接调用 Kubernetes API。用 ClusterRole 定义可复用规则时，可以通过命名空间 RoleBinding 把适用范围限制在该命名空间。ClusterRoleBinding 的授权范围更广，应单独审查。

### 11.4 Ingress 流量验收

Ingress 的路径转发需要已安装的控制器。先用 `labk get ingressclass` 找到可用类。将下例的 `nginx` 换成实际类名，保存为 `web-ingress.yaml` 后应用。裸 kind 集群需先安装并暴露支持 Ingress 的控制器。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-api
spec:
  ingressClassName: nginx  # 使用集群中实际存在的 IngressClass
  rules:
    - host: web.lab.test
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-api
                port:
                  number: 8080 # 这里引用 Service.port
```

从能够访问控制器入口的终端执行 `curl -H 'Host: web.lab.test' http://<入口地址>/`。若集群内 Service 已通过而入口失败，依次检查控制器地址、IngressClass、Host、Path 和后端端口。默认后端 404 常说明 Host 或 Path 没有命中，502/503 则结合控制器日志和 EndpointSlice 确认。Ingress API 已冻结，新项目可根据控制器支持和团队需求评估 Gateway API。

延伸　[Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) · [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

---

## 12. 日常操作速查与实战验收

| 场景 | 命令 | 要保存的证据 |
|---|---|---|
| 看节点与资源 | `get nodes`、`top pods`、`describe node` | 节点 Ready、实际资源、调度事件 |
| 看发布过程 | `rollout status/history`、`get rs` | 目标版本、旧与新副本、阻塞原因 |
| 看容器退出 | `logs --previous`、`describe pod` | 退出码、OOM、探针与启动日志 |
| 看流量链路 | `get svc`、`get endpointslice`、临时 Pod 内请求 | 标签、端口、就绪状态和 HTTP 响应 |
| 看权限 | `kubectl auth can-i` | 所用身份、命名空间与允许动作 |

**独立验收**　从空 namespace 发布两个副本，用集群内 DNS 和本地转发验证。完成一次配置更新，复现坏探针和空 EndpointSlice，再恢复服务。记录预期与实际的差别。若做过 HPA 实验，再提交一次指标、负载、扩容和缩容时间线。

官方实操　[kind 快速开始](https://kind.sigs.k8s.io/docs/user/quick-start/) · [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) · [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) · [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

延伸阅读　[Helm](Helm.md) · [Docker](../Docker/Docker.md) · [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) · [Service](https://kubernetes.io/docs/concepts/services-networking/service/) · [容器探针](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
