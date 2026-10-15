# 🐍 venv + pip 完整速查笔记

> 用**解释器、虚拟环境、包索引源**三要素管理你的 Python 项目依赖。  
> 目标：不污染全局、依赖可复现、协作可重建、部署可离线、Docker/CI 可用。

---

如果只记住三件事：

1. **`python -m venv .venv` + 激活**  
2. **`python -m pip install ...` + `pip check`**  
3. **`requirements.in` + `pip-compile` / `uv` 锁定依赖**

这三条能直接解决“装错环境、依赖冲突、无法复现”三个最常见问题。

---

## 目录

1. 核心概念
2. 环境管理
3. 包管理
4. 索引源管理
5. pip 与 venv 黄金法则
6. 依赖声明与锁定
7. 可复现与离线安装
8. 诊断命令
9. 速度优化
10. Docker 与 CI
11. 安全审计
12. 常见陷阱速查
13. 最佳实践清单
14. 项目结构模板
15. 改进版四步走
16. 常用命令速查表

---

## 一、核心概念

| 概念 | 作用 |
| ------ | ------ |
| **解释器** | 创建 venv 的 Python 本体，决定 Python 版本 |
| **虚拟环境** | 隔离的 Python 包安装目录，通常叫 `.venv` |
| **包索引源** | pip 下载包的来源仓库，如 PyPI、清华镜像 |

> [!IMPORTANT]
> ⚠️ **永远不要把项目依赖装进系统 Python / 全局环境！**  
> 系统 Python 只用来创建环境，项目依赖放进各自的 `.venv`。

推荐工作方式：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ...
```

> [!note]
`python -m` 的最大好处是“**绑定当前解释器** + 按模块语义运行”，让环境、依赖和导入路径更可控，尤其适合虚拟环境、多版本 Python 和包内开发。

---

## 二、环境管理（重中之重）

### 1. 创建环境

```bash
# 使用当前 python 创建
python -m venv .venv

# 指定 Python 版本（系统需已安装该版本）
python3.10 -m venv .venv

# 不安装 pip（少见）
python -m venv --without-pip .venv

# 允许访问系统 site-packages（不推荐）
python -m venv --system-site-packages .venv

# 清空已有环境并重建
python -m venv --clear .venv

# 创建时升级 pip/setuptools
python -m venv --upgrade-deps .venv

# 自定义激活提示符
python -m venv --prompt myproject .venv
```

### 2. 激活与退出

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Git Bash
source .venv/Scripts/activate

# 退出当前环境
deactivate
```

### 3. 查看环境

venv 没有类似 `conda env list` 的命令。

```bash
# 当前 Python 解释器路径
which python        # Linux / macOS
where python        # Windows

# 当前 pip 路径
which pip
where pip

# 查找项目内的 venv
find . -maxdepth 2 -name pyvenv.cfg

# 判断是否在 venv 中：输出 True 表示在 venv 里
python -c "import sys; print(sys.prefix != sys.base_prefix)"

# 查看 site-packages 路径
python -m site

# 查看当前 pip 属于哪个 Python
python -m pip --version
```

### 4. 克隆环境

venv 没有 `--clone` 命令，推荐用 `requirements.txt` 重建。

```bash
python -m venv newenv
source newenv/bin/activate
pip install -r requirements.txt
```

### 5. 删除环境

直接删除目录即可。

```bash
rm -rf .venv        # Linux / macOS
rmdir /s /q .venv   # Windows CMD
```

删除后如果 IDE 报错，在 IDE 中重新选择解释器。

### 6. 导出与重建（项目复现关键）

```bash
# 导出当前环境所有包
pip freeze > requirements.txt

# 导出但排除可编辑安装，跨平台更稳
pip freeze --exclude-editable > requirements.txt

# 从 requirements.txt 重建
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> [!TIP]
> **最佳实践**：每个项目一个 `.venv`，并保留 `requirements.txt` 用于协作与部署。  
> `.gitignore` 记得写 `.venv/`、`__pycache__/`、`*.pyc`。

---

## 三、包管理

### 1. 安装包

```bash
# 单包安装
python -m pip install numpy

# 指定版本
python -m pip install numpy==1.24.4

# 从特定源安装
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scikit-learn

# 同时安装多个
python -m pip install numpy pandas matplotlib

# 模拟安装，不真正安装
pip install --dry-run numpy

# 生成安装报告
pip install --report report.json numpy
```

### 2. 查看已安装的包

```bash
pip list                  # 当前环境所有包
pip list --not-required   # 顶层包
pip show numpy            # 查看特定包
pip show -f numpy         # 包信息 + 文件列表
pip freeze                # 导出格式
pip index versions numpy  # 查看可用版本
```

### 3. 更新包

```bash
python -m pip install --upgrade numpy
pip list --outdated
```

> [!WARNING]
> pip 没有官方“一键更新全部”的安全命令，谨慎使用脚本批量升级。

### 4. 卸载包

```bash
pip uninstall numpy
```

### 5. 检查依赖冲突

```bash
pip check
```

### 6. 清理缓存（节省磁盘）

```bash
pip cache dir
pip cache list
pip cache purge
```

---

## 四、索引源管理

- 默认源：**PyPI**
- 国内常用镜像：清华、阿里、中科大、豆瓣
- 可以临时指定，也可以全局配置

```bash
# 临时使用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy

