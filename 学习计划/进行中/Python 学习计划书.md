# Python 学习计划书

## 一、学习定位

**Python 定位：AI 辅助语言**

你的主线仍然是 Java / Spring Boot 后端，Python 主要用于：

* AI API 调用
* 数据处理
* RAG
* Agent
* 机器学习
* PyTorch
* 阅读 AI 项目代码
* 编写 AI 小工具

因此不追求 Python 专家级水平。

**学习频率：**

* 每周 1 次
* 每次 1～1.5 小时
* 约 60～90 分钟

**核心原则：**

> Python 本身学到“够用且扎实”，把更多时间留给 AI。

---

# 二、最终目标

完成后应该能够：

* [ ] 独立编写中小型 Python 程序
* [ ] 看懂常见 Python 项目代码
* [ ] 熟练使用 Python 数据结构
* [ ] 编写函数和简单类
* [ ] 处理文件、JSON、异常
* [ ] 使用第三方库
* [ ] 创建和管理 Python 项目环境
* [ ] 调用 HTTP / AI API
* [ ] 使用 Pydantic
* [ ] 使用 NumPy / Pandas 完成基础数据处理
* [ ] 使用 Python 完成 LLM、Embedding、RAG、Agent 实践
* [ ] 后续能够进入 scikit-learn / PyTorch

---

# 三、学习路线

## Phase 0：水平测试

**目标：先判断哪些内容已经会。**

* [ ] 基础语法测试
* [ ] 数据类型测试
* [ ] list / tuple / dict / set 测试
* [ ] 函数测试
* [ ] 综合编程题
* [ ] 简单代码阅读

**处理原则：**

已经掌握 → 测试通过后直接跳过。

似懂非懂 → 补充练习。

完全不会 → 正式学习。

---

# Phase 1：Python 基础

### 目标

能够独立写出简单 Python 程序。

### 知识点

* [ ] 变量
* [ ] int / float / str / bool
* [ ] 类型转换
* [ ] 运算符
* [ ] if / elif / else
* [ ] for
* [ ] while
* [ ] break / continue
* [ ] 字符串操作
* [ ] f-string

### 实践

* [ ] 简单计算程序
* [ ] 条件判断程序
* [ ] 循环统计程序
* [ ] 字符串处理程序

### 阶段验收

能够**不看答案**写出一个 30～50 行左右的小程序。

---

# Phase 2：Python 数据结构

这是 Python 后续 AI 编程非常重要的一部分。

* [ ] list
* [ ] tuple
* [ ] dict
* [ ] set
* [ ] 索引
* [ ] 切片
* [ ] 遍历
* [ ] 增删改查
* [ ] 嵌套数据结构
* [ ] list comprehension
* [ ] dict comprehension
* [ ] 常见内置函数
* [ ] `len`
* [ ] `range`
* [ ] `enumerate`
* [ ] `zip`
* [ ] `sorted`
* [ ] `map` / `filter` 了解

### 实践

* [ ] 学生成绩统计
* [ ] 商品数据处理
* [ ] 字典嵌套数据处理
* [ ] 简单数据清洗

### 阶段验收

能够处理类似：

```text
[
    {"name": "Tom", "score": 85},
    {"name": "Jack", "score": 92},
    {"name": "Lucy", "score": 78}
]
```

这样的数据。

---

# Phase 3：函数与模块

* [ ] 函数定义
* [ ] 参数
* [ ] 返回值
* [ ] 默认参数
* [ ] 关键字参数
* [ ] 可变参数
* [ ] 作用域
* [ ] lambda 基础
* [ ] import
* [ ] module
* [ ] package
* [ ] `__name__ == "__main__"`

### 实践

* [ ] 把之前的程序拆成多个函数
* [ ] 编写自己的工具模块
* [ ] 多文件 Python 项目

### 阶段验收

能够把一个较长程序合理拆成多个函数和模块。

---

# Phase 4：Python 实用开发

这一阶段开始进入真正的“能干活”。

