"""从 Markdown 笔记生成可直接打开的线性代数阅读页。

运行：python 数学/线性代数/阅读页面/生成阅读页.py
依赖：markdown-it-py（pip install markdown-it-py）
"""
from pathlib import Path
import html
import json
import re
from urllib.parse import quote, unquote

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
NOTES = ROOT.parent / '基础概念' / '笔记'
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
    out = re.sub(r'href="([^"#:/]+\.md)"', lambda m: 'href="../基础概念/笔记/' + quote(unquote(m[1])) + '"', out)
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
            'source': '../基础概念/笔记/' + quote(filename),
            'summary': render(SUMMARIES[ident], ident+'-quick'),
            'full': render(text, ident+'-full'),
            'search': re.sub(r'[#*$>\\{}]', ' ', text),
        })
    chapters.append({'id': 'sec-formula', 'number': '∑', 'title': '公式速查', 'description': '把最常用的结论，放在同一页。', 'tags': ['条件先行', '联系记忆'], 'source': '', 'summary': render(FORMULAS, 'formulas'), 'full': render(FORMULAS, 'formulas'), 'search': FORMULAS})
    payload = json.dumps(chapters, ensure_ascii=False).replace('</', r'<\/')
    shell = (ROOT / '阅读页模板.html').read_text(encoding='utf-8')
    (ROOT / '速查笔记.html').write_text(shell.replace('<!--CHAPTER_DATA-->', payload), encoding='utf-8', newline='\n')
    print(f'已生成速查笔记.html：{len(CHAPTERS)} 篇笔记 + 公式速查')


if __name__ == '__main__':
    build()
