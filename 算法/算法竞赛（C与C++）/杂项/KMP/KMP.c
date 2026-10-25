#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/**
 * 计算模式串的 nextval 数组（优化版的 next 数组）
 * @param needle 模式串（待查找的字符串）
 * @param nextval 存储 nextval 值的数组
 * @note nextval 数组在 next 数组基础上进行优化，避免不必要的回溯
 */
void Nextval(const char* needle, int* nextval)
{
    int i = 0, j = -1;          // i: 当前处理位置，j: 前缀末尾位置（或next值）
    int len2 = (int)strlen(needle);
    
    if(len2 == 0)              // 处理空模式串情况
        return;
    nextval[0] = -1;           // 仅构造下标 0..len2-1

    while(i < len2 - 1)
    {
        // 情况1：j为-1（初始状态）或当前字符匹配
        if(j == -1 || needle[i] == needle[j])
        {
            i++;
            j++;
            
            // KMP优化：如果当前位置字符与next值指向的字符相同
            // 则nextval[i]直接等于nextval[j]，避免不必要的比较
            if(needle[i] == needle[j])
            {
                nextval[i] = nextval[j];
            }
            else
            {
                nextval[i] = j;   // 常规next值赋值
            }
        }
        // 情况2：字符不匹配，通过nextval数组回退j
        else
        {
            j = nextval[j];
        }
    }
}

/**
 * KMP字符串匹配算法
 * @param haystack 主串（被搜索的字符串）
 * @param needle 模式串（要查找的字符串）
 * @param pos 开始搜索的位置
 * @return 匹配成功返回模式串在主串中的起始位置，失败返回-1
 */
int KMP(const char* haystack, const char *needle, int pos)
{
    int len1 = (int)strlen(haystack);    // 主串长度
    int len2 = (int)strlen(needle);      // 模式串长度
    
    // 特殊情况处理
    if(pos < 0 || pos > len1)       // 允许在串尾匹配空串
        return -1;
    if(len2 == 0)                   // 从 pos 开始，空串匹配在 pos
        return pos;
    if(len2 > len1 - pos)           // 剩余主串比模式串短
        return -1;
    
    // 分配并初始化nextval数组
    int* nextval = (int*)malloc(len2 * sizeof(int));
    if(nextval == NULL) return -1;
    Nextval(needle, nextval);
    
    int i = pos;    // 主串指针，从pos位置开始
    int j = 0;      // 模式串指针，从0开始
    
    // 开始匹配过程
    while(i < len1 && j < len2)
    {
        // j == -1 表示需要移动主串指针，同时模式串从头开始
        // 字符匹配时，两个指针都向后移动
        if(j == -1 || haystack[i] == needle[j])
        {
            i++;
            j++;
        }
        // 字符不匹配时，模式串指针通过nextval数组回退
        // 主串指针i不回溯，这是KMP算法的关键优化
        else
        {
            j = nextval[j];
        }
    }
    
    free(nextval);  // 释放动态分配的内存
    
    // 判断匹配结果
    if(j == len2)   // 模式串指针走到末尾，说明完全匹配
    {
        return i - len2;  // 返回匹配的起始位置
    }
    else            // 匹配失败
    {
        return -1;
    }
}

int main()
{
    char haystack[200] = {0};  // 主串
    char needle[200] = {0};    // 模式串
    
    // 读取输入字符串
    // 演示输入为两个不含空格、长度不超过199的字符串。
    if(scanf("%199s %199s", haystack, needle) != 2) return 1;
    
    // 执行KMP搜索，从位置0开始
    int re = KMP(haystack, needle, 0);
    
    // 输出结果
    printf("%d\n", re);
    
    return 0;
}
