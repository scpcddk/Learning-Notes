# Agent 实践记录

---

## 一、Codex CLI

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

## 二、Pi Coding Agent

---

## 三、DeepSeek Harness（DSH）

---
