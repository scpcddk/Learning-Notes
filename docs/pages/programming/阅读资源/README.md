# 编程语言阅读页封面

四张封面使用内置 `image_gen` 图像生成工具制作，延续线性代数和高等数学阅读页的暖白纸面、森林绿玻璃、黄铜细节与柔和光影。图像均为 1536 × 1024 的 3:2 横向 PNG，背景不透明。

| 用途 | 选用封面 | 最终提示词 |
| --- | --- | --- |
| 编程语言总入口 | [programming-hero.png](programming-hero.png) | [programming-hero.prompt.txt](programming-hero.prompt.txt) |
| C 与 C++ | [c-cpp-hero.png](c-cpp-hero.png) | [c-cpp-hero.prompt.txt](c-cpp-hero.prompt.txt) |
| Java | [java-hero.png](java-hero.png) | [java-hero.prompt.txt](java-hero.prompt.txt) |
| Python | [python-hero.png](python-hero.png) | [python-hero.prompt.txt](python-hero.prompt.txt) |

总封面使用代码括号、语法树和模块结构表达编程语言，不绑定具体语言数量，后续加入其他语言仍可沿用。

C/C++ 封面使用双六边形语言标识与内存模块；Java 采用用户选定的第一版咖啡杯与红色蒸汽造型；Python 使用蓝黄配色的双蛇标识。各语言图标经过立体材质重绘，不作为官方原始标志文件使用。

封面由统一构建脚本接入编程语言总览与各语言阅读页；原始 Markdown 保留在仓库的“编程语言”目录中。页面生成与发布方式见 [阅读网站说明](../../README.md)。
