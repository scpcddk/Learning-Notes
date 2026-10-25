"""从高等数学 Markdown 笔记生成离线阅读页。

运行：python 数学/高等数学/阅读页面/生成阅读页.py
依赖：markdown-it-py。页面打开时不需要 Python、服务器或网络。
"""
from pathlib import Path
import hashlib
import html
import json
import os
import re
import shutil
from urllib.parse import quote, unquote, urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
NOTES = ROOT.parent
CHAPTERS = [
    ("sec-limit", "第一章 极限与连续.md", "极限与连续", "从无限趋近，理解变化的起点。", ["极限方法", "无穷小", "连续性"]),
    ("sec-derivative", "第二章 导数与微分.md", "导数与微分", "以变化率与线性近似，刻画每一个瞬间。", ["导数定义", "链式法则", "高阶导数"]),
    ("sec-meanvalue", "第三章 微分中值定理与导数的应用.md", "中值定理与导数应用", "让局部的导数，解释整个区间的行为。", ["辅助函数", "泰勒展开", "图形与极值"]),
    ("sec-integral", "第四章 积分及其应用.md", "积分及其应用", "把微小的部分累加，得到整体的量。", ["换元与分部", "反常积分", "几何应用"]),
    ("sec-series", "第五章 无穷级数.md", "无穷级数", "从有限部分和，走向函数的无穷表达。", ["收敛判断", "幂级数", "傅里叶级数"]),
    ("sec-geometry", "第六章 向量代数与空间解析几何.md", "向量与空间解析几何", "用方向、位置与方程，搭建空间的语言。", ["点积与叉积", "平面与直线", "曲面"]),
    ("sec-multivariable", "第七章 多元函数的微分法及其应用.md", "多元微分与极值", "从一条曲线，走向多个方向的变化。", ["可微与偏导", "梯度", "条件极值"]),
    ("sec-multiple", "第八章 重积分.md", "重积分", "读懂区域，用合适的坐标完成累积。", ["积分次序", "坐标换元", "空间微元"]),
    ("sec-vectorcalculus", "第九章 曲线积分与曲面积分.md", "曲线积分与曲面积分", "沿曲线、穿曲面，连接边界与内部。", ["方向与通量", "三大公式", "奇点"]),
    ("sec-equation", "第十章 微分方程.md", "微分方程", "从变化的规律出发，寻找函数本身。", ["方程识别", "降阶", "特征根"]),
]
TOPICS = [
    ("topic-limits", "极限计算方法选择与泰勒阶数.md", "极限方法与泰勒阶数", "先判断结构，再找到抵消后的首个非零项。", ["方法选择", "完整例题"]),
    ("topic-improper", "反常积分的拆分与收敛判断.md", "反常积分与主值", "分开检查每个问题端点，辨别收敛与对称主值。", ["瑕点", "收敛判断"]),
    ("topic-counterexamples", "多元极限与可微反例.md", "多元极限与可微反例", "用路径与统一估计，辨清关系链的方向。", ["路径", "反例"]),
    ("topic-theorems", "格林高斯斯托克斯公式的选择.md", "三大积分公式的选择", "检查区域、奇点与方向，再决定如何转化。", ["补线补面", "选公式"]),
    ("topic-power", "幂级数特殊题型.md", "幂级数特殊题型", "缺项、平移、端点与求和常数，一次理清。", ["收敛域", "求和函数"]),
    ("topic-conditions", "定理条件与反例速查.md", "定理条件与反例速查", "记住结论之前，先记住它为什么能用。", ["适用条件", "逆命题"]),
    ("topic-differentiability", "可微性证明.md", "可微性证明", "从函数值、偏导数到余项，按定义逐步验证。", ["分段函数", "定义证明"]),
    ("topic-rolle", "罗尔定理的使用.md", "罗尔定理构造", "把目标等式看作求导结果，反推辅助函数。", ["辅助函数", "存在性"]),
    ("topic-substitution", "二重积分换元法.md", "二重积分换元法", "让函数变简单，让区域变规则。", ["雅可比", "区域变换"]),
    ("topic-parity", "奇偶性.md", "积分中的奇偶性", "先看区域怎样对称，再看哪个变量变号。", ["对称", "化简"]),
    ("topic-elements", "积分微元辨析.md", "积分微元辨析", "在长度、弧长、面积与体积之间选对微元。", ["ds 与 dS", "通量"]),
    ("topic-extrema", "区域最值问题.md", "区域最值问题", "内部候选点与每条边界，都要逐一检查。", ["内部与边界", "候选点"]),
    ("topic-wallis", "华莱士公式.md", "华莱士公式", "用双阶乘计算三角函数幂次积分。", ["双阶乘", "区间对称"]),
    ("topic-centroid", "形心公式.md", "形心与质心", "用加权平均，表达图形与物体的中心。", ["几何应用", "对称性"]),
    ("topic-gauss", "高斯公式/高斯公式.md", "高斯公式与方向", "对照补面例题，区分上侧、内侧与外侧。", ["方向", "补面"]),
    ("topic-ode", "微分方程判断过程.md", "微分方程判断过程", "一阶先看形式，高阶再找降阶与特征根。", ["流程", "特解"]),
]