# 设置全局默认源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 查看当前配置
pip config list

# 查看配置来源
pip config debug

# 取消设置
pip config unset global.index-url
```

> [!TIP]
> 📌 **建议固定一个镜像源**；如果公司内网有私有源，优先用私有源。  
> 私有源认证建议用 keyring 或环境变量，不要明文写密码。

---

## 五、pip 与 venv 黄金法则

- **先激活 venv，再用 pip**
- **优先用 `python -m pip`**，确保 pip 属于当前解释器
- **不要 `sudo pip install`**
- **不要往系统 Python 里装项目依赖**
- **先升级 pip**

```bash
python -m pip install --upgrade pip
```

- **用 `requirements.txt` 锁定依赖**

```bash
pip install -r requirements.txt
pip freeze --exclude-editable > requirements.txt
```

- **复杂项目可用 `pip-tools`、`uv`、`poetry` 管理依赖**

### 防止全局安装：强约束

```bash
# 全局配置：不在虚拟环境里，pip 拒绝安装
pip config set global.require-virtualenv true

# 临时启用
PIP_REQUIRE_VIRTUALENV=true python -m pip install numpy

# 取消
pip config unset global.require-virtualenv
```

> [!IMPORTANT]
> 开启 `require-virtualenv` 后，系统级 pip 安装也会被拒绝。  
> 这是有意的，能有效防止误装全局。需要临时绕过时用 `--isolated` 或明确关闭。

检查是否在 venv：

```bash
python -c "import sys; print(sys.prefix != sys.base_prefix)"
```

- `sys.prefix`：当前 Python 解释器使用的环境路径。
- `sys.base_prefix`：基础 Python 安装路径。
- 如果两者不同，说明你大概率在虚拟环境、conda 环境等非基础环境中，输出 `True`。
- 如果两者相同，说明你用的是基础 / 全局 Python，输出 `False`。

---

## 六、依赖声明与锁定

`pip freeze > requirements.txt` 是快照，不是声明。更推荐：

```text
requirements.in        # 只写直接依赖，如 numpy、fastapi
requirements.txt       # 由工具生成，锁定所有间接依赖和版本
requirements-dev.txt   # 开发依赖，如 pytest、ruff
constraints.txt        # 约束版本，不主动安装
```

### 使用 pip-tools

```bash
pip install pip-tools

# 生成锁文件
pip-compile requirements.in -o requirements.txt

# 生成带哈希的锁文件
pip-compile --generate-hashes requirements.in -o requirements.txt

# 按锁文件同步环境（会删除不在文件中的包）
pip-sync requirements.txt
```

`requirements-dev.txt` 可以这样写：

```text
-r requirements.txt
pytest
ruff
mypy
```

安装：

```bash
python -m pip install -r requirements-dev.txt
```

### 使用 uv

```bash
pip install uv

uv venv .venv
source .venv/bin/activate

uv pip install numpy pandas
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt
```

---

## 七、可复现与离线安装

```bash
# 生成带哈希的锁文件
pip-compile --generate-hashes requirements.in -o requirements.txt

# 按哈希安装
python -m pip install --require-hashes -r requirements.txt

# 下载 wheel 到本地
pip download -d wheels -r requirements.txt

# 离线安装
python -m pip install --no-index --find-links=wheels -r requirements.txt
```

---

## 八、诊断命令

```bash
python -m pip --version          # pip 属于哪个 Python
pip check                        # 依赖冲突
pip list --outdated              # 可升级包
pip list --not-required          # 顶层包
pip index versions numpy         # 可用版本
pip show -f numpy                # 包信息和文件列表
pip cache list                   # 缓存内容
pip config debug                 # 配置来源
python -m site                   # site-packages 路径
pip install --dry-run numpy      # 模拟安装
pip install --report report.json numpy
```

---

## 九、速度优化

```bash
# 更换为国内镜像（清华源）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

- 使用 **pip 缓存**：默认开启，`pip cache dir` 查看
- 使用 **uv** 替代 pip，速度更快：

```bash
pip install uv
uv venv .venv
source .venv/bin/activate
uv pip install numpy pandas
```

- `--no-cache-dir` 只在调试缓存问题时使用

---

## 十、Docker 与 CI

### 1. Docker 中更稳的用法

不要在 Docker 里 `source activate`，直接走 PATH：

```dockerfile
FROM python:3.12-slim

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PIP_REQUIRE_VIRTUALENV=true \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --require-hashes -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

`.dockerignore` 记得加：

```text
.venv/
__pycache__/
*.pyc
.git/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

