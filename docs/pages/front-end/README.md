# 前端基础阅读页

在线入口：[前端基础](https://scpcddk.github.io/Learning-Notes/front-end/)。

共用 [阅读页模板](../programming/阅读页模板.html)，构建脚本自动读取仓库 `前端基础/` 目录中的原笔记。首页只有一张总封面，内部按「标记与排版」「JavaScript」「Vue」展示文字卡片；进入板块后阅读笔记，每个板块保留自己的「待学」，HTML 与 CSS 空笔记归入标记与排版的待学目录。补充正文后会在下次构建时自动回到所属板块的正常笔记列表。

支持全文搜索、目录速览与完整笔记切换、代码高亮与复制、本篇目录、深色模式和移动端阅读。LaTeX 笔记中的行内公式使用本地 MathJax，代码示例保留字面内容。

新增、修改或删除 Markdown 后，提交并推送到 main，GitHub Actions 会重新构建并发布，无需手动维护篇目列表。源文件重命名或移动会改变其阅读入口。

封面使用内置 imagegen 生成，浏览器、分层页面、鼠标指针与代码符号体现前端主题，材质与既有封面保持一致：[封面](阅读资源/frontend-hero.png) · [提示词](阅读资源/frontend-hero.prompt.txt)。内部不增加封面。

本地生成：`python docs/pages/build_site.py --output docs/site`。预览可追加 `--serve`。回归检查：`python -m unittest discover -s docs/pages -p 'test_frontend.py'`。
