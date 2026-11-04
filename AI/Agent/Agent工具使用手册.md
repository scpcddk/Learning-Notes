# Agent 工具使用手册

> 回答“Agent 工具如何安装、配置、启动、日常操作、管理会话、控制权限、排查问题”。任务设计见 [Agent工作流指南](./实践案例/Agent工作流指南.md)，真实案例见 [Agent实践记录](./实践案例/Agent实践记录.md)，工作原理见 [Agent原理与开发](./Agent原理与开发.md)。
>
> **更新时间**：2026-11-04；主要环境为 Windows + Windows Terminal + PowerShell，WSL2 按需使用。
>
> **状态约定**：**【本机已验证】**＝已有实际终端输出/截图；**【官方资料核对】**＝2026-11-04 检查过官方资料，但未必在本机执行；**【待实践】**＝尚无本机运行证据；**【示例】**＝供参考，不意味着已完成。

> [!tip] 学习顺序
> 先掌握 **Codex CLI**，再按需体验 Pi、DSH。命令随版本变化，优先查看 `<工具> --help` 和交互菜单。

---

## 目录

1. [环境与工具状态](#1-环境与工具状态)
2. [终端和工作目录](#2-终端和工作目录)
3. [安全基线与 Git 检查](#3-安全基线与-git-检查)
4. [Codex CLI：安装到实际使用](#4-codex-cli安装到实际使用)
5. [Pi Coding Agent：安装、使用、扩展](#5-pi-coding-agent安装使用扩展)
6. [DSH：Web UI、配置、插件](#6-dshweb-ui配置插件)
7. [OpenCode：选修速查](#7-opencode选修速查)
8. [典型任务如何选择工具与操作](#8-典型任务如何选择工具与操作)
9. [通用故障排查](#9-通用故障排查)
10. [版本维护与个人记录](#10-版本维护与个人记录)
11. [官方资料入口](#11-官方资料入口)

---

## 1. 环境与工具状态

### 1.1 Agent 的定位

| 工具 | 适合做什么 | 本机进度（截至 2026-11-04） | 建议使用方式 |
| --- | --- | --- | --- |
| **Codex 桌面版** | 日常项目开发、代码修改与审查 | 已有使用经历；版本未记录 | 日常开发主力 |
| **Codex CLI** | 在终端中读代码、执行命令、测试、代码审查 | **已完成安装、登录、只读分析与可写修改实践**（见实践记录） | 当前重点 |
| **Pi Coding Agent** | 轻量 Agent、模型选择、扩展和执行循环 | **【待实践】** | 后续在隔离目录体验 |
| **DeepSeek Harness（DSH）** | 插件化 Agent、Web UI、不同运行配置 | **【待实践】** | 后续再体验 |
| **OpenCode** | 多模型 Agent 与终端开发 | **【待实践／选修】** | 有对比需求时再使用 |

### 1.2 本机已验证的环境

| 项目 | 实际结果 | 证据状态 |
| --- | --- | --- |
| Node.js | `v24.22.2` | 【本机已验证】 |
| npm | `11.19.1` | 【本机已验证】 |
| Node 路径 | `D:\Program Files\nodejs\node.exe` | 【本机已验证】 |
| npm 全局前缀（此前） | `C:\Users\Lenovo\AppData\Roaming\npm` | 【本机已验证】 |
| `npm list -g --depth=0` 的 `(empty)` | **安装 Codex 之前的历史结果，不代表现在仍为空** | 【历史快照】 |
| Codex CLI | `codex-cli 0.166.0` | 【本机已验证】 |
| Codex 登录 | `Logged in using ChatGPT` | 【本机已验证】 |
| Codex 启动后 `/status` | 工作目录 `~\codex-test`，权限 `Read Only (Ask for approval)` | 【本机已验证】 |
| Codex 实际代码分析与修改 | 已记录 Git 笔记只读分析、Python 修改及输出 `1` → `14` | 【用户提供的实践记录】 |
| PowerShell 主版本 | 未提供 `$PSVersionTable.PSVersion` 输出 | 【待确认】 |
| Pi / DSH 安装版本 | 尚无安装成功输出 | 【待实践】 |

> [!note] `(base)` 不代表 Node 来自 Conda
> 它只表示 Conda 的 `base` 环境已激活；本机 `node.exe` 已确认位于 D 盘。

只读检查：

```powershell
$PSVersionTable.PSVersion
node -v
npm -v
where.exe node
npm config get prefix
npm list -g --depth=0
codex --version
codex login status
```

> [!warning] 检查结果先脱敏
> 不要将登录令牌、API Key、私钥、`auth.json`、`.env` 或账号敏感信息复制到公开笔记。

---

## 2. 终端和工作目录

### 2.1 四个概念不要混淆

- **Windows Terminal**：终端窗口，提供标签页、分屏，可打开不同 Shell。
- **PowerShell**：执行 `cd`、`node`、`git`、`codex` 等命令的 Shell；PowerShell 7 和 Windows PowerShell 5.1 是不同版本。
- **WSL2 Ubuntu**：Linux 系统环境；其 Node、npm、Agent 安装与 Windows 侧可相互独立。
- **Codex / Pi / DSH CLI**：在 Shell 中调用的程序；它们不是另一种终端软件。

目前建议：**Windows Terminal → PowerShell → Codex CLI**。项目若已经移至 WSL 的 Linux 文件系统，再考虑在 WSL 中另装工具。Windows 盘在 WSL 中通常通过 `/mnt/c`、`/mnt/d` 访问，但跨文件系统访问大型项目可能较慢。

### 2.2 进入工作目录，再启动 Agent

```powershell
# 检查当前目录
Get-Location

# 已验证存在的 Codex 测试目录（实际创建过）
cd "$HOME\codex-test"

# 示例：进入个人学习仓库（先自行确认该路径确实存在）
cd 'D:\LearningNotes'

# 查看当前目录中的项目文件
Get-ChildItem
```

> [!important] 工作目录与权限边界
> 工作目录决定 Agent 从哪里开始查找项目与上下文；实际读写范围由工具权限、沙箱和操作系统限制。Git 用于追踪变更。

### 2.3 Windows 与 WSL 的常用路径示意

```text
Windows: D:\LearningNotes
WSL:     /mnt/d/LearningNotes
Linux 原生 WSL 项目（示例）: ~/projects/learning-notes
```

Windows 装好的 `codex` 不等于 WSL 里也装好了。需要时分别执行 `where.exe codex`（PowerShell）和 `command -v codex`（WSL）。

---

## 3. 安全基线与 Git 检查

**这一节是本目录安全基线的统一维护位置**。其他笔记可直接链接到 `./Agent工具使用手册.md#3-安全基线与-git-检查`，无需全文重复。

1. **最小权限**：代码阅读优先只读；修改任务允许工作区写入；高风险操作单独确认。
2. **区分路径与权限**：工作目录只是任务上下文，不能替代沙箱。自然语言说“不要修改”也不能替代系统限制。
3. **保护凭据**：不用真实密码、生产 API Key、数据库生产数据练习；警惕仓库里的恶意提示词、脚本和扩展。
4. **追踪变更**：有代码变更时先执行 `git status`，最后看 `git diff` 和测试结果；不要让 Agent 覆盖已有未提交修改。
5. **控制高风险动作**：删除、批量覆盖、数据库迁移、生产部署、对外发消息、下载执行不明脚本应核对实际影响。
6. **审查实际产物**：Agent 声称“已完成”不代表测试通过、文件存在或修改符合要求。
7. **第三方扩展更加谨慎**：插件、Skill、MCP 服务可能带来新的文件、网络和执行权限；读懂来源和权限后再启用。

**常用 Git 检查：**

```powershell
git status
git diff
git diff --cached
git diff --check
git log -5 --oneline
```

如果不是 Git 仓库，`git status` 会报 `not a git repository`；这表示当前目录不属于 Git 仓库，不代表 Codex 修改代码失败。临时练习可对比修改前后代码与实际运行结果；正式项目建议使用 Git。对于真实仓库，先保存自己的改动，不要直接运行 `git reset --hard` 或 `git clean -fd` 试图“清理环境”。

> [!warning] Pi 默认不逐次审批工具调用
> 在宿主系统上运行时，其执行能力受启动用户的权限约束。初次使用选择无真实凭据的隔离测试目录，必要时使用容器、虚拟机或低权限用户。参见 [Pi Security](https://pi.dev/docs/latest/security)。

---

## 4. Codex CLI：安装到实际使用

### 4.1 安装、更新与卸载

**【本机已验证：安装成功】**

```powershell
npm install -g @openai/codex
codex --version
# 实际输出：codex-cli 0.166.0
```

以后更新时（不必为了更新而频繁更新）：

```powershell
npm install -g @openai/codex@latest
codex --version
```

如果不再使用 npm 版本，可通过 `npm uninstall -g @openai/codex` 卸载 npm 包；这不保证自动清理认证与会话文件。版本更新前可查看 [Codex 官方仓库](https://github.com/openai/codex) 和 `codex --help`。

### 4.2 登录和身份验证

**【本机已验证】**

```powershell
codex login status
# 实际输出：Logged in using ChatGPT
```

登录或切换账号时，根据当前版本提示使用：

```powershell
codex login
```

通过 ChatGPT 账号登录并不等于使用 API Key；两者认证及计费规则可能不同。认证文件属于敏感信息，**不要上传、截图公开或写入仓库**。

### 4.3 启动：最常使用的四种方式

以下命令应在 **PowerShell** 中运行，不是在 Codex 输入框里运行。

```powershell
# ① 最常用：进入项目目录后启动（使用当前默认权限配置）
cd "$HOME\codex-test"
codex

# ② 学习／只读代码分析：已成功启动并通过 /status 验证
codex --sandbox read-only

# ③ 开发与修改：允许在受控工作区内写入
codex --sandbox workspace-write

# ④ 查看当前版本所支持的所有参数
codex --help
```

**三种启动方式的区别：**

| 命令 | 沙盒设置 | 适用场景 |
| --- | --- | --- |
| `codex` | 使用当前默认配置；能否修改文件取决于实际权限 | 已了解默认权限后的日常使用 |
| `codex --sandbox read-only` | 本次启动明确指定只读 | 阅读、分析代码 |
| `codex --sandbox workspace-write` | 本次启动明确指定工作区可写 | 修改代码或文档 |

> [!important] Sandbox 与 Approval 分别控制什么？
> - **沙盒（Sandbox）**：限制工具能访问、修改哪些资源。
> - **审批（Approval）**：决定哪些操作需要先获得批准。
>
> `workspace-write` 允许工作区及其他获授权目录内的受控写入，**不会自动关闭审批，也不代表所有命令都能执行**。提示词中的“只修改某个文件”是任务约束，不能替代系统级权限限制。

> [!tip] 启动后先检查权限
> 用 `/status` 查看实际权限，**不要假设直接 `codex` 默认只读**。不要为了省事使用 `--dangerously-bypass-approvals-and-sandbox`。

依据：[官方命令参考](https://learn.chatgpt.com/docs/developer-commands?surface=cli)及本机 `codex --help`（2026-11-04 核对）；可写模式的实际操作见[实践记录案例 002](./实践案例/Agent实践记录.md#案例-002codex-cli-可写模式修改-python-代码)。

### 4.4 交互界面的基础使用

Codex CLI 启动后，底部输入框可直接输入自然语言任务，例如：

```text
分析当前目录中的项目结构，列出主要模块与入口文件。
只分析，不修改文件；遇到无法确认的地方请标明。
```

Codex 会根据任务读取文件、选择工具、返回分析结果。**是否运行 Shell、能否写文件、是否需要审批，受会话当前权限控制**。

在 Codex 交互界面内输入的命令：

| 命令 | 用途 | 使用说明 |
| --- | --- | --- |
| `/status` | 查看会话信息 | 重点检查工作目录、模型、沙盒与审批配置；字段以当前版本为准；**本机已验证** |
| `/permissions` | 调整权限方案 | 选择只读、可编辑等适合当前任务的模式；以界面选项为准 |
| `/model` | 选择模型和推理强度 | 按当前订阅及工具提供的列表选择 |
| `/review` | 代码审查 | 查看是否有行为变化、遗漏测试等 |
| `/diff` | 在界面中查看 Git 差异 | 有文件变更时使用 |
| `/init` | 创建 `AGENTS.md` 项目指令文件 | 先理解内容，不建议在陌生仓库里盲目初始化 |
| `/exit` | 退出当前会话 | 也可按界面提示退出 |

> [!note] 已验证的状态是历史快照
> 当时工作目录为 `~\codex-test`，权限为 `Read Only (Ask for approval)`。后续会话仍需重新检查；代码分析与修改结果见[实践记录](./实践案例/Agent实践记录.md)。

小技巧：在交互界面输入 `/` 查看当前可用命令；使用 `@` 查找并引用工作区文件；部分版本允许使用 `!` 前缀执行本地命令，命令仍受当前审批与沙箱限制。详细快捷键以 `?` 或官方界面帮助为准。

### 4.5 三种常见任务怎么操作

**A. 只读分析（已有 Git 笔记案例，源码项目分析仍待实践）**

1. 先进入一个**存在真实源文件**且不含凭据的目录（空目录只能验证启动，无法有效分析代码）。
2. 执行 `codex --sandbox read-only`。
3. 在 Codex 输入框提交：

```text
阅读当前项目，识别入口、主要模块和关键调用关系。
请为每项结论标注文件路径；不修改文件，不安装依赖。
```

4. 对照源文件核验；如为 Git 仓库，退出后执行 `git status`，确认没有异常改动。

**B. 在受控范围内修改代码【示例】**

```powershell
cd 'D:\LearningNotes' # 仅当该路径确实存在
git status
codex --sandbox workspace-write
```

在交互框说明：任务目标、允许修改范围、验证方式。比如“只修改指定 Markdown 文档中的错别字，保留原有章节，不修改构建脚本；完成后列出 diff”。有现存未提交修改时先自行保护它们。

> [!note] 已完成的可写实践 · 2026-11-04
> 根据用户提供记录，在 `D:\demo\python-practice` 使用 `workspace-write` 修改 `test1.py`，运行 `python -B .\test1.py`，输出 **`1` → `14`**；未安装依赖或执行网络请求。完整过程见[实践记录案例 002](./实践案例/Agent实践记录.md#案例-002codex-cli-可写模式修改-python-代码)。

**C. 审查代码变更【示例】**

在 Git 仓库中进入 Codex，使用 `/review` 或 `/diff`，也可以在 PowerShell 中使用 `git diff`。从 CLI 外部执行的审查命令示例（以当前版本 `codex review --help` 为准）：

```powershell
codex review --uncommitted
```

这类审查只提供建议，不能替代自己读 diff 和运行测试。

### 4.6 继续会话和非交互执行

Codex 具备恢复已保存会话和非交互任务能力，但当前机器尚未提供实测输出：

```powershell
# 选择／恢复过去的交互会话
codex resume

# 查看非交互执行帮助
codex exec --help

# 示例：只读地一次性询问项目结构
codex exec --sandbox read-only "概括当前项目目录和主要文件，不要修改任何文件。"
```

非交互模式适合脚本化检查，但**不要在不了解权限、网络和费用影响时直接用于无人值守写入任务**。先用只读命令确认表现；后续再研究 CI 集成。

### 4.7 `AGENTS.md` 的使用

`AGENTS.md` 是帮助 Agent 理解项目约定的指令文件，可写项目结构、测试命令、编码规范和不得触碰的范围。

> [!important] 项目指令的作用边界
> `AGENTS.md` 提供行为约定，不能强制隔离文件系统，也不能写入密钥。

最小示例（**只是示例，不代表已创建**）：

```markdown
# 项目约定

- 这是 Spring Boot + MyBatis 的学习项目。
- 修改前先阅读相关 Controller、Service 和 Mapper。
- 优先做最小改动；不要主动修改数据库真实数据。
- 代码变更后说明改动文件、验证命令及实际验证结果。
```

首次使用前阅读现有项目指令，避免把互相冲突的指令重复放入多个位置。

### 4.8 Codex 常见故障

| 现象 | 先做什么 | 说明 |
| --- | --- | --- |
| `codex` 找不到 | `codex --version`、`npm list -g --depth=0`、重开终端 | 可能是 PATH 或 npm 全局目录问题 |
| 已安装但未登录 | `codex login status`，必要时 `codex login` | 不要公开认证信息 |
| 意外在桌面目录启动 | `/exit` → `cd` 到目标目录 → 重新启动 | **本机遇到并已纠正** |
| 权限不符合预期 | 在交互中执行 `/status`、`/permissions` | 不要默认当前权限和上次一致 |
| 只读模式无法写入文件 | 这是预期保护；确认任务需求后另启可写会话 | 不要为此直接关闭全部沙箱 |
| 工具说成功但没改好 | 查看文件、`git diff`、执行测试 | 优先相信实际结果 |
| 使用额度不足 | 查看 `/status` 和账号用量页面 | 不要把一次性截图数字当长期规则 |

**官方来源（2026-11-04）**：[Codex GitHub](https://github.com/openai/codex) · [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) · [开发命令与参数参考](https://learn.chatgpt.com/docs/developer-commands?surface=cli)。

---

## 5. Pi Coding Agent：安装、使用、扩展

> [!note] Pi：待实践
> 本节为 **【官方资料核对】【待实践】**，本机尚未安装运行。后续主要体验其扩展能力，当前仍以 Codex 为主。

### 5.1 安装与版本要求

Pi 的官方 npm 安装要求 Node.js **22.19 或更新版本**；本机 Node 24.22.2 在该要求之上，但**不代表 Pi 已安装成功**。

```powershell
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi --version
pi --help
```

使用 npm 安装时，更新/卸载可参考：

```powershell
npm install -g --ignore-scripts @earendil-works/pi-coding-agent@latest
npm uninstall -g @earendil-works/pi-coding-agent
```

官方另提供安装脚本，现阶段**选择一种可信安装方式即可**。不要在未经核对时复制陌生网站的 `curl | shell` 或 `irm | iex` 脚本。

### 5.2 启动、模型认证与首次任务

```powershell
# 独立测试目录：避免触达真实项目和凭据
New-Item -ItemType Directory -Force -Path "$HOME\pi-test"
cd "$HOME\pi-test"

# 启动 Pi
pi
```

进入 Pi 后：

1. 输入 `/login`，按屏幕提示选择受支持的模型提供商与认证方式。
2. 输入 `/model`，选择已授权且可用的模型。
3. 输入 `/settings`，查看基础偏好。
4. 先做文件阅读与分析，不从真实开发目录开始。

**推荐第一次任务（只作学习目标，非系统只读保证）**：

```text
请说明当前目录包含哪些文件，以及你需要调用哪些工具才能完成分析。
不要执行写入或删除操作。
```

> [!important] “不要写入”只是任务要求
> Pi 默认不逐次审批工具调用。严格只读需要由操作系统、容器或虚拟机限制写权限；测试目录中不要放真实凭据。详见[安全基线](#3-安全基线与-git-检查)。

### 5.3 Pi 交互命令与实际用途

| 命令 | 功能 | 适用场景 |
| --- | --- | --- |
| `/login` / `/logout` | 配置/移除提供商登录 | 第一次接入模型或切换账号 |
| `/model` | 选模型 | 对比不同模型的表现 |
| `/thinking` | 调整推理级别 | 任务简单或复杂时切换 |
| `/settings` | 查看与修改常见设置 | 初次配置 |
| `/new` | 新建会话 | 新的独立任务 |
| `/resume` | 恢复其他保存的会话 | 继续旧任务 |
| `/session` | 查看当前会话 ID、用量等 | 核对状态 |
| `/name` | 为当前会话命名 | 便于之后查找 |
| `/compact` | 压缩当前上下文 | 长会话变得冗长时 |
| `/tree` / `/fork` / `/clone` | 查看/分叉会话历史 | 比较不同解决路径 |
| `/reload` | 重载扩展等资源 | 安装/修改扩展后 |
| `/copy` / `/export` | 复制回答/导出会话 | 保存经检查的资料 |
| `/mcp` | 管理 MCP 连接 | 后续学习 MCP 时 |
| `/quit` | 退出 Pi | 结束会话 |

在 Pi 输入框输入 `/` 可以查看当前安装版本实际提供的命令。插件可能增添命令，因此**不能把表格当作每个安装版本的完整清单**。

### 5.4 操作文件、终端命令与会话

- `@文件名`：在输入框搜索并附加文件路径，使任务范围更明确。
- `!git status`：在 Pi 内执行终端命令，并将输出加入模型上下文。
- `!!`：用于执行命令但不把输出送回模型（详情以当前版本内置说明为准）。
- 任务进行中可按 `Escape` 停止，具体按键与 Windows Terminal 的冲突以文档为准。
- `/resume`：从已有会话中选择；退出后在相同目录用 `pi --continue` 继续最近会话。

> [!warning] `!` 会执行真实命令
> 从 Pi 内执行 `!` 会调用真实 Shell，运行权限取决于进程与隔离环境。

### 5.5 非交互与自动化（选读）

```powershell
# 一次性文字任务（只作参考，需有模型凭据）
pi --print "解释当前仓库的大致用途，不修改文件"

# 继续本目录最近会话
pi --continue
```

正式用于脚本和 CI 前先用 `pi --help` 核对参数和输出形式。严禁直接把不可信内容作为可执行命令传入。

### 5.6 Pi 的扩展概念：先会用，再尝试开发

| 机制 | 本质 | 建议何时使用 |
| --- | --- | --- |
| `AGENTS.md` | 项目约定与持续性指令 | 需要统一项目工作方式时 |
| Prompt Template | 可重复调用的提示词 | 常见的非执行性任务 |
| Skill | 任务特定指引与辅助资源 | 需要规范操作步骤时 |
| Extension | TypeScript 扩展，可提供工具、命令和事件处理 | 确有自定义能力需求时 |
| MCP | 对外部工具/服务的标准化连接 | 需要连接额外系统时 |

扩展可以读取上下文、注册工具、拦截工具调用；同样也可能访问你的文件和凭据。**不要运行不明来源的 Pi 扩展**。将来可通过 `pi -e ./my-extension.ts` 在隔离环境临时测试受信扩展；正式目录/自动加载规则见官方 Extensions 文档。当前阶段不要求写扩展源码。

**官方来源（2026-11-04）**：[Quickstart](https://pi.dev/docs/latest/quickstart) · [终端操作](https://pi.dev/docs/latest/usage) · [命令行参考](https://pi.dev/docs/latest/cli) · [斜杠命令](https://pi.dev/docs/latest/slash-commands) · [安全](https://pi.dev/docs/latest/security) · [扩展](https://pi.dev/docs/latest/extensions)。

---

## 6. DSH：Web UI、配置、插件

> [!note] DSH：待实践
> 本节为 **【官方资料核对】【待实践】**。DeepSeek Harness 仍处于开发者预览，升级可能破坏兼容；初次使用选择无真实凭据的测试目录。

### 6.1 运行要求与最简单的启动方式

官方升级说明将 Node.js 下限提升为 **24.9.0**；本机 `v24.22.2` 满足。无需现在学习完整 Node.js/TypeScript 项目开发。

```powershell
node -v
New-Item -ItemType Directory -Force -Path "$HOME\dsh-test"
cd "$HOME\dsh-test"

# 通过 npm 获取并启动 DSH 的 Web UI
npx @deepseek-ai/dsh web
```

首次 `npx` 运行可能询问是否下载依赖；先核对包名、发布来源和权限。官方文档说明：Web UI 默认使用 `http://127.0.0.1:3080`，本地启动通常会自动打开浏览器。**以程序实际输出的地址为准**，不要随意公开打印出的令牌化启动链接。

### 6.2 DSH Web UI 第一次应该怎样用

官方使用步骤：

1. 启动 `npx @deepseek-ai/dsh web`，观察终端输出的访问地址及报错。
2. 在 Web UI 中打开 **Settings → Models**，配置受支持的模型/提供商。可按官方流程使用 DeepSeek API Key，但必须注意密钥存储方式，不公开密钥。
3. 点击 **Choose workspace**，选择专门创建的测试工作区。Web UI 新启动时通常需要主动选工作区，才可以正常发起任务。
4. 在会话输入框提交只读分析任务；观察 Agent 的文件读取、计划、工具调用、审批提示。
5. 任务结束后用系统文件检查与 Git 检查核对结果；别把“模型回答已完成”等同于任务成功。

**第一次建议任务（示例）**：

```text
概括工作区有哪些文件，列出你为完成分析实际使用过的工具。
不需要创建、修改、删除文件或联网下载程序。
```

**注意**：Web UI 的权限审批取决于启用的策略与操作类型；在所有情况下都不能把自然语言请求当成系统级强制隔离。

### 6.3 DSH CLI / 运行配置（Profile）基础

DSH 的 `dsh` 启动器按 **Profile** 组合插件与配置。若通过 `npx` 启动，可将参数追加在包名后；如将来全局安装了 `dsh`，则可直接使用下表的 `dsh` 命令（**当前尚未验证全局安装**）。

| 命令（已具备 `dsh` 可执行程序时） | 作用 |
| --- | --- |
| `dsh --help` | 查看启动器帮助 |
| `dsh --version` | 查看版本 |
| `dsh web` | 启动 Web UI（等效于启动 web Profile） |
| `dsh web --help` | 查看 Web UI 专属参数 |
| `dsh web --no-open` | 启动服务器但不自动打开浏览器 |
| `dsh web --port 8080` | 换用指定端口，避免默认端口冲突 |
| `dsh headless "概括目录结构"` | 运行一次性任务后退出；需先配置好模型与权限 |
| `dsh plugin --profile web ...` | 管理指定 Profile 的插件；具体参数见官方帮助 |

**无需额外安装也可以先查询已发布包的 Web 帮助**（能否成功运行取决于实际版本与本机环境）：

```powershell
npx @deepseek-ai/dsh web --help
```

> [!warning] 首次体验保持本机访问
> 不要使用对外网卡监听参数或向其他设备暴露 Web UI。服务器部署还需考虑网络边界、认证、TLS、Host/Origin 信任和代理配置。

### 6.4 DSH 插件：先理解使用概念

- **Profile**：组合某一套运行功能及插件的配置。
- **插件**：可提供工具、服务、能力与 UI 部分；具体接口因版本变化应以官方文档为准。
- **插件管理**：通过 `dsh plugin --profile <name> ...` 将包操作应用于对应 Profile；`...` 不是实际可直接执行的命令。
- **开发插件**：属于 Agent 原理/框架开发阶段，不必为了第一次使用 DSH 而学习整个 Cordis 架构。

建议观察的内容：Web UI 中一次任务从输入到工具调用、审批、结果返回的路径；一个 Profile 下启用的能力来自哪里；失败时在哪里查看日志。具体源码分析放入 [Agent原理与开发.md](./Agent原理与开发.md)。

### 6.5 DSH 典型故障

| 情况 | 优先检查 |
| --- | --- |
| 提示 Node 版本过低 | 在**启动 DSH 的同一个终端**运行 `node -v`；需 Node ≥ 24.9.0 |
| `npx` 下载失败 | npm registry、网络代理、包名、认证/缓存日志 |
| 页面打不开 | 启动终端是否仍运行、实际监听 URL、端口是否被占用、浏览器错误 |
| 页面可开但不能聊天 | 是否选定 Workspace、Settings → Models 是否配置有效模型 |
| API Key 无效 / 调用失败 | 提供商选择、密钥有效性、余额/限流、请求错误；不要公开密钥 |
| 首次要求权限 | 查看操作内容与影响范围；对不确定的请求拒绝并缩小任务范围 |
| 插件或 Profile 不兼容 | 记录 `dsh` 版本、配置、错误日志，参考对应版本升级指南 |

**官方来源（2026-11-04）**：[DSH 中文 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md) · [Web UI 使用说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/index.md) · [CLI 帮助](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cli-help.md) · [Node 24 迁移](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/upgrade-guide/v0.2.1-rc.2/node-24/guide.md)。

---

## 7. OpenCode：选修速查

> [!note] OpenCode：选修，先确认版本
> 当前为【待实践／选修】。OpenCode 1 / OpenCode 2 的文档、配置与命令有差异，安装前先选择明确版本并查看对应文档。

作为对比工具，主要观察多模型提供商配置、终端 UI、命令与权限策略。若选择 OpenCode 1，官方文档曾提供 npm 安装方式（**先确认仍使用该版本，再执行**）：

```powershell
npm install -g opencode-ai
opencode --version
opencode
```

进入应用后按照当前 TUI 的提示登录模型提供商并选择模型。部分官方版本支持 `/connect`、`/models` 等命令，但实际名称以所安装版本为准。第一次实验使用独立目录，不让多个 Agent 同时修改同一份真实项目。

**官方入口（2026-11-04）**：[OpenCode 文档](https://opencode.ai/docs/) · [命令行参考](https://opencode.ai/docs/cli/) · [提供商](https://opencode.ai/docs/providers/)。

---

## 8. 典型任务如何选择工具与操作

这里提供**操作入口速查**。任务委托模板、探索/执行/审批模式与验收规则见 [Agent工作流指南](./实践案例/Agent工作流指南.md)，实践复盘见 [Agent实践记录](./实践案例/Agent实践记录.md)。

| 需求 | 首选工具 | 建议操作 | 必要的确认 |
| --- | --- | --- | --- |
| 阅读陌生 Java 项目 | Codex CLI | 进入项目 → `codex --sandbox read-only` → 说明分析范围 | 核对源码路径与结论 |
| 理解 Spring / MyBatis 调用链 | Codex CLI | 提供入口类/方法，让工具梳理实际调用关系 | 查阅关键源码、验证事务边界 |
| 小范围修改 Markdown / Java | Codex CLI | Git 状态检查 → 工作区可写会话 → 提交明确范围 | `git diff` 与测试 |
| 审查未提交代码 | Codex CLI | `/review` 或 `codex review --uncommitted` | 独立检查问题是否真实 |
| 研究 Agent Loop | Pi | 隔离目录 → `/login` → `/model` → 观察每次工具调用 | 不在真实文件中随意试验 |
| 对比上下文管理 | Pi | `/session`、`/resume`、`/compact` | 对照实际上下文变化 |
| 研究插件式 Agent | DSH | `npx @deepseek-ai/dsh web` → 选模型和工作区 | 检查 Profile 与权限 |
| 对比不同模型提供商 | OpenCode（选修） | 选择明确产品版本，再配置提供商 | 记录模型、任务与结果，避免混淆变量 |

> [!tip] 每次任务记住四个动作
> **进入正确目录 → 核对权限 → 检查 diff 和测试 → 记录可复用经验**。普通成功对话无需逐条存档。

---

## 9. 通用故障排查

### 9.1 一套通用诊断顺序

1. **明确环境**：Windows PowerShell、PowerShell 7 还是 WSL2？是否启用了 Conda？
2. **检查命令是否存在**：`where.exe <命令>` 或 PowerShell 的 `Get-Command <命令>`。
3. **检查版本和帮助**：`node -v`、`npm -v`、`codex --version`、`pi --version`、`<工具> --help`。
4. **核对工作目录**：`Get-Location`、项目根目录是否正确。
5. **核对认证与模型**：登录状态、模型提供商、API Key 是否有效（不要打印密钥）。
6. **核对权限**：操作是否被只读沙箱/审批策略拒绝？
7. **查看原始错误**：保留错误码、必要日志和时间；先脱敏再分享。
8. **一次只改一个因素**：不同时升级 Node、换网络、改沙箱、重装所有工具。

### 9.2 已实际遇到并解决的情况

**npm 全局目录缺失（2026-11-04）【本机已解决】**

报错关键点：`ENOENT: no such file or directory, lstat 'C:\Users\Lenovo\AppData\Roaming\npm'`。

当时的处理是：

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\npm"
npm list -g --depth=0
```

再次执行 `npm list -g --depth=0` 后显示 `(empty)`，意味着**当时的全局目录为空**。之后 Codex 已成功通过 npm 安装，此历史结果不能再作为当前包清单。

**Codex 起初在桌面工作目录启动（2026-11-04）【本机已解决】**

观察到交互界面底部为 `~\Desktop`；退出后进入 `~\codex-test` 再启动，随后 `/status` 已确认工作目录和只读权限。

> [!important] 怎样才算完成一次实践？
> 登录状态和 `/status` 证明认证、运行及配置正常。完成实践还需要**实际任务、结果核验和文件变更检查**。

### 9.3 典型错误类型速查

| 错误类别 | 常见表现 | 一般处理方向 |
| --- | --- | --- |
| PATH / 命令不存在 | `command not found`、`not recognized` | 路径、npm 全局目录、重开终端 |
| npm 权限/目录 | `EACCES`、`EPERM`、`ENOENT` | 原始路径、权限、目录存在性；勿盲目提权 |
| PowerShell 脚本策略 | `running scripts is disabled` | 先辨认是 `npm.ps1` 还是程序本身；不要默认关闭系统限制 |
| 模型认证 | `401`、`unauthorized` | 认证方式、模型提供商、密钥有效性 |
| 限流/配额 | `429`、quota exceeded | 用量、重试机制、服务端返回信息 |
| 服务端/网络 | 超时、无法解析域名 | 代理、网络、端点、服务器状态 |
| 文件权限 | `permission denied`、只读拒绝 | 沙箱与 OS 权限；确认任务是否需要写入 |
| Git 冲突/变更 | 非预期 diff、无法合并 | 保存原有改动、检查差异、缩小任务范围 |
| DSH Web UI | 页面打不开或没工作区 | 进程、URL、端口、Workspace、模型配置 |

---

## 10. 版本维护与个人记录

> [!tip] 更新记录的最小单位
> **版本 + 日期 + 实测命令 + 结果**。更新工具或切换环境时补充这四项；历史验证不保证未来版本行为一致，无需每次重写教程。

### 10.1 本机状态记录表

| 日期 | 工具 | 实际操作/命令 | 结果 | 后续事项 |
| --- | --- | --- | --- | --- |
| 2026-11-04 | Node / npm | `node -v`、`npm -v` | Node `v24.22.2`，npm `11.19.1` | 已满足已查到的 Pi/DSH Node 最低版本要求 |
| 2026-11-04 | npm | 创建全局 npm 目录后检查 | 当时 `(empty)`，报错解除 | 后续已安装 Codex，清单会变化 |
| 2026-11-04 | Codex CLI | `npm install -g @openai/codex`、`codex --version` | `codex-cli 0.166.0` | 已安装 |
| 2026-11-04 | Codex CLI | `codex login status` | `Logged in using ChatGPT` | 已登录 |
| 2026-11-04 | Codex CLI | 在 `~\codex-test` 启动、执行 `/status` | 工作目录正确，`Read Only (Ask for approval)` | 后续已有只读与可写实践记录 |
| 2026-11-04 | Codex CLI | 在 Python 练习目录启动 `workspace-write`，修改并运行 `test1.py` | 输出 `1` → `14`（用户提供记录） | 详见实践记录案例 002 |
| 待记录 | Pi | `pi --version` 等 | 未实践 | 仅在准备好后记录 |
| 待记录 | DSH | 启动 Web UI、选模型与工作区 | 未实践 | 仅在准备好后记录 |

### 10.2 新增操作的最小记录格式

```markdown
### 功能：<名称>
- 工具和版本：
- 环境：Windows / WSL / PowerShell 版本
- 官方依据（链接 + 核对日期）：
- 实际命令或操作：
- 实际输出（脱敏）：
- 状态：本机已验证 / 待实践 / 已失效
- 常见注意事项：
```

**不要逐条复制聊天记录**。独立任务的复盘、真实 diff 和验证结果写到 [Agent实践记录](./实践案例/Agent实践记录.md)；Agent Loop、上下文、工具调度等机理写到 [Agent原理与开发.md](./Agent原理与开发.md)。

---

## 11. 官方资料入口

> 以下链接均于 **2026-11-04** 核对。官网内容可能随时间改变，遇到版本差异请以对应版本 `--help` 和 Release Notes 为准。

### Codex

- [GitHub — openai/codex](https://github.com/openai/codex)
- [Codex CLI 使用说明](https://learn.chatgpt.com/docs/codex/cli)
- [开发命令、参数与交互操作](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

### Pi

- [Pi Quickstart](https://pi.dev/docs/latest/quickstart)
- [Pi 终端交互](https://pi.dev/docs/latest/usage)
- [Pi CLI 命令行](https://pi.dev/docs/latest/cli)
- [Pi 斜杠命令](https://pi.dev/docs/latest/slash-commands)
- [Pi Extensions](https://pi.dev/docs/latest/extensions)
- [Pi Security](https://pi.dev/docs/latest/security)

### DeepSeek Harness

- [DSH 中文 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md)
- [DSH Web UI 指南](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/index.md)
- [DSH CLI Help](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cli-help.md)
- [DSH Node.js 24 迁移说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/upgrade-guide/v0.2.1-rc.2/node-24/guide.md)

### OpenCode（选修）

- [OpenCode Documentation](https://opencode.ai/docs/)
- [OpenCode CLI](https://opencode.ai/docs/cli/)

---
