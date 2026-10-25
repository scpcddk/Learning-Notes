# 公式排版资源

本目录包含 MathJax 3.2.2 的 SVG 公式排版组件，供同级目录中的阅读页离线使用。

- `tex-svg.js`：TeX 输入与 SVG 输出的组合组件。
- `input/tex/extensions/`：额外的 TeX 扩展组件。
- `LICENSE`：MathJax 随包附带的 Apache License 2.0 许可证。

来源：[MathJax 3.2.2 npm 分发包](https://www.npmjs.com/package/mathjax/v/3.2.2)。文件保留分发包中的原始内容。

## 线性代数封面

- [封面图片](linear-algebra-hero.png)：立体矩阵、基向量与坐标平面的组合，用于线性代数阅读页首页和数学网站的科目卡片。
- [最终生成提示词](linear-algebra-hero.prompt.txt)：无参考图，使用内置 image_gen 工具生成，非透明背景。

图片作为装饰封面，不承载需要精确核算的公式、坐标或定理。正文公式仍由 MathJax 排版。
