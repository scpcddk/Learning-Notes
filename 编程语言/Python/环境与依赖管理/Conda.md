# 🐍 Conda 完整速查笔记

> 用**环境、包、频道**三要素管理你的数据科学工具链。  
> 目标：不污染 base、依赖可复现、跨平台可重建、Docker/CI 可用、与 pip 混用不崩。

---

如果只记住三件事：

1. **base 不装项目依赖，每个项目一个环境**  
2. **先 conda 后 pip，不要 `conda update --all`**  
3. **`environment.yml --from-history` + `spec-file.txt` / `conda-lock` 锁定环境**

这三条能直接解决“环境崩、依赖冲突、无法复现”三个最常见问题。

---

## 目录

1. 核心概念
2. 环境管理
3. 包管理
4. 频道管理
5. pip 与 conda 混用黄金法则
6. 依赖锁定与可复现
7. 诊断命令
8. 速度优化（2024 后已变）
9. micromamba / mamba / pixi
10. Docker 与 CI
11. 安全与磁盘
12. conda vs venv 对比
13. 常见陷阱速查
14. 最佳实践清单
15. 项目结构模板
16. 改进版四步走
17. 常用命令速查表

---

## 一、核心概念

| 概念 | 作用 |
| ------ | ------ |
| **环境** | 隔离的 Python / R / 二进制 运行空间 |
| **包** | 通过 `conda` 安装的软件（不仅限于 Python 包） |
| **频道** | 包的来源仓库（如 `defaults`、`conda-forge`） |
| **solver** | 依赖求解器，决定装哪些版本。新版默认 `libmamba` |

> [!IMPORTANT]
> ⚠️ **永远不要把项目依赖装进 `base` 环境！**  
> `base` 只用来放 `conda` 自身和基础工具。

推荐工作方式：

```bash
conda create -n myenv python=3.11
conda activate myenv
conda install numpy pandas
```

---

## 二、环境管理（重中之重）

### 1. 创建环境

```bash
# 指定 Python 版本
conda create -n myenv python=3.11

# 同时安装多个核心包
conda create -n myenv python=3.11 numpy pandas jupyter

# 项目内环境（用路径而非名字）
conda create -p ./.conda python=3.11

# 从 environment.yml 创建
conda env create -f environment.yml

# 从显式 spec 文件创建（完全复现）
conda create -n myenv --file spec-file.txt

# 不安装默认包，最小环境
conda create -n myenv python=3.11 --no-default-packages
```

### 2. 激活与退出

```bash
conda activate myenv      # 进入环境
conda deactivate          # 退出当前环境

# 在脚本 / CI 中激活（非交互 shell）
eval "$(conda shell.bash hook)"
conda activate myenv

# 或直接执行，不激活
conda run -n myenv python app.py
```

### 3. 查看所有环境

```bash
conda env list
# 或
conda info --envs

# 查看环境详情
conda env export -n myenv
```

### 4. 克隆环境（快速复制）

```bash
conda create -n newenv --clone oldenv
```

> [!TIP]
> 克隆会复制整个环境，包括平台相关包。跨平台复现请用 `environment.yml`，不要用 clone。

### 5. 删除环境

```bash
conda env remove -n myenv
# 等价写法
conda remove -n myenv --all
```

### 6. 更新环境（配合 yml）

```bash
# 用 yml 更新已有环境，并删除 yml 中没有的包
conda env update -f environment.yml --prune
```

### 7. 导出与重建（项目复现关键）

```bash
# 导出完整环境（含平台、build string、pip 包）
conda env export -n myenv > environment.yml

# 只导出你显式安装的包（更干净、跨平台更稳）
conda env export -n myenv --from-history > environment.yml

# 从 yml 重建环境
conda env create -f environment.yml

# 完全锁定：导出显式 URL + hash
conda list --explicit > spec-file.txt
conda create -n myenv --file spec-file.txt
```

> [!WARNING]
> `conda env export` 默认带平台信息（如 `linux-64`）和 build string，跨平台可能失败。  
> 协作推荐 `--from-history`；生产/离线推荐 `--explicit`。

> [!TIP]
> **最佳实践**：每个项目一个环境，保留 `environment.yml` 用于协作，保留 `spec-file.txt` 用于离线复现。

---

## 三、包管理

### 1. 安装包

```bash
# 单包安装
conda install numpy

# 指定版本
conda install numpy=1.24

# 指定精确版本
conda install numpy=1.24.4=py311h...  # 一般不用手写 build string

# 从特定频道安装
conda install -c conda-forge scikit-learn

# 同时安装多个
conda install numpy pandas matplotlib

# 模拟安装（不真正安装）
conda install --dry-run numpy

# 只下载不安装
conda install --download-only numpy

# 离线安装
conda install --offline numpy
```

