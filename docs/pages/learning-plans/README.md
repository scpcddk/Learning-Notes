# 学习计划阅读页

在线入口：https://scpcddk.github.io/Learning-Notes/learning-plans/

页面与构建配置统一位于 docs，正文直接读取仓库 `学习计划/`。首页按“进行中、阶段性完成、已结束或舍弃、学习方法”展示文字卡片，进入分类后查看具体计划。首页与学习导航共用同一张总封面，内部分类和计划不使用封面。

与 Java、Python、云原生共用 `../programming/阅读页模板.html`，提供全文搜索、目录速览与完整内容、本篇目录、相邻篇目、代码复制、深色模式、打印和上次阅读记录。

原 Markdown 的任务勾选记录按原文展示，网页中的复选框只读；“原文勾选记录”统计实际任务列表，不统计代码示例，不代表独立核实后的能力完成率。修改进度应编辑原 Markdown，提交并推送后自动更新。计划中的日期、旧路线和进度状态保持原文，不自动推断任务已完成。

无扩展名的《数学建模编程手一月计划》也按 Markdown 收录。两份原 HTML 指南保留原有排版，在隔离的 iframe 中阅读，支持全文检索其文字内容。有外部资源的历史 HTML 仍可能需要网络。

总封面使用内置 imagegen 生成，并按用户要求将铅笔替换为具有金属质感的钢笔：不透明墨绿色金属笔身、黄铜配件与金色笔尖。[封面](阅读资源/learning-plans-hero.png) · [最终提示词与编辑记录](阅读资源/learning-plans-hero.prompt.txt)。所有图片保存在本目录，生成站点统一位于 Git 忽略的 `docs/site`。

构建：`python docs/pages/build_site.py --output docs/site`。
检查：`python -m unittest discover -s docs/pages -p 'test_*.py'`。
