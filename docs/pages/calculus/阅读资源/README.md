# 公式排版资源

本目录包含 MathJax 3.2.2 的 SVG 公式排版组件，供同级目录中的阅读页离线使用。

- `tex-svg.js`：TeX 输入与 SVG 输出的组合组件。
- `input/tex/extensions/`：额外的 TeX 扩展组件。
- `LICENSE`：MathJax 随包附带的 Apache License 2.0 许可证。

来源：[MathJax 3.2.2 npm 分发包](https://www.npmjs.com/package/mathjax/v/3.2.2)。文件保留分发包中的原始内容。

颜色扩展 input/tex/extensions/color.js 与现有组件固定为同一版本，供原笔记中的 \color 公式离线使用。来源：[MathJax 3.2.2 颜色扩展](https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/input/tex/extensions/color.js)。

## 图片资源

- [calculus-hero.png](calculus-hero.png)：高等数学首页主题插图，使用内置图像生成工具生成。
- 插图子目录：生成脚本从原笔记复制的正文插图，文件名前缀取自内容哈希。

正文公式由 MathJax 排版，首页生成插图仅作装饰，不承担公式或定理的准确表达。

### 首页插图的最终生成提示词

生成方式：内置 image_gen 工具；新图生成，无参考图，非透明背景。

~~~text
Use case: stylized-concept. Asset type: hero illustration for an elegant offline Chinese calculus notebook, landscape 3:2 composition. Create an exquisite editorial mathematical still life, a translucent sage-green sculptural curved surface emerging from a very fine Cartesian grid, fine copper-gold tangent line touching a smooth sweeping function curve, and a subtle fan of thin integral cross-section slices, all arranged as one coherent small sculpture on warm ivory paper. Refined ink engraving meets soft matte 3D paper sculpture, understated academic book-cover quality, generous clear negative space near all edges, soft diffuse daylight and delicate shadows, muted forest green #286249, sage #c9d9c5, warm ivory #fafbf8, tiny warm brass accents. Main sculpture centered, no writing, no numerals, no labels, no letters, no equations, no logos, no watermark. This is a conceptual decorative illustration, not a labelled scientific diagram. Keep the background uniformly warm off-white with subtle paper grain and a gentle horizonless fade. Avoid neon, glossy plastic, excessive detail, busy backgrounds or dramatic gradients.
~~~
