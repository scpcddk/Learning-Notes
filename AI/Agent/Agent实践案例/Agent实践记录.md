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

### 2026-11-04｜npm 全局目录缺失

- **报错：** `ENOENT: no such file or directory, lstat 'C:\Users\Lenovo\AppData\Roaming\npm'`。
- **处理：** 执行下列命令创建目录并重新查询：

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\npm"
npm list -g --depth=0
```

- **结果：** 原报错解除，列表显示 `(empty)`；这是安装 Codex 前的记录。

### 2026-11-04｜Codex 在错误工作目录启动

- **现象：** 交互界面底部显示 `~\Desktop`。
- **处理：** 退出，进入 `~\codex-test` 后重新启动。
- **结果：** `/status` 确认工作目录正确，权限为 `Read Only (Ask for approval)`。

### 2026-11-06｜DSH Windows 沙箱授权失败（待修复）

- **报错：**

```text
SetNamedSecurityInfoW failed (Win32 5):
grantWrite(D:\demo\dsh-sandbox)
```

- **发生阶段：** DSH 为工作区设置 Windows 文件访问权限时失败，尚未进入命令执行阶段。
- **影响范围：** `pwsh` 工具可能无法执行命令、运行测试或修改文件；Web UI、模型对话、工作区读取仍可用。
- **未确定：** 是目录 ACL、沙箱实现还是版本兼容性导致；用户账户能正常写目录，不代表沙箱初始化所需的权限齐全。
- **当前处理：** 保持原有权限模式，不切换「完全权限」、不递归修改 ACL；语法与配置检查改在普通 PowerShell 中完成。
- **只读排查入口：** `icacls "D:\demo\dsh-sandbox"`，用于查看实际 ACL，不修改权限。
- **记录来源：** 用户提供的报错与转述；社区类似案例的成因说法尚未核实，不能当作本次结论。

> [!warning] 普通 PowerShell 能运行不等于沙箱可用
> `node --check` 在普通 PowerShell 中成功，只能说明源码语法可由 Node 解析；它与 DSH 沙箱能否启动子进程是两条独立的验证路径。

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

