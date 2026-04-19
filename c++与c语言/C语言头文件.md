# C语言头文件核心笔记

## ==一、高频核心头文件==

### 1. `<stdio.h>`
**核心功能**：标准输入输出

**常用函数**：
- **控制台**：`printf()`, `scanf()`, `puts()`, `getchar()`, `putchar()`
- **文件操作**：`fopen()`, `fclose()`, `fprintf()`, `fscanf()`, `fgets()`, `fputs()`, `feof()`

### 2. `<stdlib.h>`
**核心功能**：通用工具函数

**常用函数**：
- **内存管理**：`malloc()`, `calloc()`, `realloc()`, `free()`
- **随机数**：`rand()`, `srand()`

### 3. `<string.h>`
**核心功能**：字符串操作

**常用函数**：
- **长度/复制**：`strlen()`, `strcpy()`, `strncpy()`
- **比较/拼接**：`strcmp()`, `strncmp()`, `strcat()`, `strncat()`
- **查找**：`strchr()`, `strstr()`, `strtok()`
- **内存操作**：`memset()`, `memcpy()`, `memcmp()`

### 4. `<math.h>`
**核心功能**：数学计算

**常用函数**：
- **基础运算**：`sqrt()`, `pow()`, `fabs()`, `ceil()`, `floor()`, `fmod()`
- **三角函数**：`sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()`
- **指数/对数**：`exp()`, `log()`, `log10()`

> **编译注意**：Linux/macOS 编译需加 `-lm` 链接数学库  
> 示例：`gcc test.c -o test -lm`

### 5. `<ctype.h>`
**核心功能**：字符判断与转换

**常用函数**：
- **判断类**：`isalpha()`, `isdigit()`, `isalnum()`, `isspace()`, `isupper()`, `islower()`
- **转换类**：`toupper()`, `tolower()`

### 6. `<limits.h>`
**核心功能**：数据类型边界值定义

**常用宏**：`CHAR_BIT`, `CHAR_MAX`, `CHAR_MIN`, `INT_MAX`, `INT_MIN`, `LONG_MAX`

---

## 二、实用扩展头文件

### 7. `<time.h>`
**核心功能**：时间与日期处理

**常用函数**：`time()`, `ctime()`, `localtime()`, `clock()`, `difftime()`, `strftime()`

### 8. `<stddef.h>`
**核心功能**：标准类型与宏定义

**常用内容**：`size_t`, `ptrdiff_t`, `NULL`, `offsetof()`

### 9. `<stdarg.h>`
**核心功能**：可变参数处理

**常用宏**：`va_list`, `va_start()`, `va_arg()`, `va_end()`

### 10. `<errno.h>`
**核心功能**：错误码处理

**常用内容**：`errno`（错误码变量），`perror()`（打印错误信息）

### 11. `<windows.h>`（Windows 专属）
**核心功能**：Windows API 调用

**常用功能**：窗口创建、文件操作、进程控制、定时器（仅适配 MSVC 编译器）

---

## 三、自定义头文件（标准模板）

```c
// myheader.h
#ifndef MYHEADER_H  // 防止重复包含（必须加）
#define MYHEADER_H

// 1. 函数声明（仅声明，不实现）
void print_hello();
int add(int a, int b);

// 2. 宏定义
#define PI 3.1415926
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// 3. 结构体声明
typedef struct {
    int x;
    int y;
} Point;

#endif  // 结束防止重复包含