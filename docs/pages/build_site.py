"""Package the math and algorithms reading pages for GitHub Pages.

Generate and package every subject:
    python docs/pages/build_site.py --output <site-directory>

The output is a static site. Repository links point back to GitHub, while the
reading pages link to each other through stable, relative website routes.
"""
import argparse
import hashlib
import html
from html import escape
from html.parser import HTMLParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from inspect import cleandoc
import json
import os
from pathlib import Path
import re
import shutil
import zipfile
from urllib.parse import quote, unquote, urlsplit

from markdown_it import MarkdownIt


REPO = Path(__file__).resolve().parents[2]
SUBJECTS = (
    ("calculus", REPO / "docs/pages/calculus"),
    ("linear-algebra", REPO / "docs/pages/linear-algebra"),
)
DATA = re.compile(r'(<script type="application/json" id="chapter-data">)([\s\S]*?)(</script>)')
HREF = re.compile(r'(?P<prefix>\bhref\s*=\s*)(?P<q>["\'])(?P<url>[^"\']*)(?P=q)')


def generate_calculus():
    ROOT = REPO / "docs/pages/calculus"
    NOTES = REPO / "数学/高等数学"
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

    FORMULAS = cleandoc(FORMULAS)
    build()


def generate_linear_algebra():
    ROOT = REPO / "docs/pages/linear-algebra"
    NOTES = REPO / '数学/线性代数/基础概念/笔记'
    CHAPTERS = [
        ('sec-det', '第一章 行列式.md', '行列式', '用一个数，理解可逆性与空间的伸缩。', ['余子式', '展开与变换', '计算方法']),
        ('sec-matrix', '第二章 矩阵.md', '矩阵', '把线性关系写成矩阵，把计算化为变换。', ['矩阵运算', '逆与伴随', '初等变换']),
        ('sec-vector', '第三章 向量组的线性相关性.md', '向量组', '识别独立方向，用最少的向量表达更多。', ['线性相关性', '秩与表示', '正交化']),
        ('sec-linsys', '第四章 线性方程组.md', '线性方程组', '从秩判断解，再用自由变量描述全部解。', ['解的判定', '基础解系', '参数讨论']),
        ('sec-diag', '第五章 矩阵相似对角化.md', '相似对角化', '找到合适的基，让变换的结构显现出来。', ['特征值', '相似与反例', '正交对角化']),
        ('sec-quad', '第六章 二次型.md', '二次型', '从平方项的符号，看清二次型的性质。', ['合同变换', '惯性指数', '正定与半正定']),
        ('sec-space', '第七章 线性空间与线性变换.md', '线性空间与变换', '用基、核与像，把前六章连成一个整体。', ['换基', '核与像', '正交投影']),
        ('sec-extra', '拓展阅读 Cayley–Hamilton、最小二乘与SVD.md', '拓展阅读', '连接矩阵计算、数据拟合与奇异值分解。', ['Cayley–Hamilton', '最小二乘', 'SVD']),
    ]

    SUMMARIES = {
        'sec-det': r'''## 先抓住三个关键点

    行列式是一个数。它既是计算工具，也能判断方阵是否可逆。

    > [!IMPORTANT]
    > 对 $n$ 阶方阵，$\det A\neq0\iff A$ 可逆 $\iff R(A)=n$。

    ## 计算时怎么选方法

    | 看到的结构 | 优先考虑 |
    |---|---|
    | 某行或某列零很多 | 按该行或列展开，保留 $(-1)^{i+j}$ |
    | 一般矩阵 | 倍加消元，化为三角形 |
    | 幂次逐行递增 | 范德蒙德行列式 |
    | 三对角结构 | 展开后建立递推，并写初值 |
    | 对角矩阵叠加相同常数 | 加边法 |

    ## 必记公式

    $$\det(kA)=k^n\det A,\qquad\det(AB)=\det A\det B.$$

    $$D_n=\prod_{1\leq i<j\leq n}(a_j-a_i)\quad\text{（范德蒙德）}.$$

    > [!WARNING]
    > 两行互换会变号；某一行乘 $k$，行列式才乘 $k$。一般没有 $\det(A+B)=\det A+\det B$ 的加法公式。

    ## 去完整笔记看例题

    稀疏行列式展开、加边法的逐步构造、三对角递推，以及常数项与系数之和的计算均已补全。
    ''',
        'sec-matrix': r'''## 先记住乘法的方向

    若 $A$ 是 $m\times n$，$B$ 是 $n\times p$，则 $AB$ 是 $m\times p$。乘积的第 $(i,j)$ 元是 $A$ 第 $i$ 行与 $B$ 第 $j$ 列的内积。

    > [!WARNING]
    > 矩阵乘法一般不交换，也不能仅凭 $A\neq O$ 就消去 $A$。

    ## 逆、转置与伴随

    $$ (AB)^{-1}=B^{-1}A^{-1},\qquad (AB)^\mathrm{T}=B^\mathrm{T}A^\mathrm{T}. $$

    $$AA^*=A^*A=\det(A)E,\qquad A^{-1}=\frac{A^*}{\det A}\quad(\det A\neq0).$$

    ## 初等变换的两种用途

    | 目标 | 操作 |
    |---|---|
    | 求逆矩阵 | 对 $(A\mid E)$ 只作行变换，化为 $(E\mid A^{-1})$ |
    | 求矩阵的秩 | 行变换化阶梯形，数非零行 |
    | 行变换 | 左乘初等矩阵 |
    | 列变换 | 右乘初等矩阵 |

    ## 分块计算的条件

    先确认每个子块的尺寸。三角分块行列式等于对角方块行列式之积；求逆时，对角块必须可逆，乘法顺序要保留。
    ''',
        'sec-vector': r'''## 线性无关，就是没有冗余方向

    $$c_1\alpha_1+\cdots+c_s\alpha_s=0\Longrightarrow c_1=\cdots=c_s=0.$$

    只要存在一组不全为零的系数使组合为零，就线性相关。向量的个数超过分量数时，必线性相关。

    ## 秩、极大无关组与表示

    把向量按列组成 $A$，作初等行变换得到阶梯形。非零行数是秩，主元列对应的**原向量**构成极大无关组。

    $$\beta\text{ 可由 }A\text{ 的列表示}\iff R(A)=R(A\mid\beta).$$

    > [!TIP]
    > 行变换保持列之间的线性关系；用线性无关组表示时，表示系数唯一。

    ## 正交化的本质：减去已知方向

    $$\beta_k=\alpha_k-\sum_{j<k}\frac{[\beta_j,\alpha_k]}{[\beta_j,\beta_j]}\beta_j,\qquad q_k=\frac{\beta_k}{\|\beta_k\|}.$$

    > [!WARNING]
    > 投影方向要用已经正交化的 $\beta_j$；正交化完成后还要单位化。

    ## 完整例题

    完整笔记包含：四个向量的秩与极大无关组、可表示与不可表示的对照，以及三个向量的 Schmidt 正交化全过程。
    ''',
        'sec-linsys': r'''## 先比较秩，再讨论解

    设 $A$ 有 $n$ 列，即 $n$ 个未知量。

    | 条件 | 结论 |
    |---|---|
    | $R(A)<R(A\mid b)$ | 无解 |
    | $R(A)=R(A\mid b)=n$ | 唯一解 |
    | $R(A)=R(A\mid b)=r<n$ | 无穷多解，$n-r$ 个自由参数 |

    ## 通解的结构

    $$\boxed{x=\eta_0+c_1\xi_1+\cdots+c_{n-r}\xi_{n-r}.}$$

    $\eta_0$ 是一个特解，$\xi_i$ 构成齐次导出组的基础解系。分别检查 $A\eta_0=b$ 和 $A\xi_i=0$。

    ## 从行最简形构造基础解系

    1. 主元列对应主元变量，其他列对应自由变量。
    2. 将主元变量用自由变量表示。
    3. 在齐次组中，让自由变量依次取单位向量，读出基础解系。
    4. 非齐次组可令自由变量全为零，取一个特解。

    > [!WARNING]
    > 含参数消元时，先讨论可能为零的主元，再作除法。方阵行列式为零，并不能直接判定无解。

    ## 完整例题

    四未知量方程组：从消元到两个基础解向量；含参数方程组：分别出现唯一解、无穷多解和无解的三个分支。
    ''',
        'sec-diag': r'''## 特征向量，给出不改变方向的轴

    $$A\xi=\lambda\xi,\qquad\xi\neq0.$$

    先解 $\det(\lambda E-A)=0$，再对每个特征值求 $(A-\lambda E)x=0$ 的基础解系。

    ## 可对角化的真正条件

    > [!IMPORTANT]
    > 在所讨论的数域内，$n$ 阶矩阵可对角化，当且仅当有 $n$ 个线性无关的特征向量。重根要检查几何重数。

    $$P^{-1}AP=\Lambda,\qquad A^k=P\Lambda^kP^{-1}.$$

    ## 一个必须会的反例

    $$J=\begin{pmatrix}1&1\\0&1\end{pmatrix}.$$

    特征值 $1$ 是二重根，但其特征子空间只有一维，故不可对角化。它与 $E_2$ 特征值相同，但不相似。

    ## 实对称矩阵更进一步

    实对称矩阵的特征值全为实数，不同特征值的特征向量正交，且一定可以正交对角化：

    $$Q^\mathrm{T}AQ=\Lambda,\qquad Q^\mathrm{T}Q=E.$$

    完整例题用特征值 $1,3,3$ 的矩阵，演示重根内正交化、单位化和矩阵幂计算；第六章继续使用它。
    ''',
        'sec-quad': r'''## 二次型，用实对称矩阵表示

    $$f(x)=x^\mathrm{T}Ax.$$

    平方项系数放在对角线；交叉项系数除以 $2$，放在两个对称位置。

    ## 标准形与规范形

    作 $x=Cy$ 后，矩阵变成 $C^\mathrm{T}AC$，这是合同变换。正交变换给出以特征值为系数的标准形，再通过可逆缩放得到系数为 $1,-1,0$ 的规范形。

    ## 判定正定与半正定

    | 性质 | 实对称矩阵的等价条件 |
    |---|---|
    | 正定 | 特征值全正；或各阶顺序主子式全正 |
    | 负定 | 特征值全负；或顺序主子式奇负偶正 |
    | 半正定 | 特征值均非负；或所有主子式非负 |
    | 不定 | 既有正特征值，也有负特征值 |

    > [!WARNING]
    > 行列式大于零不能反推正定。半正定必须检查**所有主子式**，只看顺序主子式非负不够。

    ## 贯通例题与应用

    $$2x_1^2+2x_2^2+3x_3^2+2x_1x_2\ \xrightarrow{x=Qy}\ y_1^2+3y_2^2+3y_3^2.$$

    完整笔记继续化规范形，并用特征值、顺序主子式与配方交叉判断。用 Hessian 判断极值时，还需该点是内点、函数在其邻域二阶连续可微，并先检查驻点条件 $\nabla f(x_0)=0$。
    ''',
        'sec-space': r'''## 基是坐标的参照，换基解释相似

    若新基＝旧基乘 $C$，则旧坐标 $x$ 与新坐标 $y$ 满足

    $$x=Cy,\qquad B=C^{-1}AC.$$

    $A,B$ 是同一线性变换在两组基下的矩阵。

    ## 核与像，连接空间和方程组

    $$\ker T=\{v:T(v)=0\},\qquad\operatorname{Im}T=\{T(v):v\in V\}.$$

    $$\boxed{\dim\ker T+\dim\operatorname{Im}T=\dim V.}$$

    对 $T(x)=Ax$，核就是齐次解空间，像就是列空间。核为零等价于单射，像等于目标空间等价于满射。

    ## 子空间的和、交与直和

    $$\dim(U+W)=\dim U+\dim W-\dim(U\cap W).$$

    $U\cap W=\{0\}$ 时，$U+W$ 是直和，每个向量的分解唯一。

    ## 正交投影：空间里最近的点

    若 $Q$ 的列是 $U$ 的规范正交基，则

    $$p=QQ^\mathrm{T}x,\qquad x-p\in U^\perp.$$

    若基矩阵 $M$ 非空、列满秩但不正交，使用 $p=M(M^\mathrm{T}M)^{-1}M^\mathrm{T}x$。

    完整笔记还包括换基计算、核与像例题、到平面的投影，以及矩阵四个基本子空间的对照表。
    ''',
        'sec-extra': r'''## 矩阵满足自己的特征方程

    若 $p(\lambda)=\det(\lambda E-A)$，则 Cayley–Hamilton 定理给出 $p(A)=O$。它可以降低矩阵幂的次数，也可在矩阵可逆时求逆。

    ## 没有精确解，仍然能求最佳拟合

    最小二乘解使 $\|Ax-b\|^2$ 最小，其正规方程为

    $$A^\mathrm{T}A\hat x=A^\mathrm{T}b.$$

    若 $A$ 列满秩，解唯一。几何上，$A\hat x$ 就是 $b$ 到列空间的正交投影。

    ## SVD：从方阵走向一般矩阵

    $$A=U\Sigma V^\mathrm{T}.$$

    任意实矩阵都存在 SVD，奇异值均非负，正奇异值的个数等于秩。对实对称矩阵，奇异值是特征值的绝对值。

    ## 完整例题

    用特征方程计算矩阵幂和逆；拟合三个点的最佳直线；秩为一的矩阵的 SVD、伪逆与最小范数解。
    ''',
    }

    FORMULAS = r'''## 可逆性

    $$\det A\neq0\iff R(A)=n\iff A\text{ 可逆}\iff Ax=0\text{ 只有零解}.$$

    这里 $A$ 为 $n$ 阶方阵。

    ## 线性表示与通解

    $$Ax=b\text{ 有解}\iff R(A)=R(A\mid b).$$

    $$x=\eta_0+\sum_{i=1}^{n-r}c_i\xi_i,\qquad \dim\ker A=n-R(A).$$

    ## 相似、合同与换基

    $$B=P^{-1}AP\quad\text{（相似）},\qquad B=C^\mathrm{T}AC\quad\text{（合同）}.$$

    $$\text{新基}=\text{旧基}\cdot C,\quad x=Cy,\quad B=C^{-1}AC.$$

    ## 特征值与正交对角化

    $$\sum_i\lambda_i=\operatorname{tr}A,\qquad\prod_i\lambda_i=\det A.$$

    $$Q^\mathrm{T}AQ=\Lambda,\quad A^k=Q\Lambda^kQ^\mathrm{T}\quad(A\text{ 实对称}).$$

    ## 维数与投影

    $$\dim\ker T+\dim\operatorname{Im}T=\dim V.$$

    $$\dim(U+W)=\dim U+\dim W-\dim(U\cap W).$$

    $$\operatorname{proj}_U x=QQ^\mathrm{T}x\quad(Q\text{ 的列为 }U\text{ 的规范正交基}).$$
    '''


    def render(source, prefix):
        """先保护 LaTeX，避免 Markdown 把矩阵换行和竖线当作排版符号。"""
        protected = []

        def math_token(match):
            raw = match.group()
            display = raw.startswith(('$$', r'\['))
            tex = raw[2:-2] if raw.startswith(('$$', r'\[', r'\(')) else raw[1:-1]
            tex = re.sub(r'(?m)^\s*> ?', '', tex).strip()
            delimiters = (r'\[', r'\]') if display else (r'\(', r'\)')
            cls = 'math-display' if display else 'math-inline'
            protected.append(f'<span class="{cls}">{html.escape(delimiters[0] + tex + delimiters[1])}</span>')
            return f'MATHPLACEHOLDER{len(protected)-1}END'

        pattern = r'\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\\)\$(?!\$)[^\n$]+?(?<!\\)\$'
        source = re.sub(pattern, math_token, source)
        source = re.sub(r'==([^\n]+?)==', lambda m: m[1] if m[1].startswith('**') else '**'+m[1]+'**', source)
        md = MarkdownIt('commonmark', {'html': True, 'breaks': False}).enable('table')

        def heading_open(tokens, idx, options, env):
            token = tokens[idx]
            count = env.setdefault('heading_count', 0) + 1
            env['heading_count'] = count
            token.attrSet('id', f'{prefix}-h{count}')
            return md.renderer.renderToken(tokens, idx, options, env)

        def fence(tokens, idx, options, env):
            if tokens[idx].info.strip() == 'mermaid':
                if '只有零解' in tokens[idx].content:
                    return '<div class="concept-chain"><span>只有零解</span><b>↔</b><span>满秩</span><b>↔</b><span>可逆</span><b>↔</b><span>det A ≠ 0</span></div>'
                return '<div class="concept-chain"><span>正交相似</span><b>→</b><span>相似 / 合同</span><b>→</b><span>等价</span><b>→</b><span>等秩</span></div>'
            return '<pre><code>' + html.escape(tokens[idx].content) + '</code></pre>'

        md.renderer.rules['heading_open'] = heading_open
        md.renderer.rules['fence'] = fence
        out = md.render(source)
        for i, value in enumerate(protected):
            out = out.replace(f'MATHPLACEHOLDER{i}END', value)

        def admonition(match):
            kind = match[1].lower()
            label = {'note': '理解与联系', 'tip': '解题提示', 'warning': '易错提醒', 'important': '关键结论'}.get(kind, '笔记')
            return f'<blockquote class="callout {kind}"><p class="callout-label">{label}</p><p>'

        out = re.sub(r'<blockquote>\s*<p>\[!(NOTE|TIP|WARNING|IMPORTANT)\]\s*', admonition, out)
        out = re.sub(r'<table>([\s\S]*?)</table>', r'<div class="table-scroll"><table>\1</table></div>', out)
        out = re.sub(r'href="([^"#:/]+\.md)"', lambda m: 'href="../../../数学/线性代数/基础概念/笔记/' + quote(unquote(m[1])) + '"', out)
        return out


    def build():
        chapters = []
        for index, (ident, filename, title, desc, tags) in enumerate(CHAPTERS):
            text = (NOTES / filename).read_text(encoding='utf-8')
            text = re.sub(r'^# .*?\n', '', text, count=1)
            text = re.sub(r'^> \*\*本章主线\*\*.*\n(?:>.*\n)*', '', text, count=1, flags=re.M)
            text = re.sub(r'\n\*\*章节导航\*\*[^\n]*\n?', '\n', text)
            chapters.append({
                'id': ident, 'number': f'{index+1:02}', 'title': title, 'description': desc, 'tags': tags,
                'source': '../../../数学/线性代数/基础概念/笔记/' + quote(filename),
                'summary': render(SUMMARIES[ident], ident+'-quick'),
                'full': render(text, ident+'-full'),
                'search': re.sub(r'[#*$>\\{}]', ' ', text),
            })
        chapters.append({'id': 'sec-formula', 'number': '∑', 'title': '公式速查', 'description': '把最常用的结论，放在同一页。', 'tags': ['条件先行', '联系记忆'], 'source': '', 'summary': render(FORMULAS, 'formulas'), 'full': render(FORMULAS, 'formulas'), 'search': FORMULAS})
        payload = json.dumps(chapters, ensure_ascii=False).replace('</', r'<\/')
        shell = (ROOT / '阅读页模板.html').read_text(encoding='utf-8')
        (ROOT / '速查笔记.html').write_text(shell.replace('<!--CHAPTER_DATA-->', payload), encoding='utf-8', newline='\n')
        print(f'已生成速查笔记.html：{len(CHAPTERS)} 篇笔记 + 公式速查')

    SUMMARIES = {key: cleandoc(value) for key, value in SUMMARIES.items()}
    FORMULAS = cleandoc(FORMULAS)
    build()


