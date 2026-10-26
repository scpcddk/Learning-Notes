# CI/CD 核心知识与工程实践

> CI/CD 把代码集成、测试、构建、产物发布和部署连接成可重复执行的流程。
> 本文以 Java / Spring Boot、Docker、GitHub Actions 为主要例子，也说明与 Python AI 服务交付的衔接。
> YAML 和脚本是应用项目的配置示例；分支、目录、JDK、端口及测试环境须与实际项目匹配。代码中的命令均未在远程仓库或服务器自动执行。

---

## 一、CI、持续交付与持续部署

| 名称 | 含义 | 例子 |
|---|---|---|
| CI：Continuous Integration，持续集成 | 频繁集成代码，通过自动构建和测试及时发现问题 | PR 更新后自动编译、测试 |
| Continuous Delivery，持续交付 | 产物经过检查，发布流程可重复，保持可交付状态；生产发布可由人工决定 | 镜像已准备好，确认后部署 |
| Continuous Deployment，持续部署 | 满足检查和发布策略的变更自动部署到目标环境 | 主分支变更自动发布到测试环境 |

`CD` 可能指持续交付或持续部署，需要看上下文。两者的区别不在是否使用 Docker，而在发布到目标环境的决策与自动化方式。

**几个常见边界：**

- Git push 成功：源码已上传。
- CI 通过：已配置的检查通过，不保证未覆盖的业务都正确。
- 镜像推送成功：产物已进入仓库，不代表服务器已更新。
- 容器正在运行：主进程存在，不等于业务接口、数据库和下游服务都正常。

---

## 二、一条完整流水线由什么组成

```text
提交代码 / 创建 PR
        ↓
获取确定的代码版本 → 配置工具链 → 编译与测试
        ↓
生成版本化产物 → 构建镜像 → 发布到镜像仓库
        ↓
满足发布条件 → 更新目标环境 → 检查业务与运行状态
        ↓
记录发布版本；失败时定位、修复或回滚
```

| 环节 | 输入 | 输出 | 关键问题 |
|---|---|---|---|
| 源码获取 | 分支、提交或标签 | 工作目录 | 检查的是哪次提交？ |
| 验证 | 源码、依赖、测试配置 | 检查结果和报告 | 检查是否有实际意义？ |
| 构建 | 通过检查的源码 | JAR / 前端文件 / 镜像 | 产物能否追溯？ |
| 发布产物 | 产物、发布凭证 | 可被其他环境取得的版本 | 谁能发布、谁能拉取？ |
| 部署 | 镜像引用、环境配置 | 更新后的服务 | 是否部署了期望版本？ |
| 发布后验证 | 新服务及业务请求 | 日志、指标、检查结果 | 故障能否发现和定位？ |
| 回滚 | 旧产物、兼容配置 | 恢复到可用版本 | 外部数据是否兼容？ |

**构建一次、逐环境交付**：测试环境验证过某个镜像后，生产环境优先使用同一镜像 digest，环境差异通过运行配置表达，避免到生产环境重新构建出不同内容。

---

## 三、GitHub Actions 核心对象与 YAML

### 3.1 对象关系

```text
Workflow
├── 触发事件 on
├── Job：verify
│   └── Runner 执行多个 Step
└── Job：publish
    └── needs: verify，通过后执行发布步骤
```

| 关键词 | 含义 |
|---|---|
| Workflow | `.github/workflows/` 中的一份 YAML 流程 |
| Event / `on` | 触发流程的条件 |
| Job | 一组任务，有自己的执行环境 |
| Runner / `runs-on` | 运行 Job 的机器 |
| Step / `steps` | Job 内按顺序执行的操作 |
| `uses` | 调用一个 Action |
| `run` | 在 Runner 上执行 shell 命令 |
| `with` | 传给 Action 的参数 |
| `env` | 传给进程的环境变量 |
| `id` | 步骤的引用标识，与展示用的 name 不同 |
| `needs` | Job 依赖与输出访问 |
| `permissions` | 设置 `GITHUB_TOKEN` 的权限 |
| `environment` | 关联测试、生产等 GitHub Environment |

### 3.2 YAML 书写规则

