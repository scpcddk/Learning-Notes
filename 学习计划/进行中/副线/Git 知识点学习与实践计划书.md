# Git 知识点学习与实践计划书

**学习方式：项目穿插学习 + 遇到问题专项补弱 + 阶段性检查**

### 使用规则

- 每个 `- [ ]` 代表一个独立的知识点或实践能力。
- 学习并理解一个知识点后，将其改为 `- [x]`。
- 之前已经学过的知识点，可以回顾确认后直接勾选。
- 操作类知识点建议至少亲手实践一次；危险操作在测试仓库中练习。
- 不要求按照章节顺序学习，不设固定完成期限。
- **【核心】** 优先掌握；**【按需】** 遇到再学；**【进阶】** 可以长期保留作为扩展方向。

---

# 第一部分：Git 基础与本地版本管理

## 01. Git 基本概念【核心】

- [x] 理解 Git 是分布式版本控制系统，与普通文件备份的区别。
- [x] 区分 Git 和 GitHub / Gitee / GitLab。
- [x] 理解工作区（Working Tree）的作用。
- [x] 理解暂存区（Index / Staging Area）的作用。
- [x] 理解本地仓库和远程仓库的区别。
- [x] 理解 untracked、tracked、modified、staged 等文件状态。
- [x] 理解 `git add`、`git commit`、`git push` 各自的作用。
- [x] 理解 Git 通过提交快照管理版本。
- [x] 理解 commit 包含文件快照、提交说明、作者信息和父提交等信息。
- [x] 掌握先检查状态和差异，再执行修改、提交或恢复操作的安全习惯。

## 02. 安装、环境与配置【核心】

- [x] 使用 `git --version` 检查 Git 安装情况。
- [x] 在 PowerShell / Windows Terminal 中运行 Git，了解 Git Bash 的区别。
- [ ] 理解 Windows Git 与 WSL Ubuntu 中的 Git 可能使用不同配置。
- [x] 使用 `git config --global user.name` 配置用户名。
- [x] 使用 `git config --global user.email` 配置邮箱。
- [ ] 区分 `--system`、`--global`、`--local` 的配置范围和优先级。
- [ ] 使用 `git config --list` 查看配置。
- [ ] 使用 `git config --show-origin --list` 查看配置及来源。
- [ ] 使用 `git config --show-origin --get user.email` 查询指定配置的来源。
- [ ] 设置或识别默认分支名称，例如 `main`。
- [ ] 理解 Git 默认编辑器的作用，能退出并完成提交信息编辑。
- [ ] 理解 CRLF 和 LF 换行符差异，以及 `core.autocrlf` 的用途。
- [ ] 了解 Windows 与 Linux 文件路径、大小写敏感性、空格文件名的区别。

## 03. 仓库创建与初始化【核心】

- [x] 使用 `git init` 初始化已有项目。
- [ ] 使用 `git init -b main` 指定初始分支。
- [ ] 使用 `git clone <URL>` 克隆远程仓库。
- [ ] 使用 `git clone <URL> <目录>` 指定克隆位置。
- [ ] 理解 `.git` 目录的作用。
- [x] 使用 `git status` 判断当前目录是否为 Git 仓库的一部分。
- [x] 使用 `git rev-parse --show-toplevel` 查找仓库根目录。
- [ ] 识别在错误目录执行 Git、误创建嵌套仓库等问题。
- [ ] 区分初始化新仓库与克隆已有仓库的使用场景。

## 04. 工作区状态与代码差异【核心】

- [x] 使用 `git status` 查看文件状态。
- [ ] 使用 `git status -sb` 查看简洁状态及当前分支。
- [x] 使用 `git diff` 查看尚未暂存的修改。
- [x] 使用 `git diff --staged` 查看已经暂存的修改。
- [ ] 使用 `git diff HEAD` 查看相对当前提交的已跟踪文件修改。
- [x] 使用 `git diff --stat` 查看变更统计。
- [ ] 使用 `git diff --name-only` 查看发生变化的文件名称。
- [x] 使用 `git diff -- <文件>` 只查看指定文件的修改。
- [x] 理解 diff 中 `+`、`-`、`@@` 和上下文行的意义。
- [ ] 使用 `git diff --check` 检查空白字符问题。
- [ ] 理解普通 `git diff` 为什么不显示未跟踪的新文件。
- [ ] 养成提交前检查调试代码、临时文件和无关改动的习惯。

