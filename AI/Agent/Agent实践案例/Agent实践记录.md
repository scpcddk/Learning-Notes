# Agent 实践记录

---

## 一、环境准备与历史快照

### 环境与认证记录

| 项目 | 历史结果 | 记录说明 |
| --- | --- | --- |
| Node.js | `v24.22.2` | 原记录标为本机已验证 |
| npm | `11.19.1` | 原记录标为本机已验证 |
| Node 路径 | `D:\Program Files\nodejs\node.exe` | Windows 侧路径，不代表 WSL 中的安装 |
| npm 全局前缀 | `C:\Users\Lenovo\AppData\Roaming\npm` | 当时的配置 |
| 全局包列表 | `npm list -g --depth=0` 返回 `(empty)` | 安装 Codex 前的历史结果，不代表当前包列表 |
| Codex 安装 | `npm install -g @openai/codex`；`codex --version` 返回 `codex-cli 0.166.0` | 原记录标为安装成功 |
| Codex 登录 | `codex login status` 返回 `Logged in using ChatGPT` | 当时已登录 |
| Codex 启动与权限 | 工作目录 `~\codex-test`，`/status` 显示 `Read Only (Ask for approval)` | 当时的会话快照 |
| Codex 代码实践 | Git 笔记只读分析；Python 修改后输出 `1` → `14` | 详见案例 001、002 |
| Pi | 版本 `1.5.0`，已完成模型连接与文件创建、读取 | 用户提供记录，详见案例 003 |
| PowerShell 版本 | 未提供 `$PSVersionTable.PSVersion` 输出 | 待确认 |
| DSH 安装版本 | `0.2.2-rc.1` | 2026-11-06 全局安装并启动 Web UI 服务，详见案例 009 |

环境问题摘要：