* [ ] 异常处理
* [ ] try / except / finally
* [ ] 自定义异常了解
* [ ] 文件读写
* [ ] pathlib
* [ ] JSON
* [ ] CSV 基础
* [ ] 时间日期
* [ ] random
* [ ] os / sys 基础
* [ ] logging 基础

### 实践

* [ ] 文件批量处理
* [ ] JSON 数据读取与修改
* [ ] 简单日志系统
* [ ] 配置文件读取

---

# Phase 5：Python 面向对象

不追求特别深入。

* [ ] class
* [ ] object
* [ ] `__init__`
* [ ] 实例属性
* [ ] 实例方法
* [ ] 类属性
* [ ] 类方法
* [ ] 静态方法
* [ ] 继承
* [ ] 多态
* [ ] 封装
* [ ] `__str__`
* [ ] `__repr__`

### 实践

* [ ] 学生管理类
* [ ] 简单游戏对象
* [ ] API 数据对象

### 阶段目标

看到 Python 项目里的 class，能够基本理解它在干什么。

---

# Phase 6：Python 进阶核心

**这一阶段不需要一次性全部深入。**

* [ ] 迭代器
* [ ] 可迭代对象
* [ ] 生成器
* [ ] yield
* [ ] 装饰器
* [ ] 闭包
* [ ] 上下文管理器
* [ ] `with`
* [ ] typing
* [ ] 泛型基础
* [ ] dataclass

### 原则

这些内容以：

**理解 → 能看懂 → 能简单使用**

为目标。

暂时不追求底层原理。

---

# Phase 7：Python 工程基础

* [ ] venv
* [ ] pip
* [ ] requirements.txt
* [ ] Python 项目结构
* [ ] 环境变量
* [ ] `.env`
* [ ] logging
* [ ] pytest 基础
* [ ] Git 配合 Python 项目

### 实践

* [ ] 创建标准 Python 项目
* [ ] 创建虚拟环境
* [ ] 安装第三方库
* [ ] 编写测试
* [ ] 使用 `.env` 管理 API Key

---

# Phase 8：HTTP 与 API

这一阶段开始直接服务 AI。

* [ ] HTTP 基础
* [ ] GET / POST
* [ ] Request / Response
* [ ] Header
* [ ] Query Parameter
* [ ] JSON
* [ ] Status Code
* [ ] httpx
* [ ] API Key
* [ ] Timeout
* [ ] 异常处理

### 实践

* [ ] 调用一个公开 API
* [ ] 发送 GET 请求
* [ ] 发送 POST 请求
* [ ] 解析 JSON
* [ ] 封装自己的 API 调用函数

---

# Phase 9：AI Python 基础

进入你的 AI 主线。

* [ ] LLM API 调用
* [ ] Prompt
* [ ] Message
* [ ] Token 基础
* [ ] Streaming
* [ ] Structured Output
* [ ] Pydantic
* [ ] 数据模型
* [ ] API 错误处理
* [ ] 多轮对话程序

### 项目

**Python AI 对话程序**

能够：

```text
Python
 ↓
LLM API
 ↓
模型
 ↓
返回结果
 ↓
Python 处理
```

---

# Phase 10：数据处理

只学 AI 需要的部分。

### NumPy

* [ ] ndarray
* [ ] shape
* [ ] dtype
* [ ] 索引
* [ ] 切片
* [ ] 基础运算

### Pandas

* [ ] DataFrame
* [ ] Series
* [ ] 读取数据
* [ ] 查询
* [ ] 筛选
* [ ] 排序
* [ ] 缺失值
* [ ] 分组
* [ ] 基础统计

### Matplotlib

* [ ] 基础绘图
* [ ] 折线图
* [ ] 柱状图
* [ ] 散点图

目标只是：

> **能够看懂和处理 AI / ML 项目里的基础数据。**

---

# Phase 11：Embedding + RAG

结合你的 AI 路线学习。

* [ ] Embedding API
* [ ] 向量
* [ ] 向量相似度
* [ ] 文本切分
* [ ] 向量化
* [ ] 向量存储
* [ ] 相似度搜索
* [ ] Retrieval
* [ ] Context
* [ ] RAG 基本流程

### 项目

**个人知识库 RAG**

