# 云原生阅读页

在线入口：https://scpcddk.github.io/Learning-Notes/cloud-native/

使用 `../build_site.py` 自动读取仓库 `云原生/` 下的 Markdown、HTML 图解、PDF 与课件。与 Java、Python 共用 `../programming/阅读页模板.html`，统一维护阅读模式、搜索、目录、主题与代码复制功能。页面相关源文件在 docs，生成站点位于被 Git 忽略的 `docs/site`。

首页按现有目录展示 Docker、DevOps、数据库与中间件、运维与服务部署、Kubernetes、可观测性、微服务七个板块。进入板块后才展开子目录与笔记；全文搜索覆盖全部板块。空白笔记显示“待补充”，不计入已有正文的笔记数。新文件与目录在下次构建时自动收录。

内容完全相同的非空 Markdown 只保留一个阅读入口，优先使用项目部署目录中的版本；指向重复文件的链接转到同一入口。有差异的同名手册分别保留。原笔记不移动、不删除。

封面由内置 imagegen 生成，以玻璃云朵、服务器、容器与数据库体现主题，与数学和编程语言页面的米白、墨绿、黄铜材质保持一致：[封面](阅读资源/cloud-native-hero.png) · [最终提示词](阅读资源/cloud-native-hero.prompt.txt)。

构建：`python docs/pages/build_site.py --output docs/site`。
检查：`python -m unittest discover -s docs/pages -p 'test_*.py'`。

修改原 Markdown 或新增笔记后，提交并推送 main，GitHub Actions 会重新生成和发布。