## 05. 暂存区与本地提交【核心】

- [x] 使用 `git add <文件>` 暂存指定文件。
- [ ] 使用 `git add <目录>` 暂存目录内的改动。
- [ ] 理解 `git add .` 和 `git add -A` 的作用及路径范围差异。
- [ ] 使用 `git add -p` 选择性暂存部分修改。
- [x] 使用 `git restore --staged <文件>` 取消暂存。
- [x] 理解暂存文件后再次修改时，暂存内容可能不同于工作区内容。
- [x] 使用 `git commit -m "说明"` 创建提交。
- [x] 编写清晰且有实际意义的提交信息。
- [ ] 理解为什么建议一次提交只完成一个相对独立的目的。
- [ ] 使用 `git commit` 通过编辑器编写多行提交说明。
- [ ] 使用 `git log -1` 查看最近一次提交。
- [x] 区分已修改、已暂存和已提交三种状态。
- [ ] 了解空提交 `--allow-empty` 的含义和适用场景。

## 06. .gitignore 与文件管理【核心】

- [x] 理解 `.gitignore` 的作用。
- [ ] 编写指定文件、目录、扩展名的忽略规则。
- [ ] 理解 `/`、`*`、`**`、`!` 等忽略规则符号。
- [ ] 为 Java / Maven 项目配置适当的忽略规则。
- [ ] 为 Python 项目配置适当的忽略规则。
- [x] 识别 `.env`、API Key、数据库密码、私钥等不应提交的敏感文件。
- [x] 理解已经被 Git 跟踪的文件不会因为新增 `.gitignore` 自动停止跟踪。
- [ ] 使用 `git rm --cached <文件>` 停止跟踪但保留本地文件。
- [ ] 使用 `git check-ignore -v <文件>` 查看文件为何被忽略。
- [ ] 使用 `git rm` 删除已跟踪文件。
- [ ] 使用 `git mv` 重命名或移动文件。
- [ ] 理解敏感信息一旦提交到历史记录，仅删除当前文件并不能消除泄漏；应先吊销或轮换凭据。

---

# 第二部分：历史记录与分支管理

## 07. 提交历史查询【核心】

- [x] 使用 `git log` 查看历史记录。
- [x] 使用 `git log --oneline` 查看精简记录。
- [ ] 使用 `git log --graph --decorate --oneline --all` 查看提交图。
- [ ] 使用 `git show <commit>` 查看某次提交。
- [ ] 使用 `git show <commit>:<文件>` 查看特定历史版本的文件。
- [ ] 理解提交哈希和短哈希。
- [ ] 理解 `HEAD`、`HEAD~1`、`HEAD^` 等提交引用。
- [x] 使用 `git log -- <文件>` 查询文件历史。
- [ ] 使用 `git blame <文件>` 查询文件各行最后修改的提交。
- [ ] 使用 `git log --author`、`--since` 等条件筛选。
- [ ] 使用 `git diff <commitA> <commitB>` 比较历史版本。
- [ ] 使用 `git log -S"关键词"` 搜索引入或删除指定文本的提交。

## 08. Git 分支管理【核心】

- [ ] 理解主分支和功能分支的作用。
- [ ] 使用 `git branch` 查看本地分支。
- [ ] 使用 `git branch -a` 查看本地与远程跟踪分支。
- [ ] 使用 `git switch -c <分支>` 创建并切换分支。
- [ ] 使用 `git switch <分支>` 切换已有分支。
- [ ] 了解 `git checkout` 的历史用途及其与 `switch`、`restore` 的关系。
- [ ] 理解未提交修改可能被带到其他分支，或阻止分支切换。
- [ ] 使用 `git branch -m` 重命名分支。
- [ ] 使用 `git branch -d` 删除已合并的本地分支。
- [ ] 理解 `git branch -D` 强制删除分支的风险。
- [ ] 理解 HEAD 和 detached HEAD 状态。
- [ ] 理解分支是指向提交的引用，而不是独立复制整个项目。

