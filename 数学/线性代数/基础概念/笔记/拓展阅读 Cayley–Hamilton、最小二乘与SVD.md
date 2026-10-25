# 拓展阅读：Cayley–Hamilton、最小二乘与 SVD

> **本章主线**：把矩阵多项式、正交投影与一般矩阵分解联系起来。
>
> **学习目标**：理解 Cayley–Hamilton、最小二乘正规方程、SVD 与伪逆的用途。

本篇承接第二、四、五、七章，介绍矩阵多项式降阶、无精确解时的最佳拟合，以及适用于长方形矩阵的分解方法。

## 一、Cayley–Hamilton 定理：矩阵满足自己的特征方程

设 $A$ 为 $n$ 阶实矩阵，特征多项式为

$$p(\lambda)=\det(\lambda E-A)=\lambda^n+c_{n-1}\lambda^{n-1}+\cdots+c_1\lambda+c_0.$$

则

$$\boxed{p(A)=A^n+c_{n-1}A^{n-1}+\cdots+c_1A+c_0E=O.}$$

这里常数项对应 $c_0E$，结果为零矩阵；该定理不要求 $A$ 可对角化。

**用途**：把高次幂降到低于 $n$ 次；若 $c_0\neq0$，还可以解出逆矩阵：

$$A^{-1}=-\frac1{c_0}\left(A^{n-1}+c_{n-1}A^{n-2}+\cdots+c_1E\right).$$

**例**：取 $A=\begin{pmatrix}1&1\\0&2\end{pmatrix}$，有

$$p(\lambda)=(\lambda-1)(\lambda-2)=\lambda^2-3\lambda+2.$$

于是 $A^2-3A+2E=O$，从而

$$A^3=3A^2-2A=7A-6E,\qquad A^{-1}=\frac12(3E-A)=\begin{pmatrix}1&-1/2\\0&1/2\end{pmatrix}.$$

> [!WARNING]
> $p(A)$ 表示先将特征多项式展开，再用矩阵幂代入。不能把行列式中的标量变量直接替换成矩阵后，仍按普通数值行列式来解释。

## 二、最小二乘：没有精确解时，求残差最小的解

### 1. 从方程组到优化问题

对 $A\in\mathbb{R}^{m\times n}$、$b\in\mathbb{R}^m$，若 $Ax=b$ 无解，可寻找使

$$\|Ax-b\|^2$$

最小的 $x$，称为**最小二乘解**。

$Ax$ 总在列空间 $\operatorname{Col}(A)$ 内，所以最优的拟合向量 $A\hat x$ 是 $b$ 在列空间上的正交投影。最优残差 $b-A\hat x$ 与列空间正交，故

$$\boxed{A^\mathrm{T}(b-A\hat x)=0\quad\Longleftrightarrow\quad A^\mathrm{T}A\hat x=A^\mathrm{T}b.}$$

此方程称为**正规方程**。反之，只要 $\hat x$ 满足正规方程，正交分解就能保证它使残差平方和最小。

- 若 $A$ 列满秩，则 $A^\mathrm{T}A$ 正定、可逆，最小二乘解唯一：$\hat x=(A^\mathrm{T}A)^{-1}A^\mathrm{T}b$。
- 若 $A$ 列不满秩，最小二乘解不唯一；但拟合向量 $A\hat x$ 仍唯一。全部最小二乘解相差一个 $\ker A$ 中的向量。

### 2. 完整例题：用直线拟合三个数据点

用直线 $y=a+bt$ 拟合 $(0,1),(1,2),(2,2)$。目标是使三个纵向误差的平方和最小，矩阵形式为

$$
M\begin{pmatrix}a\\b\end{pmatrix}\approx d,\qquad
M=\begin{pmatrix}1&0\\1&1\\1&2\end{pmatrix},\qquad d=\begin{pmatrix}1\\2\\2\end{pmatrix}.
$$

正规方程为

$$
\begin{pmatrix}3&3\\3&5\end{pmatrix}\begin{pmatrix}a\\b\end{pmatrix}
=\begin{pmatrix}5\\6\end{pmatrix}.
$$

两式相减得 $2b=1$，故 $b=1/2$，再得 $a=7/6$。最佳拟合直线为

$$\boxed{y=\frac76+\frac12t.}$$

拟合值、残差及平方和分别为