- 使用空格缩进；同一层级的键对齐，不使用 Tab。
- `-` 表示列表项，`jobs` 下的任务名是映射键。
- `run: |` 表示多行脚本，换行是脚本的一部分。
- GitHub 表达式使用 `${{ ... }}`，Bash 环境变量通常写 `$NAME` 或 `${NAME}`；两者发生在不同处理层。
- `defaults.run.working-directory` 影响 `run`，不会自动修改 `uses` 中的文件路径、Docker context 或缓存路径。

Workflow 基础和语法见 [GitHub Workflow 说明](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)、[完整语法参考](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)。

---

## 四、事件、分支与执行条件

### 4.1 常用事件

| 事件 | 适用场景 | 注意 |
|---|---|---|
| `push` | 分支提交后检查或发布 | 分支过滤和 tag 过滤分别配置 |
| `pull_request` | 合并前检查 | branches 过滤的是 PR 目标分支；默认 checkout 通常检查 PR 合并引用 |
| `workflow_dispatch` | 人工触发流程 | 工作流须存在于默认分支，才满足该事件的要求 |
| `schedule` | 定时检查或维护 | 按 UTC 写 cron，可能延迟，不适合严格准点任务 |
| `workflow_call` | 复用其他 workflow | 通过 inputs、secrets、outputs 定义调用接口 |

分支名 main 只是本文约定，实际仓库不同就修改。配置 branches 与 paths 时，需要同时满足两类过滤条件；路径过滤可能使必需检查一直等待，须与分支保护规则配合设计。

### 4.2 PR 检查与主分支发布

PR 可以运行测试，但发布镜像应限定为满足策略的受信任变更。例如下面的 Job 条件只允许 main 的 push 事件：

```yaml
# Job 内片段
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

不要为了让 PR 获得 Secrets 而随意改成 `pull_request_target`。该事件的权限上下文与普通 PR 不同，尤其不能把不受信任的 PR 代码放入持有发布凭证的执行流程。

### 4.3 状态函数与错误处理

| 写法 | 含义与用途 |
|---|---|
| `success()` | 此前相关执行成功；普通步骤默认受成功状态约束 |
| `failure()` | 此前相关执行失败，常用于保存失败信息 |
| `cancelled()` | 运行被取消 |
| `always()` | 即使失败或取消也会考虑执行，适合有限的清理/报告步骤 |
| `!cancelled()` | 未取消时执行，常用于结束时保存诊断材料 |
| `continue-on-error: true` | 容忍该项失败，适合明确不阻断发布的辅助检查 |

测试、镜像发布等关键步骤不应靠 `continue-on-error` 或 `|| true` 隐藏失败。前置 Job 失败或跳过，依赖它的 Job 通常也会跳过；例外行为需显式设计条件。

---

## 五、变量、Secrets 与输出传递

### 5.1 几种数据各放哪里

| 方式 | 适合保存 | 使用例子 |
|---|---|---|
| Workflow / Job / Step 的 `env` | 普通运行参数 | JDK 选项、非敏感环境标识 |
| `${{ vars.NAME }}` | 仓库或 Environment 的普通配置 | 部署地址、镜像名 |
| `${{ secrets.NAME }}` | 令牌、密码、私钥等敏感配置 | 镜像仓库凭证 |
| `$GITHUB_ENV` | 传给同一个 Job 后续步骤的变量 | 计算出的版本号 |
| `$GITHUB_OUTPUT` | 当前步骤的具名输出 | 镜像引用、digest |
| Job outputs | 传给下游 Job 的少量文本 | 经 `needs` 引用发布结果 |
| Artifact | 跨 Job 传文件 | JAR、测试报告 |

同名 env 在更具体的层级覆盖外层。写入 GITHUB_ENV 后，当前步骤不会自动重新获得该变量；后续步骤才读取到。跨 Job 不共享这些环境变量，需要 Job outputs 或 artifact。

### 5.2 Step 输出 → Job 输出 → 下游 Job

以下是可独立运行的输出传递示例：

```yaml
name: Job Output Example

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
    steps:
      - id: meta
        run: echo "image=ghcr.io/example/app:sha-$GITHUB_SHA" >> "$GITHUB_OUTPUT"

  show:
    runs-on: ubuntu-latest
    needs: prepare
    steps:
      - env:
          APP_IMAGE: ${{ needs.prepare.outputs.image }}
        run: printf '%s\n' "$APP_IMAGE"
