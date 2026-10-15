# ⚡ uv 完整速查笔记

> 用**项目、环境、锁文件、Python 版本、工具**五要素统一管理 Python 工程。  
> uv = pip + pip-tools + virtualenv + pipx + pyenv 的极速替代。  
> 目标：快、可复现、跨平台、Docker/CI 友好、与现有 pip 生态兼容。

---

如果只记住三件事：

1. **新项目：`uv init` → `uv add` → `uv sync` → `uv run`**  
2. **提交 `pyproject.toml` + `uv.lock`，不提交 `.venv/`**  
3. **CI/Docker 用 `uv sync --frozen`，全局 CLI 用 `uvx` / `uv tool`**

这三条能直接解决“慢、乱、不可复现”三个最常见问题。

---

## 目录

1. 核心概念
2. 安装与升级
3. 两种使用模式
4. 项目管理模式（推荐）
5. pip 兼容模式
6. 环境管理
7. Python 版本管理
8. 依赖声明与锁定
9. 工具管理（uvx / uv tool）
10. 脚本与内联依赖（PEP 723）
11. 缓存与速度
12. Docker 与 CI
13. 与 pip / venv / conda 对比
14. 常见陷阱速查
15. 最佳实践清单
16. 项目结构模板
17. 改进版四步走
18. 常用命令速查表

---

## 一、核心概念

| 概念 | 作用 |
| ------ | ------ |
| **项目** | 有 `pyproject.toml` 的 Python 工程，uv 管理依赖和锁 |
| **环境** | `.venv`，隔离的 Python 运行空间 |
| **锁文件** | `uv.lock`，记录所有依赖的精确版本和哈希 |
| **Python 版本** | uv 可下载、安装、切换 Python 解释器 |
| **工具** | 全局可执行的 Python CLI，如 ruff、black、httpie |
| **脚本** | 单文件 Python，可用内联依赖元数据运行 |

> [!IMPORTANT]
> ⚠️ **uv 不是 conda 的完全替代**。  
> 它管 Python 生态，不管 CUDA、C 库、R、系统二进制。  
> 数据科学/ML 需要非 Python 依赖时，仍可用 micromamba/conda。

---

## 二、安装与升级

### 1. 安装

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew
brew install uv

# pipx
pipx install uv

# pip
pip install uv

# cargo
cargo install --locked uv
```

### 2. 升级

```bash
uv self update
```

### 3. 查看版本

```bash
uv --version
uv help
uv help pip
uv help python
```

---

## 三、两种使用模式

| 模式 | 命令风格 | 适用 |
|---|---|---|
| **项目管理模式** | `uv init`、`uv add`、`uv sync`、`uv run` | 新项目、标准工程 |
| **pip 兼容模式** | `uv pip install`、`uv pip compile`、`uv pip sync` | 迁移老项目、临时环境 |

> [!TIP]
> 新项目优先用项目管理模式；  
> 老项目或 CI 里已有 `requirements.txt`，用 `uv pip` 无缝替换 pip。

---

## 四、项目管理模式（推荐）

### 1. 初始化项目

```bash
# 创建新项目目录
uv init myproject
cd myproject

# 在当前目录初始化
uv init .

# 指定 Python 版本
uv init --python 3.12 myproject

# 创建库项目（含 src 布局）
uv init --lib myproject

# 创建应用项目（默认）
uv init --app myproject
```

生成结构：

```text
myproject/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
└── src/
    └── myproject/
        └── __init__.py
```

### 2. 添加依赖

```bash
# 添加运行时依赖
uv add requests

# 指定版本
uv add "requests>=2.31"

# 添加开发依赖
uv add --dev pytest ruff mypy

# 添加可选依赖组
uv add --optional test pytest
uv add --group docs sphinx

# 从 git 添加
uv add git+https://github.com/psf/requests.git

# 从本地路径添加
uv add ./mylib

# 从 URL 添加
uv add https://example.com/pkg.tar.gz
```

### 3. 移除依赖

```bash
uv remove requests
uv remove --dev pytest
```

### 4. 同步环境

```bash
# 根据 pyproject.toml + uv.lock 创建/更新 .venv
uv sync

