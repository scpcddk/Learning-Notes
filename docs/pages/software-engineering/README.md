# 软件工程与计算机基础

板块对应仓库根目录的 [软件工程与计算机基础](../../../软件工程与计算机基础/)，网站入口为 `/software-engineering/`。

| 科目 | 页面地址 | 原始资料 |
|---|---|---|
| 计算机组成原理 | `/computer-organization/` | [计算机组成原理](../../../软件工程与计算机基础/计算机组成原理/) |
| 计算机网络 | `/computer-networking/` | [计算机网络](../../../软件工程与计算机基础/计算机网络/) |
| 软件测试 | `/software-testing/` | [软件测试](../../../软件工程与计算机基础/软件测试/) |
| 软件需求与分析 | `/software-requirements/` | [软件需求与分析](../../../软件工程与计算机基础/软件需求与分析/) |

计算机组成原理和软件需求与分析提供站内阅读，按原目录收录笔记、课件和习题。计算机网络和软件测试提供原资料入口。科目页可通过面包屑返回板块目录。新增科目后，统一构建时会自动生成相应科目页。

首页卡片和板块目录共用[新版总封面](阅读资源/software-engineering-hero-v2.webp)。各科目的入口卡片与科目页共用各自的封面。

| 科目 | 封面 | 最终提示词 |
|---|---|---|
| 计算机组成原理 | [图片](../computer-organization/阅读资源/computer-organization-hero-v3.webp) | [提示词](../computer-organization/阅读资源/computer-organization-hero-v3.prompt.txt) |
| 计算机网络 | [图片](../computer-networking/阅读资源/computer-networking-hero.webp) | [提示词](../computer-networking/阅读资源/computer-networking-hero.prompt.txt) |
| 软件测试 | [图片](../software-testing/阅读资源/software-testing-hero.webp) | [提示词](../software-testing/阅读资源/software-testing-hero.prompt.txt) |
| 软件需求与分析 | [图片](../software-requirements/阅读资源/software-requirements-hero.webp) | [提示词](../software-requirements/阅读资源/software-requirements-hero.prompt.txt) |

新封面由内置图像生成工具生成：1536×1024、3:2、暖白背景、墨绿与鼠尾草绿玻璃、黄铜连接件。新版把分散面板收拢为一座螺旋上升的玻璃模块建筑，用连续黄铜路径与底层处理器表现软件的分层、依赖和计算基础；无文字、不透明背景。它是装饰性插图，不代替精确架构图。

[最终生成提示词](阅读资源/software-engineering-hero-v2.prompt.txt) 与图片一同保存。[第一版](阅读资源/software-engineering-hero.webp)及[第一版提示词](阅读资源/software-engineering-hero.prompt.txt)保留，供后续比较。构建时自动生成带内容指纹的响应式 WebP 尺寸，页面不直接下载大尺寸 PNG。

按 [统一构建说明](../README.md) 生成和预览。`docs/site` 为构建产物，不直接手工修改；本地修改在提交并推送后由 GitHub Actions 发布。
