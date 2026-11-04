# Agent 工具使用手册

> **定位**：日常速查手册。只保留「如何安装、如何操作、怎样安全使用」等可复用信息，不记录每次聊天。
>
> **适用环境**：Windows + PowerShell / Windows Terminal；必要时使用 WSL2（Ubuntu）。
>
> **更新日期**：2026-11-04。官方功能与命令可能变化，安装前优先查阅文末官方资料。
>
> **状态说明**：`[官方已核对]` 表示根据官方公开文档确认；`[本机待验证]` 表示尚未在自己的电脑上执行；`[经验建议]` 是可采用的工作习惯，不代表工具的硬性要求。

## 1. 总览：选择工具，而不是收集工具

| 工具 | 主要定位 | 我的使用目标 | 当前记录状态 |
| --- | --- | --- | --- |
| Codex 桌面版 | 可视化的日常编程辅助 | 项目理解、实现、审查与测试 | 根据实际使用逐步补充 |
| Codex CLI | 终端中的编程 Agent | 结合 Git、Shell、Maven 完成工程任务 | 安装与首用待本机验证 |
| Pi | 可扩展的终端 Agent | 观察工具调用、Agent Loop 和扩展 | 待体验 |
| DSH（DeepSeek Harness） | 插件化 Agent 运行环境 | 观察插件组合、Agent 运行机制 | 待体验 |
| OpenCode | 多模型编程 Agent（选修） | 对比不同 Agent 的开发流程 | 暂不安排 |

**当前优先级**：继续使用 Codex → 体验 Codex CLI → 体验 Pi → 按需研究 DSH。不要为了测试工具而改变后端与 AI 的主线学习计划。

### 终端、Shell、WSL 与 Agent 的关系

- **Windows Terminal**：终端窗口，可在标签页中打开不同 Shell。
- **PowerShell 7**：Windows 命令行 Shell，适合操作 Windows 下的项目。
- **WSL2**：Linux 运行环境，适合 Linux 原生工具与后续容器化实验。
- **Codex CLI / Pi**：运行在所选环境中的 Agent 程序，并不是新的 Shell。

**[经验建议]**：如果项目实际存放在 `D:\...` 并由 Windows IDEA 管理，就先在 PowerShell 中启动 Codex。项目迁入 WSL 的 Linux 文件系统后，再考虑在 WSL 内单独安装。Windows 与 WSL 的工具安装、路径和环境变量通常应分别管理。

## 2. 使用 Agent 前的安全基线

1. **明确范围**：告诉 Agent 可以读取哪些目录、是否允许修改文件、是否允许执行命令。
2. **先审查再修改**：不确定的任务先使用分析模式；对重要修改先要求它给出方案。
3. **保留版本控制**：操作前运行 `git status`，重要任务在独立分支或工作树中进行；不在未保存的改动上盲目运行自动编辑。
4. **不暴露秘密**：不要发送 `.env`、API Key、Token、数据库密码、私有密钥、个人隐私资料。
5. **谨慎授权**：删除、批量覆盖、联网下载或执行陌生脚本、数据库写入与部署命令都要单独审查。
6. **验证输出**：Agent 回答不等于事实；必须结合代码、Git diff、测试、日志判断。
7. **最小隔离**：首次体验扩展性强或执行命令不逐次审批的 Agent，尽量使用独立测试目录、低权限账户、容器或虚拟机，并避免共享真实凭据。

> 提醒：文字上的“不要修改文件”属于任务约束，**不能替代**沙箱、只读文件系统、操作系统权限或工具本身的授权机制。

## 3. Codex CLI

### 3.1 安装与启动（[官方已核对]；本机待验证）