```

这里的镜像名只演示文本传递，不会实际构建或发布。实际输出的镜像路径应转为小写，并使用自己有权限的命名空间。

Secrets 不写入产物、日志或 Dockerfile。对于来自 PR 标题、分支名等外部文本，优先通过 env 传给脚本并正确引用，不直接把表达式拼接为 shell 代码，也不使用 eval 再解释。

参考：[Job outputs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs)、[Secrets](https://docs.github.com/en/actions/concepts/security/secrets)。

---

## 六、Runner、Job 隔离与执行顺序

### 6.1 Runner 与本机不是同一环境

GitHub 托管的 Ubuntu Runner 通常为 Job 提供新的环境。不能依赖自己电脑上的文件、数据库、环境变量或已经登录的 Docker 账号。自托管 Runner 可能保留上次任务的状态，需要自行隔离和清理。

每个 Job 要自行获取需要的源码和产物。Job 内各步骤通常共享工作目录，但每个 `run` 都启动新的 shell；上一条脚本中执行 cd 或 export，不会自动改变下一条脚本的进程状态。

### 6.2 并行、依赖与矩阵

- 没有 needs 约束的 Job 可以并行。
- `needs: verify` 表示等待 verify 成功，并允许读取其 Job outputs；不代表继承它的文件系统。
- Java 17/21 等多环境检查可以用 `strategy.matrix` 展开；不是项目不支持的 JDK 也必须加入测试。
- 矩阵的 fail-fast 控制同组失败后的取消策略，`max-parallel` 控制并发量。

### 6.3 防止重复检查和交叉部署

CI 可用分支/PR 维度的 concurrency group，取消已过时的运行，节省资源。部署则应按目标环境串行化，通常不宜中途取消正在更新服务的任务。

```yaml
# 放在部署 Job 下的片段
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

Concurrency 用于限制同组并行，不应直接当作可靠 FIFO 队列。目标环境在其他仓库或手工渠道也能被更新时，还需统一发布入口或采用额外锁定机制。

参考：[并发控制](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency)。

---

## 七、Java / Maven CI：编译、测试与产物

### 7.1 Maven 命令的区别

| 命令 | 通常执行的内容 |
|---|---|
| `./mvnw test` | 编译并运行配置的单元测试 |
| `./mvnw package` | 包含此前阶段，生成 JAR / WAR 等产物 |
| `./mvnw verify` | 包含此前阶段，并执行配置的验证目标 |
| `./mvnw install` | 将构建产物安装进当前环境的本地 Maven 仓库 |
| `./mvnw deploy` | 将 Maven 产物发布到配置的远程 Maven 仓库，不是启动应用 |

verify 不会自动发现并正确运行所有集成测试；常见做法是配置 Failsafe 等插件。项目没有测试或断言无效时，命令成功也不代表业务已经验证。跳过测试适合明确的独立打包步骤，不应代替 CI 的质量检查。

### 7.2 最小 Java CI

前提：Java 应用根目录有 pom.xml、mvnw 和 Maven Wrapper 所需文件；示例使用 JDK 21，Java 17 项目应相应调整。

文件：应用仓库的 `.github/workflows/ci.yml`。

```yaml
name: Java CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: java-ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Check out source
        uses: actions/checkout@v6

      - name: Set up Java
        uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: '21'
          cache: maven

      - name: Compile and verify
        run: |
          chmod +x mvnw
          ./mvnw --batch-mode --no-transfer-progress verify

      - name: Preserve test reports
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v7
        with:
          name: java-test-reports
          path: |
            target/surefire-reports/
            target/failsafe-reports/
          if-no-files-found: ignore
          retention-days: 7
```

报告步骤在测试失败时仍有机会运行，但本身不会把失败的 Job 改成成功。这里上传报告，不上传数据库密码、运行环境文件或整个工作目录。