### 2. 查看已安装的包

```bash
conda list                  # 当前环境所有包
conda list numpy            # 查看特定包
conda list --revisions      # 环境历史版本
conda list --explicit       # 导出格式
```

### 3. 更新包

```bash
conda update numpy          # 更新指定包
conda update --all          # 更新当前环境所有包（谨慎！）
conda update conda          # 更新 conda 自身
```

> [!WARNING]
> `conda update --all` 可能触发大规模依赖变动，甚至降级。  
> 生产/论文环境不要随便跑，先 `--dry-run` 看影响。

### 4. 卸载包

```bash
conda remove numpy
conda remove numpy pandas   # 一次删多个
```

### 5. 回滚环境

conda 有环境快照，可以回滚：

```bash
conda list --revisions
conda install --revision 2   # 回到第 2 个版本
```

### 6. 清理缓存（节省磁盘）

```bash
conda clean --all           # 删索引缓存、tarball、未使用包
conda clean --dry-run --all # 先看会删什么
conda clean --packages      # 只删未使用的包
conda clean --tarballs      # 只删下载的压缩包
conda clean --index-cache   # 只删索引缓存
```

---

## 四、频道管理

- **`conda-forge`** 是最活跃的社区频道，通常比 `defaults` 更新、更全。
- 严格设置频道优先级，避免包冲突。
- `defaults` 在 2024 后有商业条款变化，很多团队已全面转 `conda-forge`。

```bash
# 添加 conda-forge 并设为首选（prepend 保证在最前面）
conda config --add channels conda-forge
conda config --set channel_priority strict

# 查看当前频道配置
conda config --show channels
conda config --show channel_priority

# 查看配置来源
conda config --show-sources

# 移除频道
conda config --remove channels conda-forge
```

`.condarc` 示例（推荐）：

```yaml
channels:
  - conda-forge
  - defaults
channel_priority: strict
show_channel_urls: true
```

> [!TIP]
> 📌 **建议顺序**：`conda-forge` > `defaults`，并且尽量只用 `conda-forge`。  
> 不要轻易混用不同渠道的核心库，尤其 `pytorch`、`cuda`、`numpy`、`mkl` 这类。

---

## 五、pip 与 conda 混用黄金法则

- **先用 conda 安装，再补 pip**。

```bash
conda install numpy pandas scipy
pip install some-special-package
```

- **conda 装的核心库不要再用 pip 升级或重装**，否则可能破坏依赖关系。
- **pip 装完不要再跑 `conda update --all`**，conda 会覆盖 pip 的包。
- **把 pip 包也写进 `environment.yml`**：

```yaml
name: myenv
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy=1.26
  - pandas
  - pip
  - pip:
      - some-special-package==1.2.3
```

- **导出时灵活使用 `--from-history` 与 `--explicit`**。
- **在 conda 环境里用 pip 时，务必用**：

```bash
python -m pip install ...
```

不要裸 `pip install`，避免装到别的环境。

> [!IMPORTANT]
> 混用顺序总结：  
> **conda 装二进制/核心库 → pip 补 conda 没有的纯 Python 包 → 不要再 conda update 覆盖 pip 包。**

---

## 六、依赖锁定与可复现

conda 原生没有 `pip-compile` 那样的锁文件，但有几种方案：

### 1. `environment.yml`（人读）

```bash
conda env export --from-history > environment.yml
```

### 2. `spec-file.txt`（完全复现，平台绑定）

```bash
conda list --explicit > spec-file.txt
conda create -n myenv --file spec-file.txt
```

### 3. `conda-lock`（跨平台锁，推荐）

```bash
pip install conda-lock
conda-lock -f environment.yml -p linux-64 -p osx-64
# 生成 conda-lock.yml
conda-lock install --name myenv conda-lock.yml
```

### 4. `conda env export` 带 pip 包

```yaml
dependencies:
  - python=3.11
  - numpy
  - pip:
      - requests==2.31.0
```

> [!TIP]
> 跨平台协作 → `conda-lock`；  
> 单平台离线部署 → `spec-file.txt`；  
> 日常开发 → `environment.yml --from-history`。

---

## 七、诊断命令

```bash
conda info                        # conda 自身信息
conda info --envs                 # 所有环境
conda config --show               # 所有配置
conda config --show-sources       # 配置来源
conda list                        # 当前环境包
conda list --revisions            # 环境历史
conda doctor                      # 检查环境健康（新版本）
conda search numpy                # 搜索包
conda search numpy --info         # 包详情
conda install --dry-run numpy     # 模拟安装
conda env export -n myenv         # 导出环境
```

