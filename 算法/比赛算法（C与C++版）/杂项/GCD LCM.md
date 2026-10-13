# GCD与LCM学习笔记
## 一.基本概念
- GCD：最大公约数
- LCM：最小公倍数
- 0 与任何数无有效公约数/公倍数，需特殊处理
## 二.核心公式
==最小公倍数 = 两数乘积的绝对值 ÷ 最大公约数==
## 三.欧几里得算法（辗转相除法）
1.原理： GCD(a,b) = GCD(b, a%b) ，直到余数为0，此时a为最大公约数
2.终止条件： b = 0 ，返回a
3.计算步骤：
<br>
+ 计算 a 除以 b 的余数
- 将 b 赋值给 a，余数赋值给 b
* 重复直到 b=0，返回 a
## 四.代码
// 求最大公约数 GCD
int gcd(int a, int b) 
{
    while (b != 0) 
    {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
// 求最小公倍数 LCM
int lcm(int a, int b) 
{
    if (a == 0 || b == 0)
    return 0;
    return abs(a * b) / gcd(a, b);
}