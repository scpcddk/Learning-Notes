# 🐍 Conda 速查笔记

> 用 **包、环境、频道** 三要素管理你的数据科学工具链

---

## 一、核心概念

| 概念 | 作用 |
| ------ | ------ |
| **环境** | 隔离的 Python/R/二进制运行空间 |
| **包** | 通过 `conda` 安装的软件（不仅限于 Python 包） |
| **频道** | 包的来源仓库（如 `defaults`、`conda-forge`） |

> ⚠️ **永远不要把项目依赖装进 `base` 环境！**  
> `base` 只用来放 `conda` 自身和基础工具

---

## 二、==环境管理==（重中之重）

### 1. **创建环境**

```bash
# 指定 Python 版本
conda create -n myenv python=3.10

# 同时安装多个核心包
conda create -n myenv python=3.10 numpy pandas jupyter
```

### 2. **激活与退出**

```bash
conda activate myenv      # 进入环境
conda deactivate          # 退出当前环境
```

### 3. **查看所有环境**

```bash
conda env list
# 或
conda info --envs
```

### 4. **克隆环境**（快速复制）

```bash
conda create -n newenv --clone oldenv
```

### 5. **删除环境**

```bash
conda remove -n myenv --all
```

### 6. **导出与重建**（项目复现关键）

```bash
# 导出为 .yml（跨平台共享）
conda env export -n myenv > environment.yml

# 从 yml 重建环境
conda env create -f environment.yml
```

> [!TIP]
> 🔥 **最佳实践**：每个项目一个环境，并保留 `environment.yml` 用于协作与部署

---

## 三、包管理

### 1. 安装包

```bash
# 单包安装
conda install numpy

# 指定版本
conda install numpy=1.24

# 从特定频道安装
conda install -c conda-forge scikit-learn

# 同时安装多个
conda install numpy pandas matplotlib
```

### 2. 查看已安装的包

```bash
conda list                  # 当前环境所有包
conda list numpy            # 查看特定包
```

### 3. 更新包

```bash
conda update numpy          # 更新指定包
conda update --all          # 更新当前环境所有包（谨慎！）
```

### 4. 卸载包

```bash
conda remove numpy
```

### 5. 清理缓存（节省磁盘）

```bash
conda clean --all           # 删除所有缓存和未使用的包
```

---

## 四、频道管理

- **`conda-forge`** 是最活跃的社区频道，通常比 `defaults` 更新、更全
- 严格设置频道优先级，避免包冲突

```bash
# 添加 conda-forge 并设为首选
conda config --add channels conda-forge
conda config --set channel_priority strict
```

查看当前频道配置：

```bash
conda config --show channels
```

> [!TIP]
> 📌 **建议顺序**：`conda-forge` > `defaults`，且不要轻易混用不同渠道的包（尤其是 `pytorch` 等大型框架）

---

## 五、pip 与 conda 混用黄金法则

1. **先用 conda 安装，再补 pip**

```bash
conda install numpy pandas scipy
pip install some-special-package
```

2. **conda 安装的包绝对不要用 pip 升级**  否则可能导致环境崩溃
3. **把 pip 的包也写进 environment.yml**  
   导出时 `--from-history` 与 `--explicit` 灵活使用

---

## 六、速度优化

```bash
# 更换为国内镜像（清华源）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

- 使用 **mamba** 作为快速替代（并行求解依赖）：

```bash
conda install mamba -n base -c conda-forge
mamba install numpy   # 用法几乎与conda相同
```

---

## 七、常见陷阱速查

| 问题 | 解决方法 |
| ------ | ---------- |
| 环境解不开依赖（Solving environment 太久） | 使用 mamba，或指定包版本范围，清理缓存 |
| 误删 base 环境 | 重新安装 Miniconda/Anaconda |
| 激活失败 `conda: command not found` | 重新执行 `conda init` 或手动 source 配置文件 |
| `pip` 和 `conda` 依赖冲突 | 严格遵循“先 conda 后 pip”顺序，避免混装核心库 |

---

> [!TIP]
> ✨ **记住四步走**：  
>
> 1. 创建环境  
> 2. 激活环境  
> 3. conda 装主力包  
> 4. pip 补漏，锁定环境文件
