# 🐍 venv 速查笔记

> 用**解释器、虚拟环境、包索引源**三要素管理你的 Python 项目依赖

---

## 一、核心概念

| 概念 | 作用 |
| ------ | ------ |
| **解释器** | 创建 venv 的 Python 本体，决定 Python 版本 |
| **虚拟环境** | 隔离的 Python 包安装目录，通常叫 `.venv` |
| **包索引源** | pip 下载包的来源仓库，如 PyPI、清华镜像 |

> [!IMPORTANT]
> ⚠️ **永远不要把项目依赖装进系统 Python / 全局环境！**  
> 系统 Python 只用来创建环境，项目依赖放进各自的 `.venv`

---

## 二、==环境管理==（重中之重）

### 1. **创建环境**

```bash
# 使用当前 python 创建
python -m venv .venv

# 指定 Python 版本（系统需已安装该版本）
python3.10 -m venv .venv

# 不安装 pip（少见）
python -m venv --without-pip .venv

# 允许访问系统 site-packages（不推荐）
python -m venv --system-site-packages .venv
```

### 2. **激活与退出**

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

### 3. **查看环境**

venv 没有类似 `conda env list` 的命令。

```bash
# 当前 Python 解释器路径
which python        # Linux / macOS
where python        # Windows

# 当前 pip 路径
which pip

# 查找项目内的 venv
find . -maxdepth 2 -name pyvenv.cfg
```

### 4. **克隆环境**

venv 没有 `--clone` 命令，推荐用 `requirements.txt` 重建。

```bash
python -m venv newenv
source newenv/bin/activate
pip install -r requirements.txt
```

### 5. **删除环境**

直接删除目录即可。

```bash
rm -rf .venv        # Linux / macOS
rmdir /s /q .venv   # Windows CMD
```

### 6. **导出与重建**（项目复现关键）

```bash
# 导出当前环境所有包
pip freeze > requirements.txt

# 从 requirements.txt 重建
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> [!TIP]
> **最佳实践**：每个项目一个 `.venv`，并保留 `requirements.txt` 用于协作与部署。  
> `.gitignore` 记得写 `.venv/`、`__pycache__/`。

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
```

### 2. 查看已安装的包

```bash
pip list                  # 当前环境所有包
pip show numpy            # 查看特定包
pip freeze                # 导出格式
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

### 5. 清理缓存（节省磁盘）

```bash
pip cache dir
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

# 取消设置
pip config unset global.index-url
```

> [!TIP]
> 📌 **建议固定一个镜像源**；如果公司内网有私有源，优先用私有源。

---

## 五、**pip 与 venv 混用黄金法则**

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
pip freeze > requirements.txt
```

- 复杂项目可用 `pip-tools`、`uv`、`poetry` 管理依赖

---

## 六、速度优化

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

## 七、常见陷阱速查

| 问题 | 解决方法 |
| ------ | ---------- |
| `No module named venv` | Ubuntu/Debian 安装：`sudo apt install python3-venv` |
| `Activate.ps1 cannot be loaded` | PowerShell 执行：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `pip: command not found` | 用 `python -m pip`，或确认 venv 已激活 |
| 装到了全局环境 | `which pip` / `where pip` 检查路径应在 `.venv` 内 |
| 依赖冲突 | 每个项目独立 venv，锁定 `requirements.txt` |
| 删除 `.venv` 后 IDE 报错 | 在 IDE 中重新选择解释器 |
| Windows 路径含空格 | 路径加引号 |
| 与 conda 混用混乱 | 通常不要嵌套；二选一，或明确用哪个 Python 创建 venv |

---

> [!TIP]
> ✨ **记住四步走**：
>
> 1. 创建环境：`python -m venv .venv`
> 2. 激活环境：`source .venv/bin/activate`
> 3. pip 装包：`python -m pip install ...`
> 4. 锁定环境：`pip freeze > requirements.txt`

---