# 包含开发依赖
uv sync --dev

# 不安装项目本身（只装依赖）
uv sync --no-install-project

# 只同步指定组
uv sync --group docs

# 冻结锁文件，不更新
uv sync --frozen

# 锁定后不更新，用于 CI
uv sync --locked
```

### 5. 更新锁文件

```bash
# 更新所有依赖并重新锁定
uv lock

# 只升级指定包
uv lock --upgrade-package requests

# 升级所有包
uv lock --upgrade
```

### 6. 运行命令

```bash
# 在项目环境中运行
uv run python app.py
uv run pytest
uv run ruff check .

# 临时带某个包运行
uv run --with requests python -c "import requests; print(requests.__version__)"

# 指定 Python 版本运行
uv run --python 3.12 python app.py
```

### 7. 导出 requirements.txt

```bash
uv export --format requirements-txt > requirements.txt
uv export --format requirements-txt --no-dev > requirements.txt
uv export --format requirements-txt --no-hashes > requirements.txt
```

### 8. 查看依赖树

```bash
uv tree
uv tree --depth 2
```

### 9. 构建与发布

```bash
uv build
uv publish
```

---

## 五、pip 兼容模式

### 1. 创建环境

```bash
uv venv .venv
uv venv --python 3.12
uv venv --seed          # 同时安装 pip/setuptools/wheel
uv venv --system-site-packages
```

### 2. 安装包

```bash
uv pip install numpy
uv pip install "numpy==1.26.4"
uv pip install -r requirements.txt
uv pip install -e .
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple numpy
```

### 3. 编译锁文件

```bash
uv pip compile requirements.in -o requirements.txt
uv pip compile requirements.in -o requirements.txt --generate-hashes
uv pip compile pyproject.toml -o requirements.txt
```

### 4. 同步环境

```bash
uv pip sync requirements.txt
uv pip sync requirements.txt --require-hashes
```

### 5. 查看与卸载

```bash
uv pip list
uv pip show numpy
uv pip freeze
uv pip uninstall numpy
uv pip check
```

> [!TIP]
> `uv pip` 默认操作当前激活的 venv，或 `VIRTUAL_ENV` 指向的环境。  
> 也可用 `--python .venv/bin/python` 显式指定。

---

## 六、环境管理

### 1. 创建环境

```bash
uv venv .venv
uv venv --python 3.12 .venv
uv venv --python 3.12 --seed .venv
uv venv --prompt myproject .venv
```

### 2. 激活与退出

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

deactivate
```

### 3. 不激活直接运行

```bash
uv run python app.py
uv run --python .venv/bin/python python app.py
```

### 4. 删除环境

```bash
rm -rf .venv
```

### 5. 查看环境

```bash
uv venv --help
uv python find
uv python list
```

---

## 七、Python 版本管理

uv 可以下载并管理 Python 解释器，类似 pyenv。

```bash
# 安装 Python
uv python install 3.12
uv python install 3.11 3.12 3.13

# 查看可用版本
uv python list

# 查看已安装版本
uv python list --only-installed

# 固定项目 Python 版本，写入 .python-version
uv python pin 3.12

# 查找 Python
uv python find
uv python find 3.12
```

`.python-version` 示例：

```text
3.12
```

> [!TIP]
> `uv python pin 3.12` 后，`uv run`、`uv sync` 都会用 3.12。  
> 不需要系统预装 Python，uv 可自动下载。

---

## 八、依赖声明与锁定

### 1. pyproject.toml

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31",
    "fastapi>=0.110",
]

[dependency-groups]
dev = [
    "pytest>=8",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8",
]
```

### 2. uv.lock

- 由 `uv lock` / `uv add` / `uv sync` 自动生成。
- 记录所有依赖的精确版本、哈希、来源。
- **必须提交到 Git**。

### 3. 常用锁定命令

```bash
uv lock
uv lock --upgrade
uv lock --upgrade-package requests
uv sync --frozen
uv sync --locked
```

### 4. 导出给 pip 用

```bash
uv export --format requirements-txt > requirements.txt
uv export --format requirements-txt --no-dev > requirements.txt
uv export --format requirements-txt --no-hashes > requirements.txt
```

---

## 九、工具管理（uvx / uv tool）

uv 可替代 pipx，安装和运行全局 Python CLI。

### 1. 临时运行

```bash
uvx ruff check .
uvx black .
uvx httpie GET https://example.com
uvx --from ruff ruff check .
```

`uvx` 等价于 `uv tool run`。

### 2. 安装工具

```bash
uv tool install ruff
uv tool install black
uv tool install httpie