## 09. 分支合并与冲突解决【核心】

- [ ] 理解 `git merge` 的功能和合并方向。
- [ ] 使用 `git merge <分支>` 完成普通合并。
- [ ] 区分快进合并（Fast-forward）和三方合并。
- [ ] 理解 merge commit 的含义。
- [x] 理解什么情况下会发生合并冲突。
- [x] 识别 `<<<<<<<`、`=======`、`>>>>>>>` 冲突标记。
- [x] 使用 `git status` 查看存在冲突的文件。
- [ ] 手工编辑文件解决冲突并清除冲突标记。
- [ ] 使用 `git add` 标记冲突已解决，并完成合并。
- [ ] 使用 `git merge --abort` 中止未完成的合并。
- [ ] 理解冲突标记解决后，业务逻辑仍然需要测试。
- [ ] 理解 `ours` 和 `theirs` 在普通合并场景中的含义。
- [ ] 在测试仓库中独立制造并解决一次真实冲突。

---

# 第三部分：远程仓库与协作

## 10. 远程仓库配置与身份认证【核心】

- [x] 理解 `origin` 是远程仓库的常用别名。
- [x] 使用 `git remote -v` 查看远程仓库。
- [ ] 使用 `git remote add origin <URL>` 添加远程仓库。
- [ ] 使用 `git remote set-url origin <URL>` 修改远程地址。
- [ ] 区分 HTTPS 和 SSH 两种远程连接方式。
- [ ] 理解 HTTPS 身份认证中的个人访问令牌（PAT）。
- [ ] 理解 SSH 公钥、私钥的作用及保护要求。
- [ ] 学习生成 SSH 密钥和配置平台公钥。
- [ ] 了解 SSH 首次连接时的主机指纹验证。
- [ ] 区分 Git 本地提交身份与远程平台登录身份。
- [ ] 理解凭据管理器的用途，避免泄漏令牌与私钥。

## 11. Git 远程同步【核心】

- [x] 使用 `git fetch` 获取远程仓库更新。
- [x] 理解 `git pull` 及其由配置决定的合并或变基行为。
- [x] 理解 `git fetch + git merge` 与 `git pull` 的关系。
- [ ] 使用 `git push origin <分支>` 推送提交。
- [ ] 使用 `git push -u origin <分支>` 设置 upstream。
- [ ] 理解设置 upstream 后直接使用 `git push`、`git pull` 的常见行为。
- [ ] 使用 `git branch -vv` 查看分支跟踪关系。
- [ ] 理解 `origin/main` 等远程跟踪分支。
- [ ] 使用 `git pull --ff-only` 仅在能快进时更新。
- [x] 理解推送前检查工作状态、测试结果和远程更新的重要性。
- [ ] 理解 non-fast-forward 推送被拒绝的原因。
- [ ] 了解 `git push origin --delete <分支>` 删除远程分支。

## 12. Git 撤销、回滚与恢复【核心】

- [ ] 区分撤销工作区修改、取消暂存、撤销本地提交、撤销已共享提交。
- [x] 使用 `git restore <文件>` 丢弃工作区中指定的未暂存修改。
- [x] 使用 `git restore --staged <文件>` 取消暂存。
- [ ] 使用 `git restore --source=<commit> -- <文件>` 恢复指定版本的文件。
- [ ] 理解 `git reset --mixed` 的效果。
- [ ] 理解 `git reset --soft` 的效果。
- [ ] 理解 `git reset --hard` 的效果及其危险性。
- [ ] 理解 `git reset HEAD~1` 撤销尚未共享的最近提交的使用边界。
- [ ] 使用 `git commit --amend` 修正最近提交。
- [ ] 理解为什么不能随意改写已共享的提交历史。
- [ ] 使用 `git revert <commit>` 创建反向提交。
- [ ] 区分 `revert` 和 `reset`。
- [ ] 使用 `git reflog` 查找引用的历史移动记录。
- [ ] 在测试仓库中通过 reflog 找回仍可访问的历史提交。
- [ ] 区分 `git clean -n` 预览与 `git clean -fd` 删除未跟踪文件和目录。
- [ ] 理解 Git 无法保证恢复所有未提交而被覆盖或删除的数据。
- [ ] 在执行危险操作前确认分支、目标提交和需要保留的修改。