FORMULAS = r"""## 极限与局部近似

$$\frac{\sin x}{x}\to1,\quad\frac{\ln(1+x)}x\to1,\quad
\frac{e^x-1}x\to1\qquad(x\to0).$$

$$\sin x=x-\frac{x^3}{6}+o(x^3),\quad
\ln(1+x)=x-\frac{x^2}{2}+o(x^2).$$

## 导数与变限积分

$$\frac{dy}{dx}=\frac{dy}{du}\frac{du}{dx},\qquad
\frac d{dx}\int_{\varphi(x)}^{\psi(x)}f(t)\,dt
=f(\psi(x))\psi'(x)-f(\varphi(x))\varphi'(x).$$

变限积分公式在被积函数连续、上下限可导等条件下使用。

## 积分计算

$$\int u\,dv=uv-\int v\,du,\qquad
\int_a^b f(x)\,dx=F(b)-F(a)\quad(F'=f,\ f\text{ 连续}).$$

$$\int_0^{\pi/2}\sin^m x\cos^n x\,dx
=\frac{(m-1)!!(n-1)!!}{(m+n)!!}
\begin{cases}\pi/2,&m,n\text{ 均偶},\\1,&\text{其他情况}.\end{cases}$$

最后一式要求 $m,n$ 为非负整数，约定 $(-1)!!=0!!=1$。

## 常见收敛条件

$$\sum_{n=1}^\infty\frac1{n^p}\text{ 收敛}\iff p>1,\qquad
\int_0^1\frac{dx}{x^p}\text{ 收敛}\iff p<1.$$

## 多元微分与梯度

$$dz=f_x\,dx+f_y\,dy,\qquad
D_{\boldsymbol e}f=\nabla f\cdot\boldsymbol e
\quad(f\text{ 可微},\ |\boldsymbol e|=1).$$

$$D=f_{xx}f_{yy}-f_{xy}^2.$$

在驻点且邻域内有连续二阶偏导时，$D>0$ 配合 $f_{xx}$ 的符号判极小或极大；$D<0$ 为鞍点，$D=0$ 另行判断。

## 面积元与体积元

$$dxdy=r\,drd\theta,\qquad
dV=r^2\sin\varphi\,drd\varphi d\theta.$$

$$dS=\sqrt{1+z_x^2+z_y^2}\,dxdy,\qquad
dxdy=\left|\frac{\partial(x,y)}{\partial(u,v)}\right|dudv.$$

## 三大积分公式

$$\oint_{\partial D}^{+}Pdx+Qdy=\iint_D(Q_x-P_y)\,dxdy.$$

$$\oiint_{\partial\Omega,\text{外}}\boldsymbol F\cdot\boldsymbol n\,dS
=\iiint_\Omega\nabla\cdot\boldsymbol F\,dV.$$

$$\oint_{\partial\Sigma}^{+}\boldsymbol F\cdot d\boldsymbol r
=\iint_\Sigma(\nabla\times\boldsymbol F)\cdot\boldsymbol n\,dS.$$

检查边界、方向、区域内的光滑性与奇点，不能只看公式形式。

## 一阶线性与二阶常系数

$$y'+P(x)y=Q(x),\qquad
y=e^{-\int Pdx}\left[\int Qe^{\int Pdx}\,dx+C\right].$$

$$y''+py'+qy=0\quad\longrightarrow\quad r^2+pr+q=0.$$

相异实根对应两个指数解，二重实根对应 $(C_1+C_2x)e^{rx}$，共轭复根对应指数乘正弦、余弦。
"""


def summaries():
    """提要的二级标题对应页面标题；内部三级标题提升一级。"""
    parts = re.split(r"(?m)^## (.+)\n", (ROOT / "速查提要.md").read_text(encoding="utf-8"))
    return {parts[i].strip(): re.sub(r"(?m)^### ", "## ", parts[i + 1])
            for i in range(1, len(parts), 2)}


