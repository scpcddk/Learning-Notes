# LaTeX 学习手册

> **从入门到精通的排版速查笔记**
>
> 适用：论文排版 / 笔记整理 / 学术写作

[参考网课](https://www.bilibili.com/video/BV1ihYKeQEKH/?spm_id_from=333.1387.favlist.content.click&vd_source=e0c0ad2a316e90d4078b1131e8182407)

---

## 目录

- [快速开始](#快速开始)
- [文档结构](#文档结构)
- [常用宏包](#常用宏包)
- [文字与段落](#文字与段落)
- [数学公式](#数学公式)
- [列表与表格](#列表与表格)
- [图片与浮动体](#图片与浮动体)
- [参考文献](#参考文献)
- [自定义命令与环境](#自定义命令与环境)
- [页面设置](#页面设置)
- [常见问题速查](#常见问题速查)

---

## 快速开始

### 最小工作示例（MWE）

> **任何 LaTeX 文档的骨架**
>
> ```latex
> \documentclass{article}
> \usepackage[UTF8]{ctex}   % 中文支持
> \begin{document}
>   你好，\LaTeX！
> \end{document}
> ```

### 💡 编译方式

| 编译器 | 特点 | 适用场景 |
|--------|------|----------|
| **pdflatex** | 速度快，不支持中文 | 纯英文文档 |
| **xelatex** | 支持中文，字体处理现代 | 中文文档（推荐） |
| **lualatex** | 功能最强，支持复杂字体操作 | 高级排版需求 |

### 文档类选项

```latex
\documentclass[11pt,a4paper]{article}  % 11号字，A4纸
\documentclass[12pt]{report}          % 12号字，report（含章节）
\documentclass{book}                   % 书籍结构（part/chapter）
\documentclass{beamer}                 % 幻灯片
```

---

## 文档结构

### 📘 章节命令层级

```latex
\part{部}        % 仅 book/report
\chapter{章}     % 仅 book/report
\section{节}
\subsection{小节}
\subsubsection{小小节}
\paragraph{段落}
\subparagraph{子段落}
```

> ⚠️ **注意**：`article` 类没有 `chapter` 和 `part`！`book/report` 类才有 `chapter`。

### 目录与摘要

```latex
\tableofcontents   % 生成目录（需编译两次）
\listoffigures     % 图目录
\listoftables      % 表目录

\begin{abstract}
  这是摘要内容……
\end{abstract}
```

### 📘 分页与换行

| 命令 | 作用 |
|------|------|
| `\\` 或 `\\[6pt]` | 强制换行（不推荐多用） |
| `\newpage` | 强制分页 |
| `\clearpage` | 强制分页并清空浮动体 |
| `\thispagestyle{empty}` | 当前页无页码 |

---

## 常用宏包

### ⭐ 必装宏包清单

```latex
\usepackage{amsmath,amssymb}   % 数学公式
\usepackage{graphicx}           % 插图
\usepackage{geometry}             % 页面边距
\usepackage{hyperref}           % 超链接
\usepackage{booktabs}           % 三线表
\usepackage{enumitem}           % 列表定制
\usepackage{caption}            % 图表标题
\usepackage{listings}           % 代码高亮
\usepackage{xcolor}             % 颜色
\usepackage{tcolorbox}          % 彩色盒子
```

> 💡 **宏包加载顺序**：`hyperref` 通常放在最后加载，避免冲突。`geometry` 在 `hyperref` 之前。

---

## 文字与段落

### 📘 字体样式

| 效果 | 命令 | 示例 |
|------|------|------|
| 粗体 | `\textbf{text}` | **粗体** |
| 斜体 | `\emph{text}` | *斜体* |
| 下划线 | `\underline{text}` | <u>下划线</u> |
| 删除线 | `\sout{text}` | 需 `ulem` 宏包 |
| 等宽 | `\texttt{text}` | `等宽` |
| 上标 | `\textsuperscript{n}` | n<sup>上标</sup> |
| 下标 | `\textsubscript{n}` | n<sub>下标</sub> |

### 字号与行距

```latex
\tiny \scriptsize \footnotesize \small
\normalsize \large \Large \LARGE \huge \Huge
```

```latex
\usepackage{setspace}
\onehalfspacing    % 1.5 倍行距
\doublespacing      % 2 倍行距
\setstretch{1.3}    % 自定义
```

### 对齐方式

```latex
\begin{center}  居中内容  \end{center}
\begin{flushleft} 左对齐   \end{flushleft}
\begin{flushright}右对齐   \end{flushright}
```

---

## 数学公式

### 📘 行内与行间

| 模式 | 语法 | 示例 |
|------|------|------|
| **行内公式** | `$...$` 或 `\(...\)` | $E=mc^2$ |
| **行间公式** | `\[...\]` | 独立居中 |
| **编号公式** | `\begin{equation}...\end{equation}` | 自动编号 |

```latex
行内：$E=mc^2$ 或 \( E=mc^2 \)

行间：
\[ E = mc^2 \]

编号：
\begin{equation}
  E = mc^2
\end{equation}
```

### 📘 常用数学符号

| 命令 | 符号 | 命令 | 符号 | 命令 | 符号 |
|------|------|------|------|------|------|
| `\alpha` | $\alpha$ | `\beta` | $\beta$ | `\gamma` | $\gamma$ |
| `\Gamma` | $\Gamma$ | `\delta` | $\delta$ | `\Delta` | $\Delta$ |
| `\theta` | $\theta$ | `\lambda` | $\lambda$ | `\mu` | $\mu$ |
| `\pi` | $\pi$ | `\sigma` | $\sigma$ | `\infty` | $\infty$ |
| `\partial` | $\partial$ | `\nabla` | $\nabla$ | `\forall` | $\forall$ |
| `\exists` | $\exists$ | `\in` | $\in$ | `\notin` | $\notin$ |

### 📘 上下标与分式

```latex
x^2, x_i, x_i^j, x^{i+j}
\frac{a}{b}, \dfrac{a}{b}   % dfrac 更美观
\sqrt{x}, \sqrt[n]{x}
\sum_{i=1}^{n}, \prod_{i=1}^{n}
\int_a^b, \iint_D, \oint_C
\lim_{x\to 0}, \max_{x\in D}
```

### 📘 矩阵与对齐

> **矩阵环境**
>
> ```latex
> \begin{pmatrix} a & b \\ c & d \end{pmatrix}   % 圆括号
> \begin{bmatrix} a & b \\ c & d \end{bmatrix}   % 方括号
> \begin{vmatrix} a & b \\ c & d \end{vmatrix}   % 竖线（行列式）
> \begin{matrix}  a & b \\ c & d \end{matrix}    % 无括号
> ```

> **对齐环境**
>
> ```latex
> \begin{align}
>   f(x) &= x^2 + 2x + 1 \\
>        &= (x+1)^2
> \end{align}
>
> \begin{align*}
>   % 无编号版本
> \end{align*}
> ```

> ⚠️ **注意**：`align` 中每行只能有一个 `&` 对齐点！多对齐点用 `alignat` 环境。

### 📘 定理环境

> **定义定理环境**
>
> ```latex
> \usepackage{amsthm}
> \newtheorem{theorem}{定理}[section]
> \newtheorem{lemma}[theorem]{引理}
> \newtheorem{definition}{定义}[section]
>
> \begin{theorem}
>   这是定理内容。
> \end{theorem}
>
> \begin{proof}
>   这是证明。
> \end{proof}
> ```

---

## 列表与表格

### 📘 三种列表

```latex
% 无序列表
\begin{itemize}
  \item 第一项
  \item 第二项
\end{itemize}

% 有序列表
\begin{enumerate}
  \item 第一步
  \item 第二步
\end{enumerate}

% 描述列表
\begin{description}
  \item[关键词] 解释内容
\end{description}
```

> 💡 **列表定制（enumitem）**
>
> ```latex
> \usepackage{enumitem}
> \begin{itemize}[leftmargin=2em,itemsep=3pt]
> \begin{enumerate}[label=(\arabic*)]
> ```

### 📘 基础表格

```latex
\begin{table}[htbp]
  \centering
  \caption{表标题}
  \begin{tabular}{lcr}      % l左 c居中 r右
    \toprule
    姓名 & 年龄 & 成绩 \\
    \midrule
    张三 & 20   & 85   \\
    李四 & 21   & 90   \\
    \bottomrule
  \end{tabular}
\end{table}
```

> ⚠️ **表格注意**
>
> - `\hline` 画横线，`booktabs` 的 `\toprule/\midrule/\bottomrule` 更美观
> - 单元格内换行用 `\makecell`（需 `makecell` 宏包）
> - 合并单元格用 `\multicolumn` 和 `\multirow`

---

## 图片与浮动体

### 📘 插入图片

> **graphicx 宏包**
>
> ```latex
> \usepackage{graphicx}
> \graphicspath{{images/}}   % 图片搜索路径
>
> \begin{figure}[htbp]
>   \centering
>   \includegraphics[width=0.8\textwidth]{figure.png}
>   \caption{图片标题}
>   \label{fig:example}
> \end{figure}
> ```

> 💡 **位置参数**
>
> | 参数 | 含义 |
> |------|------|
> | `h` | here，尽量放在此处 |
> | `t` | top，页顶 |
> | `b` | bottom，页底 |
> | `p` | page，单独一页 |
> | `!` | 忽略限制 |

### 子图

```latex
\usepackage{subcaption}

\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.45\textwidth}
    \includegraphics[width=\linewidth]{a.png}
    \caption{子图A}
  \end{subfigure}
  \hfill
  \begin{subfigure}{0.45\textwidth}
    \includegraphics[width=\linewidth]{b.png}
    \caption{子图B}
  \end{subfigure}
  \caption{总标题}
\end{figure}
```

---

## 参考文献

### 📘 BibTeX 方式（三步走）

> **Step 1**：创建 `refs.bib` 文件
>
> ```bibtex
> @article{einstein1905,
>   author  = {Albert Einstein},
>   title   = {Zur Elektrodynamik bewegter K{\"o}rper},
>   journal = {Annalen der Physik},
>   year    = {1905},
>   volume  = {322},
>   pages   = {891--921}
> }
> ```

> **Step 2**：文档中引用
>
> ```latex
> \usepackage[numbers]{natbib}
> \bibliographystyle{plain}
>
> 文中引用：\cite{einstein1905}
>
> \bibliography{refs}   % 放在文档末尾
> ```

> **Step 3**：编译顺序
>
> ```
> xelatex -> bibtex -> xelatex -> xelatex
> ```

### 直接引用（简易版）

```latex
\begin{thebibliography}{99}
  \bibitem{einstein1905}
  A. Einstein, \textit{Zur Elektrodynamik bewegter K{\"o}rper},
  Annalen der Physik, 322(1905), 891--921.
\end{thebibliography}
```

---

## 自定义命令与环境

### 📘 newcommand

> **简化输入**
>
> ```latex
> % 无参数
> \newcommand{\R}{\mathbb{R}}
>
> % 有参数
> \newcommand{\norm}[1]{\left\|#1\right\|}
> % 使用：\norm{x} -> ||x||
>
> % 可选参数
> \newcommand{\dv}[2][x]{\frac{\mathrm{d}#2}{\mathrm{d}#1}}
> % 使用：\dv{y} -> dy/dx；\dv[t]{y} -> dy/dt
> ```

### renewcommand

```latex
\renewcommand{\baselinestretch}{1.5}   % 1.5倍行距
\renewcommand{\figurename}{图}          % 图标题前缀
\renewcommand{\tablename}{表}           % 表标题前缀
```

---

## 页面设置

### 📘 geometry 宏包

> **页面边距**
>
> ```latex
> \usepackage{geometry}
> \geometry{
>   top=2.5cm, bottom=2.5cm,
>   left=2.5cm, right=2.5cm,
>   headheight=15pt
> }
> ```

### 页眉页脚

```latex
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\lhead{\leftmark}
\rhead{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
```

---

## 常见问题速查

### 📘 Q & A

| 问题 | 解决方案 |
|------|----------|
| **中文显示不出来？** | 用 `xelatex` 编译，并加载 `ctex` 或 `xeCJK` |
| **公式编号乱了？** | 使用 `amsmath` 的 `\eqref` 代替 `\ref` |
| **图片位置乱跑？** | 浮动体特性，用 `[H]`（需 `float` 宏包）强制固定 |
| **参考文献不显示？** | 确认编译了四次：xelatex → bibtex → xelatex → xelatex |
| **表格太宽？** | 用 `tabularx` 或 `resizebox` 缩放 |
| **如何插入代码？** | 用 `listings` 或 `minted`（后者需 Python pygments） |
| **编译报错找不到字体？** | 检查系统字体，或用 `\setCJKmainfont{SimSun}` 显式指定 |
| **公式太长换行？** | 用 `multline` 或 `split` 环境 |
| **多行公式对齐？** | 用 `align` 环境，`&` 放等号前 |
| **页码从正文开始？** | `\frontmatter` / `\mainmatter`（book 类）或手动 `\setcounter{page}{1}` |

---

> **— 笔记结束 —**
>
> 本手册涵盖 LaTeX 核心用法，建议边查边练。
> 遇到新问题及时补充，形成个人专属速查手册。
