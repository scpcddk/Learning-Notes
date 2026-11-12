# 前端基础阅读页

在线入口：[前端基础](https://scpcddk.github.io/Learning-Notes/front-end/)。

共用 [阅读页模板](../programming/阅读页模板.html)，构建脚本自动读取仓库 `前端基础/` 目录中的原笔记。总览页按「标记与排版」「JavaScript」「Vue」展示带封面的卡片；进入板块后阅读笔记，每个板块保留自己的「待学」，HTML 与 CSS 空笔记归入标记与排版的待学目录。补充正文后会在下次构建时自动回到所属板块的正常笔记列表。

支持全文搜索、目录速览与完整笔记切换、代码高亮与复制、本篇目录、深色模式和移动端阅读。LaTeX 笔记中的行内公式使用本地 MathJax，代码示例保留字面内容。

新增、修改或删除 Markdown 后，提交并推送到 main，GitHub Actions 会重新构建并发布，无需手动维护篇目列表。源文件重命名或移动会改变其阅读入口。

封面使用内置 imagegen 生成。三个板块封面参考了站内前端、算法、Python、DevOps 和法律封面的暖白背景、光线和材质。

| 位置 | 主题 | 封面 | 提示词 |
| --- | --- | --- | --- |
| 前端基础 | 浏览器、分层页面与鼠标指针 | [封面](阅读资源/frontend-hero.webp) | [提示词](阅读资源/frontend-hero.prompt.txt) |
| 标记与排版 | 微型印刷机、活字与 Markdown 印样 | [封面](阅读资源/section-markup.webp) | [提示词](阅读资源/section-markup.prompt.txt) |
| JavaScript | 琥珀弹珠、分岔机关与 JS 方标 | [封面](阅读资源/section-javascript.webp) | [提示词](阅读资源/section-javascript.prompt.txt) |
| Vue | 玻璃榫接组件与 Vue 双色标志 | [封面](阅读资源/section-vue.webp) | [提示词](阅读资源/section-vue.prompt.txt) |

标志参考：[Markdown Mark（Dustin Curtis）](https://github.com/dcurtis/markdown-mark)、[JavaScript 社区标志（Christopher Williams，MIT）](https://github.com/voodootikigod/logo.js)、[Vue.js 官方标志（Evan You）](https://github.com/vuejs/art)。Vue 封面将该标志融入玻璃场景，按 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 提供。

本地生成：`python docs/pages/build_site.py --output docs/site`。预览可追加 `--serve`。回归检查：`python -m unittest discover -s docs/pages -p 'test_frontend.py'`。