# 指定版本
uv tool install "ruff==0.4.0"

# 从 git 安装
uv tool install git+https://github.com/psf/black.git
```

### 3. 管理工具

```bash
uv tool list
uv tool upgrade ruff
uv tool upgrade --all
uv tool uninstall ruff
uv tool dir
```

### 4. 工具隔离

```bash
uv tool install --python 3.12 ruff
```

---

## 十、脚本与内联依赖（PEP 723）

uv 支持单文件脚本内联依赖。

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "rich",
# ]
# ///

import requests
from rich import print

print(requests.get("https://example.com").status_code)
```

运行：

```bash
uv run script.py
```

添加依赖到脚本：

```bash
uv add --script script.py requests rich
```

锁定脚本依赖：

```bash
uv lock --script script.py
```

> [!TIP]
> 适合小工具、一次性脚本、分享可复现的 Python 文件。

---

## 十一、缓存与速度

uv 默认使用全局缓存，硬链接到各环境，速度快、占盘少。

```bash
uv cache dir
uv cache clean
uv cache prune
uv cache size
```

速度优化：

- 使用 `uv pip` 替代 `pip`，通常快 10–100 倍。
- 使用 `uv sync --frozen` 避免重新解析。
- CI 中缓存 `~/.cache/uv` 和 `uv.lock`。
- 国内镜像：

```bash
# 临时
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple numpy

# 环境变量
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 或写 pyproject.toml
[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

---

## 十二、Docker 与 CI

### 1. Dockerfile（推荐）

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python", "app.py"]
```

### 2. 多阶段构建

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "app.py"]
```

### 3. GitHub Actions

```yaml
- uses: astral-sh/setup-uv@v3
  with:
    enable-cache: true

- run: uv sync --frozen --dev
- run: uv run pytest
- run: uv run ruff check .
```

### 4. .dockerignore

```text
.venv/
__pycache__/
*.pyc
.git/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

---

## 十三、与 pip / venv / conda 对比

| 维度 | pip + venv | conda / micromamba | uv |
|---|---|---|---|
| 速度 | 慢 | 中 | 极快 |
| 语言 | Python | 跨语言 | Python |
| 二进制依赖 | wheel | 原生 | wheel |
| 锁文件 | requirements.txt | environment.yml | uv.lock |
| Python 版本管理 | 靠 pyenv | 内置 | 内置 |
| 工具管理 | pipx | 无 | uv tool / uvx |
| 脚本内联依赖 | 无 | 无 | PEP 723 |
| Docker | 简单 | 偏重 | 极简 |
| 数据科学/ML | 一般 | 强 | 可用，非 Python 依赖弱 |
| 适合 | 通用 | 数据科学 | 新项目首选 |

> [!TIP]
> 结合你的路线：  
> - **Java 主线**：Maven/Gradle + Docker  
> - **Python AI 副线**：uv 优先  
> - **数据科学/ML 需要 CUDA/C 库**：micromamba/conda  
> - **Docker/CI**：uv 最快最干净

---

## 十四、常见陷阱速查