## 13. Git stash 临时保存【按需】

- [ ] 理解 stash 的用途与适用场景。
- [ ] 使用 `git stash push -m "说明"` 临时保存修改。
- [ ] 使用 `git stash list` 查看 stash。
- [ ] 使用 `git stash show -p` 查看 stash 差异。
- [ ] 区分 `git stash apply` 和 `git stash pop`。
- [ ] 使用 `git stash push -u` 保存包括未跟踪文件在内的改动。
- [ ] 理解 stash 恢复时可能产生冲突。
- [ ] 理解 `git stash drop`、`git stash clear` 的删除风险。

## 14. Git 多人协作【按需】

- [ ] 理解功能分支、提交、推送、PR/MR 的协作流程。
- [ ] 区分 Pull Request / Merge Request 与 `git pull`。
- [ ] 学会在托管平台创建 PR/MR 并填写变更说明。
- [ ] 学会查看其他开发者的代码差异并提交 Review 意见。
- [ ] 理解代码评审、CI 检查和审批之间的关系。
- [ ] 理解主分支保护规则。
- [ ] 区分 Merge commit、Squash merge、Rebase merge。
- [ ] 理解 Fork 和 upstream 仓库。
- [ ] 掌握通过小提交、及时同步和明确分工减少冲突的方法。
- [ ] 理解为什么不能擅自强推覆盖他人的提交。

## 15. Git 标签与版本发布【按需】

- [ ] 理解 Tag 和 Branch 的区别。
- [ ] 使用 `git tag` 查看标签。
- [ ] 使用 `git tag <名称>` 创建轻量标签。
- [ ] 使用 `git tag -a <名称> -m "说明"` 创建附注标签。
- [ ] 使用 `git show <标签>` 查看标签对应版本。
- [ ] 使用 `git push origin <标签>` 推送标签。
- [ ] 理解语义化版本号的基本规则。
- [ ] 理解修改或删除已共享标签可能造成的风险。

---

# 第四部分：项目工程实践

## 16. Git 与 IDE、Agent 的结合【核心】

- [x] 在 IntelliJ IDEA 或 VS Code 中查看 Git 状态、diff 和提交历史。
- [x] 在 IDE 中完成提交，并理解其背后的 Git 命令。
- [ ] 为 Spring Boot / MyBatis 项目建立 Git 仓库和合理的 `.gitignore`。
- [x] 修改 Mapper、Service、配置文件前检查仓库状态。
- [ ] 功能开发完成后，先查看 diff、运行测试，再提交代码。
- [ ] 为 Python / LLM API 项目隔离 `.env` 和 API Key 等敏感文件。
- [ ] 区分自己编写的代码和 Agent 修改的代码。
- [x] Agent 修改代码前，使用 `git status` 核对现有改动。
- [x] Agent 修改代码后，使用 `git diff` 和 `git diff --staged` 审查实际变化。
- [ ] 对 Agent 修改的关键逻辑亲自检查，并运行相关测试。
- [ ] 给 Agent 设定文件修改范围和命令执行权限边界。
- [ ] 使用独立 Git 分支隔离 Agent 实验，失败时安全恢复。
- [ ] 坚持自己审核后再提交和推送，而不是直接接受 Agent 的所有修改。

## 17. Git 常见错误排查与安全【核心 / 按需】

- [ ] 解决 `fatal: not a git repository`。
- [ ] 诊断 `nothing to commit`。
- [ ] 排查 `.gitignore` 导致文件无法被追踪的问题。
- [ ] 解决 `Author identity unknown`。
- [ ] 排查 `Permission denied (publickey)`。
- [ ] 排查 HTTPS 凭据、权限和令牌过期问题。
- [ ] 解决 `src refspec ... does not match any`。
- [ ] 排查 non-fast-forward 推送拒绝。
- [ ] 解决 `no upstream branch`。
- [ ] 理解并处理 `You have divergent branches`。
- [ ] 解决 `MERGE_HEAD exists` 等未完成合并问题。
- [ ] 识别和处理 detached HEAD 状态。
- [ ] 排查 CRLF/LF、文件权限、大小写、大文件导致的异常变更。
- [ ] 理解密钥进入提交历史后的应急处理：吊销/轮换凭据、评估暴露、再处理历史。

