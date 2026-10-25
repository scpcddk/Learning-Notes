# 数学阅读网站

在线入口：[数学首页](https://scpcddk.github.io/Learning-Notes/) · [高等数学](https://scpcddk.github.io/Learning-Notes/calculus/) · [线性代数](https://scpcddk.github.io/Learning-Notes/linear-algebra/)。

## 从 GitHub 进入

仓库 README → [数学导航](../../数学/README.md) → 科目导航 → 在线阅读页。

README 中的普通仓库链接仍用于查阅 Markdown、课件与试卷；在线入口使用 GitHub Pages 展示 HTML、公式和交互。

## 自动更新

发布配置位于 [.github/workflows/pages.yml](../../.github/workflows/pages.yml)。main 分支上数学笔记、网站模板、构建脚本或工作流变更时，自动执行：

1. 安装固定版本的 Markdown 渲染依赖。
2. 分别运行高等数学与线性代数的生成脚本。
3. 用 [build_site.py](build_site.py) 打包数学首页、阅读页和配套资源。
4. 上传 Pages 构建产物并发布。

构建只打包阅读网站所需的文件，不复制整个仓库。阅读页中的 Markdown 原笔记、课件与目录链接会转换为 GitHub 地址；两套阅读页之间的链接则保留为网站内部跳转。本地离线阅读页不受影响。

也可在 GitHub 的 Actions 页面手动运行 “Publish math reading pages”。

## 本地构建

在仓库根目录运行：

~~~powershell
python -m pip install markdown-it-py==4.0.0
python "数学/高等数学/阅读页面/生成阅读页.py"
python "数学/线性代数/阅读页面/生成阅读页.py"
python docs/pages/build_site.py --output "$env:TEMP/LearningNotes-math-site"
~~~

构建输出包含首页、两个科目的阅读页面、公式组件与图片。若更换仓库，构建脚本支持通过 repository 参数指定新的 owner/name；README 中的在线地址需要相应更新。