DISCRETE = REPO / "docs/pages/discrete-math"
DISCRETE_NOTES = REPO / "数学/离散数学"
CALCULUS_ASSETS = REPO / "docs/pages/calculus/阅读资源"


def copy_mathjax(destination):
    math = destination / "mathjax"
    math.mkdir(exist_ok=True)
    for name in ("tex-svg.js", "LICENSE"):
        shutil.copyfile(CALCULUS_ASSETS / name, math / name)
    shutil.copytree(CALCULUS_ASSETS / "input", math / "input", dirs_exist_ok=True)


def render_discrete(text, ident):
    text = re.sub(r"\A---\n[\s\S]*?\n---\n", "", text)
    protected = []

    def math(match):
        raw = match[0]
        display = raw.startswith(("$$", r"\["))
        tex = raw[2:-2] if raw.startswith(("$$", r"\[", r"\(")) else raw[1:-1]
        tex = re.sub(r"(?m)^\s*> ?", "", tex).strip()
        pair = (r"\[", r"\]") if display else (r"\(", r"\)")
        cls = "math-display" if display else "math-inline"
        protected.append(f'<span class="{cls}">{html.escape(pair[0]+tex+pair[1])}</span>')
        return f"DISCRETEMATH{len(protected)-1}TOKEN"

    text = re.sub(r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\\)\$(?!\$)[^\n$]+?(?<!\\)\$", math, text)
    text = re.sub(r"==([^\n]+?)==", r"<mark>\1</mark>", text)
    md = MarkdownIt("commonmark", {"html": True}).enable("table")

    def heading(tokens, idx, options, env):
        env["headings"] = env.get("headings", 0) + 1
        tokens[idx].attrSet("id", f'{ident}-h{env["headings"]}')
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["heading_open"] = heading
    result = md.render(text)
    for i, value in enumerate(protected):
        result = result.replace(f"DISCRETEMATH{i}TOKEN", value)
    result = re.sub(r"<table>([\s\S]*?)</table>", r'<div class="table-scroll"><table>\1</table></div>', result)
    result = re.sub(r"\[!(NOTE|TIP|WARNING|IMPORTANT)\]", lambda m: {
        "NOTE": "理解与联系", "TIP": "解题提示", "WARNING": "易错提醒", "IMPORTANT": "关键结论"}[m[1]], result)
    return result