应用位于 backend 子目录时，需要同时考虑 run 的工作目录、报告路径和 Maven 缓存依赖路径。缓存启用时通常根据 POM 等依赖文件生成键，不等于下载过的每个依赖永远可用。

---

## 八、测试数据库与外部服务

### 8.1 CI 数据库必须独立准备

测试应使用隔离的数据库和可重复初始化的数据。可选方式有 Actions service containers、Testcontainers 或专门的测试环境，具体按测试要求选择。

使用 Runner 上执行的 Job 时，MySQL service 的一个配置片段如下。合并到上节 verify Job 中，并将 env 作用于运行测试的步骤：

```yaml
# verify Job 内片段，不是独立 workflow
services:
  mysql:
    image: mysql:8.4
    env:
      MYSQL_DATABASE: app_test
      MYSQL_USER: ci_user
      MYSQL_PASSWORD: ci_only_password
      MYSQL_ROOT_PASSWORD: ci_only_root_password
    ports:
      - 3306:3306
    options: >-
      --health-cmd="mysqladmin ping -h 127.0.0.1 --silent"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=12

env:
  SPRING_DATASOURCE_URL: jdbc:mysql://127.0.0.1:3306/app_test
  SPRING_DATASOURCE_USERNAME: ci_user
  SPRING_DATASOURCE_PASSWORD: ci_only_password
  SPRING_PROFILES_ACTIVE: ci
```

这些凭证仅用于该次运行的临时测试数据库。应用使用哪个 profile、如何建表、是否初始化数据，需要在测试配置中明确；还要使用与服务器认证方式兼容的 JDBC 驱动。

### 8.2 两种网络地址不能混用

| Job 运行方式 | 连接 service container 的方式 |
|---|---|
| 命令直接在 Ubuntu Runner 上执行 | 使用 127.0.0.1 和已发布端口，如上例 |
| Job 本身使用 `container:` | 通常使用服务名 mysql 和容器端口 3306；localhost 指 Job 容器自身 |

mysqladmin ping 主要证明进程可响应，不保证业务用户权限、建表脚本和测试数据都正确。测试仍需真正建立业务连接并执行查询。

模型 API 等外部服务可以用 stub/mock 测边界，另设受控集成测试；不要让所有 PR 都依赖真实付费 API、网络稳定性与长期生产凭证。