- **2026-11-04｜npm 全局目录缺失**：创建 `%APPDATA%\npm` 后解除，当时全局包列表为空。
- **2026-11-04｜Codex 工作目录错误**：在 `~\Desktop` 启动，退出后进入 `~\codex-test` 重启，`/status` 确认工作目录与只读权限。
- **2026-11-06｜DSH Windows 沙箱授权失败**：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(D:\demo\dsh-sandbox)`，待修复；未切换完全权限、未修改 ACL。
- **2026-11-07｜Codex TUI 启动超时**：`workspace routing discovery timed out (code -32603)`；诊断显示 HTTPS 可达、WebSocket 握手超时、Windows 手动代理未启用，改用本地代理后仍失败。用户判断与网络环境有关，未继续排查 TUI。跨 Agent 只读审查后来用 `codex exec` 完成，见[案例 011](#案例-011codexpidsh-跨-agent-代码审查对比)。

### WSL2 Agent 安装与验证

**整理日期**：2026-11-13。环境为 WSL2 Ubuntu 24.04、Bash。据用户贴出的对话转述记录，尚未独立复核原始终端输出或截图。

**初始现象**：在 Ubuntu 中运行 `npm install -g @openai/codex` 后曾看到 `changed 2 packages in 36s`。随后运行 `codex` 时，Windows npm 目录中的启动脚本报找不到 `node`。`type -a` 的转述结果显示 `node` 在当时的 Bash 中无法解析，`npm` 来自 `/mnt/d/Program Files/nodejs/npm`，`codex` 来自 `/mnt/c/Users/Lenovo/AppData/Roaming/npm/codex`。`npm config get prefix` 返回 Windows 路径 `C:\Users\Lenovo\AppData\Roaming\npm`。这组证据指向当时调用的是 Windows 的 npm 与 Codex。安装输出只表明 npm 做过包变更，具体改动的 Windows 包版本未核实。

**调整与核对结果**

| 验证项 | 据对话转述的结果 |
| --- | --- |
| nvm 加载 | 对话确认已安装并加载，未提供 nvm 版本 |
| Linux 版 Node.js 与 npm | `node -v` 为 `v24.22.3`，`npm -v` 为 `11.19.1`，两者位于 `/home/lenovo/.nvm/` 下。nvm 默认版本指向 `24` 系列 |
| Linux 版 Codex 命令路径 | `type -a codex` 首项为 `/home/lenovo/.nvm/versions/node/v24.22.3/bin/codex`，Windows 入口仍列在后面 |
| Codex CLI 启动 | `codex --version` 返回 `0.169.0` |
| Codex 登录与交互界面 | 后续截图转述显示已通过 ChatGPT 账号登录（Plus），交互界面已打开，模型显示为 `GPT-6.1-Sol` |
| 工作目录与权限显示 | `/mnt/d/demo` 对应 Windows 的 `D:\demo`，界面显示 `Workspace（granular）` |
| Linux 版 Pi 命令路径与版本 | `type -a pi` 首项为 `/home/lenovo/.nvm/versions/node/v24.22.3/bin/pi`，Windows 入口 `/mnt/c/Users/Lenovo/AppData/Roaming/npm/pi` 排在后面。`pi --version` 返回 `1.5.2` |
| Pi 交互启动与模型调用 | 后续截图转述显示已登录 OpenAI，选中 `gpt-6.1-sol`，收到纯文本回复 `Hello! What can I help you with?`，界面显示用量统计 |
| Linux 版 DSH 命令路径与版本 | `type -a dsh` 首项为 `/home/lenovo/.nvm/versions/node/v24.22.3/bin/dsh`，`dsh --version` 返回 `0.2.2-rc.1` |

**启动警告**：据截图转述，Codex 提示在 `PATH` 上找不到系统的 `bubblewrap`，并报告将使用内置版本。交互界面已打开，仍需通过实际任务核对工具能否在该沙箱下执行。警告说明见[工具手册第 4.8 节](../Agent工具使用手册.md#48-codex-常见故障)。

**Pi 安装输出**：据对话转述，npm 显示 `added 123 packages`，随后通过命令路径和版本确认 WSL2 优先使用 Linux 版 Pi。`packages are looking for funding` 是依赖的资助信息。[npm fund 文档](https://docs.npmjs.com/cli/v11/commands/npm-fund/)

**Pi 首次启动与登录提示**：据截图转述，Pi 先提示 `fd not found`、`ripgrep not found`，随后报告已将 `fd` 和 `rg` 安装到 `/home/lenovo/.pi/agent/bin/`。登录时曾出现 `Failed to login to OpenAI Codex: Missing authorization code`，之后显示 `Logged in to OpenAI. Selected gpt-6.1-sol.`，并收到模型回复。判断本次登录是否成功，以后续状态和实际回复为准。[工具手册第 5.2 节](../Agent工具使用手册.md#52-启动模型认证与首次任务)

**DSH 安装输出**：据对话转述，npm 11.19.1 首次全局安装时提示 5 个依赖的安装脚本未获准执行。随后使用 `--allow-scripts` 放行 `@deepseek-ai/dsh-subprocess-local`、`koffi`、`node-pty` 并重装 `0.2.2-rc.1`。重装完成后仍提示 `@google/genai` 和 `protobufjs` 的脚本未执行。现有结果确认到安装和 CLI 版本检查，脚本执行详情及其对运行功能的影响仍需实际输出或测试验证。[工具手册第 6.1 节](../Agent工具使用手册.md#61-全局安装启动与更新)

**本次配置收尾**：按用户确认，WSL2 中已用 nvm 配置 Node.js `v24.22.3`，Codex `0.169.0` 已登录并打开交互界面，Pi `1.5.2` 已登录并收到模型回复，DSH `0.2.2-rc.1` 已安装。Windows 原有的三个 Agent 均保留，Windows 上的 DSH 沙箱 `Win32 5` 仍待修复。

**下次从这里继续**：在 WSL2 为 DSH 配置 DeepSeek API Key，先用 [Headless 纯文本任务](../Agent工具使用手册.md#63-dsh-cli--运行配置profile基础)验证模型连接，再在独立测试目录验证 Shell 执行和文件修改。本次停在安装阶段，尚无 Headless、Web UI 或工具执行的实测结果。Codex 的文件读写和沙箱执行、Pi 的文件搜索与读写也仍待单独验证。

复用命令见[工具手册第 2.5 节](../Agent工具使用手册.md#25-在-wsl2-中配置-linux-版-nodejs-和-agent)。

---

## 二、Codex CLI

### 案例 001：Git 笔记分析与中文乱码排查

> [!note] 实践信息
> - **日期 / 工具**：2026-11-04 · Codex CLI 0.166.0
> - **环境**：Windows + PowerShell
> - **状态**：已完成，部分结论待独立验证。

#### 1. 实践目标

使用 Codex 只读分析 Git.md，
观察 Agent 如何调用工具、处理异常。

#### 2. 实际过程

1. Codex 使用 Get-Content 读取文件。
2. 中文出现乱码。
3. 使用 -Encoding UTF8 重新读取。
4. 检查文件字节和终端输出编码。
5. 使用 Unicode 转义绕过乱码。
6. 完成 Git 笔记分析。
7. 通过 git status --short 检查工作区。

#### 3. 遇到的问题

> [!warning] 工具执行成功，输出仍可能有误
> 文件为 UTF-8，但工具输出中文乱码；应继续检查解码方式和终端输出编码。

#### 4. 排查结果

- 文件可以正确按 UTF-8 解码。
- 控制台输出编码为 gb2312。
- 通过 Unicode 转义可以恢复中文。
- 尚未永久修复终端编码设置。

#### 5. 经验总结

- Agent 能调用 Shell 工具读取文件。
- 工具执行成功不代表输出一定正确。
- 发现问题后，可以要求 Agent 继续排查。
- 操作前应记录 Git 状态以便对比。
- Agent 的分析结论需要人工验证。

---

### 案例 002：Codex CLI 可写模式修改 Python 代码

> [!note] 实践信息
> - **日期 / 工具**：2026-11-04 · Codex CLI v0.166.0
> - **工作目录**：`D:\demo\python-practice`
> - **权限模式**：`workspace-write`
> - **状态**：已完成，运行结果已验证。
> - **记录来源**：用户提供的实践过程与结果；整理时未重新运行代码。

#### 1. 实践目标

让 Codex 修改已有 Python 练习文件 `test1.py`，使嵌套函数 `fun1()` 最终输出 `14`，并保留原有嵌套函数结构。

**操作限制：** 仅修改目标文件，不安装依赖，不执行网络请求。

**启动命令：**

```powershell
cd 'D:\demo\python-practice'
codex --sandbox workspace-write
```

#### 2. 修改前的代码

```python
def fun1():
    count = 1

    def fun_in():
        count = 12

        def fun_inn():
            nonlocal count
            count = 14

    fun_in()
    print(count)