def build_discrete(output, github, branch):
    dest = output / "discrete-math"
    dest.mkdir(parents=True, exist_ok=True)
    courseware = dest / "courseware"
    courseware.mkdir(exist_ok=True)
    pages = []

    def original(path):
        return f"{github}/blob/{quote(branch, safe='')}/{quote(path.relative_to(REPO).as_posix())}"

    def pdf(ident, title, group, path, source=None, description="课堂课件 · 保留原始排版", kind="courseware"):
        target = courseware / (ident + ".pdf")
        shutil.copyfile(path, target)
        pages.append(dict(id=ident, title=title, group=group, kind=kind, pdf="courseware/"+target.name,
                          source=original(source or path), description=description,
                          search=title+" "+group))

    lecture_titles = ["导论：离散数学与课程概览", "命题、联结词与真值", "命题公式与符号化",
                      "重言式与重言蕴涵", "等价公式", "范式", "直接推理与条件论证", "反证法", "逻辑推理习题课"]
    logic_files = sorted((DISCRETE_NOTES / "离散数学概念/章节课件/1数理逻辑").glob("*.pdf"))
    for title, path in zip(lecture_titles, logic_files, strict=True):
        number = "00" if path.name.startswith("CH0") else re.match(r"CH1-(\d)", path.name)[1].zfill(2)
        pdf("logic-"+number, title, "01 / 命题逻辑", path)

    for ident, title, group, name in [
        ("predicates", "谓词逻辑", "02 / 谓词逻辑", "2谓词逻辑.pdf"),
        ("sets", "集合论基础", "03 / 集合论基础", "3集合论基础.pdf"),
        ("relations", "二元关系", "04 / 二元关系", "4二元关系(1).pdf"),
        ("functions", "函数", "05 / 函数", "5函数.pdf"),
        ("graphs", "图论", "08 / 图论", "8图论(1).pdf"),
    ]:
        pdf(ident, title, group, DISCRETE_NOTES / "离散数学概念/章节课件" / name)
    pdf("review", "课程总复习", "复习 / 总览", DISCRETE_NOTES / "离散数学概念/总复习.pdf")

    quick = DISCRETE_NOTES / "离散数学概念/速查笔记.md"
    quick_text = re.sub(r"(?m)^## 第[一二三]篇 [^\n]*\n", "", quick.read_text(encoding="utf-8"))
    parts = re.split(r"(?m)(?=^## (?:第[一二三四五六]章|附录))", quick_text)[1:]

    def note(ident, title, group, path, text=None, kind="note"):
        text = path.read_text(encoding="utf-8") if text is None else text
        text = re.sub(r"\A\s*#{1,2} [^\n]+\n", "", text, count=1)
        if kind == "practice":
            pieces = re.split(r"(?m)^#{1,2} (?:第二部分：参考答案|参考答案[^\n]*)\n", text, maxsplit=1)
            body = render_discrete(pieces[0], ident)
            if len(pieces) == 2:
                body += '<details class="answers"><summary>展开参考答案与解析</summary>' + render_discrete(pieces[1], ident+"-answers") + '</details>'
        else:
            body = render_discrete(text, ident)
        pages.append(dict(id=ident, title=title, group=group, kind=kind, full=body, summary=body,
                          source=original(path), search=text, description="个人笔记 · 概念、条件与推理" if kind=="note" else "先独立作答，再展开解析"))

    for i, part in enumerate(parts, 1):
        title = re.match(r"## (.*)", part)[1].replace("**", "")
        note(f"note-{i}", title, "速查 / 章节笔记", quick, part)
    for ident, title, name in [("symbolization", "谓词符号化与证明", "命题符号化.md"),
                               ("warshall", "Warshall 算法", "Warshall算法.md"),
                               ("supplement", "图论补充与学习记录", "杂项.md")]:
        note(ident, title, "补充 / 理解与辨析", DISCRETE_NOTES / "补充理解" / name)
    for ident, title, name in [("practice-logic", "命题与谓词逻辑综合练习", "数理逻辑习题1.md"),
                               ("practice-sets", "集合与二元关系测试", "集合与关系习题1.md"),
                               ("practice-graphs", "图论一小时测试", "图论.md"),
                               ("practice-1", "离散数学一小时测验", "离散数学习题1.md"),
                               ("practice-2", "全课程综合阶段测试", "离散数学习题2.md")]:
        note(ident, title, "练习 / 自测与解析", DISCRETE_NOTES / "习题" / name, kind="practice")
    for year, name in [(2010,"东北大学2010离散数学试题A(1)(1).pdf"),
                        (2011,"东北大学软件学院离散数学期末试题2011(1)(1).pdf")]:
        pdf(f"exam-{year}", f"东北大学 {year} 年期末试卷", "试卷 / 历年 PDF", DISCRETE_NOTES / "习题" / name,
            description="历年试卷 · 扫描 PDF", kind="exam")
        pages[-1]["scanned"] = True

    payload = json.dumps(pages, ensure_ascii=False).replace("</", r"<\/")
    template = (DISCRETE / "index.html").read_text(encoding="utf-8")
    template = template.replace("<!--CHAPTER_DATA-->", payload)
    template = template.replace("<!--ARCHIVE_URL-->", original(DISCRETE_NOTES / "习题/离散数学历年考试卷子.rar"))
    template = template.replace("<!--SOURCE_URL-->", f"{github}/tree/{quote(branch, safe='')}/{quote('数学/离散数学')}")
    (dest / "index.html").write_text(template, encoding="utf-8", newline="\n")
    for name in ("discrete-math-hero.png",):
        shutil.copyfile(DISCRETE / name, dest / name)
    copy_mathjax(dest)

    vendor = output / "pdfjs"
    vendor.mkdir(exist_ok=True)
    with zipfile.ZipFile(DISCRETE.parent / "vendor/pdfjs-5.4.624-dist.zip") as archive:
        for entry in archive.infolist():
            if entry.is_dir() or entry.filename.endswith((".map", ".pdf")):
                continue
            if not (vendor / entry.filename).resolve().is_relative_to(vendor.resolve()):
                raise ValueError("PDF.js archive contains an unsafe path")
            archive.extract(entry, vendor)
    print(f"Packaged discrete-math: {len(pages)} sections, 17 PDFs, 9 Markdown sources.")