def render(source, prefix, source_path, routes):
    """先保护公式，再解析 Markdown，最后解析内部路由与相对图片。"""
    protected = []

    def math_token(match):
        raw = match.group()
        display = raw.startswith(("$$", r"\["))
        tex = raw[2:-2] if raw.startswith(("$$", r"\[", r"\(")) else raw[1:-1]
        tex = re.sub(r"(?m)^\s*> ?", "", tex).strip()
        delimiters = (r"\[", r"\]") if display else (r"\(", r"\)")
        cls = "math-display" if display else "math-inline"
        protected.append(f'<span class="{cls}">{html.escape(delimiters[0] + tex + delimiters[1])}</span>')
        return f"CALCULUSMATHTOKEN{len(protected)-1}END"

    pattern = r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\\)\$(?!\$)[^\n$]+?(?<!\\)\$"
    source = re.sub(pattern, math_token, source)
    source = re.sub(r"==([^\n]+?)==", lambda m: m[1] if m[1].startswith("**") else "**" + m[1] + "**", source)
    md = MarkdownIt("commonmark", {"html": True, "breaks": False}).enable("table")

    def heading_open(tokens, idx, options, env):
        count = env.setdefault("heading_count", 0) + 1
        env["heading_count"] = count
        tokens[idx].attrSet("id", f"{prefix}-h{count}")
        return md.renderer.renderToken(tokens, idx, options, env)

    def local_target(url, is_image=False):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        target = (source_path.parent / unquote(parts.path)).resolve()
        if not is_image and target in routes and not parts.fragment:
            return "#" + routes[target]
        if not is_image and target == (NOTES / "README.md").resolve() and not parts.fragment:
            return "#overview"
        if is_image and target.is_file():
            # 将正文插图带入阅读资源，便于连同阅读页面文件夹一起离线使用。
            digest = hashlib.sha256(target.read_bytes()).hexdigest()[:10]
            copied = ROOT / "阅读资源" / "插图" / (digest + "-" + target.name)
            copied.parent.mkdir(parents=True, exist_ok=True)
            if not copied.exists() or copied.read_bytes() != target.read_bytes():
                shutil.copyfile(target, copied)
            target = copied
        path = quote(Path(os.path.relpath(target, ROOT)).as_posix())
        return path + ("#" + parts.fragment if parts.fragment else "")

    def link_open(tokens, idx, options, env):
        tokens[idx].attrSet("href", local_target(tokens[idx].attrGet("href") or ""))
        return md.renderer.renderToken(tokens, idx, options, env)

    def image_rule(tokens, idx, options, env):
        tokens[idx].attrSet("src", local_target(tokens[idx].attrGet("src") or "", True))
        tokens[idx].attrSet("loading", "lazy")
        return md.renderer.image(tokens, idx, options, env)

    md.renderer.rules["heading_open"] = heading_open
    md.renderer.rules["link_open"] = link_open
    md.renderer.rules["image"] = image_rule
    out = md.render(source)
    for i, value in enumerate(protected):
        out = out.replace(f"CALCULUSMATHTOKEN{i}END", value)

    def admonition(match):
        kind = match[1].lower()
        label = {"note": "理解与联系", "tip": "解题提示", "warning": "易错提醒", "important": "关键结论"}[kind]
        return f'<blockquote class="callout {kind}"><p class="callout-label">{label}</p><p>'

    out = re.sub(r"<blockquote>\s*<p>\[!(NOTE|TIP|WARNING|IMPORTANT)\]\s*", admonition, out)
    out = re.sub(r"<table>([\s\S]*?)</table>", r'<div class="table-scroll"><table>\1</table></div>', out)
    return out


def build():
    entries = []
    for i, (ident, filename, title, desc, tags) in enumerate(CHAPTERS, 1):
        entries.append(dict(id=ident, number=f"{i:02}", kind="chapter", title=title,
                            description=desc, tags=tags, path=NOTES / "高等数学基础概念" / filename))
    for i, (ident, filename, title, desc, tags) in enumerate(TOPICS, 1):
        entries.append(dict(id=ident, number=f"T{i:02}", kind="topic", title=title,
                            description=desc, tags=tags, path=NOTES / "补充理解" / filename))
    entries.append(dict(id="sec-practice", number="30", kind="practice", title="章节自测与解析",
                        description="十章各三道题，先独立作答，再展开解析。",
                        tags=["30 道自测", "折叠解析", "错题记录"], path=NOTES / "题目" / "章节自测与解析.md"))
    routes = {entry["path"].resolve(): entry["id"] for entry in entries}
    quick = summaries()
    pages = []
    for entry in entries:
        path = entry["path"]
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^ ?# [^\n]+\n", "", text, count=1)
        # 页面上已有同等的阅读导航，保留原笔记中的其他引用。
        text = re.sub(r"(?m)^> 配套阅读：[^\n]+\n", "", text)
        data = {key: value for key, value in entry.items() if key != "path"}
        data["source"] = quote(Path(os.path.relpath(path, ROOT)).as_posix())
        data["full"] = render(text, entry["id"] + "-full", path, routes)
        data["summary"] = render(quick[entry["title"]], entry["id"] + "-quick", ROOT / "速查提要.md", routes) if entry["kind"] == "chapter" else data["full"]
        data["search"] = re.sub(r"[#*$>\\{}]", " ", text)
        pages.append(data)
    formula = render(FORMULAS, "sec-formula-full", ROOT / "速查提要.md", routes)
    pages.append(dict(id="sec-formula", number="∑", kind="formula", title="公式速查",
                      description="把常用公式与适用条件，放在同一页。",
                      tags=["条件先行", "公式索引"], source="", full=formula, summary=formula, search=FORMULAS))
    payload = json.dumps(pages, ensure_ascii=False).replace("</", r"<\/")
    shell = (ROOT / "阅读页模板.html").read_text(encoding="utf-8")
    assert shell.count("<!--CHAPTER_DATA-->") == 1
    (ROOT / "速查笔记.html").write_text(shell.replace("<!--CHAPTER_DATA-->", payload), encoding="utf-8", newline="\n")
    print(f"Generated {len(CHAPTERS)} chapters, {len(TOPICS)} topics, 30 practice questions and a formula index.")


if __name__ == "__main__":
    build()
