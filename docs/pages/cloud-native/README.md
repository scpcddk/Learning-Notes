# 云原生阅读页

在线入口：https://scpcddk.github.io/Learning-Notes/cloud-native/

使用 `../build_site.py` 自动读取仓库 `云原生/` 下的 Markdown、HTML 图解、PDF 与课件。与 Java、Python 共用 `../programming/阅读页模板.html`，统一维护阅读模式、搜索、目录、主题与代码复制功能。页面相关源文件在 docs，生成站点位于被 Git 忽略的 `docs/site`。

首页保留 Docker、DevOps、数据库与中间件、运维与服务部署、Kubernetes、可观测性、微服务七个板块。每个板块内部都有独立的“待学”入口，只收纳该板块的空白笔记；没有空白笔记时显示“当前没有待学笔记”。当前共 10 篇空白笔记，分别属于数据库与中间件、Kubernetes、可观测性和微服务。补充正文后，下次构建自动加入所属板块的正常目录，原文件位置和篇目锚点不变。

“数据库与中间件”先展示 MySQL、Nginx、EMQX、MinIO、SRS 和“待学”入口，点击后再显示笔记；“运维与服务部署”先选择换热站、ANIC 项目或“待学”。Docker、DevOps 等目录较少的板块直接展示已有笔记，另提供“待学”卡片。侧栏同步只展开当前主题，面包屑和返回链接保留层级。搜索覆盖全部板块，已有文章与小节地址继续有效。之前的全局“待学与拓展”入口返回云原生总览。

内容完全相同的非空 Markdown 只保留一个阅读入口，优先使用项目部署目录中的版本；指向重复文件的链接转到同一入口。有差异的同名手册分别保留。原笔记不移动、不删除。

封面由内置 imagegen 生成，以玻璃云朵、服务器、容器与数据库体现主题，与数学和编程语言页面的米白、墨绿、黄铜材质保持一致：[封面](阅读资源/cloud-native-hero.png) · [最终提示词](阅读资源/cloud-native-hero.prompt.txt)。

七个板块使用各自的 imagegen 封面，采用与总封面一致的材质与配色。板块内的主题和“待学”入口为文字卡片。封面保留完整比例并延迟加载，小屏幕切换为单列。

| 板块 | 封面 | 最终提示词 | 主题 |
| --- | --- | --- | --- |
| Docker | [图片](阅读资源/section-docker.png) | [提示词](阅读资源/section-docker.prompt.txt) | 鲸鱼与集装箱 |
| DevOps | [图片](阅读资源/section-devops.png) | [提示词](阅读资源/section-devops.prompt.txt) | 无限循环与交付流水线 |
| 数据库与中间件 | [图片](阅读资源/section-database-middleware.png) | [提示词](阅读资源/section-database-middleware.prompt.txt) | 数据库与消息路由 |
| 运维与服务部署 | [图片](阅读资源/section-operations-deployment.png) | [提示词](阅读资源/section-operations-deployment.prompt.txt) | 服务器、扳手与部署箭头 |
| Kubernetes | [图片](阅读资源/section-kubernetes.png) | [提示词](阅读资源/section-kubernetes.prompt.txt) | 七辐舵轮与容器节点 |
| 可观测性 | [图片](阅读资源/section-observability.png) | [提示词](阅读资源/section-observability.prompt.txt) | 放大镜、指标、日志与链路 |
| 微服务 | [图片](阅读资源/section-microservices.png) | [提示词](阅读资源/section-microservices.prompt.txt) | 独立服务模块与连接 |

构建：`python docs/pages/build_site.py --output docs/site`。
检查：`python -m unittest discover -s docs/pages -p 'test_*.py'`。

修改原 Markdown 或新增笔记后，提交并推送 main，GitHub Actions 会重新生成和发布。