fun1()
```

**修改前输出：** `1`

> [!important] 为什么仍然输出 `1`？
> - `fun_in()` 中的 `count = 12` 创建了局部变量，没有修改 `fun1()` 的 `count`。
> - `fun_inn()` 的 `nonlocal count` 原本绑定 `fun_in()` 的 `count`，但 `fun_inn()` 没有被调用。

#### 3. Agent 实际执行过程

1. 检查工作目录，使用 `rg` 搜索 `fun1`、`fun_in`、`fun_inn`。
2. 定位到 `test1.py` 并读取文件。
3. 尝试检查 Git 状态，但目录不是 Git 仓库，因此命令失败。
4. 运行 `python -B .\test1.py`，得到输出 `1`。
5. 修改 `fun_in()` 的作用域声明，并调用 `fun_inn()`。
6. 再次运行程序，得到输出 `14`。
7. 报告修改内容和实际验证结果。

#### 4. 修改后的关键代码

```python
def fun1():
    count = 1

    def fun_in():
        nonlocal count
        count = 12

        def fun_inn():
            nonlocal count
            count = 14

        fun_inn()

    fun_in()
    print(count)

fun1()
```

> [!tip] 两处改动决定结果
> 在 `fun_in()` 中添加 `nonlocal count`，并调用 `fun_inn()`。两个内层函数的 `nonlocal count` 都关联到 `fun1()` 的 `count`，最终输出 **`14`**；同时规范了赋值语句格式。

#### 5. 验证结果

**执行命令：**

```powershell
python -B .\test1.py
```

> [!note] `python -B` 的作用
> 禁止 Python 在导入源码模块时写入 `.pyc` 字节码缓存文件，减少验证时产生的缓存。参见 [Python 官方说明](https://docs.python.org/3/using/cmdline.html#cmdoption-B)。

| 检查项目 | 结果 |
| --- | --- |
| 修改前输出 | `1` |
| 修改后输出 | `14` |
| 是否保留三层嵌套结构 | 是 |
| 是否运行真实 Python 程序 | 是 |
| 是否修改其他文件 | 执行记录未显示 |
| 是否使用 Git diff | 否，目录不是 Git 仓库 |
| 是否执行网络请求或安装依赖 | 否 |

#### 6. 遇到的问题

Codex 尝试检查 Git 信息时出现：

```text
fatal: not a git repository (or any of the parent directories): .git
```

> [!note] 非 Git 目录如何验收？
> 当前目录是普通 Python 练习目录，Git 报错未阻止修改和运行文件。可用**修改前后代码对比 + 实际运行输出**验收。

#### 7. 经验总结

**有效做法：**
- 提前给出明确目标：输出必须为 `14`。
- 限定修改范围：只允许修改 `test1.py`。
- 要求修改前后分别运行程序，形成可比较的验证结果。
- 让 Agent 说明关键代码变化，而不只报告任务完成。

**需要注意：**
- `workspace-write` 允许工作区内的受控写入，提示词限制不能代替实际沙盒隔离。
- 非 Git 目录也能使用 Codex，但无法直接通过 `git diff` 验证改动。
- Agent 的代码修改应结合实际测试结果检查。

#### 8. 涉及的 Agent 原理

- **Agent Loop**：读取代码 → 分析问题 → 修改文件 → 运行测试 → 根据输出确认结果。
- **Tool Calling**：使用搜索工具、Shell 命令和文件编辑操作。
- **工具反馈**：通过 Python 的实际输出判断修改是否达到目标。
- **执行权限**：使用 `workspace-write` 完成受控代码修改。

> [!important] 实践结论
> 完成 Codex CLI 首次可写实践：修改 `test1.py`，并通过真实运行输出 **`1` → `14`** 验证目标。过程覆盖了文件搜索、读取、修改、Shell 调用与结果检查。

---

## 三、Pi Coding Agent

### 案例 003：Pi 首次工具调用

> [!note] 实践信息
> - **日期 / 工具**：2026-11-05 · Pi Coding Agent 1.5.0
> - **状态**：已完成（据用户提供记录）。
> - **记录来源**：用户提供的 AI 对话摘要；未附完整原始工具日志，整理时未重新执行。

**任务：**
在 `D:\demo\pi-sandbox` 创建 `pi-test.txt`，写入 `Hello Pi Agent!`，并重新读取验证内容。

**实际过程（据提供记录）：**
1. `bash`：执行 `pwd`，返回 `/mnt/d/demo/pi-sandbox`。
2. `write`：创建 `pi-test.txt`，写入 `Hello Pi Agent!`。
3. `read`：重新读取文件，返回内容为 `Hello Pi Agent!`。
4. 模型依据读取结果判断任务完成。

**结果：**
文件创建与内容读取成功；执行摘要中未发现修改其他文件的记录，但整理时未独立核查文件变更范围。

**经验：**
- 模型选择工具并生成参数，由运行时调度工具实际执行，再将结果返回模型。
- 连续调用 `bash → write → read`，体现了 Agent Loop 中的工具执行、结果反馈与完成判断。
- 创建文件后重新读取，可以核对实际内容，不能只凭写入成功提示验收。
- `bash` 返回 Linux 风格路径，与常见 WSL 挂载路径一致；不能仅凭路径认定整个 Pi 进程运行在 WSL 中，具体环境待确认。

本案例记录文件创建与读取；会话、Skill 和 Extension 的后续实践分别见案例 004～008。

---

### 案例 004：Pi 会话查看与分支操作

> [!note] 实践信息
> - **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
> - **状态：** 会话查看与历史节点分支切换完成（据用户提供记录）。
> - **记录来源：** 用户提供的 AI 对话摘要；整理时未独立重跑。

**操作与结果：**

1. 执行 `/session`，查看 `.jsonl` 会话文件及统计信息；当时显示 21 条消息、5 次工具调用及 5 次工具结果返回。
2. 使用 `/tree` 浏览历史节点，选择较早节点并确认。
3. 在分支摘要提示中选择 `No summary`，发送“请只回复：这是 Pi 的新会话分支。不要调用工具或修改文件。”
4. Pi 回复指定文字，再次打开会话树，可观察新旧分支同时保留。

**可复用结论：** `/session` 用于核对会话信息，统计数字只是当时的快照；`/tree` 可以从历史节点探索另一条路线，原有路径仍然保留。

**验证范围：** 本案例覆盖同一会话树中的分支操作；未包含 `/fork`、`/clone`、`/resume` 和 `/compact`。

---

### 案例 005：Pi Skill 创建与只读审查

> [!note] 实践信息
> - **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
> - **状态：** 【本机已验证】创建、内容核对、重新加载与一次只读审查调用（据用户提供记录与截图）。
> - **记录来源：** 创建与重新加载过程依据用户提供的 AI 对话摘要，实际审查结果依据截图；整理时未重新运行程序或独立核查文件变更。

**创建与审查时的位置：** `D:\demo\python-practice\.pi\skills\python-review\SKILL.md`。据提供记录，当时会话工作目录为 `D:\demo\python-practice`。

**后续迁移：** 据用户补充记录，`python-review` 已迁移至 `D:\demo\pi-sandbox\.pi\skills\python-review\SKILL.md`。下列审查结果仍对应迁移前的 `python-practice/test1.py`。

**操作与结果（据提供记录）：**

1. 创建项目级 `python-review` Skill，填写 `name`、`description` 和 Python 审查流程。
2. 使用 `read` 重新读取并核对文件内容。
3. 使用 `/reload` 重新加载 Skill（据后续补充记录）。
4. 成功触发 `python-review`，Pi 显示 `[skill] python-review` 提示。
5. 指定 `test1.py` 后，截图显示 Pi 使用 `read` 读取 `D:/demo/python-practice/test1.py`，随后输出只读代码审查结果。

**实际审查结果（据截图）：**

| 检查项 | Pi 返回的结果 |
| --- | --- |
| 作用域与基本逻辑 | 未发现明确错误；两处 `nonlocal count` 均指向 `fun1()` 中的 `count` |
| 输出组织 | 使用“发现的问题、对应代码位置、改进建议”三列表格，列出当时文件的行号 |
| 可读性建议 | 非作用域教学场景下，可简化被覆盖的赋值与嵌套结构，改善函数命名和空行 |
| 导入行为 | 顶层调用 `fun1()` 会在模块被导入时触发打印；若仅希望直接运行时调用，可加主模块入口保护 |
| 异常处理 | 未看到需要专门捕获的业务异常，不建议额外添加宽泛的 `try/except` |
| 不确定之处 | 未提供预期行为；若用于演示嵌套作用域，当前结构合理 |

> [!important] 静态分析与运行验证的边界
> 截图中的“预计打印 `14`”来自静态分析；Pi 明确说明本次未运行程序、未修改文件。这符合 Skill 的只读审查要求，但不是本次实际执行 Python 得到的输出；文件变更范围未另外通过 diff 核查。

**可复用经验：** 项目级 Skill 的实际位置取决于项目目录，应先核对工作目录。除技能名称提示外，还应检查实际读取的文件和最终输出；本次结果体现了指定的审查范围、三列格式与不确定性说明。风格建议需结合练习目的判断，不应全部当作必须修复的 Bug。

通用创建与调用方法见[工具手册 5.7 节](../Agent工具使用手册.md#57-pi-skills创建加载与管理)。

---

### 案例 006：Pi 自定义命令 hello-agent

> [!note] 实践信息
> - **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
> - **状态：** 【本机已验证】文件创建、内容核对、加载与自定义命令运行成功（据用户提供结果）。
> - **记录来源：** 用户提供的 AI 对话说明与运行结果；整理时未独立重跑扩展命令。

**文件位置：** `D:\demo\pi-sandbox\.pi\extensions\hello-agent.ts`。

**实际过程（据提供记录）：**

1. 创建 `.pi/extensions/hello-agent.ts`，并通过 `read` 核对内容。
2. 使用 `pi.registerCommand("hello-agent", ...)` 注册命令，处理函数调用 `ctx.ui.notify()`。
3. 执行 `/reload` 加载扩展，再执行 `/hello-agent`。
4. Pi 显示 `Hello from Pi Extension!`，与预期通知一致。

**可复用经验：** 项目级 Extension 能通过代码新增交互命令。本例由用户触发处理函数后直接显示通知，区别于模型选择工具再由运行时执行的工具调用。

完整代码与通用操作见[工具手册 5.8 节](../Agent工具使用手册.md#58-pi-extensions自定义交互命令)。

状态查询与模型工具调用的后续验证结果分别见下方 `my-status`、`greet_user` 记录。

---

### 案例 007：Pi 状态查询 my-status

> [!note] 实践信息
> - **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
> - **状态：** 【本机已验证】自定义状态命令运行成功（据用户提供结果）。
> - **记录来源：** 用户提供的 AI 对话与输出说明；整理时未独立重跑命令。

**文件位置：** `D:\demo\pi-sandbox\.pi\extensions\my-status.ts`。

**操作：** 通过 `pi.registerCommand()` 注册 `/my-status`，处理函数读取工作目录、模型与会话条目数量，再用 `ctx.ui.notify()` 显示；执行 `/reload` 后调用命令。

**该次输出快照：**

```text
当前工作目录：D:\demo\pi-sandbox
当前模型：openai-codex/gpt-6.1-sol
会话记录数量：38
```

**可复用经验：** 状态查询可由 Extension 的处理函数直接完成，无需模型先决定调用工具。`38` 是当时 `getEntries().length` 的结果，不代表 38 轮对话，也不应据此推断当前活动分支的消息数量。

通用实现见[工具手册 5.8 节](../Agent工具使用手册.md#58-pi-extensions自定义交互命令)，模型可调用工具的验证结果见下一条记录。

---

### 案例 008：Pi 自定义工具 greet_user

> [!note] 实践信息
> - **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
> - **状态：** 【本机已验证】工具创建、加载与真实调用成功（据用户提供执行记录）。
> - **记录来源：** 用户提供的 AI 对话与调用结果；整理时未独立重跑。

**文件位置：** `D:\demo\pi-sandbox\.pi\extensions\greet-tool.ts`。

**实际过程（据提供记录）：**

1. 使用 `pi.registerTool()` 注册 `greet_user`，通过 `parameters` 定义字符串参数 `name`，由 `execute()` 返回问候文本。
2. 创建并加载扩展后，用自然语言明确请求调用 `greet_user`，设置 `name` 为 `Alice`，并依据真实返回结果回复。
3. 观察工具调用、工具结果和模型最终回复：

```text
工具调用：greet_user name="Alice"
工具返回：Hello, Alice!
模型回复：Hello, Alice!
```

**可复用经验：** 与 `/hello-agent`、`/my-status` 的交互命令不同，本次由模型发出结构化调用，Pi 执行扩展实现，再把结果送回模型，形成一轮自定义 Agent Loop。参数 Schema、执行函数和结果内容共同构成可调用工具。

> [!important] 验证边界
> 本次是在用户明确指定工具与参数的条件下完成简单文本调用，不能据此认定模型在任意自然语言任务下都会自动选对工具；复杂参数、外部 API、错误恢复与权限控制尚未验证。

完整代码见[工具手册 5.9 节](../Agent工具使用手册.md#59-pi-extensions注册模型可调用的工具)，执行分工见[原理笔记 2.2 节](../Agent原理与开发.md#22-pi-extension注册模型可调用的自定义工具)。

---

## 四、DeepSeek Harness（DSH）

### 案例 009：DSH 全局安装与 Web UI 启动

> [!note] 实践信息
> - **日期与环境** 2026-11-06 · Windows PowerShell
> - **验证状态** 全局安装、CLI 版本、Web UI 启动与 DeepSeek 模型基础对话已验证；文件操作、工具调用与执行轨迹待验证。
> - **记录来源** 用户提供的安装结果、终端输出摘要与对话说明；未附截图或完整原始日志。

**安装与版本核对**

```powershell
npm install -g @deepseek-ai/dsh@latest
dsh --version
```

据提供记录，npm 报告安装了 652 个包，`dsh --version` 返回 `0.2.2-rc.1`。

| 安装提示 | 本次观察 |
| --- | --- |
| `node-domexception` 废弃提示 | 安装完成并能查询 CLI 版本 |
| `npm warn install-scripts` | 5 个依赖的安装脚本未获准执行，其中包括 `node-pty`、`koffi` 和 `@deepseek-ai/dsh-subprocess-local` |

**启动 Web UI（2026-11-06）**

环境：Windows PowerShell；工作目录 `D:\demo\dsh-sandbox`；DSH `0.2.2-rc.1`。

```powershell
dsh web
```

| 检查项 | 实际结果 |
| --- | --- |
| Web 服务 | 启动成功 |
| 监听地址 | `http://127.0.0.1:3080`（以终端实际输出为准） |
| 浏览器 | 已发出自动打开指令；页面实际内容未核对 |
| 模型列表 | 从 DeepSeek API 获取到 2 个模型 |

