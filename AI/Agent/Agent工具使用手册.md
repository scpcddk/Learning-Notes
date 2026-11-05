# Agent 工具使用手册

> 回答“Agent 工具如何安装、配置、启动、日常操作、管理会话、控制权限、排查问题”。任务设计见 [Agent工作流指南](./实践案例/Agent工作流指南.md)，真实案例见 [Agent实践记录](./实践案例/Agent实践记录.md)，工作原理见 [Agent原理与开发](./Agent原理与开发.md)。
>
> **更新时间**：2026-11-05；主要环境为 Windows + Windows Terminal + PowerShell，WSL2 按需使用。
>
> **内容范围**：工具用途、操作命令、参数说明、配置方法和故障排查。示例路径按实际项目替换，命令随版本变化，优先查看 `<工具> --help` 和交互菜单。

---

## 目录

1. [环境与工具定位](#1-环境与工具定位)
2. [终端和工作目录](#2-终端和工作目录)
3. [安全基线与 Git 检查](#3-安全基线与-git-检查)
4. [Codex CLI：安装到实际使用](#4-codex-cli安装到实际使用)
5. [Pi Coding Agent：安装、使用、扩展](#5-pi-coding-agent安装使用扩展)
6. [DSH：Web UI、配置、插件](#6-dshweb-ui配置插件)
7. [OpenCode：操作速查](#7-opencode操作速查)
8. [典型任务如何选择工具与操作](#8-典型任务如何选择工具与操作)
9. [通用故障排查](#9-通用故障排查)
10. [版本与配置维护](#10-版本与配置维护)
11. [官方资料入口](#11-官方资料入口)

---

## 1. 环境与工具定位

### 1.1 Agent 的定位

| 工具 | 适合做什么 | 常用入口 |
| --- | --- | --- |
| **Codex 桌面版** | 日常项目开发、代码修改与审查 | 桌面应用中的项目与对话 |
| **Codex CLI** | 在终端中读代码、执行命令、测试、代码审查 | 项目目录中执行 `codex` |
| **Pi Coding Agent** | 轻量 Agent、模型选择、扩展和执行循环 | 项目目录中执行 `pi` |
| **DeepSeek Harness（DSH）** | 插件化 Agent、Web UI、不同运行配置 | `npx @deepseek-ai/dsh web` |
| **OpenCode** | 多模型 Agent 与终端开发 | 项目目录中执行 `opencode` |

### 1.2 环境检查

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

> [!note] `(base)` 不代表 Node 来自 Conda
> 它只表示 Conda 的 `base` 环境已激活；Node 的实际路径通过 `where.exe node` 检查。

> [!warning] 检查结果先脱敏
> 不要将登录令牌、API Key、私钥、`auth.json`、`.env` 或账号敏感信息复制到公开笔记。

---

## 2. 终端和工作目录

### 2.1 四个概念不要混淆

- **Windows Terminal**：终端窗口，提供标签页、分屏，可打开不同 Shell。
- **PowerShell**：执行 `cd`、`node`、`git`、`codex` 等命令的 Shell；PowerShell 7 和 Windows PowerShell 5.1 是不同版本。
- **WSL2 Ubuntu**：Linux 系统环境；其 Node、npm、Agent 安装与 Windows 侧可相互独立。
- **Codex / Pi / DSH CLI**：在 Shell 中调用的程序；它们不是另一种终端软件。

一种常见组合是：**Windows Terminal → PowerShell → Agent CLI**。项目若位于 WSL 的 Linux 文件系统，可在 WSL 中安装对应工具。Windows 盘在 WSL 中通常通过 `/mnt/c`、`/mnt/d` 访问，但跨文件系统访问大型项目可能较慢。

### 2.2 进入工作目录，再启动 Agent

```powershell
# 检查当前目录
Get-Location

# 示例：进入项目目录（替换为实际路径）
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

```powershell
npm install -g @openai/codex
codex --version
```

更新命令：

```powershell
npm install -g @openai/codex@latest
codex --version
```

如果不再使用 npm 版本，可通过 `npm uninstall -g @openai/codex` 卸载 npm 包；这不保证自动清理认证与会话文件。版本更新前可查看 [Codex 官方仓库](https://github.com/openai/codex) 和 `codex --help`。

### 4.2 登录和身份验证

```powershell
codex login status
# 通过 ChatGPT 登录时的输出示例：Logged in using ChatGPT
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

# ② 只读代码分析
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

依据：[官方命令参考](https://learn.chatgpt.com/docs/developer-commands?surface=cli)（2026-11-04 核对）；具体支持的参数以安装版本的 `codex --help` 为准。

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
| `/status` | 查看会话信息 | 重点检查工作目录、模型、沙盒与审批配置；字段以当前版本为准 |
| `/permissions` | 调整权限方案 | 选择只读、可编辑等适合当前任务的模式；以界面选项为准 |
| `/model` | 选择模型和推理强度 | 按当前订阅及工具提供的列表选择 |
| `/review` | 代码审查 | 查看是否有行为变化、遗漏测试等 |
| `/diff` | 在界面中查看 Git 差异 | 有文件变更时使用 |
| `/init` | 创建 `AGENTS.md` 项目指令文件 | 先理解内容，不建议在陌生仓库里盲目初始化 |
| `/exit` | 退出当前会话 | 也可按界面提示退出 |

每次启动或切换会话后，用 `/status` 重新核对工作目录和权限，不沿用上一次会话的判断。

小技巧：在交互界面输入 `/` 查看当前可用命令；使用 `@` 查找并引用工作区文件；部分版本允许使用 `!` 前缀执行本地命令，命令仍受当前审批与沙箱限制。详细快捷键以 `?` 或官方界面帮助为准。

### 4.5 三种常见任务怎么操作

**A. 只读分析**

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

**C. 审查代码变更【示例】**

在 Git 仓库中进入 Codex，使用 `/review` 或 `/diff`，也可以在 PowerShell 中使用 `git diff`。从 CLI 外部执行的审查命令示例（以当前版本 `codex review --help` 为准）：

```powershell
codex review --uncommitted
```

这类审查只提供建议，不能替代自己读 diff 和运行测试。

### 4.6 继续会话和非交互执行

恢复已保存的会话，或以非交互方式执行一次任务：

```powershell
# 选择／恢复过去的交互会话
codex resume

# 查看非交互执行帮助
codex exec --help

# 示例：只读地一次性询问项目结构
codex exec --sandbox read-only "概括当前项目目录和主要文件，不要修改任何文件。"
```

非交互模式适合脚本化检查，但**不要在不了解权限、网络和费用影响时直接用于无人值守写入任务**。接入脚本或 CI 前，先用只读命令确认行为和输出。

#### 会话分叉与子 Agent

以下命令按 **2026-11-05 官方文档**整理。不同版本支持的命令可能不同，在交互框输入 `/` 或在 PowerShell 查看 `codex fork --help`，核对安装版本。

| 输入位置 | 命令 | 用途 |
| --- | --- | --- |
| Codex 输入框 | `/fork` | 将当前对话复制成具有新 ID 的对话，保留原对话历史，尝试另一条路线 |
| PowerShell | `codex fork` | 打开选择器，从已保存的会话创建分叉 |
| PowerShell | `codex fork --last` | 从当前目录最近的会话创建分叉 |
| Codex 输入框 | `/side` | 发起临时侧边对话，继承当前对话背景，单独记录这次讨论 |
| Codex 输入框 | `/subagents` | 查看并切换子 Agent 线程；该命令本身不是创建子 Agent 的指令 |

任务委派示例：“使用两个子 Agent 并行只读分析，一个负责 Controller / Service，另一个负责 Mapper / SQL；等待结果后汇总，不修改文件。”子 Agent 侧重分工与结果汇总，会话分叉侧重另开路线。

分叉对话不会自动隔离项目文件；若界面提供工作目录或 worktree 选择，应核对实际目录。共用目录时，不同对话仍会看到彼此的文件改动。

**官方依据（2026-11-05）**：[OpenAI 官方命令参考](https://learn.chatgpt.com/docs/developer-commands?surface=cli) · [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

### 4.7 `AGENTS.md` 的使用

`AGENTS.md` 是帮助 Agent 理解项目约定的指令文件，可写项目结构、测试命令、编码规范和不得触碰的范围。

> [!important] 项目指令的作用边界
> `AGENTS.md` 提供行为约定，不能强制隔离文件系统，也不能写入密钥。

最小示例：

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
| 意外在桌面目录启动 | `/exit` → `cd` 到目标目录 → 重新启动 | 启动后用 `/status` 核对工作目录 |
| 权限不符合预期 | 在交互中执行 `/status`、`/permissions` | 不要默认当前权限和上次一致 |
| 只读模式无法写入文件 | 这是预期保护；确认任务需求后另启可写会话 | 不要为此直接关闭全部沙箱 |
| 工具说成功但没改好 | 查看文件、`git diff`、执行测试 | 优先相信实际结果 |
| 使用额度不足 | 查看 `/status` 和账号用量页面 | 不要把一次性截图数字当长期规则 |

**官方来源（2026-11-04）**：[Codex GitHub](https://github.com/openai/codex) · [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) · [开发命令与参数参考](https://learn.chatgpt.com/docs/developer-commands?surface=cli)。

---

## 5. Pi Coding Agent：安装、使用、扩展

### 5.1 安装与版本要求

按 2026-11-04 核对的官方要求，Pi 的 npm 安装需要 Node.js **22.19 或更新版本**。应在运行 Pi 的同一环境中检查 `node -v`；Windows 与 WSL 中的 Node 安装可能不同。

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

官方另提供安装脚本，选择一种可信安装方式即可。不要在未经核对时复制陌生网站的 `curl | shell` 或 `irm | iex` 脚本。

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

**只读任务示例（自然语言要求不能代替系统权限）**：

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
| `/session` | 查看当前会话 ID、用量等 | 核对会话信息 |
| `/name` | 为当前会话命名 | 便于之后查找 |
| `/compact` | 压缩当前上下文 | 长会话变得冗长时 |
| `/tree` / `/fork` / `/clone` | 浏览会话树／从历史节点或当前位置创建新会话 | 比较不同解决路径；区别见 5.4 节 |
| `/reload` | 重载扩展等资源 | 安装/修改扩展后 |
| `/copy` / `/export` | 复制回答/导出会话 | 保存经检查的资料 |
| `/mcp` | 管理 MCP 连接 | 连接外部工具和服务 |
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

#### Pi 会话管理与分支操作

**查看会话信息：** 在 Pi 输入框执行 `/session`，可核对会话文件、ID、消息与工具调用统计、Token 用量及费用等信息，具体字段以版本为准。默认会话目录为 `~/.pi/agent/sessions/`，按工作目录组织 `.jsonl` 文件；Windows 下通常对应 `%USERPROFILE%\.pi\agent\sessions\`。`/session` 只查看信息，不会创建分支。

| 命令（Pi 输入框） | 作用与适用情况 |
| --- | --- |
| `/session` | 查看会话文件、ID、消息数量和用量；切换前后可用来核对会话 |
| `/tree` | 在同一会话文件中浏览和切换历史节点；让相关的不同路线保留在同一棵树中 |
| `/fork` | 从较早的用户消息创建新会话；适合把另一条路线独立保存 |
| `/clone` | 从当前位置复制活动分支到新会话；适合保留当前状态后另开路线，不等于复制整棵会话树 |
| `/resume` | 打开已保存会话的选择器，继续其中一个会话；本身不创建分支 |
| `/name [名称]` | 为当前会话命名，方便恢复时辨认 |
| `/compact [指令]` | 压缩当前上下文，可指定需保留的信息；本身不创建分支 |

**浏览会话树：** 输入 `/tree` 进入会话树界面，浏览用户消息、助手消息与工具记录。显示哪些节点可能受界面筛选条件影响。

| 按键 | 用途 |
| --- | --- |
| `↑` / `↓` | 选择上一个或下一个节点 |
| `PageUp` / `PageDown` | 列表翻页，具体按键以当前界面提示为准 |
| `Enter` | 确认节点，进入从该位置继续对话的流程 |
| `Shift+L` | 编辑选中节点的标签，便于辨认共同起点和各方案结论 |
| `Escape` | 取消当前选择或退出界面 |

快捷键可以自定义，版本间也可能不同，以当前界面提示为准。参见 [Pi 官方按键参考](https://pi.dev/docs/latest/keybindings)（2026-11-05 核对）。

节点标签可命名为“共同起点”“方案 A 结论”等；标签用于标识树中的节点，不会创建新会话或独立工作目录。多分支探索与方案决策方法见[会话分支工作流](./方法指南/会话分支工作流.md)。

**分支操作步骤：**

1. 用 `/session` 核对当前会话信息；可先用 `/name` 给原会话命名。
2. 输入 `/tree`，选择希望返回的历史节点并按 `Enter`。
3. 若出现 `Summarize branch?` 提示，根据需要选择是否携带离开分支的摘要。
4. 选择历史用户消息时，文本会放回输入框，修改并提交后形成另一条路线；选择助手消息等其他节点时，从该节点之后继续输入新消息。
5. 再次输入 `/tree`，检查新旧路径是否同时保留，并辨认当前活动位置。返回旧分支时仍通过 `/tree` 选择节点。
6. 希望另一条路线成为独立会话时，用 `/fork`；希望从当前位置复制活动分支时，用 `/clone`。用 `/session` 核对会话 ID，并通过 `/resume` 找回原会话。

可用以下消息观察新分支的回复与树形记录：

```text
请只回复：这是 Pi 的新会话分支。
不要调用工具或修改文件。
```

**分支摘要选项：** 菜单名称以当前版本为准。

| 选项 | 作用 |
| --- | --- |
| `No summary` | 不生成离开分支的摘要，沿目标节点对应的历史路径继续 |
| `Summarize` | 总结离开的分支，将相关信息带入目标活动路径 |
| `Summarize with custom prompt` | 按自定义要求生成分支摘要，例如只保留已确认的结论和文件路径 |

若想从共同历史重新尝试，且不需要带入离开分支的工作，可选择 `No summary`；需要保留其中的有效发现时，可选择生成摘要。分支摘要与 `/compact` 的区别是：前者用于切换路线时携带信息，后者用于缩减当前上下文。参见 [Pi 官方摘要机制说明](https://pi.dev/docs/latest/compaction)（2026-11-05 核对）。

Pi 根据活动分支组织下一次模型请求，共享的早期历史会保留，其他分支在分叉点之后的全部消息不会自动一起发送。具体导航行为见 [Pi 会话与上下文官方说明](https://pi.dev/docs/latest/sessions)（2026-11-05 核对）。

**会话树操作只改变对话路径，不会撤销文件修改，也不会自动并行运行多个 Agent。** 在同一项目目录使用不同分支或会话时，磁盘文件状态仍然共享。概念区别见[原理笔记 6.1 节](./Agent原理与开发.md#61-子-agent会话分支与会话分叉)。

**命令依据（2026-11-05）**：[Pi 斜杠命令](https://pi.dev/docs/latest/slash-commands)。

### 5.5 非交互与自动化（选读）

```powershell
# 一次性文字任务（只作参考，需有模型凭据）
pi --print "解释当前仓库的大致用途，不修改文件"

# 继续本目录最近会话
pi --continue
```

正式用于脚本和 CI 前先用 `pi --help` 核对参数和输出形式。严禁直接把不可信内容作为可执行命令传入。

### 5.6 Pi 的扩展机制

| 机制 | 本质 | 建议何时使用 |
| --- | --- | --- |
| `AGENTS.md` | 项目约定与持续性指令 | 需要统一项目工作方式时 |
| Prompt Template | 可重复调用的提示词 | 常见的非执行性任务 |
| Skill | 任务特定指引与辅助资源 | 需要规范操作步骤时 |
| Extension | TypeScript 扩展，可提供工具、命令和事件处理 | 确有自定义能力需求时 |
| MCP | 对外部工具/服务的标准化连接 | 需要连接额外系统时 |

扩展可以读取上下文、注册工具、拦截工具调用；同样也可能访问你的文件和凭据。**不要运行不明来源的 Pi 扩展**。可通过 `pi -e ./my-extension.ts` 在隔离环境临时测试受信扩展；正式目录与自动加载规则见官方 Extensions 文档。

**官方来源（2026-11-04）**：[Quickstart](https://pi.dev/docs/latest/quickstart) · [终端操作](https://pi.dev/docs/latest/usage) · [命令行参考](https://pi.dev/docs/latest/cli) · [斜杠命令](https://pi.dev/docs/latest/slash-commands) · [安全](https://pi.dev/docs/latest/security) · [扩展](https://pi.dev/docs/latest/extensions)。

### 5.7 Pi Skills：创建、加载与管理

> [!note] Skill 的作用与按需加载
> Skill 是可复用的任务操作说明，通常由 `SKILL.md` 定义。Pi 启动时将可用 Skill 的名称、描述与路径提供给模型，需要使用时再加载完整说明；详细流程不必在每次任务中重复输入。

#### 项目级与用户级目录

| 范围 | 默认位置 | 用途 |
| --- | --- | --- |
| 项目级 | `<项目目录>/.pi/skills/<技能名>/SKILL.md` | 随对应项目组织任务指导 |
| 用户级 | `~/.pi/agent/skills/<技能名>/SKILL.md` | 在不同项目中复用；用户目录可由配置调整 |

Pi 支持这些目录及配置中的其他发现位置。创建前先核对会话实际工作目录，避免将项目级 Skill 写进另一个项目。目录规则见 [Pi 官方配置说明](https://pi.dev/docs/latest/configuration)。

#### 创建项目级 Skill

以只读 Python 代码审查为例，在目标项目中创建以下结构：

```text
.pi/
└── skills/
    └── python-review/
        └── SKILL.md
```

`SKILL.md` 示例：

```markdown
---
name: python-review
description: Review Python source code for correctness, readability, and common mistakes. Use when the user asks for a read-only Python code review.
---

# Python Review

1. 先读取用户指定的 Python 文件。
2. 检查变量作用域、异常处理和基本代码逻辑。
3. 按“发现的问题、对应代码位置、改进建议”组织结果。
4. 仅提供分析与建议，不修改代码、不执行程序。
5. 没有足够证据时，明确说明不确定之处。
```

`name` 用于标识技能；`description` 说明用途和适用条件，帮助模型判断何时加载；Markdown 正文规定具体执行流程。创建后重新读取文件，检查路径、头部字段和正文是否正确。

#### 重新加载与显式调用

在 Pi 交互输入框中依次执行：

```text
/reload
/skill:python-review test1.py
```

`/reload` 重新加载 Skills、扩展等资源。`/skill:python-review` 显式加载指定技能，其后的 `test1.py` 作为用户请求传给技能；也可以使用其他明确的文件路径。

可以直接用自然语言提出只读 Python 审查，由模型根据描述选择 Skill；自动选择可能遗漏，明确需要某个 Skill 时使用 `/skill:技能名`。命令与加载机制见 [Pi 官方 Skills 说明](https://pi.dev/docs/latest/skills)。

> [!tip] 通过真实任务检查执行效果
> 核对实际读取了哪个文件、输出是否包含问题与代码位置、是否区分事实与疑点，以及是否遵守不修改、不运行程序的要求。文件存在或出现技能名称提示，不能单独证明审查行为符合技能说明。

> [!important] Skill 指令与权限边界
> Skill 提供任务指导，不会自动增加底层工具权限；正文中的“只读”也不能代替系统级只读限制。需要严格控制写入或执行时，仍应配置相应权限与隔离环境。

**官方依据（2026-11-05）**：[Skills](https://pi.dev/docs/latest/skills) · [配置与目录](https://pi.dev/docs/latest/configuration) · [斜杠命令](https://pi.dev/docs/latest/slash-commands)。

### 5.8 Pi Extensions：自定义交互命令

> [!note] 从任务指导到程序扩展
> Skill 用 Markdown 提供任务流程；Extension 是可执行模块，可以注册交互命令、模型可调用的工具及运行时事件处理。具体职责见[原理笔记 2.1 节](./Agent原理与开发.md#21-extension扩展-agent-的程序能力)。

#### 创建项目级扩展

在目标项目中创建 `.pi/extensions/hello-agent.ts`：

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerCommand("hello-agent", {
    description: "Display a greeting notification",
    handler: async (_args, ctx) => {
      ctx.ui.notify("Hello from Pi Extension!", "info");
    },
  });
}
```

文件导出扩展入口函数，Pi 加载时向它传入 API 对象。项目级 `.pi/extensions/` 用于发现该项目的扩展；用户级扩展默认位于 `~/.pi/agent/extensions/`，加载行为需符合对应版本的项目信任配置。

#### 核心 API 与调用过程

| 项目 | 作用 |
| --- | --- |
| `ExtensionAPI` | 描述 Pi 扩展 API 的 TypeScript 类型 |
| `pi.registerCommand("hello-agent", ...)` | 注册名为 `hello-agent` 的交互命令，注册名称不含 `/` |
| `description` | 描述命令用途 |
| `handler` | 用户执行命令时运行的处理函数 |
| `_args` | 接收命令参数；此示例未使用 |
| `ctx.ui.notify(..., "info")` | 在 Pi 界面显示一条信息级通知 |

```text
Pi 加载扩展 → 注册 hello-agent
用户输入 /hello-agent → 执行 handler → 显示通知
```

> [!important] 交互命令与模型工具调用
> `registerCommand()` 注册交互命令；`registerTool()` 注册供模型选择调用的工具。上面的处理函数只显示固定通知，不需要模型先选择工具，也不包含 Shell 或其他项目代码的执行。

#### 重新加载与检查

在 Pi 交互输入框中执行：

```text
/reload
/hello-agent
```

预期显示通知：`Hello from Pi Extension!`。检查时应同时确认扩展加载是否报错、命令是否被识别，以及通知内容是否符合处理函数。创建文件后可重新读取，核对保存路径和代码。

#### 自定义 `/my-status` 状态查询命令

命令处理函数也可以读取 Pi 提供的运行上下文，再通过通知展示。参考实现保存为 `.pi/extensions/my-status.ts`，保留已有的其他扩展文件：

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerCommand("my-status", {
    description: "Show working directory, model, and session entry count",
    handler: async (_args, ctx) => {
      const model = ctx.model
        ? `${ctx.model.provider}/${ctx.model.id}`
        : "未选择模型";
      const entryCount = ctx.sessionManager.getEntries().length;

      ctx.ui.notify(
        [
          `当前工作目录：${ctx.cwd}`,
          `当前模型：${model}`,
          `会话记录数量：${entryCount}`,
        ].join("\n"),
        "info"
      );
    },
  });
}
```

| API | 用途 |
| --- | --- |
| `ctx.cwd` | 获取当前工作目录 |
| `ctx.model` | 获取当前模型；需处理未选择模型的情况 |
| `ctx.model.provider` / `ctx.model.id` | 取得提供商与模型 ID |
| `ctx.sessionManager.getEntries().length` | 统计当前会话的记录条目 |
| `ctx.ui.notify()` | 在交互界面显示结果 |

在 Pi 输入框执行 `/reload`，再执行 `/my-status`，核对目录、模型与记录数量。此处理函数直接读取状态并显示结果，不包含模型请求。

> [!important] 会话条目数量不等于对话轮次
> `getEntries()` 返回会话中的全部条目，可能包含消息、模型设置、摘要等记录，也不等于仅统计当前活动分支。`getBranch()` 用于取得当前分支。数量会随会话发展变化，不能把某次结果作为固定值。

这些字段由 Pi 的 API 提供。自定义命令只展示实际可读取的信息，不会因此获得其他 Agent 的全部状态或底层权限能力。参见 [Pi 官方 ExtensionContext 说明](https://pi.dev/docs/latest/extensions#extensioncontext)及[会话记录格式](https://pi.dev/docs/latest/session-format)。

> [!warning] 扩展的执行权限
> Extension 在 Pi 进程内运行，具有该进程的操作系统权限。只加载经过审查或来源可信的代码；示例中的简单通知不能代表所有扩展都只有界面操作能力。

**官方依据（2026-11-05）**：[Pi Extensions：目录、命令与 API](https://pi.dev/docs/latest/extensions)。命令名称与接口以所用版本为准。

### 5.9 Pi Extensions：注册模型可调用的工具

#### 定义工具与输入参数

在项目目录中创建 `.pi/extensions/greet-tool.ts`，保留现有扩展：

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "greet_user",
    label: "Greet User",
    description: "Return a greeting for a specified name",
    parameters: Type.Object({
      name: Type.String(),
    }),
    async execute(_toolCallId, params) {
      return {
        content: [
          { type: "text", text: `Hello, ${params.name}!` },
        ],
        details: {},
      };
    },
  });
}
```

`Type` 用于定义参数 Schema，`execute()` 接收参数并返回结果。此示例使用 Pi 提供的扩展 API 和 TypeBox 模块；结构与执行分工见[原理笔记 2.2 节](./Agent原理与开发.md#22-pi-extension注册模型可调用的自定义工具)。

#### 加载并验证工具调用

在 Pi 输入框执行 `/reload`，随后提交自然语言任务：

```text
请调用 greet_user 工具，参数 name 设置为 Alice。
根据工具的实际返回结果回复。
```

预期观察到模型发起 `greet_user` 调用、提供 `name="Alice"`，工具返回 `Hello, Alice!`，随后模型根据结果回复。这里通过自然语言请求工具调用，不是输入 `/greet_user` 执行交互命令。

> [!tip] 检查工具调用与回复之间的证据
> 同时核对工具名称、实际参数、工具返回和最终回复。仅看到模型输出问候语，不能证明工具执行过；需要看到对应的工具调用与结果记录。

**官方依据（2026-11-05）**：[Pi Extensions：自定义工具与参数定义](https://pi.dev/docs/latest/extensions)。具体接口和模块导入以安装版本为准。

---

## 6. DSH：Web UI、配置、插件

> [!note] DSH 版本兼容性
> 按 2026-11-04 核对的资料，DeepSeek Harness 处于开发者预览，升级可能破坏兼容；使用时应查看对应版本说明。

### 6.1 运行要求与最简单的启动方式

按 2026-11-04 核对的官方升级说明，Node.js 下限为 **24.9.0**。在启动 DSH 的同一个终端运行 `node -v` 检查版本。

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

DSH 的 `dsh` 启动器按 **Profile** 组合插件与配置。通过 `npx` 启动时，可将参数追加在包名后；全局安装并配置 PATH 后，可直接使用下表的 `dsh` 命令。

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
- **开发插件**：为运行时提供自定义能力，具体接口见对应版本的开发文档。

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

## 7. OpenCode：操作速查

> [!note] OpenCode 版本差异
> OpenCode 1 / OpenCode 2 的文档、配置与命令有差异，安装前先选择明确版本并查看对应文档。

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
| 对比不同模型提供商 | OpenCode | 选择明确产品版本，再配置提供商 | 记录模型、任务与结果，避免混淆变量 |

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

### 9.2 常见故障的处理方法

**npm 全局目录缺失**

报错可能包含 `ENOENT: no such file or directory, lstat`，并指向 npm 全局目录。先用 `npm config get prefix` 核对路径；如果缺失的是默认的 `%APPDATA%\npm`，可创建该目录后重试：

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\npm"
npm list -g --depth=0
```

`npm list -g --depth=0` 显示 `(empty)` 表示本次查询的全局包列表为空，不是目录访问错误；安装包后应重新查询。

**Codex 工作目录不正确**

用 `/status` 检查实际目录。若目录错误，用 `/exit` 退出，执行 `cd` 进入目标项目，再启动 Codex 并核对目录与权限。

> [!important] 环境检查与任务验收
> 登录状态和 `/status` 用于检查认证与配置；任务结果还需通过文件内容、diff、测试输出等证据验收。

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

## 10. 版本与配置维护

### 10.1 更新与切换环境时的检查

1. 在实际运行工具的终端查看版本与帮助，区分 Windows、WSL 和不同 Shell 中的安装。
2. 更新前查看 Release Notes，确认命令、配置字段、插件和认证方式是否变化。
3. 保留必要的配置备份；备份包含凭据时应妥善保管，不提交仓库。
4. 更新后检查版本、命令路径、模型连接、工作目录与权限，再执行范围明确的小任务验证。

历史版本的行为不能直接推定到新版本，命令说明应与对应版本的帮助和官方文档核对。

### 10.2 操作笔记的维护格式

```markdown
### 功能：<名称>
- 用途与适用场景：
- 适用工具、版本与环境：
- 命令或操作步骤：
- 参数与输出说明：
- 常见问题和注意事项：
- 官方依据（链接 + 核对日期）：
```

本手册按功能维护可复用的操作说明。个人环境快照、操作结果与复盘放入[Agent实践记录](./实践案例/Agent实践记录.md)，学习进度放入[学习计划](../../学习计划/进行中/副线/Agent%20工具使用与架构学习计划.md)，执行循环与上下文等机理放入[Agent原理与开发](./Agent原理与开发.md)。

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

### OpenCode

- [OpenCode Documentation](https://opencode.ai/docs/)
- [OpenCode CLI](https://opencode.ai/docs/cli/)

---