def build_algorithms(output, github, branch):
    """Reuse the site renderer for course chapters, contest notes and resources."""
    root = REPO / "算法"
    competition = root / "算法竞赛（C与C++）"
    destination = output / "algorithms"
    destination.mkdir(parents=True, exist_ok=True)
    pages, routes = [], {}

    def original(path):
        return f"{github}/blob/{quote(branch, safe='')}/{quote(path.relative_to(REPO).as_posix())}"

    def add(ident, title, group, path, kind="topic", text=None, description="概念、思路与代码实现"):
        body = path.read_text(encoding="utf-8-sig") if text is None else text
        if not body.strip():
            return
        entry = dict(id=ident, title=title, group=group, path=path, text=body,
                     kind=kind, description=description, source=original(path))
        pages.append(entry)
        routes.setdefault(path.resolve(), ident)

    course = root / "数据结构与算法（C语言版）/数据结构与算法笔记.md"
    chapters = re.split(r"(?m)(?=^## (?:第[一二三四五六七八九]章|附录 A))", course.read_text(encoding="utf-8"))[1:]
    for index, chapter in enumerate(chapters, 1):
        title = re.match(r"## ([^\n]+)", chapter)[1] if index <= 9 else "附录：公式、易错点与解题模板"
        add("chapter-"+str(index), title, "课程 / 数据结构与算法", course,
            kind="chapter", text=chapter, description="课程速查 · 公式、条件与典型方法")

    topics = [
        ("bubble", "冒泡排序", "排序", "排序/冒泡排序.md"),
        ("insertion", "插入排序", "排序", "排序/插入排序.md"),
        ("selection", "选择排序", "排序", "排序/选择排序.md"),
        ("search", "DFS 与 BFS", "搜索与树", "搜索与树/DFS,BFS/dfs,bfs使用场景.md"),
        ("bst", "有序数组与平衡搜索树", "搜索与树", "搜索与树/树/平衡二叉搜索树.md"),
        ("floyd", "Floyd 最短路径", "图论", "图论/Floyd/Floyd.md"),
        ("monotonic", "单调栈", "数据结构", "数据结构/单调栈.md"),
        ("dp-count", "动态规划：组合与排列", "动态规划", "动态规划/分析组合数与排列数.md"),
        ("johnson", "Johnson 双机调度", "贪心", "贪心算法/Johnson rule.md"),
        ("bigint", "高精度整数运算", "高精度", "高精度/高精度.md"),
        ("sieve", "素数与筛法", "数学", "数学/素数.md"),
        ("newton", "牛顿迭代法", "数学", "数学/牛顿迭代法.md"),
        ("bits", "位运算：颠倒位与计数", "数学", "数学/位运算/颠倒位 & 统计“1”的个数.md"),
        ("gcd", "GCD 与 LCM", "基础方法", "杂项/GCD LCM.md"),
        ("josephus", "约瑟夫环", "基础方法", "杂项/约瑟夫环问题.md"),
        ("postfix", "逆波兰表示法", "基础方法", "杂项/逆波兰表示法.md"),
        ("enumeration", "枚举与不降原则", "基础方法", "杂项/枚举/不降原则.md"),
    ]
    for ident, title, group, path in topics:
        add(ident, title, "专题 / "+group, competition / path)
    for ident, title, path in [("code-kmp", "KMP 字符串匹配源码", "杂项/KMP/KMP.c"),
                               ("code-floyd", "Floyd 完整源码", "图论/Floyd/Floyd.cpp")]:
        path = competition / path
        language = "c" if path.suffix == ".c" else "cpp"
        add(ident, title, "源码 / C 与 C++", path, kind="code",
            text="```"+language+"\n"+path.read_text(encoding="utf-8")+"\n```",
            description="完整示例 · 支持复制代码")
    for ident, title, path in [
        ("practice-search", "搜索题单与池塘计数", "搜索与树/DFS,BFS/例题"),
        ("practice-binary", "二分搜索题单", "搜索与树/二分搜索/例题"),
        ("practice-graph", "图论题单", "图论/例题"),
        ("practice-dp", "动态规划题单", "动态规划/例题"),
        ("practice-data", "数据结构题单", "数据结构/例题.md"),
        ("practice-math", "数学题单", "数学/例题"),
        ("practice-bigint", "高精度题单与平方差", "高精度/例题"),
        ("practice-enumeration", "枚举题单", "杂项/枚举/例题"),
    ]:
        add(ident, title, "习题 / 分类题单", competition / path, kind="practice",
            description="按方法练习 · 原题链接与已有题解")

    def render(text, ident, source):
        code = []

        def fence(match):
            language = match[1].strip() or "text"
            snippet = match[2].rstrip("\n")
            code.append('<figure class="code-block"><figcaption><span>'+escape(language.upper())+
                        '</span><button class="copy-code" type="button" aria-label="复制代码">复制代码</button></figcaption>'+
                        '<pre><code class="language-'+escape(language, quote=True)+'">'+escape(snippet)+'</code></pre></figure>')
            return "\nALGORITHMCODE"+str(len(code)-1)+"TOKEN\n"

        text = re.sub(r"(?m)^```([^\n]*)\n([\s\S]*?)^```\s*$", fence, text)
        text = re.sub(r"\A\s*#{1,2} [^\n]+\n", "", text, count=1)
        text = re.sub(r"(?m)^(\d+)\.\s*(?=https?://)", r"\1. ", text)
        # The raw question lists contain URLs without Markdown link syntax.
        text = re.sub(r'''(?<![(<"'])https?://[^\s<>()\u3000-\u9fff\uff00-\uffef]+''',
                      lambda match: '<'+match[0]+'>', text)
        result = render_discrete(text, ident)
        for index, block in enumerate(code):
            result = result.replace('<p>ALGORITHMCODE'+str(index)+'TOKEN</p>', block)

        def local_link(match):
            url = match["url"]
            parts = urlsplit(url)
            if not parts.scheme and not parts.netloc and parts.path:
                target = (source.parent / unquote(parts.path)).resolve()
                if target in routes:
                    url = "#"+routes[target]
                elif target.is_file() and target.is_relative_to(REPO):
                    url = original(target)
                else:
                    raise FileNotFoundError(f"Algorithm note link is missing: {source}: {url}")
            return match["prefix"]+match["q"]+url+match["q"]

        return HREF.sub(local_link, result)

    for page in pages:
        page["search"] = page["text"]
        page["full"] = page["summary"] = render(page.pop("text"), page["id"], page.pop("path"))

    # Keep originals in the notes tree; identical lecture files share one web entry.
    seen = set()
    materials = [p for p in root.rglob("*") if p.suffix.lower() in (".pdf", ".pptx", ".docx")]
    for path in sorted(materials, key=lambda p: ("数据结构与算法（C语言版）" not in p.parts, p.as_posix())):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        ident = "material-"+digest[:10]
        entry = dict(id=ident, title=path.stem.replace("+", " · "),
                     group="课件 / "+("课程资料" if "数据结构与算法（C语言版）" in path.parts else "竞赛与集训"),
                     kind="courseware" if path.suffix.lower()==".pdf" else "resource",
                     format=path.suffix[1:].upper(), source=original(path), search=path.stem,
                     description="PDF 课件 · 在线阅读" if path.suffix.lower()==".pdf" else "原始资料 · 下载后使用对应软件打开")
        if path.suffix.lower()==".pdf":
            target = destination / "courseware" / (ident+".pdf")
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, target)
            entry["pdf"] = "courseware/"+target.name
        else:
            entry["full"] = entry["summary"] = '<div class="resource-card"><span>'+entry["format"]+'</span><h2>'+escape(entry["title"])+\
                '</h2><p>这份资料保留原始格式。打开原文件页面后，可下载到本地阅读。</p><a class="primary" href="'+entry["source"]+'" target="_blank" rel="noopener">查看与下载原文件 ↗</a></div>'
        pages.append(entry)

    template = (REPO / "docs/pages/algorithms/index.html").read_text(encoding="utf-8")
    payload = json.dumps(pages, ensure_ascii=False).replace("</", r"<\/")
    template = template.replace("<!--CHAPTER_DATA-->", payload)
    template = template.replace("<!--SOURCE_URL-->", f"{github}/tree/{quote(branch, safe='')}/{quote('算法')}")
    template = template.replace("<!--RESOURCE_COUNT-->", str(len(seen)))
    (destination / "index.html").write_text(template, encoding="utf-8", newline="\n")
    shutil.copyfile(REPO / "docs/pages/algorithms/algorithms-hero.png", destination / "algorithms-hero.png")
    copy_mathjax(destination)
    print(f"Packaged algorithms: {len(pages)} sections, {len(topics)} topics, 8 question lists, {len(seen)} unique resources.")