| 问题 | 解决方法 |
|---|---|
| `uv: command not found` | 重新执行安装脚本，或 `source ~/.bashrc` |
| 装到了系统 Python | 用 `uv venv` 或 `uv sync`，不要裸 `uv pip install --system` |
| `uv pip install` 找不到环境 | 先 `uv venv` 或激活 `.venv` |
| `uv sync` 删除手动装的包 | 正常，uv 以 `uv.lock` 为准；临时包用 `uv run --with` |
| `uv.lock` 冲突 | 提交锁文件，冲突时 `uv lock` 重新生成 |
| 跨平台锁失败 | `uv.lock` 跨平台，但某些包有平台标记；用 `uv sync --frozen` |
| Docker 中 `.venv` 路径失效 | 用 `UV_LINK_MODE=copy`，不要挂载宿主 `.venv` |
| CI 中重新解析太慢 | `uv sync --frozen` + 缓存 `~/.cache/uv` |
| 国内下载慢 | 设置 `UV_INDEX_URL` 或 `[[tool.uv.index]]` |
| 与 conda 混用 | 先 `conda deactivate`，再用 uv；不要嵌套 |
| `uv tool install` 后命令找不到 | 确认 `~/.local/bin` 在 PATH |
| `uvx` 每次重新下载 | 正常，uv 有缓存；可 `uv tool install` 固定 |
| `uv run` 找不到项目 | 确认在含 `pyproject.toml` 的目录，或 `uv init` |
| Python 版本不对 | `uv python pin 3.12` 并检查 `.python-version` |
| 想用系统 Python | `uv venv --python /usr/bin/python3` |

---

## 十五、最佳实践清单

- 新项目用 `uv init` + `uv add` + `uv sync` + `uv run`。
- 提交 `pyproject.toml` 和 `uv.lock`，不提交 `.venv/`。
- 用 `uv run` 代替手动激活。
- 开发依赖用 `uv add --dev`。
- CI 用 `uv sync --frozen`。
- Docker 用官方 uv 镜像 + `UV_LINK_MODE=copy`。
- 全局 CLI 用 `uv tool install` 或 `uvx`。
- 小脚本用 PEP 723 内联依赖。
- 国内设 `UV_INDEX_URL`。
- 数据科学非 Python 依赖再上 micromamba/conda。
- 不要 `uv pip install --system`，除非明确知道在做什么。
- 定期 `uv cache prune`。

---

## 十六、项目结构模板

```text
myproject/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
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

`.dockerignore`：

```text
.venv/
__pycache__/
*.pyc
.git/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

---

## 十七、改进版四步走

```bash
# 1. 初始化项目
uv init myproject
cd myproject

# 2. 固定 Python 并添加依赖
uv python pin 3.12
uv add requests fastapi
uv add --dev pytest ruff

# 3. 同步并运行
uv sync
uv run python -m myproject

# 4. 锁定并提交
# 提交 pyproject.toml + uv.lock + .python-version
```

> [!TIP]
> ✨ **记住四步走**：
>
> 1. `uv init`  
> 2. `uv add` / `uv python pin`  
> 3. `uv sync` / `uv run`  
> 4. 提交 `pyproject.toml` + `uv.lock`

---

## 十八、常用命令速查表

| 操作 | 命令 |
|---|---|
| 安装 uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| 升级 uv | `uv self update` |
| 初始化项目 | `uv init myproject` |
| 固定 Python | `uv python pin 3.12` |
| 安装 Python | `uv python install 3.12` |
| 创建环境 | `uv venv .venv` |
| 添加依赖 | `uv add requests` |
| 添加开发依赖 | `uv add --dev pytest` |
| 移除依赖 | `uv remove requests` |
| 同步环境 | `uv sync` |
| 冻结同步 | `uv sync --frozen` |
| 更新锁 | `uv lock` |
| 升级包 | `uv lock --upgrade-package requests` |
| 运行 | `uv run python app.py` |
| 临时带包运行 | `uv run --with requests python -c "..."` |
| 导出 requirements | `uv export --format requirements-txt > requirements.txt` |
| pip 安装 | `uv pip install numpy` |
| pip 编译 | `uv pip compile requirements.in -o requirements.txt` |
| pip 同步 | `uv pip sync requirements.txt` |
| 查看依赖树 | `uv tree` |
| 临时工具 | `uvx ruff check .` |
| 安装工具 | `uv tool install ruff` |
| 列出工具 | `uv tool list` |
| 升级工具 | `uv tool upgrade ruff` |
| 脚本运行 | `uv run script.py` |
| 脚本加依赖 | `uv add --script script.py requests` |
| 清缓存 | `uv cache clean` |
| 查看缓存 | `uv cache dir` |
| 构建 | `uv build` |
| 发布 | `uv publish` |

---

完成于 2026-10-15