---

## 八、速度优化（2024 后已变）

> [!IMPORTANT]
> **conda 23.10+ 已默认使用 libmamba solver，速度大幅提升。**  
> 以前“装 mamba 才能快”的说法已经过时。现在优先升级 conda，而不是装 mamba。

```bash
# 升级 conda 到最新
conda update -n base conda

# 确认 solver
conda config --show solver
# 如仍是 classic，可显式设置
conda config --set solver libmamba
```

国内镜像配置（清华源示例）：

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

其他提速手段：

- `conda clean --index-cache` 后重试。
- 指定版本范围，别让 solver 搜太大空间。
- 用 `micromamba` 替代（见下一节）。
- 用 `pixi` 做项目级环境。

---

## 九、micromamba / mamba / pixi

| 工具 | 说明 | 适用 |
|---|---|---|
| **conda** | 官方全功能 | 通用 |
| **mamba** | conda 的快速前端，现已内置 libmamba | 老习惯 |
| **micromamba** | 单二进制、无 base、极快 | 推荐给新项目、Docker、CI |
| **pixi** | 项目级 conda 生态工具，类似 poetry | 项目制开发 |

### micromamba 常用命令

```bash
# 安装（示例）
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba

# 创建环境
micromamba create -n myenv python=3.11 numpy pandas

# 激活
eval "$(micromamba shell hook -s bash)"
micromamba activate myenv

# 安装
micromamba install -c conda-forge scikit-learn

# 导出
micromamba env export -n myenv > environment.yml
```

> [!TIP]
> 对“云原生 + AIOps”路线：  
> - 本地实验：`micromamba`  
> - Docker 镜像：`mambaorg/micromamba`  
> - 纯 Python 项目：`uv + venv` 更轻。

---

## 十、Docker 与 CI

### 1. Docker 中用 micromamba（推荐）

```dockerfile
FROM mambaorg/micromamba:1.5-jammy

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
CMD ["python", "app.py"]
```

### 2. Docker 中用 conda（传统）

```dockerfile
FROM continuumio/miniconda3:latest

COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean --all --yes

ENV PATH=/opt/conda/envs/myenv/bin:$PATH
CMD ["python", "app.py"]
```

`.dockerignore`：

```text
.conda/
env/
__pycache__/
*.pyc
.git/
.pytest_cache/
```

### 3. CI 示例（GitHub Actions）

```yaml
- uses: mamba-org/setup-micromamba@v1
  with:
    environment-file: environment.yml
    cache-environment: true

- run: python -m pytest
```

或传统 conda：

```yaml
- uses: conda-incubator/setup-miniconda@v3
  with:
    environment-file: environment.yml
    activate-environment: myenv
    auto-activate: true

- run: conda list
```

---

## 十一、安全与磁盘

- **不要 `sudo conda install`**，也不要 `sudo` 运行 conda。
- 环境默认在 `~/miniconda3/envs/` 或 `~/anaconda3/envs/`，注意磁盘占用。
- 定期清理：

```bash
conda clean --all
conda clean --dry-run --all   # 先看
```

- 私有频道认证：`.condarc` 配合环境变量或 token，不要明文提交。
- 用 `conda doctor`（新版本）检查环境健康。
- 生产镜像不要把 `base` 环境暴露给用户，创建专用环境。

---

## 十二、conda vs venv 对比

| 维度 | venv + pip | conda / micromamba |
|---|---|---|
| 语言 | 仅 Python | 跨语言（Python、R、C 库） |
| 二进制依赖 | 靠 wheel | 原生管理 |
| 环境隔离 | 目录级 | 目录级 + 二进制 |
| 锁文件 | `requirements.txt`、`pip-tools`、`uv` | `environment.yml`、`spec-file.txt`、`conda-lock` |
| 速度 | pip 慢，uv 快 | libmamba 已快 |
| 体积 | 小 | 大 |
| 数据科学/ML | 一般 | 强 |
| Web/纯 Python | 推荐 | 可用但偏重 |
| Docker | 简单 | 需额外镜像 |

> [!TIP]
> 结合你的路线：  
> **Java 主线 → Maven/Gradle + Docker**  
> **Python AI 副线 → venv + uv 起步，数据科学/ML 再上 micromamba/conda**

---

## 十三、常见陷阱速查