def build(output, repository, branch):
    output = output.resolve()
    if output == REPO or REPO.is_relative_to(output):
        raise ValueError("The output must not replace the repository or its parent.")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Expected repository in owner/name format.")
    generate_calculus()
    generate_linear_algebra()
    output.mkdir(parents=True, exist_ok=True)
    github = "https://github.com/" + repository
    targets = {(source / "速查笔记.html").resolve(): output / slug / "index.html"
               for slug, source in SUBJECTS}

    def link(url, source, destination):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        # HTML fragments assembled at runtime are handled by their JSON source.
        if any(character in parts.path for character in ("'", '"', "+")):
            return url
        target = (source / unquote(parts.path)).resolve()
        if target in targets:
            relative = Path(os.path.relpath(targets[target].parent, destination)).as_posix()
            return relative + "/" + ("#" + parts.fragment if parts.fragment else "")
        if not target.is_relative_to(REPO):
            raise ValueError(f"Link outside repository: {url}")
        if not target.exists():
            raise FileNotFoundError(f"Missing link target: {target}")
        relative = quote(target.relative_to(REPO).as_posix())
        kind = "tree" if target.is_dir() else "blob"
        return f"{github}/{kind}/{quote(branch, safe='')}/{relative}" + (
            "#" + parts.fragment if parts.fragment else "")

    def markup(text, source, destination):
        return HREF.sub(lambda match: match["prefix"] + match["q"] +
                        link(match["url"], source, destination) + match["q"], text)

    for slug, source in SUBJECTS:
        destination = output / slug
        destination.mkdir(parents=True, exist_ok=True)
        text = (source / "速查笔记.html").read_text(encoding="utf-8")
        match = DATA.search(text)
        if not match:
            raise ValueError(f"No embedded note data in {source}")
        pages = json.loads(match[2])
        for page in pages:
            if page.get("source"):
                page["source"] = link(page["source"], source, destination)
            for field in ("summary", "full"):
                page[field] = markup(page[field], source, destination)
        payload = json.dumps(pages, ensure_ascii=False).replace("</", r"<\/")
        text = text[:match.start(2)] + "<!--PROTECTED_NOTE_DATA-->" + text[match.end(2):]
        text = markup(text, source, destination)
        text = text.replace("<!--PROTECTED_NOTE_DATA-->", payload)
        text = text.replace("<span>我的学习笔记</span>", '<a href="../">学习导航</a>')
        text = text.replace("</head>", '<link rel="icon" href="../favicon.svg" type="image/svg+xml"><style>.breadcrumb{min-width:0}.breadcrumb b{min-width:0;overflow:hidden;text-overflow:ellipsis}.breadcrumb>a,.top-actions{flex-shrink:0}</style></head>')
        (destination / "index.html").write_text(text, encoding="utf-8", newline="\n")
        shutil.copytree(source / "阅读资源", destination / "阅读资源", dirs_exist_ok=True)
    build_discrete(output, github, branch)
    build_algorithms(output, github, branch)
    template = (REPO / "docs/pages/index.html").read_text(encoding="utf-8")
    template = template.replace("<!--REPO_URL-->", escape(github, quote=True))
    template = template.replace("<!--MATH_URL-->", escape(
        f"{github}/blob/{quote(branch, safe='')}/{quote('数学/README.md')}", quote=True))
    (output / "index.html").write_text(template, encoding="utf-8", newline="\n")
    shutil.copyfile(REPO / "docs/pages/favicon.svg", output / "favicon.svg")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    validate(output)
    print("Validated static resources and page links.")