```text
文档
 ↓
切分
 ↓
Embedding
 ↓
向量数据库
 ↓
检索
 ↓
LLM
 ↓
答案
```

---

# Phase 12：Tool Calling + Agent

* [ ] Tool Calling
* [ ] Function Schema
* [ ] 参数定义
* [ ] 工具执行
* [ ] 工具返回结果
* [ ] 多工具
* [ ] Agent 基础
* [ ] Agent Loop
* [ ] 状态管理
* [ ] LangChain 了解
* [ ] LangGraph 后续学习
* [ ] MCP 后续学习

### 项目

**Python AI Agent**

例如：

```text
用户
 ↓
Agent
 ↓
判断需要什么工具
 ↓
调用工具
 ↓
得到结果
 ↓
继续推理
 ↓
最终回答
```

---

# Phase 13：机器学习 Python

等 AI 应用基础稳定后再进入。

* [ ] scikit-learn
* [ ] Dataset
* [ ] Feature
* [ ] Train / Test
* [ ] Regression
* [ ] Classification
* [ ] Clustering
* [ ] Evaluation
* [ ] Pipeline
* [ ] 基础数据预处理

目标：

> 能够用 Python 实际跑一个机器学习模型。

---

# Phase 14：PyTorch

进入深度学习阶段。

* [ ] Tensor
* [ ] Shape
* [ ] Dataset
* [ ] DataLoader
* [ ] Model
* [ ] Forward
* [ ] Loss
* [ ] Optimizer
* [ ] Backpropagation
* [ ] Training Loop
* [ ] GPU
* [ ] 基础神经网络

之后再与：

**Transformer → LLM → 深度学习**

衔接。

---

# 四、暂时不学

以下内容目前不值得占用你的有限 Python 时间：

* [ ] CPython 源码
* [ ] Python C API
* [ ] 字节码深入
* [ ] AST 深入
* [ ] 元类深入
* [ ] 描述符深入
* [ ] Cython
* [ ] Python GUI
* [ ] Django
* [ ] Flask
* [ ] 大规模爬虫
* [ ] 数据分析师完整技术栈
* [ ] Python 性能优化深入

以后项目真正需要再学。

---

# 五、库学习优先级

### 必须掌握

* [ ] Python Standard Library
* [ ] pathlib
* [ ] json
* [ ] typing
* [ ] logging
* [ ] httpx
* [ ] Pydantic
* [ ] NumPy
* [ ] Pandas

### AI 阶段掌握

* [ ] 对应 LLM SDK
* [ ] Embedding SDK
* [ ] 向量数据库 SDK
* [ ] LangChain
* [ ] LangGraph
* [ ] MCP Python SDK

### 后续学习

* [ ] scikit-learn
* [ ] PyTorch

### 了解即可

* [ ] requests
* [ ] Matplotlib 深入
* [ ] Seaborn
* [ ] Plotly
* [ ] Poetry
* [ ] uv

---

# 六、每周学习模式

因为你只有 **1～1.5 小时/周**，固定采用：

### ① 10分钟：复习

* 回忆上周内容
* 2～3 个问题
* 一个小代码题

### ② 20～30分钟：新知识

只讲**一个核心概念**。

### ③ 25～40分钟：自己写

由你完成代码，不直接给完整答案。

### ④ 10分钟：检查

* 找错误
* 解释原因
* 修改代码
* 总结

### ⑤ 最后 5分钟

记录：

```text
本周学习：
已掌握：
薄弱：
未完成：
下周：
```

---

# 七、最重要的学习原则

你的 Python 不应该走：

> Python → Python → Python → 学完 Python → 再学 AI

而应该走：

> **Python基础 → Python够用 → API → AI → RAG → Agent → ML → PyTorch**

也就是说，**Python 和 AI 是逐渐融合的**。

你每周只有 1～1.5 小时，所以我们之后实际学习时也不会死守这个计划。**如果某个 Python 知识点已经足够支撑当前 AI 学习，就停止深入，把时间留给 AI。**

这套计划更适合你目前“**Java 后端主线 + AI 第二主线 + Python 辅助**”的整体安排。
