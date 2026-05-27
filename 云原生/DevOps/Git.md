# Git 常用操作笔记

## **一、初次上传本地项目到远程仓库**

### 1. 初始化 Git 仓库

```bash
git init
```

### 2. 将所有文件添加到暂存区

```bash
git add .
```

### 3. 提交到本地仓库

```bash
git commit -m "feat: 上传Java相关代码与练习文件"
```

### 4. 关联远程仓库

先在 GitHub 等平台创建一个**空仓库**（不勾选 README、.gitignore、License），然后执行：

```bash
git remote add origin [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
```

### 5. 推送到远程仓库

```bash
git push -u origin main
```

+ 加上 `-u` 后，本地 `main` 分支会与远程 `origin/main` 建立追踪关系，后续可直接使用 `git push`。

---

## **二、日常更新操作**

### 1.代码实现

当项目内容有变化时，依次执行：

```bash
git add .
git commit -m "描述本次更新的内容"
git push
```

+ `git add .`：将所有变更添加到暂存区
+ `git commit -m "xxx"`：提交到本地仓库，建议填写有意义的提交信息
+ `git push`：推送至已关联的远程仓库（已建立追踪关系后可省略远程名和分支名）

### 2.Git Commit 消息规范（Conventional Commits）笔记

使用统一的提交标签可以使项目历史更清晰，便于自动化生成更新日志。

#### (1)常用标签说明

| 标签 | 全称 | 适用场景 | 举个例子 |
| ------ | ------ | ---------- | ---------- |
| `feat` | feature | 开发**新功能**。只要是系统里以前没有、现在刚写完的功能，都用它。 | `feat: 编写GourmetCoffee的购物车商品添加功能` |
| `fix` | fix | **修复 Bug**。代码报错、逻辑漏洞、死循环，只要是改错都用它。 | `fix: 修复咖啡数量输入负数时导致金额计算错误的Bug` |
| `docs` | documentation | 仅仅**修改了文档**。比如改了 README.md、写了注释、改了脑图。 | `docs: 更新W4阶段Python测试接口脑图说明` |
| `style` | style | 不影响代码逻辑的**格式调整**。比如对齐空格、删掉多余空行、格式化代码。 | `style: 格式化GourmetCoffee主类的缩进和空格` |
| `refactor` | refactor | **重构代码**。既不是新功能，也不是修 Bug，而是把烂代码写得更优雅、更健壮。 | `refactor: 提取公共咖啡属性到基类以优化代码结构` |
| `test` | test | **增加或修改测试用例**。比如你在写 Java 时用的 JUnit 测试代码。 | `test: 增加购物车结算逻辑的单元测试` |
| `chore` | chore | **杂务/日常构建维护**。比如修改了 pom.xml 引入了新依赖、改了 .gitignore、配置了 IntelliJ IDEA 的环境。 | `chore: 导入老师提供的GourmetCoffee第三方类库` |

#### (2)补充标签（可选）

| 标签 | 全称 | 适用场景 | 举个例子 |
| ------ | ------ | ---------- | ---------- |
| `perf` | performance | **性能优化**相关的改动。 | `perf: 优化图片加载策略减少首页白屏时间` |
| `build` | build | 影响构建系统或外部依赖的改动（如 Maven/Gradle 配置）。 | `build: 升级Spring Boot版本至2.7.0` |
| `ci` | continuous integration | 修改 CI 配置或脚本（如 GitHub Actions、Jenkins）。 | `ci: 添加自动化测试流水线` |
| `revert` | revert | **撤销**之前的某次提交。 | `revert: 回退feat(购物车)因为发现性能瓶颈` |

## 使用格式

---

## 三、分支管理

### 1.查看分支

```bash
git branch         # 查看本地分支，当前分支前有 *
git branch -r      # 查看远程分支
git branch -a      # 查看所有分支（本地+远程）
```

### 2.创建并切换到新分支

```bash
git checkout -b 分支名
# 或新版命令
git switch -c 分支名
```

+ -b 是 --branch 的简写,代表创建并切换
+ -c 是 --create 的简写,代表创建并切换

### 3.切换分支

```bash
git checkout 分支名
# 或
git switch 分支名
```

### 4.合并分支

#### (1)先切换到目标分支（例如 `main`）

```bash
git checkout main
```

#### (2)执行合并

```bash
git merge 要合并的分支名
```

### 5.删除分支

```bash
git branch -d 分支名   # 删除已合并的分支
git branch -D 分支名   # 强制删除分支（即使未合并）
```

### 6.推送新分支到远程

```bash
git push -u origin 分支名
```

---

## 四、撤销与回退

### 1.撤销工作区的修改（未 add）

```bash
git checkout -- 文件名
# 新版
git restore 文件名
```

放弃所有文件修改（慎用）：

```bash
git checkout .
```

### 2.撤销暂存区的文件（已 add 未 commit）

```bash
git reset HEAD 文件名
# 新版
git restore --staged 文件名
```

### 3.修改最近一次提交信息（未 push）

```bash
git commit --amend -m "新的提交信息"
```

如果漏了文件，可以先 `git add`，再执行 `git commit --amend`（不加 `-m` 进入编辑器），会将新变更并入上一次提交。

### 4.撤销本地提交（已 commit 未 push）

+ 保留修改，仅撤销 commit：

```bash
git reset --soft HEAD~1
```

+ 保留修改，同时清空暂存区：

```bash
git reset HEAD~1          # 等同 --mixed
```

+ 彻底丢弃所有修改（危险）：

```bash
git reset --hard HEAD~1
```

### 5.撤销已推送到远程的提交

```bash
git revert HEAD       # 生成一个反向提交
git push
```

---

## 五、查看状态与历史

```bash
git status                    # 详细状态
git status -s                 # 简略模式
git log                       # 详细提交日志
git log --oneline             # 一行一条
git log --graph --all --oneline   # 图形化显示所有分支历史
git show 提交哈希             # 查看某次提交的详细内容
```

---

## 六、远程同步

### 1.拉取并合并

```bash
git pull                     # 相当于 git fetch + git merge
```

### 2.仅获取远程更新不合并

```bash
git fetch origin
```

查看远程与本地的差异：

```bash
git diff origin/main
```

### 3.本地有未提交修改时拉取

先用 `stash` 暂存：

```bash
git stash
git pull
git stash pop
```

---

## 七、暂存工作现场（stash）

临时保存当前修改，以便切换分支处理急事：

```bash
git stash                 # 暂存所有修改
git stash pop             # 恢复最近一次暂存并删除记录
git stash list            # 查看暂存列表
```

---

## 八、忽略文件（.gitignore）

在仓库根目录创建 `.gitignore` 文件，示例内容：

```bash
# 编译产物
target/
*.class

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
```

如果文件已被跟踪，需先取消跟踪：

```bash
git rm --cached 文件名
```

---

## 九、常用小贴士

+ 首次推送 `git push -u origin main` 后，日常直接 `git push` 即可。
+ 提交信息遵循约定式提交，如 `feat:`、`fix:`、`docs:` 等，便于回溯。
+ 操作前可用 `git status` 确认当前状态，避免误操作。
