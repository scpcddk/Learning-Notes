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
| DSH 安装版本 | 尚无安装成功输出 | 待实践 |

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

**后续：** 会话保存、恢复与上下文管理；已有文件修改、Extensions / Skills 及与 Codex 的差异仍待实践。

### 会话信息观察：`/session`

- **日期 / 工具：** 2026-11-05 · Pi Coding Agent 1.5.0。
- **操作与结果：** 据用户提供的 AI 对话摘要，执行 `/session` 后看到 `.jsonl` 会话文件、21 条消息、5 次工具调用及 5 次工具结果返回；整理时未独立复核。
- **可复用结论：** 可通过 `/session` 核对会话信息；消息和调用数量是该次观察的快照，不是固定值。
- **边界：** 仅记录会话信息查看；`/tree`、`/fork`、`/clone`、恢复与压缩仍待实践，不能据此认定已掌握分支或上下文管理。

---

## 四、DeepSeek Harness（DSH）

---

