# 数学阅读网站

[数学首页](https://scpcddk.github.io/Learning-Notes/) · [高等数学](https://scpcddk.github.io/Learning-Notes/calculus/) · [线性代数](https://scpcddk.github.io/Learning-Notes/linear-algebra/) · [离散数学](https://scpcddk.github.io/Learning-Notes/discrete-math/)

访客可从仓库 README 进入 [数学导航](../../数学/README.md)，选择科目后打开在线阅读页。

## 文件布局

页面相关文件集中在这里，数学目录保留笔记、课件和习题。

| 位置 | 内容 |
| --- | --- |
| [build_site.py](build_site.py) | 三科共用的生成、课件打包与链接检查入口，篇目配置也在此维护 |
| [index.html](index.html) | 数学首页，包含专用样式 |
| [calculus/](calculus/) | 高等数学模板、精要内容、生成的离线页与图片、公式组件 |
| [linear-algebra/](linear-algebra/) | 线性代数模板、生成的离线页与图片、公式组件 |
| [discrete-math/](discrete-math/) | 离散数学模板与封面；构建时直接读取数学目录的 Markdown 和 PDF |
| [vendor/](vendor/README.md) | Mozilla PDF.js 5.4.624 官方发行包及许可证 |

每页专用的样式和交互代码并入对应 HTML 模板，不再另设科目生成脚本或 CSS、JS 配置文件。第三方公式组件与 PDF 阅读器保持原有资源结构和许可证。

## 生成与发布

在仓库根目录只需运行：

~~~powershell
python -m pip install markdown-it-py==4.0.0
python docs/pages/build_site.py --output "$env:TEMP/LearningNotes-math-site"
~~~

统一脚本先更新高等数学和线性代数的离线 HTML，再打包三个科目的在线站点。Markdown 原笔记链接转换为 GitHub 地址，科目阅读页之间保留网站内部跳转，最后检查页面和资源链接。

[发布工作流](../../.github/workflows/pages.yml) 也只调用这一条构建命令。修改数学 Markdown、PDF 或这里的模板后，提交并推送到 main，GitHub Actions 会自动生成并发布；发布成功后，线上显示新内容。尚未推送的本地修改不会影响网站。

PowerPoint 课件已在原课件目录转换为 PDF 并替换对应 PPTX，不保留两套课件或额外导出目录。原文件的历史版本仍可通过 Git 提交记录查阅。

## 本地阅读

高等数学与线性代数可直接打开各自目录中的速查笔记.html；单独复制时携带该科目完整文件夹，正文、搜索和公式不依赖网络。离开仓库后，“查看 Markdown 原笔记”等仓库链接不保证存在。

离散数学的 PDF 阅读器需要 HTTP 服务。构建后运行：

~~~powershell
python -m http.server 8768 --bind 127.0.0.1 --directory "$env:TEMP/LearningNotes-math-site"
~~~

然后在浏览器访问 http://127.0.0.1:8768/。

离散数学收录15份课堂课件、9份个人笔记与练习、2份历年试卷。PDF 可在线翻页、搜索、缩放、打印、下载并记住上次页码；两份历年试卷为扫描件，正文暂不支持文字搜索。已有答案的 Markdown 习题提供折叠解析。

封面使用内置 imagegen 生成，图的结点与边、集合交叠与树形结构体现离散数学主题，最终提示词保存在 [discrete-math-hero.prompt.txt](discrete-math/discrete-math-hero.prompt.txt)。