$$
M\hat x=\begin{pmatrix}7/6\\5/3\\13/6\end{pmatrix},\quad
r=d-M\hat x=\begin{pmatrix}-1/6\\1/3\\-1/6\end{pmatrix},\quad
\|r\|^2=\frac16.
$$

检查 $M^\mathrm{T}r=0$，即残差分别与常数列 $(1,1,1)^\mathrm{T}$ 和自变量列 $(0,1,2)^\mathrm{T}$ 正交。

> [!NOTE]
> 正规方程便于理解理论；实际浮点计算中，形成 $A^\mathrm{T}A$ 可能放大数值误差，常用 QR 分解或 SVD 求解。这里的直线拟合最小化纵向误差，并非点到直线的垂直距离平方和。

## 三、奇异值分解（SVD）：长方形矩阵也能分解

### 1. 定义与矩阵尺寸

任意实矩阵 $A\in\mathbb{R}^{m\times n}$ 均可写成

$$\boxed{A=U\Sigma V^\mathrm{T},}$$

其中 $U$ 为 $m$ 阶正交矩阵，$V$ 为 $n$ 阶正交矩阵，$\Sigma$ 为 $m\times n$ 矩阵，其主对角线元素满足

$$\sigma_1\geq\sigma_2\geq\cdots\geq\sigma_p\geq0,\qquad p=\min(m,n),$$

其他元素均为零。$\sigma_i$ 称为**奇异值**，正奇异值的个数等于 $R(A)$。

由

$$A^\mathrm{T}A=V(\Sigma^\mathrm{T}\Sigma)V^\mathrm{T}$$

可知，正奇异值是 $A^\mathrm{T}A$ 的正特征值的平方根；当 $n>m$ 时，$A^\mathrm{T}A$ 还至少有 $n-m$ 个额外的零特征值。

### 2. 与特征值、对角化的区别

| 对比项 | 相似对角化 | SVD |
|--------|------------|-----|
| 矩阵形状 | 方阵 | 方阵或长方形矩阵 |
| 是否总存在 | 不一定 | 对任意实矩阵都存在 |
| 变换方式 | $A=P\Lambda P^{-1}$，同一空间换基 | $A=U\Sigma V^\mathrm{T}$，输入、输出各选正交基 |
| 数值 | 特征值可能为负或复数 | 奇异值都是非负实数 |

对实对称矩阵，奇异值等于特征值的绝对值（再按大小排序）。一般矩阵没有这种简单对应。

### 3. 可直接验证的例子

设

$$
A=\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
U=V=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad
\Sigma=\begin{pmatrix}2&0\\0&0\end{pmatrix}.
$$

则 $U^\mathrm{T}U=V^\mathrm{T}V=E$，直接相乘得到 $U\Sigma V^\mathrm{T}=A$。奇异值为 $2,0$，所以秩为 $1$。

几何上，先用 $V^\mathrm{T}$ 把输入坐标转到两个正交方向，再沿第一个方向放大 $2$ 倍、沿第二个方向压缩为零，最后用 $U$ 表示输出方向。

### 4. 伪逆与最小范数解

在 $\Sigma^\mathrm{T}$ 中，将所有正奇异值替换为倒数、零仍保留为零，得到 $n\times m$ 矩阵 $\Sigma^+$。定义

$$A^+=V\Sigma^+U^\mathrm{T}.$$

则 $\hat x=A^+b$ 是最小二乘解中长度最小的唯一一个；若 $Ax=b$ 有解，它也是所有精确解中长度最小的一个。

上例中 $A^+=\frac14\begin{pmatrix}1&1\\1&1\end{pmatrix}$。对 $b=(2,2)^\mathrm{T}$，精确解满足 $x_1+x_2=2$；伪逆给出 $\hat x=(1,1)^\mathrm{T}$，其长度最小。

## 四、与原七章的衔接

- 第二、五章：矩阵幂、逆矩阵与特征多项式 → Cayley–Hamilton 定理。
- 第四、七章：列空间、方程组、正交投影 → 最小二乘。
- 第三、五、七章：正交基、实对称矩阵对角化、核与像 → SVD。

---

**章节导航**：[阅读指南](<阅读指南.md>) · [上一章](<第七章 线性空间与线性变换.md>) · [打开阅读网页](<https://scpcddk.github.io/Learning-Notes/linear-algebra/>)
