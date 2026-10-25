# GCD与LCM学习笔记

## 一.基本概念

- GCD：最大公约数；LCM：最小公倍数。
- 对 a≠0，gcd(a,0)=|a|；0 并非“没有公约数”，因为每个非零整数都整除0。
- 编程中常约定 gcd(0,0)=0、lcm(a,0)=0。

## 二.核心公式

至少一个数非零时，lcm(a,b)=|a×b|/gcd(a,b)。实际计算应先除后乘，并检查乘法是否超出类型范围；两数均为0时直接返回0。

## 三.欧几里得算法（辗转相除法）

1. 对非负整数，gcd(a,b)=gcd(b,a%b)。
2. 重复更新 a=b、b=旧a%旧b。
3. b=0 时返回 a。输入含负数时，须先安全地转为绝对值；有符号类型的最小负值不能直接在同一类型中取正值。

## 四.代码（C11，非负整数）

```c
#include <stdbool.h>
#include <limits.h>

typedef unsigned long long ull;

ull gcd(ull a, ull b) {
    while (b != 0) {
        ull remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

// result 指向有效存储；false 表示结果超出 unsigned long long 范围。
bool lcm(ull a, ull b, ull *result) {
    if (a == 0 || b == 0) {
        *result = 0;
        return true;
    }
    ull reduced = a / gcd(a, b);
    if (reduced > ULLONG_MAX / b) return false;
    *result = reduced * b;
    return true;
}
```