| 问题 | 解决方法 |
| ------ | ---------- |
| 解依赖太久 | 升级 conda 用 libmamba；`conda clean --index-cache`；指定版本范围 |
| 误删 base 环境 | 重装 Miniconda/Anaconda |
| `conda: command not found` | `conda init` 或手动 source 配置文件 |
| 激活失败 | 新 shell 里执行 `eval "$(conda shell.bash hook)"` |
| pip 和 conda 冲突 | 先 conda 后 pip；核心库只用 conda；别 `conda update --all` 覆盖 pip |
| `conda env export` 跨平台失败 | 用 `--from-history` 或 `conda-lock` |
| `conda update --all` 把环境搞崩 | 先 `--dry-run`；用 `conda install --revision` 回滚 |
| 环境占磁盘太大 | `conda clean --all`；删旧环境；用 micromamba |
| Docker 镜像太大 | 用 micromamba + `clean --all`；多阶段构建 |
| `defaults` 商业条款 | 全面转 `conda-forge` |
| channel_priority 不严格导致冲突 | `conda config --set channel_priority strict` |
| 装到 base | 永远不激活 base 装项目依赖 |
| pip 装完 conda 不认 | conda 不知道 pip 包；导出时用 `pip:` 段 |

---

## 十四、最佳实践清单

- base 只放 conda 自身。
- 每个项目一个环境。
- 优先 `conda-forge` + `channel_priority: strict`。
- 先用 conda 装核心库，再用 `python -m pip` 补包。
- 不要 `conda update --all`，除非你清楚影响。
- 用 `environment.yml`（`--from-history`）协作。
- 用 `conda-lock` 或 `spec-file.txt` 做完全复现。
- Docker 用 micromamba。
- CI 用 `setup-micromamba`。
- 定期 `conda clean --all`。
- 不要 `sudo conda`。
- 需要轻量/极速时用 micromamba。

---

## 十五、项目结构模板

```text
myproject/
├── environment.yml         # 主环境声明
├── spec-file.txt           # 可选，完全复现
├── conda-lock.yml          # 可选，跨平台锁
├── .condarc                # 可选，项目级频道配置
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
.conda/
env/
__pycache__/
*.pyc
.pytest_cache/
```

`environment.yml` 示例：

```yaml
name: myproject
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy=1.26
  - pandas
  - scikit-learn
  - pip
  - pip:
      - fastapi==0.110.0
      - uvicorn
```

---

## 十六、改进版四步走

```bash
# 1. 创建环境
conda create -n myenv python=3.11

# 2. 激活
conda activate myenv

# 3. conda 装主力包，pip 补漏
conda install -c conda-forge numpy pandas scikit-learn
python -m pip install some-special-package

# 4. 锁定环境
conda env export --from-history > environment.yml
conda list --explicit > spec-file.txt
```

> [!TIP]
> ✨ **记住四步走**：
>
> 1. 创建环境：`conda create -n myenv python=3.11`  
> 2. 激活环境：`conda activate myenv`  
> 3. conda 装主力包 → pip 补漏  
> 4. 锁定环境：`environment.yml` + `spec-file.txt`

---

## 十七、常用命令速查表

| 操作 | 命令 |
|---|---|
| 创建环境 | `conda create -n myenv python=3.11` |
| 项目内环境 | `conda create -p ./.conda python=3.11` |
| 克隆环境 | `conda create -n newenv --clone oldenv` |
| 激活 | `conda activate myenv` |
| 退出 | `conda deactivate` |
| 列出环境 | `conda env list` |
| 删除环境 | `conda env remove -n myenv` |
| 更新环境 | `conda env update -f environment.yml --prune` |
| 导出（推荐） | `conda env export --from-history > environment.yml` |
| 导出完全复现 | `conda list --explicit > spec-file.txt` |
| 从 yml 重建 | `conda env create -f environment.yml` |
| 安装包 | `conda install -c conda-forge numpy` |
| 指定版本 | `conda install numpy=1.24` |
| 模拟安装 | `conda install --dry-run numpy` |
| 查看包 | `conda list` / `conda list numpy` |
| 更新包 | `conda update numpy` |
| 卸载包 | `conda remove numpy` |
| 回滚 | `conda install --revision 2` |
| 清缓存 | `conda clean --all` |
| 添加频道 | `conda config --add channels conda-forge` |
| 严格优先级 | `conda config --set channel_priority strict` |
| 看配置 | `conda config --show` |
| 非交互执行 | `conda run -n myenv python app.py` |
| solver 设置 | `conda config --set solver libmamba` |
| micromamba 创建 | `micromamba create -n myenv python=3.11` |
| micromamba 安装 | `micromamba install -c conda-forge numpy` |
| 跨平台锁 | `conda-lock -f environment.yml -p linux-64` |

---

完成于 2026-05
改进于 2026-10-15