### 2. CI 示例

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip

- run: python -m pip install --upgrade pip
- run: python -m pip install -r requirements.txt
- run: pip check
```

---

## 十一、安全审计

```bash
pip install pip-audit
pip-audit
```

---

## 十二、常见陷阱速查

| 问题 | 解决方法 |
| ------ | ---------- |
| `No module named venv` | Ubuntu/Debian 安装：`sudo apt install python3-venv` |
| `Activate.ps1 cannot be loaded` | PowerShell 执行：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `pip: command not found` | 用 `python -m pip`，或确认 venv 已激活 |
| 装到了全局环境 | `which pip` / `where pip` 检查路径应在 `.venv` 内 |
| 依赖冲突 | 每个项目独立 venv，锁定 `requirements.txt`，运行 `pip check` |
| 删除 `.venv` 后 IDE 报错 | 在 IDE 中重新选择解释器 |
| Windows 路径含空格 | 路径加引号 |
| 与 conda 混用混乱 | 通常不要嵌套；先 `conda deactivate`，再激活 venv |
| `sudo pip install` | 禁止，会污染系统 |
| `pip install --user` | 和 venv 混用容易乱，不推荐 |
| `pip freeze` 带 `-e` | 跨平台不可用，可加 `--exclude-editable` |
| 提交 `.venv` | 不要提交，写进 `.gitignore` |
| 想重建环境 | `python -m venv --clear .venv` |
| 想升级 pip/setuptools | `python -m venv --upgrade-deps .venv` |
| 想改激活提示符 | `python -m venv --prompt myproject .venv` |
| 私有源认证 | 用 keyring 或环境变量，别明文写密码 |
| 临时忽略配置 | `pip install --isolated ...` |

---

## 十三、最佳实践清单

- 每个项目一个 `.venv`。
- 永远用 `python -m pip`。
- 开启 `PIP_REQUIRE_VIRTUALENV=true`。
- 用 `requirements.in` 声明直接依赖。
- 用 `pip-compile` / `uv` 生成锁文件。
- 提交 `requirements.txt`，不提交 `.venv/`。
- 运行 `pip check`。
- Docker 中用 PATH 激活 venv，不 `source activate`。
- CI 中缓存 pip，安装后跑 `pip check`。
- 定期 `pip-audit`。
- 复杂项目再上 `uv`、`poetry`、`pdm`。

---

## 十四、项目结构模板

```text
myproject/
├── .venv/                  # 不提交
├── requirements.in         # 直接依赖
├── requirements.txt        # 锁定依赖，提交
├── requirements-dev.txt    # 开发依赖
├── constraints.txt         # 可选，版本约束
├── .gitignore
├── .dockerignore
├── Dockerfile
├── src/
│   └── myproject/
│       └── __init__.py
└── tests/
    └── test_main.py
```

`.gitignore`：

```text
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

---

## 十五、改进版四步走

```bash
# 1. 创建
python -m venv .venv

# 2. 激活（或直接用 .venv/bin/python -m pip）
source .venv/bin/activate

# 3. 安装并锁定
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pip check
pip freeze --exclude-editable > requirements.txt

# 4. 防全局
pip config set global.require-virtualenv true
```

> [!TIP]
> ✨ **记住四步走**：
>
> 1. 创建环境：`python -m venv .venv`
> 2. 激活环境：`source .venv/bin/activate`
> 3. pip 装包：`python -m pip install ...`
> 4. 锁定环境：`pip freeze --exclude-editable > requirements.txt`

---

## 十六、常用命令速查表

| 操作 | 命令 |
|---|---|
| 创建环境 | `python -m venv .venv` |
| 指定版本 | `python3.10 -m venv .venv` |
| 清空重建 | `python -m venv --clear .venv` |
| 激活 Linux/macOS | `source .venv/bin/activate` |
| 激活 Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| 退出 | `deactivate` |
| 判断是否在 venv | `python -c "import sys; print(sys.prefix != sys.base_prefix)"` |
| 安装包 | `python -m pip install numpy` |
| 指定版本 | `python -m pip install numpy==1.24.4` |
| 导出依赖 | `pip freeze --exclude-editable > requirements.txt` |
| 重建依赖 | `pip install -r requirements.txt` |
| 检查冲突 | `pip check` |
| 查看包 | `pip list` / `pip show numpy` |
| 升级包 | `pip install --upgrade numpy` |
| 卸载包 | `pip uninstall numpy` |
| 清缓存 | `pip cache purge` |
| 设置镜像 | `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple` |
| 防全局安装 | `pip config set global.require-virtualenv true` |
| 生成锁文件 | `pip-compile requirements.in -o requirements.txt` |
| 同步锁文件 | `pip-sync requirements.txt` |
| uv 创建环境 | `uv venv .venv` |
| uv 安装 | `uv pip install numpy pandas` |
| 安全审计 | `pip-audit` |

---

完成于 2026-10-15