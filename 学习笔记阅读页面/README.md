# 学习笔记阅读页面

[学习首页](https://scpcddk.github.io/Learning-Notes/) · [数学科目页](https://scpcddk.github.io/Learning-Notes/math/) · [高等数学](https://scpcddk.github.io/Learning-Notes/calculus/) · [线性代数](https://scpcddk.github.io/Learning-Notes/linear-algebra/) · [离散数学](https://scpcddk.github.io/Learning-Notes/discrete-math/) · [算法](https://scpcddk.github.io/Learning-Notes/algorithms/)

网站首页展示仓库根目录的知识板块。点击数学进入数学科目页，再选择高等数学、线性代数、离散数学等；点击算法进入算法阅读页。其他板块先展示现有目录，子项链接到仓库原笔记，后续可逐步接入阅读页。

访客可从仓库 README 进入 [数学导航](../数学/README.md) 或 [算法导航](../算法/README.md)，选择内容后打开在线阅读页。

## 文件布局

页面相关文件集中在仓库根目录的“学习笔记阅读页面”文件夹，数学、算法目录保留笔记、课件和习题。

| 位置 | 内容 |
| --- | --- |
| [build_site.py](build_site.py) | 四个科目共用的生成、课件打包与链接检查入口，篇目配置也在此维护 |
| [index.html](index.html) | 一级板块与科目目录共用的导航模板，包含专用样式 |
| [calculus/](calculus/) | 高等数学模板、精要内容、生成的离线页与图片、公式组件 |
| [linear-algebra/](linear-algebra/) | 线性代数模板、生成的离线页与图片、公式组件 |
| [discrete-math/](discrete-math/) | 离散数学模板与封面；构建时直接读取数学目录的 Markdown 和 PDF |
| [algorithms/](algorithms/) | 算法阅读模板与封面；课程、专题、源码、题单、课件统一生成 |
| [vendor/](vendor/README.md) | Mozilla PDF.js 5.4.624 官方发行包及许可证 |

每页专用的样式和交互代码并入对应 HTML 模板，不再另设科目生成脚本或 CSS、JS 配置文件。第三方公式组件与 PDF 阅读器保持原有资源结构和许可证。

## 生成与发布

在仓库根目录只需运行：

~~~powershell
python -m pip install markdown-it-py==4.0.0
python 学习笔记阅读页面/build_site.py --output "$env:TEMP/LearningNotes-math-site"
~~~

统一脚本先更新高等数学和线性代数的离线 HTML，再打包数学与算法的在线站点。Markdown 原笔记链接转换为 GitHub 地址，科目阅读页之间保留网站内部跳转，最后检查页面和资源链接。

[发布工作流](../.github/workflows/pages.yml) 也只调用这一条构建命令。修改仓库笔记、目录或这里的模板后，提交并推送到 main，GitHub Actions 会自动生成并发布；发布成功后，线上显示新内容。尚未推送的本地修改不会影响网站。

PowerPoint 课件已在原课件目录转换为 PDF 并替换对应 PPTX，不保留两套课件或额外导出目录。原文件的历史版本仍可通过 Git 提交记录查阅。

## 本地阅读

高等数学与线性代数可直接打开各自目录中的速查笔记.html；单独复制时携带该科目完整文件夹，正文、搜索和公式不依赖网络。离开仓库后，“查看 Markdown 原笔记”等仓库链接不保证存在。

离散数学与算法的 PDF 阅读器需要 HTTP 服务。构建后运行：

~~~powershell
python 学习笔记阅读页面/build_site.py --output "$env:TEMP/LearningNotes-math-site" --serve
~~~

然后在浏览器访问 http://127.0.0.1:8768/。

`--serve` 会在构建后启动本机预览，并设置 PDF.js 所需的模块脚本类型，避免 Windows 文件关联导致 `.mjs` 无法载入。可用 `--serve 8772` 更换端口。

离散数学收录15份课堂课件、9份个人笔记与练习、2份历年试卷。PDF 可在线翻页、搜索、缩放、打印、下载并记住上次页码；两份历年试卷为扫描件，正文暂不支持文字搜索。已有答案的 Markdown 习题提供折叠解析。

封面使用内置 imagegen 生成，图的结点与边、集合交叠与树形结构体现离散数学主题，最终提示词保存在 [discrete-math-hero.prompt.txt](discrete-math/discrete-math-hero.prompt.txt)。

算法页收录九章课程与附录、17篇竞赛专题、2份源码、8份题单，以及19份按内容去重的课件资料。代码支持高亮和复制，首页有可逐步操作的排序演示。PDF 在线阅读，PPTX、DOCX 提供原件入口，既有课件无需重复保存。

算法封面使用内置 imagegen，采用用户选定的第一张立体排序柱、二叉树与状态网格图：[封面](algorithms/algorithms-hero.png) · [提示词](algorithms/algorithms-hero.prompt.txt)。

首页根据仓库一级目录生成知识板块，排除隐藏目录、docs 和阅读页面配置目录；新增一级知识板块后也会生成相应目录入口。发布工作流在 main 更新后统一重新构建。
