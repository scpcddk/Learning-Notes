# 学习笔记阅读页面

[学习首页](https://scpcddk.github.io/Learning-Notes/) · [数学科目页](https://scpcddk.github.io/Learning-Notes/math/) · [高等数学](https://scpcddk.github.io/Learning-Notes/calculus/) · [线性代数](https://scpcddk.github.io/Learning-Notes/linear-algebra/) · [离散数学](https://scpcddk.github.io/Learning-Notes/discrete-math/) · [算法](https://scpcddk.github.io/Learning-Notes/algorithms/) · [编程语言](https://scpcddk.github.io/Learning-Notes/programming-languages/) · [Linux](https://scpcddk.github.io/Learning-Notes/linux/)

网站首页展示仓库根目录的知识板块。点击数学进入数学科目页，再选择高等数学、线性代数、离散数学等；编程语言进入语言总览，再选择 C/C++、Java 或 Python。算法和 Linux 可直接进入各自的阅读页。其他板块展示现有目录，子项链接到仓库原笔记。

访客可从仓库 README 进入 [数学导航](../../数学/README.md) 或 [算法导航](../../算法/README.md)，选择内容后打开在线阅读页。

## 文件布局

页面相关文件集中在 `docs/pages`，数学、算法、Linux 目录保留原笔记、课件和习题。`docs/README.md` 用于仓库介绍，`docs/assets` 保存介绍配图，`docs/pages` 维护阅读网站。

| 位置 | 内容 |
| --- | --- |
| [build_site.py](build_site.py) | 各科目共用的生成、资源打包与链接检查入口，篇目配置也在此维护 |
| [index.html](index.html) | 一级板块与科目目录共用的导航模板，包含专用样式 |
| [calculus/](calculus/) | 高等数学模板、精要内容、生成的离线页与图片、公式组件 |
| [linear-algebra/](linear-algebra/) | 线性代数模板、生成的离线页与图片、公式组件 |
| [discrete-math/](discrete-math/) | 离散数学模板与封面；构建时直接读取数学目录的 Markdown 和 PDF |
| [algorithms/](algorithms/) | 算法阅读模板与封面；课程、专题、源码、题单、课件统一生成 |
| [linux/](linux/) | Linux 阅读模板与封面；沿核心知识、Shell.md、补充理解、习题组织内容 |
| [programming/](programming/) | 编程语言共用阅读模板、四张封面及提示词；自动收录各语言目录的笔记、图解与资料 |
| [vendor/](vendor/README.md) | Mozilla PDF.js 5.4.624 官方发行包及许可证 |

每页专用的样式和交互代码并入对应 HTML 模板，不再另设科目生成脚本或 CSS、JS 配置文件。第三方公式组件与 PDF 阅读器保持原有资源结构和许可证。

## 生成与发布

在仓库根目录只需运行：

~~~powershell
python -m pip install markdown-it-py==4.0.0
python docs/pages/build_site.py --output docs/site
~~~

统一脚本先更新高等数学和线性代数的离线 HTML，再打包数学与算法的在线站点。Markdown 原笔记链接转换为 GitHub 地址，科目阅读页之间保留网站内部跳转，最后检查页面和资源链接。

[发布工作流](../../.github/workflows/pages.yml) 也只调用这一条构建命令。修改仓库笔记、目录或这里的模板后，提交并推送到 main，GitHub Actions 会自动生成并发布；发布成功后，线上显示新内容。尚未推送的本地修改不会影响网站。

PowerPoint 课件已在原课件目录转换为 PDF 并替换对应 PPTX，不保留两套课件或额外导出目录。原文件的历史版本仍可通过 Git 提交记录查阅。

## 本地阅读

高等数学与线性代数可直接打开各自目录中的速查笔记.html；单独复制时携带该科目完整文件夹，正文、搜索和公式不依赖网络。离开仓库后，“查看 Markdown 原笔记”等仓库链接不保证存在。

离散数学与算法的 PDF 阅读器需要 HTTP 服务。构建后运行：

~~~powershell
python docs/pages/build_site.py --output docs/site --serve
~~~

然后在浏览器访问 http://127.0.0.1:8768/。

`--serve` 会在构建后启动本机预览，并设置 PDF.js 所需的模块脚本类型，避免 Windows 文件关联导致 `.mjs` 无法载入。可用 `--serve 8772` 更换端口。

离散数学收录15份课堂课件、9份个人笔记与练习、2份历年试卷。PDF 可在线翻页、搜索、缩放、打印、下载并记住上次页码；两份历年试卷为扫描件，正文暂不支持文字搜索。已有答案的 Markdown 习题提供折叠解析。

封面使用内置 imagegen 生成，图的结点与边、集合交叠与树形结构体现离散数学主题，最终提示词保存在 [discrete-math-hero.prompt.txt](discrete-math/discrete-math-hero.prompt.txt)。

算法页收录九章课程与附录、17篇竞赛专题、2份源码、8份题单，以及19份按内容去重的课件资料。代码支持高亮和复制，首页有可逐步操作的排序演示。PDF 在线阅读，PPTX、DOCX 提供原件入口，既有课件无需重复保存。

算法封面使用内置 imagegen，采用用户选定的第一张立体排序柱、二叉树与状态网格图：[封面](algorithms/algorithms-hero.png) · [提示词](algorithms/algorithms-hero.prompt.txt)。

首页根据仓库一级目录生成知识板块，排除隐藏目录和 docs；新增一级知识板块后也会生成相应目录入口。发布工作流在 main 更新后统一重新构建。源码目录的位置不改变公开站点地址，首页和各科目的 URL 保持不变。

## Linux 阅读页

Linux 沿用原笔记目录：核心知识、根目录的 Shell.md、补充理解、习题。当前阅读页包含 8 篇 Markdown 笔记与习题，同目录新增的 Markdown 和 HTML 文件也会在构建时收录。

与线性代数一致，每篇现有笔记提供“精要速查 / 完整笔记”切换，并记住浏览器中的阅读模式。完整笔记从 Linux 目录的 Markdown 生成；[精要速查.md](linux/精要速查.md) 单独整理方法、要点和易错点，不截断原文。习题速查展示复习范围与作答建议，完整笔记保留全部题目、默认折叠的参考答案及练习后的补充笔记。

《命令大全》的精要模式整合命令分类卡片，支持按命令、用途和参数检索；卡片的描述、语法、参数及完整用法锚点均从同一份 Markdown 自动生成。点击“阅读完整用法”会切换到完整模式并定位到相应命令。原 `Linux/核心知识/知识图谱.html` 保留在笔记目录中，网站不再单独展示重复入口；已有 `#command-map` 地址转到命令大全的精要模式。

侧栏支持按分类和全文关键词筛选，正文提供本篇目录、代码复制、相邻笔记、深色模式与打印。模式切换、本篇锚点、卡片跳转与 Markdown 原笔记入口分别保留。

Linux 不使用数学公式转换，确保 `$name`、`$?` 等 Shell 内容按原文展示。源 Markdown 仍在 Linux 目录维护，构建脚本统一生成 `/linux/` 阅读入口，并将首页 Linux 板块替换为带封面的阅读卡片。

封面通过内置 imagegen 生成，保留 Tux 企鹅特征，配合终端、文件夹与服务器元素；材质和配色与既有科目封面保持一致：[封面](linux/linux-hero.png) · [提示词](linux/linux-hero.prompt.txt)。

## 编程语言阅读页

访问 `/programming-languages/` 选择语言，再进入 `c-cpp/`、`java/`、`python/`。页面模板、配图和提示词位于 `docs/pages/programming`；本地生成站点统一放在 `docs/site`，该目录不提交到 Git。GitHub Actions 使用同一命令生成和发布。

正文从仓库的 `编程语言/` 目录读取，不复制维护另一套 Markdown。构建会自动扫描语言子目录及其全部层级，按原目录分组收录 Markdown、HTML 图解、PDF 和 Office、ZIP 资料；空笔记显示“待补充”。新增语言子目录也会自动生成入口，未知语言暂时沿用编程语言总封面。

Java 和 Python 采用“语言总览 → 学习板块 → 笔记”的三级阅读结构。Java 总览只展示 Java基础语法、MyBatis、Spring、实战日志四个板块；Python 按原目录展示基础语法、后端、环境与依赖管理、习题、课件。进入板块后才展开该板块的子目录和笔记，侧栏同步只展开当前板块，面包屑与返回入口保留层级。全文搜索仍覆盖该语言的全部笔记，可直接打开其他板块中的匹配内容。C/C++ 的文件较少，保持直接阅读。

修改已有笔记、新增 Markdown 或新增语言目录后，提交并推送到 `main`，自动构建成功即可更新网站，无需逐篇修改章节配置。阅读入口和正文锚点由相对路径生成；文件更名或移动会改变对应入口。

阅读页支持按类型和全文关键词筛选、目录速览与完整笔记切换、代码高亮和复制、本篇目录、相邻笔记、深色模式、打印，以及浏览器内的上次阅读记录。目录速览直接使用原文章节标题，不自动编写精要摘要。代码中的 `$`、`#{}`、`${}` 等按原文展示。

现有 Markdown 互链转为站内阅读入口，配图随站点打包。HTML 图解在隔离的 iframe 中展示，PDF 使用已有 PDF.js 阅读器，Office 与 ZIP 资料提供 GitHub 原文件入口。PDF 和图解推荐通过本地 HTTP 预览阅读。

四张封面使用内置图像生成工具制作，与数学页面保持同一视觉风格；Java 使用用户选定的第一版。查看 [封面与最终提示词](programming/阅读资源/README.md)。

自动收录与 Markdown 渲染的回归检查：`python -m unittest discover -s docs/pages -p test_programming.py`。检查新增、修改和移除笔记，新增语言，站内锚点、跨语言链接、配图、空笔记，以及代码中的特殊字符。