def validate(output):
    class ResourceParser(HTMLParser):
        def __init__(self, page):
            super().__init__()
            self.page = page

        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            target = attrs.get("href") if tag in ("a", "link") else attrs.get("src") if tag in ("script", "img") else None
            if not target:
                return
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                return
            path = (self.page.parent / unquote(parts.path)).resolve()
            if not path.is_relative_to(output) or not path.exists():
                raise FileNotFoundError(f"{self.page.name}: {target}")

    for page in output.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        parser = ResourceParser(page)
        parser.feed(text)
        match = DATA.search(text)
        if match:
            for entry in json.loads(match[2]):
                parser.feed(entry.get("summary", ""))
                parser.feed(entry.get("full", ""))
                if entry.get("pdf"):
                    parser.feed('<a href="' + escape(entry["pdf"], quote=True) + '"></a>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "scpcddk/Learning-Notes"))
    parser.add_argument("--branch", default="main")
    parser.add_argument("--serve", nargs="?", const=8768, type=int, metavar="PORT",
                        help="Serve the built site on 127.0.0.1 (default port: 8768).")
    arguments = parser.parse_args()
    build(arguments.output, arguments.repository, arguments.branch)
    if arguments.serve is not None:
        class PreviewHandler(SimpleHTTPRequestHandler):
            # Windows registry associations can otherwise map .mjs to text/plain.
            extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                              ".mjs": "text/javascript", ".js": "text/javascript",
                              ".wasm": "application/wasm"}

        handler = partial(PreviewHandler, directory=str(arguments.output.resolve()))
        with ThreadingHTTPServer(("127.0.0.1", arguments.serve), handler) as server:
            print(f"Local preview: http://127.0.0.1:{arguments.serve}/", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