参考：[GitHub service containers](https://docs.github.com/en/actions/concepts/use-cases/about-service-containers)。

---

## 九、Cache、Artifact 与镜像仓库

| 对象 | 核心用途 | 例子 | 不能替代什么 |
|---|---|---|---|
| Cache | 减少重复下载或构建 | Maven 依赖缓存、BuildKit 缓存 | 经过确认的发布产物 |
| Artifact | 保存运行结果或跨 Job 传文件 | JAR、测试报告、前端 dist | 长期镜像分发与运行数据备份 |
| 镜像仓库 | 按 tag/digest 分发容器镜像 | GHCR、Docker Hub | 数据库与对象存储业务数据 |

Artifact 有保留期限和权限边界，不应当作无限期发布存档。多个 Job 上传不同内容时使用清楚的名字，避免意外覆盖或下载错产物。

构建缓存能加速重复工作，但命中缓存不等于代码通过检查。缓存失效时流程仍应能够从干净环境完成构建。

参考：[Artifacts 的保存与跨 Job 传递](https://docs.github.com/en/actions/tutorials/store-and-share-data)、[Docker Actions 缓存](https://docs.docker.com/build/ci/github-actions/cache/)。

---

## 十、完整示例：测试 → 同一 JAR → 发布 GHCR 镜像

### 10.1 构建约定

这个示例使用两个 Job：verify 构建可执行 JAR 并上传；publish 下载同一 JAR 后封装镜像，避免在发布 Job 重新编译 Java。

在 Spring Boot 应用的 Maven build 中设置固定产物名，并配置 Spring Boot repackage，确保 `target/app.jar` 确实可执行：

```xml
<!-- 放在 pom.xml 的 project/build 中，不另建第二个 build -->
<finalName>app</finalName>
```

应用根目录的 `Dockerfile.ci`：

```dockerfile
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY dist/app.jar /app/app.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

这个模板用非 root UID 运行，应用应使用可写的临时目录或显式挂载并授权的目录；不假设 /app 可写。构建上下文中的 dist/app.jar 需要通过 artifact 下载得到，也不能被 .dockerignore 排除。Java 17 项目须同时调整构建 JDK 与运行镜像。

### 10.2 工作流

将下面内容作为应用仓库的 `.github/workflows/build-publish.yml`；它是独立的完整示例，包含自己的 verify，不需要再拼接上节 CI。数据库有依赖时，还需合并第八节的测试环境配置。

第七节与本节是两种配置方案。采用本节完整流程时，通常只启用这一份，避免每次提交重复运行相同检查。

```yaml
name: Build and Publish

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - name: Build and verify
        run: |
          chmod +x mvnw
          ./mvnw --batch-mode --no-transfer-progress verify
      - name: Upload executable JAR
        uses: actions/upload-artifact@v7
        with:
          name: application-jar
          path: target/app.jar
          if-no-files-found: error
          retention-days: 7

  publish:
    needs: verify
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      packages: write
    outputs:
      image: ${{ steps.meta.outputs.image }}
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: actions/download-artifact@v8
        with:
          name: application-jar
          path: dist
      - name: Compute image reference
        id: meta
        run: |
          image="ghcr.io/${GITHUB_REPOSITORY,,}:sha-${GITHUB_SHA}"
          echo "image=$image" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@v4
      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        id: build
        uses: docker/build-push-action@v7
        with:
          context: .
          file: Dockerfile.ci
          push: true
          tags: ${{ steps.meta.outputs.image }}
          labels: org.opencontainers.image.source=https://github.com/${{ github.repository }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Record published version
        env:
          IMAGE: ${{ steps.meta.outputs.image }}
          DIGEST: ${{ steps.build.outputs.digest }}
        run: |
          printf 'Image: %s\nDigest: %s\n' "$IMAGE" "$DIGEST" >> "$GITHUB_STEP_SUMMARY"
```

### 10.3 关键行为

- PR 和手动运行执行验证，只有 main 的 push 在检查通过后发布镜像。手动运行不会因选择 main 就自动满足 push 条件。
- publish 使用 Job 级写权限；构建检查只有源码读取权限。
- `${GITHUB_REPOSITORY,,}` 是 Bash 转小写，避免账号/仓库名称中的大写导致镜像路径无效。
- 指定 `context: .` 使用当前工作目录，才能包含刚下载的 dist/app.jar；不能换成忽略这些本地变化的默认 Git context。
- JAR artifact 是同一次 workflow 的输出，不从任意历史运行下载不明产物。
- GITHUB_TOKEN 仍受组织与 Package 访问策略约束；Package 已存在时，可能还需明确关联仓库和授权。
- 工作流显示发布成功后，仍需独立执行部署。稳定版本可进一步把 Actions 与基础镜像固定为已核对的 SHA/digest。

版本标签、digest、私有镜像读取权限见 [镜像仓库与版本管理](../Docker/镜像仓库与版本管理.md)。Docker Hub 的替代发布示例见 [Docker 笔记第 5 节](../Docker/Docker.md#5-cicd-流水线示例github-actions)。

发布语法与 Action 参数参考：[GitHub 镜像发布](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)、[upload-artifact](https://github.com/actions/upload-artifact)、[download-artifact](https://github.com/actions/download-artifact)、[build-push-action](https://github.com/docker/build-push-action)。

---

## 十一、环境、配置与发布凭证

### 11.1 开发、测试和生产的差异

同一镜像可以读取不同环境的数据库地址、服务地址、日志级别和密钥。业务配置在发布时注入，避免在镜像中写入生产密码。

Spring Boot 常用环境变量与 profile 表达配置；Python 服务也可从环境变量读取配置。镜像可复用不代表数据库迁移、配置键或外部接口天然兼容。

### 11.2 GitHub Environment

Environment 可表达 production、staging 等部署目标，并关联环境变量、Secrets、允许发布的分支及保护规则。仅在 YAML 写 `environment: production` 不代表已经配置审批。

所需审批、分支限制等功能的可用性取决于仓库可见性和账户方案，须核对实际设置。审批用来决定是否向该任务开放环境及凭证，不能代替业务验证。

### 11.3 Runner 与服务器的身份是两回事

CI 已登录 GHCR，不代表部署服务器能拉取私有镜像。服务器需要自己的读取凭证；SSH 登录凭证、镜像仓库凭证和应用数据库凭证也应分别管理。

生产环境可在支持的云平台上使用 OIDC 换取短期身份；部署到普通 SSH 服务器时，应核对主机指纹并使用受限账号，不通过关闭主机验证掩盖配置问题。

参考：[部署 Environment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)、[GHCR 访问规则](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)。

---

## 十二、Docker Compose 部署与回滚

### 12.1 服务配置示例

```yaml
services:
  backend:
    image: ${APP_IMAGE:?请设置已发布的镜像引用}
    ports:
      - "127.0.0.1:8080:8080"
    restart: unless-stopped
    environment:
      SPRING_PROFILES_ACTIVE: prod
    stop_grace_period: 40s
```

APP_IMAGE 可使用版本标签，也可使用仓库名加实际 digest。数据库等配置按应用另行提供。回环端口发布适用于本机检查或宿主机反向代理，Nginx 位于另一个容器时要按真实网络拓扑调整。

### 12.2 更新指定版本

下面的脚本在目标服务器的 Compose 项目目录执行；先设置实际镜像和健康检查 URL。HEALTH_URL 必须能表达应用健康，不能用 Nginx 固定返回 200 的静态路径。

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${APP_IMAGE:?请设置实际镜像 tag 或 digest}"
: "${HEALTH_URL:?请设置实际健康检查 URL}"

# 配置完整文件可能含敏感值，使用 --quiet 只进行验证。
docker compose config --quiet
docker compose pull backend
docker compose up -d --no-deps backend

ready=false
for attempt in {1..20}; do
    if curl --fail --silent --show-error --max-time 3 "$HEALTH_URL" >/dev/null; then
        ready=true
        break
    fi
    sleep 3
done

if [ "$ready" != true ]; then
    docker compose logs --tail 100 backend
    printf '新版本健康检查失败，请保留现场并按回滚策略处理。\n' >&2
    exit 1
fi
```

`--no-deps` 假设数据库等依赖已经就绪，适合只更新应用，不适用于首次初始化整个系统。更新镜像或 environment 后要用 up 重建相关容器，restart 不会自动应用这些变化。

脚本成功还需结合业务冒烟请求、日志和指标判断；有负载均衡或多个实例时，应确认观察的是新版本，而不是旧实例仍在提供健康响应。

### 12.3 回滚程序版本

保存上一个已验证的镜像引用、配置版本及发布记录。回滚时恢复旧的 APP_IMAGE，再 pull、up，并重新验证实际业务。

镜像回退不自动恢复数据库数据、对象存储、外部索引或消息队列状态。数据库变更尽量先新增兼容结构，再迁移读写，最后另次发布移除旧结构，避免新版本修改后旧程序无法运行。错误数据的恢复应按数据库备份与业务补偿方案处理。

Compose 命令行为参考：[docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)。

---

## 十三、常见发布策略

| 策略 | 做法 | 主要取舍 |
|---|---|---|
| 停机替换 | 停止旧实例后启动新实例 | 流程直接，但通常有服务空窗 |
| 滚动发布 | 分批替换实例 | 需要容量、就绪检查与新旧版本兼容 |
| 蓝绿发布 | 同时保留两套环境，验证后切流 | 回退方便，但消耗额外资源，数据仍可能共享 |
| 金丝雀发布 | 少量流量先进入新版本，观察后扩大 | 需要流量分配和版本维度的观测数据 |

单实例 Compose 的 up 重建不自动等于无中断滚动发布。策略的效果取决于代理切流、连接处理、就绪状态、数据兼容和容量，而不只是写了一个发布命令。

---

## 十四、Java 后端与 Python AI 服务的交付

| 方面 | Java / Spring Boot | Python / FastAPI |
|---|---|---|
| 依赖与构建 | Maven Wrapper、POM、JDK | 依赖锁定、Python 版本、安装方式 |
| 自动检查 | 单元测试、配置的集成测试、打包 | 测试、导入与启动检查、API 契约检查 |
| 产物 | 可执行 JAR 或镜像 | 应用镜像及依赖 |
| 发布约束 | 数据库迁移、事务与配置兼容 | 模型 API、提示词、知识库、工具权限兼容 |
| 运行验证 | 健康端点、关键业务接口 | 健康端点、结构化输出、超时与失败处理 |

Java 与 AI 服务可以独立构建镜像，但接口、字段和错误约定应保持兼容。AI 发布还应记录模型配置、提示词/Schema、知识库版本及小型评估结果，不能仅凭容器能启动就认为效果没有退化。

已有稳定接口时，两个服务不必每次一起发布；修改接口契约时，需要联合检查与明确的兼容过渡。

---

## 十五、故障排查速查

| 现象 | 优先检查 |
|---|---|
| Workflow 没有触发 | 文件目录、事件、目标分支、路径过滤、默认分支要求 |
| Job 一直 skipped | needs 的状态、Job if 条件、事件是否为 PR/手动运行 |
| 本地成功，CI 编译失败 | JDK、Wrapper、大小写、文件是否提交、依赖仓库与工作目录 |
| mvnw 提示权限不足或解释器异常 | 执行权限、文件首行、Windows CRLF 与 Linux LF 差异 |
| 测试连接不上数据库 | service 是否就绪、Job 网络模式、账号、建表与 profile |
| 找不到 app.jar | finalName、Boot 重打包、模块路径、artifact 名称与下载路径 |
| Docker COPY 找不到 dist/app.jar | artifact 下载是否成功、context 是否为本地目录、dockerignore |
| 缓存未命中或构建仍很慢 | 缓存键、POM 变化、缓存作用域、网络、实际耗时步骤 |
| GHCR 返回 denied | GITHUB_TOKEN 权限、命名空间、Package 关联及组织策略 |
| Image reference 无效 | 镜像名大写、空变量、非法标签字符 |
| 推送成功但线上没更新 | 目标服务器是否 pull/up、运行镜像、代理路径和缓存 |
| 部署进程启动后退出 | 应用日志、环境变量、文件权限、数据库和内存限制 |
| 回滚旧镜像仍报错 | 配置和数据库是否仍兼容、外部状态是否已变化 |

排查顺序通常是：**找到首个真实失败步骤 → 看完整错误 → 核对输入、环境和版本 → 在匹配环境复现 → 修复并重新运行**。不要只盯着最后的非零退出码。

---

## 十六、命令与信息速查

| 需求 | 方法 |
|---|---|
| 查看 CI 原因 | Actions → 对应运行 → 第一个失败 Job / Step |
| 查看当前 Compose 应用状态 | `docker compose ps` |
| 查看应用最近日志 | `docker compose logs --tail 100 backend` |
| 验证 Compose 配置 | `docker compose config --quiet` |
| 拉取声明的应用镜像 | `docker compose pull backend` |
| 更新应用容器 | `docker compose up -d --no-deps backend`，依赖已就绪时 |
| 对应源码 | 记录提交 SHA；PR 检查时区分合并引用与 PR head |
| 对应部署内容 | 记录镜像完整引用、digest、配置及数据迁移版本 |
| 同一 Job 传变量 | 通过 GITHUB_ENV 供后续步骤读取 |
| 跨 Job 传文本/文件 | Job outputs / artifact |

---

## 十七、关联笔记与官方资料

- [Git](Git.md)、[Maven](Maven.md)、[Docker](../Docker/Docker.md)、[镜像仓库与版本管理](../Docker/镜像仓库与版本管理.md)。
- [GitHub Actions 语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)。
- [GitHub 工作流产物](https://docs.github.com/en/actions/tutorials/store-and-share-data)。
- [setup-java](https://github.com/actions/setup-java)、[checkout](https://github.com/actions/checkout)、[Docker build-push-action](https://github.com/docker/build-push-action)。
- 示例中的 Action 主版本为已核对的引用，不代表不可变化；使用自托管 Runner 或 GitHub Enterprise Server 时，需再核对各 Action 的支持范围与运行要求。