官方项目：[openai/codex](https://github.com/openai/codex)；[Codex CLI 文档](https://learn.chatgpt.com/docs/codex/cli)；[Windows 沙箱说明](https://learn.chatgpt.com/docs/windows/windows-sandbox)。

在 **Windows PowerShell** 中：

```powershell
# 前提：已安装 Node.js 与 npm
node --version
npm --version

# 官方支持的 npm 安装方式
npm install -g @openai/codex

# 检查可执行文件
codex --version
```

首次进入已有项目后执行：

```powershell
cd D:\LearningNotes

git status
codex
```

首次运行时按照终端提示登录。`D:\LearningNotes` 是示例项目路径，进入其他项目时请替换。

**安全起步任务（可复制给 Agent）**：

```text
请只分析当前仓库的目录结构和 README，说明主要模块之间的关系。
不要修改文件，也不要运行会改变文件或环境状态的命令。
如果需要额外权限，先说明原因并等待我的决定。
对于每个重要结论，给出对应文件路径。
```

常用交互入口（以实际版本为准）：

| 用法 | 目的 |
| --- | --- |
| `codex` | 在当前目录启动交互会话 |
| `/status` | 查看当前会话/权限状态 |
| `/review` | 审查修改，寻找潜在问题 |
| `codex --help` | 查看当前安装版本的完整命令和参数 |

**权限注意**：Windows 原生 Codex 有沙箱与审批机制；能执行到什么程度取决于当前配置。不要为省事直接开启不受限制的执行权限。需要确认实际状态时，先查看 `/status`。

### 3.2 第一次实际体验的验证记录（[本机待验证]）

- [ ] `node --version` / `npm --version` 正常
- [ ] `codex --version` 正常
- [ ] 已确认当前工作目录
- [ ] 已确认授权和沙箱设置
- [ ] 完成一次**只读**代码分析
- [ ] 使用 `git status` 确认没有意外修改

**本机安装版本 / 日期**：待填。  
**遇到的问题与解决办法**：待实际发生时再填。

## 4. Pi

### 4.1 安装与启动（[官方已核对]；本机待验证）

官方：[Pi 官网](https://pi.dev/) · [Quickstart](https://pi.dev/docs/latest/quickstart) · [安全说明](https://pi.dev/docs/latest/security)

截至 2026-11-04，官网提供以下 npm 安装方式，要求 **Node.js 22.19 或更新版本**：

```powershell
node --version
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi
```

也可以根据官方 Quickstart 选择平台安装器。首次启动需配置受支持的模型提供方；可按界面引导使用 `/login` 等方式完成认证。**不要把密钥直接写进笔记、截图或 Git 仓库。**

> 特别注意：网上有旧教程使用不同的 Pi npm 包名，安装前以当前 `pi.dev` 官方文档为准。

### 4.2 初体验观察点

先在**无真实数据、无生产密钥的隔离测试目录**中体验：

1. Agent 获取用户目标后做了什么？
2. 使用了哪些工具？如读取文件、执行命令、编辑文件。
3. 工具返回后，Agent 如何决定下一步？
4. 出现失败时，它会重试、换方法还是停止？
5. 对话消息、上下文和文件修改分别在哪里体现？

**安全提醒（[官方已核对]）**：Pi 默认并非每次工具调用都要求用户审批，它可以使用当前启动账户拥有的文件与进程权限。仅靠提示词限制“只读”并不可靠；应采用真正的隔离与权限限制。

### 4.3 扩展机制（先理解，不急于实作）

- **Extensions**：通过代码增加工具、命令或其他行为。
- **Skills**：向 Agent 提供可复用的任务能力说明。
- **Prompt templates**：复用常见任务提示词。
- **Pi packages**：打包和分发扩展、Skills、模板等资源。

参考：[Pi 文档首页](https://pi.dev/docs/latest) · [Packages](https://pi.dev/docs/latest/packages)。

**本机验证情况**：待安装、待记录。

## 5. DeepSeek Harness（DSH）

### 5.1 定位与启动入口（[官方已核对]；本机待验证）

官方：[DeepSeek Harness](https://www.deepseek.com/harness/en/) · [源代码](https://github.com/deepseek-ai/deepseek-harness)。

DSH 采用 Cordis 的插件化架构，提供桌面端，也支持从命令启动 Web UI。官方给出的 Web UI 入口如下（先确认 Node.js 已安装）：

```powershell
npx @deepseek-ai/dsh web
```

`npx` 可能按需下载并运行依赖，因此初次执行前应确认来源及风险。DSH 仍在预览阶段，插件接口和配置可能迭代。

### 5.2 初体验关注点

- 核心功能如何由插件组合而成？
- 工具、技能、界面插件分别承担什么职责？
- Agent 在哪里调用插件、获取结果、继续执行？
- 插件如何获取权限？对文件、网络和命令的影响是什么？

以后研究源码时，再参考[官方插件入门](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/index.md)。当前不要求编写插件。

**本机验证情况**：待安装、待记录。

## 6. 通用故障速查

| 现象 | 优先检查 | 记录方式 |
| --- | --- | --- |
| `codex` / `pi` 找不到命令 | 是否安装成功、终端是否重启、npm 全局可执行文件是否在 PATH | 记下环境和最终修复办法 |
| 登录或模型调用失败 | 使用的登录方式、模型权限、网络连接、余额或限额 | **不记录完整密钥和敏感日志** |
| 命令与教程不一致 | 工具版本、官方更新日期、是否混用了旧包名 | 标注文档版本与查询日期 |
| Agent 改动超出范围 | 立刻停止，检查 `git status` / `git diff` | 写入工作流复盘，记录边界失效原因 |
| Windows 和 WSL 行为不同 | 所在 Shell、文件系统路径、各自的安装版本与变量 | 说明 Windows/WSL 环境，不混写 |

### Git 最小核查命令

```powershell
git status
git diff
git diff --check
```

`git diff` 默认主要查看未暂存的改动；如已暂存，另用 `git diff --cached`。不熟悉改动来源时不要盲目执行 `git reset --hard`、`git clean -fd` 等不可逆清理命令。

## 7. 如何维护这份手册

只在发生以下情况时更新：

- 某工具首次**真实安装成功**：补版本、环境、安装步骤和踩坑。
- 学会一种反复用到的命令/配置：补入对应小节。
- 官方升级导致命令失效：修正文档并标注时间。
- 发现与具体任务相关的高价值操作方法：放到 [Agent工作流与实践.md](./Agent工作流与实践.md)，避免重复。

**不记录**：每次普通问答、完整会话流水账、没有验证过的“神奇参数”、未经筛选的大量提示词。

## 8. 资料来源（官方，2026-11-04 核对）

- [OpenAI Codex GitHub / 安装说明](https://github.com/openai/codex)
- [Codex CLI 指南](https://learn.chatgpt.com/docs/codex/cli)
- [Codex Windows Sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [Pi 官方 Quickstart](https://pi.dev/docs/latest/quickstart)
- [Pi 官方安全说明](https://pi.dev/docs/latest/security)
- [Pi Packages 文档](https://pi.dev/docs/latest/packages)
- [DeepSeek Harness 官网](https://www.deepseek.com/harness/en/)
- [DSH 官方仓库](https://github.com/deepseek-ai/deepseek-harness)
