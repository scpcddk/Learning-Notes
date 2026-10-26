# 云原生阅读页

在线入口：https://scpcddk.github.io/Learning-Notes/cloud-native/

使用 `../build_site.py` 自动读取仓库 `云原生/` 下的 Markdown、HTML 图解、PDF 与课件。与 Java、Python 共用 `../programming/阅读页模板.html`，统一维护阅读模式、搜索、目录、主题与代码复制功能。页面相关源文件在 docs，生成站点位于被 Git 忽略的 `docs/site`。

首页展示 Docker、DevOps、数据库与中间件、运维与服务部署，以及“待学与拓展”五个板块。所有空白笔记集中归入“待学与拓展”，按原主题分组；当前共 10 篇。补上正文后，下次构建自动回到对应板块，原文件位置和篇目锚点不变。Kubernetes、可观测性、微服务目前只有空白笔记，首页不单独展示。

“数据库与中间件”先展示 MySQL、Nginx、EMQX、MinIO、SRS 五个主题入口，点击后才显示该主题的子目录、笔记和资料；“运维与服务部署”先选择换热站或 ANIC 项目。侧栏同步只展开当前主题，面包屑和返回链接保留层级。搜索覆盖全部板块和待学主题，已有文章与小节地址继续有效；旧的空白板块入口转到“待学与拓展”。

内容完全相同的非空 Markdown 只保留一个阅读入口，优先使用项目部署目录中的版本；指向重复文件的链接转到同一入口。有差异的同名手册分别保留。原笔记不移动、不删除。

封面由内置 imagegen 生成，以玻璃云朵、服务器、容器与数据库体现主题，与数学和编程语言页面的米白、墨绿、黄铜材质保持一致：[封面](阅读资源/cloud-native-hero.png) · [最终提示词](阅读资源/cloud-native-hero.prompt.txt)。

已有内容的四个板块使用各自的 imagegen 封面，采用与总封面一致的材质与配色；“待学与拓展”为文字卡片。之前生成的 Kubernetes、可观测性、微服务封面保留在 `阅读资源/`，这些板块出现正文后会自动使用。主题入口为文字卡片。封面保留完整比例并延迟加载，小屏幕切换为单列。

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