---

# 第五部分：Git 进阶能力

## 18. Git 高级操作与开发效率【进阶选修】

- [ ] 使用 `git cherry-pick` 移植指定提交。
- [ ] 理解 `git rebase` 和 `git merge` 的主要区别。
- [ ] 使用 `git rebase -i` 整理自己尚未共享的提交。
- [ ] 理解 rebase 发生冲突后的 `--continue`、`--abort`。
- [ ] 理解 `git push --force-with-lease` 的使用边界和风险。
- [ ] 使用 `git bisect` 定位引入缺陷的提交。
- [ ] 使用 `git grep` 搜索仓库中的内容。
- [ ] 结合 `git log -- <路径>` 和 `git blame` 追踪代码演变。
- [ ] 了解 `git worktree` 管理多个工作目录。
- [ ] 了解 `.gitattributes` 的作用。
- [ ] 了解 Git LFS 管理大文件的用途和限制。
- [ ] 了解 Git Submodule 的用途和管理成本。
- [ ] 了解 Sparse Checkout 的使用场景。
- [ ] 了解 Git Hooks 的基本机制。
- [ ] 使用 Git Alias 配置命令别名。

## 19. Git 底层原理【进阶选修】

- [ ] 理解 blob、tree、commit、tag 对象。
- [ ] 理解 Git 对象之间的引用关系。
- [ ] 理解内容寻址与对象哈希 ID 的意义。
- [ ] 理解分支引用（refs）和 HEAD 的关系。
- [ ] 理解 HEAD、Index、Working Tree 的三层状态模型。
- [ ] 理解本地 Git 对象数据库与远程传输的关系。
- [ ] 理解 Git 对象不可变和历史改写生成新对象。
- [ ] 了解垃圾回收和 reflog 的保留限制。
- [ ] 理解提交图（DAG）与共同祖先的作用。
- [ ] 知道复杂恢复、历史整理和疑难冲突时如何运用 Git 底层原理。

---

# 第六部分：实战能力验收

## 20. 综合实战任务【综合验证】

- [ ] **仓库初始化实战**：独立为一个 Java 或 Python 项目初始化仓库，配置忽略规则并创建首个提交。
- [ ] **提交管理实战**：修改多个文件，选择性暂存其中部分改动，检查差异后完成提交。
- [ ] **分支开发实战**：创建功能分支、完成开发、切换回主分支、合并功能并检查历史。
- [ ] **冲突处理实战**：在两个分支制造冲突，手动解决，运行测试并确认结果。
- [ ] **远程仓库实战**：完成远程关联、推送、获取更新、拉取以及 upstream 检查。
- [ ] **撤销恢复实战**：在测试仓库分别练习 restore、取消暂存、revert，并理解各自的适用场景。
- [ ] **Agent 协作实战**：让 Agent 在受控范围修改测试项目，自己检查 diff、验证功能并选择性提交。
- [ ] **Git 排障实战**：面对错误分支、upstream 未设置或推送被拒绝等情况，先诊断再解决。

---

# 第七部分：后续维护记录

可以在学习过程中补充以下信息：

**最近完成：**

日期｜功能模块｜具体知识点｜对应项目

**待复习：**

记录已经接触但尚不能独立解释或操作的知识点。

**新增问题：**

遇到原清单未覆盖的新知识点时，把它补充到对应功能模块，并建立独立复选框。

**长期执行原则：**

日常开发优先使用 `status → diff → add → commit`；逐步掌握忽略规则、分支、合并和远程同步；遇到撤销、恢复、冲突等问题时再专项强化；进阶能力完全按实际需求补充。

**这份计划书不是学习时间表，而是 Git 知识地图。**