> [!important] 服务启动、页面可用与模型调用是三个环节
> 模型列表加载成功不代表认证通过或对话可正常调用；页面是否正常渲染、能否成功选择工作区，仍需分别验证。

> [!warning] 启动地址包含访问令牌
> 终端输出的启动链接带有 `token=` 参数，属于本机 Web UI 的访问凭据；分享日志或截图前应遮盖。

**模型连接测试（2026-11-06）**

依据用户转述的界面结果与对话摘要，未直接查看截图。

| 检查项 | 实际结果 |
| --- | --- |
| Web UI | 正常打开，界面显示工作区 `dsh-sandbox` |
| 模型选择 | 标准模式下选择 DeepSeek 模型 |
| 测试消息 | 不调用工具的简单消息 |
| 返回内容 | `DSH 模型连接成功。` |
| 耗时 | 约 1 秒（据界面显示） |
| 工具调用 | 截图未显示，尚未确认 |

> [!note] 「轨迹」标签
> Web UI 中可见「轨迹」入口，用于查看工具调用与执行过程；本次未核对其内容，DSH 的工具执行机制仍待观察。

**尚未验证：** 工作区文件读取与修改、实际工具调用、执行轨迹内容、插件体系与权限机制。

**下一步：** 后续只读检查与工具轨迹见[案例 010](./Agent实践记录.md#案例-010dsh-首次工作区只读检查与工具轨迹)；本次基础对话未核对工具轨迹。操作步骤见[工具手册 6.2 节](../Agent工具使用手册.md#62-dsh-web-ui-第一次应该怎样用)。

---

### 案例 010：DSH 首次工作区只读检查与工具轨迹

> [!note] 实践信息
> - **日期 / 工具**：2026-11-06 · DSH 0.2.2-rc.1
> - **环境**：Windows PowerShell；Web UI 权限模式「仅可查看」
> - **状态**：据用户提供的轨迹截图说明，目录读取与轨迹观察完成；整理时未直接查看截图。
> - **记录来源**：用户转述的界面结果与轨迹解读，未附原始日志。

**任务与边界**

在工作区 `D:\demo\dsh-sandbox` 中读取工作区路径、列出根目录内容；不创建、修改或删除文件，不安装依赖、不联网。

**观察到的工具执行链**

| 顺序 | 工具 | 观察结果 |
| --- | --- | --- |
| 1 | `working_directory` | 返回 `D:\demo\dsh-sandbox` |
| 2 | `pwsh` | `Get-ChildItem` 报 `InvalidOperation` |
| 3 | `pwsh` | 检查环境信息时仍有报错 |
| 4 | `pwsh` | `Test-Path` 返回 `True`，同时伴随错误 |
| 5 | `pwsh` | 改用 `cmd /c dir` 检查目录 |
| 6 | `pwsh` | 再次尝试统计目录项目数量 |

最终 DSH 报告根目录为空，并称未进行文件修改。

**实际发现**

1. 「轨迹」能显示工具名称、调用参数摘要与执行结果，可用于核对真实执行，而不只看最终回复。
2. PowerShell 报错后，Agent 改用 `cmd /c dir` 检查目录，最终报告根目录为空；未摘录该命令的返回内容，失败根因也尚未确认。
3. PowerShell 错误伴随中文乱码，`InvalidOperation` 不能仅凭截图归因于受限语言模式。
4. 可见调用均围绕工作区，但未展开完整参数逐项审计，不能严格证明没有工作区外访问。
5. 界面显示本次用量约 64.5K Tokens，不能直接等同于新增输入 Token，需结合缓存与调用明细判断。

> [!important] 最终回复与执行记录是两回事
> “未修改文件”来自 Agent 自述；只读结论应由轨迹与文件系统状态共同支持。

**未验证**

- 展开后的完整参数，以及是否存在工作区外访问。
- PowerShell 报错的根因与乱码修复。
- 插件的安装、启用、禁用与开发。
- 工具服务与插件之间的具体注册关系（需核对对应版本官方文档）。

**可复用经验**

- 只读实验也要打开「轨迹」核对工具名、参数和结果，不能只凭总结判断。
- 环境命令报错时，换用等价命令先行验证可以推进任务，但根因仍需单独排查。

工具、模型与运行时的通用分工见[原理笔记第 2 节](../Agent原理与开发.md#2-把系统拆成五个部分)。

---

## 五、跨 Agent 对比

### 案例 011：Codex、Pi、DSH 跨 Agent 代码审查对比

> [!note] 实践信息
> - **日期 / 工具**：2026-11-07 · Codex CLI `0.166.0`、Pi `1.5.0`、DSH `0.2.2-rc.1`
> - **环境**：Windows PowerShell；工作目录 `D:\demo\dsh-sandbox`
> - **状态**：三款 Agent 均完成任务；记录依据用户提供的界面与终端结果整理，未直接查看原始截图。
> - **记录来源**：用户转述的审查结论、工具调用与用量；Token 只记录到 Codex。

**1. 目的与统一条件**

比较三款 Agent 在同一只读审查任务中的准确性、工具调用、只读遵守情况与稳定性。统一要求：读取 `compare_scores.py`，指出违反业务要求的问题，按「问题位置、原因、修复建议」回复；不修改文件、不运行程序、不读取其他项目文件、不联网。

**2. 测试代码与业务要求**

```python
def average_score(scores):
    total = 0
    count = 0

    for score in scores:
        if score:
            total += score
            count += 1

    return total / count


if __name__ == "__main__":
    print(average_score([0, 80, 100]))
    print(average_score([]))
```

- 计算所有成绩的平均分；
- `0` 是合法成绩，必须参与计算；
- 空列表返回 `None`，不应抛出异常。

**3. 预设问题**

1. `if score:` 使用真值判断，`0` 被跳过。`[0, 80, 100]` 会得到 `90`（80 与 100 的平均），正确结果为 `60`。
2. 空列表时 `count == 0`，`total / count` 抛 `ZeroDivisionError`，没有返回 `None`。

参考修复：

```python
def average_score(scores):
    if not scores:
        return None
    return sum(scores) / len(scores)
```

**4. 对比结果**

| 对比项目 | Codex CLI | Pi | DSH |
| --- | --- | --- | --- |
| 读取目标文件 | 成功 | 成功（`read`） | 成功（`read`） |
| 零分被跳过 | 正确识别 | 正确识别 | 正确识别 |
| 空列表除零 | 正确识别 | 正确识别 | 正确识别 |
| 修复建议 | 正确，给出简洁完整实现 | 正确，给出最小修改 | 正确，给出两种实现 |
| 可见文件修改 | 无 | 无 | 无 |
| Token 用量 | 9,959 | 未记录 | 未记录 |
| 本轮异常 | 网络超时与重连 | 登录时曾 `fetch failed` | 无（沿用旧会话） |

**5. 各工具的实际过程**

**Codex CLI**：以 `codex exec --sandbox read-only` 完成，通过终端命令读取文件，正确定位两个问题并给出完整替代实现。执行期间记录到工作区路由超时与重连。该轮报告 9,959 Tokens，缺少逐次请求的用量明细。

**Pi 1.5.0**：一次 `read compare_scores.py` 完成审查，问题定位准确，按最小改动给出修复；未观察到写入或运行程序。登录阶段曾出现 `fetch failed`，随后恢复。Token 用量未记录。

**DSH 0.2.2-rc.1**：标准模式、只读权限，轨迹显示一次 `read` 调用，回答最详细，并补充了 `[0]`、`[0, 0]` 等边界输入的影响。本轮沿用了包含插件开发内容的旧会话，并非独立新会话。

> [!important] 本轮对比能说明什么
> 能说明三款工具在基础只读审查上都可完成任务；不能据此比较 Token 效率或速度，也不能证明文件系统隔离能力。DSH 本次 `read` 成功，不代表此前的 `pwsh` 沙箱 `Win32 5` 已修复。

**6. 结论**

- **准确性**：三者均命中两个预设问题，本次未见准确率差异。
- **工具路径**：Codex 通过终端命令读取，Pi 与 DSH 使用 `read` 工具；差异与各自工具集和配置有关。
- **安全性**：可见记录符合只读要求，但单次运行不足以证明隔离完整。
- **效率**：仅 Codex 有数值且含重连，数据不足，不做排名。
- **本轮故障**：Codex 出现超时和重连，Pi 曾遇到登录错误，DSH 沿用旧会话完成审查。

**7. 选型倾向**

| 工具 | 优先用途 |
| --- | --- |
| Codex CLI | 真实项目的代码开发、修复、审查与测试 |
| Pi | 轻量任务、自定义 Skill / Extension、Agent 工作流实验 |
| DSH | 插件化架构、Cordis、多 Agent 与工具系统研究 |

以上基于工具定位、已有实践与个人学习方向，不是单次实验的能力排名。

**8. 可复用经验**

1. 结论要结合工具执行记录核对，不能只看最终回答。
2. 工作区、提示词约束与操作系统权限是三个层次。
3. 同一任务下不同 Agent 可能选择不同工具路径。
4. 网络与登录故障会影响体验，但不能直接归因于模型能力。
5. 评价 Agent 时，区分模型能力、Agent 框架能力与运行环境。

**本案例结论：三款 Agent 的基础只读审查均通过，跨 Agent 对比实践完成。**

---

### 案例 012：Agent Benchmark V2 复杂 LLM 客户端修复对比

> [!note] 实践信息
> - **日期 / 工具**：2026-11-07 · Codex CLI `0.166.0`、Pi `1.5.0`、DSH `0.2.2-rc.1`、TRAE + DeepSeek API
> - **状态**：四组代码均完成独立评分（用户在本机执行评分器）；结果据其提供的输出整理，未直接查看原始日志。
> - **记录来源**：用户转述的成绩、执行情况与界面统计；Token 方面 Codex、Pi、DSH 有数据，TRAE 缺失，费用仅 Pi 有估算值。

**1. 任务与统一条件**

四组使用同一套初始代码，各自在独立目录中修复 `chat_client.py`。任务覆盖 HTTP `429` / `503` 重试、指数退避与 `Retry-After`、请求 ID 幂等、SSE 分片与完整事件解析、消息事务性提交与失败回滚、深拷贝隔离、上下文裁剪及输入检查。统一限制：不改公开测试、不硬编码答案、不联网安装、不查看评分包。

**2. 评分方式与结果**

6 项公开测试 + 17 项额外边界测试，共 23 项。

| Agent | 公开测试 | 额外测试 | 总分 |
| --- | --- | --- | --- |
| Codex CLI | 6/6 | 17/17 | 100 |
| Pi Coding Agent | 6/6 | 16/17 | 96 |
| DSH | 6/6 | 17/17 | 100 |
| TRAE + DeepSeek API | 6/6 | 17/17 | 100 |

**3. Pi 的失败项**

失败测试：`test_stream_iteration_error_rolls_back`。

流式读取中途抛出 `TransportError("stream dropped")` 时，Pi 将其包装为：

```python
raise ProtocolError("bad or interrupted event stream") from exc
```

测试期望保留 `TransportError`，实际得到 `ProtocolError`。异常类型改变后，上层若按网络故障或协议错误分支处理，会进入错误路径。

> [!note] 捕获不等于处理正确
> 能捕获异常、能回滚会话，与"保留接口契约要求的异常类型"是两件事；公开测试通过不代表这一层对了。

**4. 执行过程与环境**

**Codex CLI**：完成修改，公开 6/6、总分 23/23；报告 35,433 Tokens；期间出现网络超时与重连，执行体验受影响。

**Pi 1.5.0**：完成修改，公开 6/6、总分 22/23；仅流式异常类型一项失败。Token 和耗时见下方补录表。

**DSH 0.2.2-rc.1**：完成修改；自身 `pwsh` 因 `SetNamedSecurityInfoW failed (Win32 5)` 无法执行测试，未擅自提权；由用户在普通 PowerShell 中独立评分，公开 6/6、总分 23/23。沙箱问题仍未修复。

**TRAE + DeepSeek API**：完成修改，公开 6/6、总分 23/23；自述补充检查过 17 项边界行为；Token 与费用未记录。此前存在越界读取关注点，本次行为控制需与代码能力分开评价。

> [!important] 代码正确性与自主执行能力分开记
> DSH 的 23/23 来自普通 PowerShell 的独立评分，不代表 DSH 能自行运行测试；"写对代码"与"能自主验证"是两个维度。

**5. 结论**

- **代码正确性**：Codex、DSH、TRAE 并列满分，Pi 因异常契约差一项；本次未出现明显能力断层。
- **工程执行**：Codex、Pi、TRAE 自主运行了公开测试；DSH 受 Windows 沙箱阻断。
- **本轮运行情况**：Codex 出现超时和重连，Pi 无明显运行阻断，TRAE 同期运行多个任务，DSH 的测试执行受 Windows 沙箱阻断。
- **选型**：Codex 适合日常编码与项目修改；Pi 适合轻量任务、Skill / Extension 与工作流实验；DSH 适合插件架构与 Agent 系统研究，使用前需解决沙箱问题；TRAE + DeepSeek 在本次实际修复中表现良好，可作为日常候选，但需继续观察 Token 消耗与文件访问控制。

**6. 资源与耗时（补录）**

| Agent | 正确性 | Token | 耗时 | 实验条件 |
| --- | --- | --- | --- | --- |
| Codex CLI | 100 | 35,433 | 未记录 | 曾发生网络超时与重连 |
| Pi | 96 | 42,776（缓存 28,928；非缓存输入 10,727；输出 3,121） | 94.4 秒 | 会话时间戳计算，暂未发现并发干扰 |
| DSH | 100 | 271,454（缓存读取 228,992；非缓存输入 9,691；输出 32,771） | 约 185 秒 | 轨迹推算的下限，含 `Win32 5` 排查 |
| TRAE + DeepSeek | 100 | 未记录 | 258 秒（4 分 18 秒） | 界面显示；同期运行多个 TRAE 任务 |

- Pi 显示的 `$0.056` 是工具估算。Codex 使用订阅，本次任务费用未单独记录。DSH、TRAE 的费用未记录。
- 三组耗时来源不同（会话时间戳、轨迹推算、界面计时），且 DSH 含故障排查、TRAE 存在并发任务，**不能据此排速度名次**。
- Token 统计口径也不同：缓存读取的计价通常低于非缓存输入，总量不能直接换算成成本。

> [!warning] 并发会污染耗时与费用
> TRAE 测试期间同时运行多个任务，可能受网络、CPU 与服务端并发限制影响；共享同一 API Key 时，平台累计 Token 与费用也不能全部归给本次 Benchmark。

**7. 局限**

- 单文件 Python 任务，未覆盖多文件工程、并发与集成测试。
- 四组模型与运行条件未完全统一，成绩代表"Agent + 模型 + 环境"的组合。
- Codex、Pi、DSH 有 Token 数据，统计口径有差异。只有 Pi 有单任务费用估算。TRAE 的计时与其他任务重叠，单任务耗时待独立测量。
- 若比较执行效率，应让各工具在无其他任务竞争、统一模型配置下单独运行，并记录单任务 Token、耗时与费用；不要用本轮数据强行排名。
- 后续若继续比较代码能力，优先使用多文件 Java / Spring Boot 项目与集成测试，不必无限增加模拟题。

**本次测试结果**：Codex、DSH、TRAE 均通过 23 项，Pi 通过 22 项，唯一失败项涉及流式读取时的异常类型。

---

