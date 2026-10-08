# 个人 AI 学习路线计划书

## —— AI 应用开发 → LLM / Agent → 机器学习 / 深度学习 → AI Engineering

> **用途：**
> 本文是个人 AI 学习的长期路线、任务清单和教学交接文档。
>
> 如果切换到新的 AI 对话，应优先阅读本文，以快速理解：
>
> * AI 学习目标
> * 当前学习阶段
> * 已完成与未完成的知识点
> * 后续学习顺序
> * 每个阶段的实践任务
> * 学习阶段切换标准
> * 教学方式
>
> **核心原则：不是追求快速看完，而是真正理解、能够自己操作和使用。**

---

# 一、最终目标

不是以成为纯 AI 算法研究员为第一目标。

长期目标：

```text
AI 应用开发
    ↓
LLM / RAG / Tool Calling / Agent
    ↓
机器学习
    ↓
深度学习 / PyTorch
    ↓
Transformer / LLM 深入理解
    ↓
LLM Engineering
    ↓
AI Engineering
    ↓
Production AI
```

最终希望具备：

* [x] 理解 AI / LLM 基本原理
* [ ] 能够使用 LLM
* [ ] 能够调用 LLM API
* [ ] 能够使用 Python 开发 AI 程序
* [ ] 能够开发 Structured Output 应用
* [ ] 理解 Embedding
* [ ] 能够独立构建基础 RAG
* [ ] 理解 Tool Calling
* [ ] 能够独立构建基础 Agent
* [ ] 理解机器学习基本原理
* [ ] 能够使用 Scikit-learn
* [ ] 理解神经网络
* [ ] 能够使用 PyTorch
* [ ] 深入理解 Transformer
* [ ] 深入理解 LLM
* [ ] 理解 LLM Engineering
* [ ] 能够构建工程化 AI 应用
* [ ] 能够部署和维护 Production AI

最终能力结构：

> **懂原理 + 能开发 + 能使用模型 + 能构建 AI 系统**

---

# 二、总体路线

```text
阶段 0
AI 基础认知
    ↓
阶段 1
Python + LLM API
    ↓
阶段 2
Structured Output + AI 应用基础
    ↓
阶段 3
Embedding
    ↓
阶段 4
RAG
    ↓
阶段 5
Tool Calling
    ↓
阶段 6
Agent
    ↓
阶段 7
机器学习
    ↓
阶段 8
数学重新激活
    ↓
阶段 9
深度学习 + PyTorch
    ↓
阶段 10
Transformer / LLM 深入
    ↓
阶段 11
LLM Engineering
    ↓
阶段 12
AI Engineering / Production AI
```

---

# 三、重要学习原则：Transformer 学习两遍

Transformer 不采用“一次学完”的方式。

## 第一遍：当前阶段建立基础认知

目标：

> 知道 LLM 大概是怎么工作的，避免以后只会调用 API。

学习：

* [x] Token
* [x] Token ID
* [x] Embedding
* [x] Attention
* [x] Q / K / V
* [x] Transformer
* [x] FFN
* [x] Residual Connection
* [x] LayerNorm
* [x] Next Token Prediction

这一遍：

* [x] 理解各组件是什么
* [x] 理解各组件之间的关系
* [x] 能画出基本流程
* [x] 能用自己的话解释
* [x] 能完成简单计算
* [x] 不要求深入复杂数学推导

---

## 第二遍：后期深入 Transformer / LLM

完成：

```text
机器学习
 ↓
深度学习
 ↓
PyTorch
```

之后重新深入：

* [x] Self-Attention
* [ ] Multi-Head Attention
* [ ] Positional Encoding
* [ ] RoPE
* [ ] Encoder
* [ ] Decoder
* [ ] Mask
* [ ] Transformer Block
* [ ] Pre-training
* [ ] Fine-tuning
* [ ] Instruction Tuning
* [ ] RLHF
* [ ] Alignment
* [ ] LoRA
* [ ] PEFT
* [ ] Quantization
* [ ] Inference
* [ ] KV Cache

这一遍进入数学和实现层面：

* [ ] 理解 Attention 矩阵计算
* [ ] 理解张量维度
* [ ] 理解 Forward
* [ ] 理解 Loss
* [ ] 理解 Backpropagation
* [ ] 理解 Transformer 的训练过程
* [ ] 能使用 PyTorch 实现简化版组件

---

# 四、阶段 0：AI 基础认知

## 阶段目标

从：

> “会使用 AI”

升级到：

> **“理解 LLM 到底是什么，以及一次模型调用背后大概发生了什么。”**

---

## 1. LLM

* [x] 理解 LLM 是什么
* [x] 理解 Large Language Model 的含义
* [x] 理解模型与数据库的区别
* [x] 理解模型参数是什么
* [x] 理解模型知识如何通过参数表达
* [x] 理解训练与推理的区别
* [x] 理解 Inference 是什么

---

## 2. Token

* [x] 理解 Token 是什么
* [x] 理解 Token 与字符的区别
* [x] 理解 Token 与单词的区别
* [x] 理解 Tokenizer
* [x] 理解 Vocabulary
* [x] 理解 Token ID

核心认知：

> Token 是模型处理文本时使用的基本单位，不一定等于一个汉字或一个完整单词。

---

## 3. Token ID

* [x] 理解 Token ID 是什么
* [x] 理解为什么需要 Token ID
* [x] 理解 Token 与 Token ID 的关系
* [x] 理解 Token ID 与 Embedding 的关系
* [x] 理解 Token ID 数字大小没有语义距离

核心认知：

> **Token ID 主要用于确定 Token 的身份，本身不是语义表示。**

---

## 4. Embedding

* [x] 理解 Embedding 是什么
* [x] 理解 Token 如何得到 Embedding
* [x] 理解 Embedding 是向量
* [x] 理解向量为什么可以表示信息
* [x] 理解 Embedding 与 Token ID 的区别
* [x] 理解向量之间可以计算相似度
* [ ] 理解 Embedding 与语义关系
* [ ] 理解 Embedding 的单个维度通常不是简单的人类可读属性

核心流程：

```text
Token
 ↓
Token ID
 ↓
Embedding
 ↓
Vector
```

---

## 5. Attention

* [x] 理解为什么需要 Attention
* [x] 理解 Context
* [x] 理解 Token 与 Token 的上下文关系
* [x] 理解 Self-Attention
* [x] 理解 Attention 根据上下文动态计算关系

核心认知：

> **Embedding 提供基本表示，Attention 根据上下文动态计算 Token 之间的关系。**

---

## 6. Q / K / V

* [x] 理解 Q（Query）
* [x] 理解 K（Key）
* [x] 理解 V（Value）
* [x] 记住 Q：我想找什么？
* [x] 记住 K：你有什么可以匹配？
* [x] 记住 V：你真正提供什么信息？

---

## 7. Attention 基本计算

* [x] 理解 Q 与 K 的匹配
* [x] 理解 Dot Product
* [x] 理解匹配分数
* [x] 理解 Softmax
* [x] 理解 Attention Weight
* [x] 理解 Weight × V
* [x] 理解加权求和
* [x] 能手算简单 Attention

核心流程：

```text
Q
 ↓
与 K 比较
 ↓
匹配分数
 ↓
Softmax
 ↓
Attention Weight
 ↓
Weight × V
 ↓
求和
 ↓
新的上下文表示
```

核心认知：

> **Q 和 K 决定“关注谁、关注多少”；V 决定“拿什么信息”。**

---

## 8. Transformer

* [x] 理解 Transformer 是什么
* [x] 理解 Transformer ≠ Attention
* [x] 理解 Transformer 是一种神经网络架构
* [x] 理解 Attention 是 Transformer 的核心组件之一
* [x] 理解 Transformer Layer
* [x] 理解多个 Transformer Layer 可以堆叠

---

## 9. FFN

* [x] 理解 FFN 是什么
* [x] 理解 FFN 的基本作用
* [x] 区分 Attention 与 FFN
* [x] 理解 Attention 主要负责上下文信息交互
* [x] 理解 FFN 对信息进一步加工和变换

核心记忆：

> **Attention：拿信息。**
> **FFN：加工信息。**

---

## 10. Residual Connection

* [x] 理解 Residual Connection
* [x] 理解原始输入 X
* [x] 理解加工结果 F(X)
* [x] 理解 `X + F(X)`
* [x] 能进行简单残差计算
* [x] 理解残差连接可以保留原始信息

核心公式：

```text
Output = X + F(X)
```

---

## 11. LayerNorm

* [x] 理解 Layer Normalization 是什么
* [x] 理解为什么需要归一化
* [x] 理解 LayerNorm 对表示进行规范化
* [x] 理解它与网络训练稳定性的关系
* [x] 第一遍暂不要求深入公式

---

## 12. Next Token Prediction

* [x] 理解 Next Token Prediction
* [x] 理解模型不是一次性生成完整答案
* [x] 理解模型会根据已有上下文预测下一个 Token
* [x] 理解输出的是下一个 Token 的概率分布
* [x] 理解选择 Token 后继续预测
* [x] 理解自回归生成

核心流程：

```text
已有 Token
 ↓
Transformer
 ↓
预测下一个 Token 的概率
 ↓
选择 Token
 ↓
继续预测
 ↓
直到生成结束
```

---

## 阶段 0 实践任务

* [x] 能用自己的话解释 LLM
* [x] 能解释 Token / Token ID / Embedding 的区别
* [x] 能解释 Embedding 与 Attention 的区别
* [x] 能解释 Q / K / V
* [x] 能手算简单 Attention
* [x] 能解释 Transformer 与 Attention 的关系
* [x] 能解释 FFN
* [x] 能解释 Residual Connection
* [x] 能解释 LayerNorm 的基本作用
* [x] 能完整描述一次简单的 Next Token Prediction 流程

### 阶段完成标准

达到：

> **不用看笔记，能够用自己的话把 LLM 从文本输入讲到 Next Token 输出。**

---

# 五、阶段 1：Python + LLM API

## 阶段目标

把：

```text
DeepSeek API
    ↓
hello
```

升级为：

> **能够独立使用 Python 调用 LLM API，并完成基础 AI 程序。**

---

# 1. HTTP / API 基础

* [x] API 基础
* [x] HTTP 基础
* [x] Request / Response
* [x] URL
* [x] Endpoint
* [x] HTTP Method
* [x] GET / POST
* [x] Header
* [x] Body
* [x] Status Code
* [x] JSON
* [x] HTTPX
* [x] HTTPX 发送 GET / POST

---

# 2. Python 调用 LLM API

* [x] 使用 HTTPX 发送请求
* [x] 设置 Request Header
* [x] 构造 Request Body
* [x] 配置 `model`
* [x] 配置 `messages`
* [x] 发送 API 请求
* [x] 接收 Response
* [ ] 解析 JSON
* [x] 从嵌套 JSON 提取模型输出
* [x] 封装成 Python 函数
* [x] 完成第一次独立 API 调用

---

# 3. API Key 与安全

* [ ] 理解 API Key
* [ ] 理解认证 / 授权基本概念
* [ ] 环境变量
* [ ] Python 读取环境变量
* [ ] 不把 Key 写入代码
* [ ] `.gitignore`
* [ ] 避免 Key 提交 Git
* [ ] 基础 Secret 安全意识

---

# 4. LLM API 参数

* [x] `model`
* [x] `messages`
* [x] `system`
* [x] `user`
* [x] `assistant`
* [x] `temperature`
* [x] 输出 Token 限制
* [ ] 理解常用参数对输出的影响

---

# 5. 多轮对话

* [x] 理解 `messages`
* [x] 理解 `system / user / assistant`
* [x] 理解对话历史
* [x] 理解 Context
* [x] 理解 Context Window
* [x] 保存对话历史
* [x] 将历史消息发送给模型
* [x] 实现多轮聊天
* [ ] 处理过长的历史消息

核心流程：

```text
用户输入
 ↓
加入 messages
 ↓
发送给模型
 ↓
获得回答
 ↓
加入 assistant 消息
 ↓
继续下一轮
```

---

# 6. Streaming

* [ ] 理解 Streaming
* [ ] 普通响应 vs 流式响应
* [ ] 理解逐步显示的原理
* [ ] Chunk / Delta / Event
* [ ] Python 处理流式响应
* [ ] 实现 CLI 流式输出

---

# 7. 错误处理

* [ ] HTTP 错误
* [ ] API 错误
* [ ] 网络异常
* [ ] Timeout
* [ ] 429 限流
* [ ] 基础重试
* [ ] 给用户友好的错误提示

---

# 8. AI 程序基础工程化

* [x] API 调用函数封装
* [ ] 配置与代码分离
* [ ] 基础日志
* [ ] 基础异常处理
* [ ] 简单项目结构
* [ ] Git 基础安全

---

# 9. 阶段实践项目

### 基础练习

* [x] `hello`
* [x] Python 简单问答程序
* [x] JSON API 调用练习
* [x] API 调用函数

### 综合练习

* [x] CLI AI Chat
* [x] 多轮聊天
* [ ] Streaming
* [ ] 错误处理
* [ ] 基础日志

### 最终项目

> **Python CLI AI Chat**

要求：

```text
Python
 ↓
API Key
 ↓
LLM API
 ↓
JSON
 ↓
模型回答
 ↓
多轮 Context
 ↓
Streaming
 ↓
错误处理
```

---

# 10. 阶段完成标准

能够独立：

* [x] 创建 Python AI 项目
* [x] 配置 API Key
* [x] 使用 HTTPX / SDK 调用 LLM API
* [x] 理解 Request / Response
* [x] 构造 JSON 请求
* [x] 解析 JSON Response
* [x] 提取模型输出
* [ ] 理解并使用常见 LLM 参数
* [ ] 实现多轮对话
* [ ] 实现 Streaming
* [ ] 处理基本 API 错误
* [ ] 完成一个可运行的 CLI AI Chat

**完成后进入：**

> **阶段 2：Structured Output + AI 应用基础**

---

# 六、阶段 2：Structured Output + AI 应用基础

## 阶段目标

从：

> LLM 返回自然语言

升级到：

> **LLM 按照程序要求返回结构化数据。**

---

## 1. JSON

* [ ] JSON Object
* [ ] JSON Array
* [ ] String
* [ ] Number
* [ ] Boolean
* [ ] Null
* [ ] JSON 嵌套结构
* [ ] Python JSON 解析

---

## 2. Structured Output

* [ ] 理解 Structured Output
* [ ] Schema
* [ ] Field
* [ ] Type
* [ ] Required Field
* [ ] Enum
* [ ] 嵌套结构
* [ ] 模型输出结构化数据
* [ ] Python 读取结构化结果
* [ ] 处理结构化输出错误

---

## 3. Prompt Engineering

* [ ] Role
* [ ] Context
* [ ] Task
* [ ] Constraints
* [ ] Examples
* [ ] Output Format
* [ ] Few-shot
* [ ] Prompt 调试
* [ ] Prompt 版本管理的基本思想

---

## 实践

* [ ] 学习笔记整理器
* [ ] 文本分类器
* [ ] 信息提取器
* [ ] 结构化学习计划分析器

阶段完成标准：

* [ ] 能让模型按照指定 Schema 返回数据
* [ ] 能让 Python 程序读取结果
* [ ] 能处理基本格式错误
* [ ] 能写出相对稳定的 Prompt

---

# 七、阶段 3：Embedding

## 阶段目标

理解：

> **为什么文本可以转换成向量，并利用向量之间的关系进行检索。**

---

## 学习

* [ ] Embedding Model
* [ ] Text Embedding
* [ ] Sentence Embedding
* [ ] Document Embedding
* [ ] Vector
* [ ] Vector Space
* [ ] Similarity
* [ ] Cosine Similarity
* [ ] Dot Product
* [ ] Vector Search

---

## 重点

* [ ] 理解为什么 Token ID 不能直接表示语义
* [ ] 理解为什么 Embedding 可以用于语义比较
* [ ] 理解向量相似度
* [ ] 理解 Cosine Similarity
* [ ] 能计算简单向量相似度

---

## 实践

```text
文本 A
文本 B
文本 C
 ↓
Embedding
 ↓
计算相似度
 ↓
排序
```

* [ ] 调用 Embedding API
* [ ] 保存 Embedding
* [ ] 计算向量相似度
* [ ] 根据相似度排序
* [ ] 实现简单文本搜索

阶段完成标准：

> **能够解释“文本 → Embedding → 向量 → 相似度 → 检索”的完整过程，并能自己写出简单实现。**

---

# 八、阶段 4：RAG

## 阶段目标

理解：

> **LLM + 外部知识检索。**

---

## 1. RAG 基础

* [ ] 理解为什么需要 RAG
* [ ] 理解 RAG 基本流程
* [ ] 理解 Retrieval
* [ ] 理解 Context
* [ ] 理解 Generation

核心：

```text
文档
 ↓
切分
 ↓
Embedding
 ↓
Vector Database
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Answer
```

---

## 2. 文档处理

* [ ] TXT
* [ ] Markdown
* [ ] PDF
* [ ] 文本清洗
* [ ] 文档加载

---

## 3. Chunk

* [ ] 理解 Chunk
* [ ] 为什么需要 Chunk
* [ ] Chunk Size
* [ ] Chunk Overlap
* [ ] Chunk 太大有什么问题
* [ ] Chunk 太小有什么问题
* [ ] 基础 Chunking 策略

---

## 4. Vector Database

* [ ] 理解 Vector Database
* [ ] 向量存储
* [ ] 向量检索
* [ ] Metadata
* [ ] Metadata Filtering
* [ ] 基础 Vector DB 操作

---

## 5. Retrieval

* [ ] Similarity Search
* [ ] Top-K
* [ ] Retrieval Pipeline
* [ ] Retrieval Quality
* [ ] 相关内容筛选

---

## 6. Context

* [ ] 检索结果如何进入 Prompt
* [ ] Context 构造
* [ ] Context 长度
* [ ] Context 噪声
* [ ] Context Relevance

---

## RAG 实践项目

# 个人知识库 AI

数据可以使用：

* [ ] MySQL 笔记
* [ ] Java 笔记
* [ ] MyBatis 笔记
* [ ] Linux 笔记
* [ ] AI 笔记

完整实现：

```text
个人学习笔记
 ↓
Document Loader
 ↓
Chunk
 ↓
Embedding
 ↓
Vector Database
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
回答问题
```

---

## RAG 第二阶段

* [ ] Hybrid Search
* [ ] Reranking
* [ ] Query Rewrite
* [ ] Multi-query
* [ ] Context Compression
* [ ] Metadata Filtering
* [ ] RAG Evaluation
* [ ] Retrieval Evaluation

阶段完成标准：

* [ ] 能自己构建基础 RAG
* [ ] 能解释每一步为什么存在
* [ ] 能定位 Retrieval 不准确的问题
* [ ] 能修改 Chunk / Top-K / Retrieval 策略
* [ ] 能完成个人知识库 AI

---

# 九、阶段 5：Tool Calling

## 阶段目标

从：

> AI 只能回答问题

升级到：

> **AI 可以请求程序执行操作。**

---

## 学习

* [ ] Tool 是什么
* [ ] Function Calling
* [ ] Tool Schema
* [ ] Tool Parameters
* [ ] Tool Result
* [ ] Tool Selection
* [ ] Tool Execution
* [ ] Tool Error Handling
* [ ] 参数校验
* [ ] 工具权限的基本概念

---

## 核心流程

```text
用户
 ↓
LLM
 ↓
判断是否需要工具
 ↓
Tool Call
 ↓
程序执行
 ↓
Tool Result
 ↓
LLM
 ↓
最终回答
```

---

## 实践工具

* [ ] Calculator
* [ ] 日期 / 时间工具
* [ ] 天气 API
* [ ] 搜索 API
* [ ] 自己编写的 Python 函数
* [ ] 自己的后端 API

---

## 与后端结合

* [ ] LLM 调用 Spring Boot API
* [ ] Spring Boot 调用 MySQL
* [ ] 返回结构化结果
* [ ] LLM 根据结果生成最终回答

核心：

```text
LLM
 ↓
Tool Calling
 ↓
Spring Boot
 ↓
MySQL
 ↓
Tool Result
 ↓
LLM
```

阶段完成标准：

> **能够让 LLM 根据任务自主决定是否调用工具，并正确处理工具结果。**

---

# 十、阶段 6：Agent

## 阶段目标

理解：

> **Agent = 围绕目标进行多步决策、工具使用和执行循环。**

---

## 1. Workflow

* [ ] 理解 Workflow
* [ ] 理解固定流程
* [ ] 理解 Workflow 与 Agent 的区别

---

## 2. Agent

* [ ] Agent 基本概念
* [ ] Goal
* [ ] Observation
* [ ] Reasoning
* [ ] Action
* [ ] Tool Use
* [ ] Agent Loop

核心：

```text
Goal
 ↓
Observe
 ↓
Reason
 ↓
Choose Tool
 ↓
Execute
 ↓
Observe Result
 ↓
Continue
 ↓
Finish
```

---

## 3. Planning

* [ ] 理解任务拆分
* [ ] 理解多步任务
* [ ] 基础 Planning
* [ ] 任务依赖

---

## 4. Memory

* [ ] 短期记忆
* [ ] 长期记忆
* [ ] Context Memory
* [ ] External Memory
* [ ] Memory 的基本实现方式

---

## 5. ReAct

* [ ] 理解 ReAct
* [ ] Reason
* [ ] Act
* [ ] Observe
* [ ] 理解 Reasoning 与 Tool Use 的循环

---

## 6. Reflection

* [ ] 理解 Reflection
* [ ] 执行后检查
* [ ] 错误发现
* [ ] 结果修正

---

## 7. Multi-Agent

* [ ] 理解 Multi-Agent
* [ ] Agent 分工
* [ ] Agent 协作
* [ ] Agent 通信
* [ ] Multi-Agent 的适用场景

---

## 实践

第一阶段：

* [ ] 不使用大型 Agent Framework
* [ ] 手写简化 Agent Loop
* [ ] 让 LLM 调用多个工具
* [ ] 让 Agent 根据结果继续执行

第二阶段：

* [ ] 接触主流 Agent Framework
* [ ] LangChain 基本概念
* [ ] LangGraph 基本概念
* [ ] 理解 Framework 如何实现 Agent

原则：

> **先理解 Agent 本质，再学习框架。**

阶段完成标准：

* [ ] 能解释 Agent 与普通 Chatbot 的区别
* [ ] 能解释 Agent 与 Workflow 的区别
* [ ] 能手写简化 Agent Loop
* [ ] 能实现多工具调用
* [ ] 能处理工具执行失败
* [ ] 能理解基本 Memory / Planning / Reflection

---

# 十一、阶段 7：机器学习

## 时间定位

计划在大三开始进入重点学习。

---

## 1. 机器学习基本思想

* [ ] 理解机器学习解决什么问题
* [ ] Data
* [ ] Feature
* [ ] Label
* [ ] Model
* [ ] Training
* [ ] Prediction
* [ ] Evaluation
* [ ] Generalization

核心：

```text
Data
 ↓
Features
 ↓
Model
 ↓
Training
 ↓
Prediction
 ↓
Evaluation
```

---

## 2. 数据工具

* [ ] NumPy
* [ ] Pandas
* [ ] Matplotlib
* [ ] 数据读取
* [ ] 数据清洗
* [ ] 数据分析
* [ ] 数据可视化

---

## 3. 数据集

* [ ] Training Set
* [ ] Validation Set
* [ ] Test Set
* [ ] 数据划分
* [ ] Data Leakage 基本概念

---

## 4. 特征工程

* [ ] Feature
* [ ] Feature Engineering
* [ ] 数值特征
* [ ] 类别特征
* [ ] 特征缩放
* [ ] 特征选择

---

## 5. 回归

* [ ] Linear Regression
* [ ] Prediction
* [ ] Loss
* [ ] 基础优化思想

---

## 6. 分类

* [ ] Logistic Regression
* [ ] Classification
* [ ] Probability
* [ ] Decision Boundary

---

## 7. 决策树与集成学习

* [ ] Decision Tree
* [ ] Random Forest
* [ ] Ensemble Learning
* [ ] Gradient Boosting 基本思想

---

## 8. 聚类

* [ ] K-Means
* [ ] Unsupervised Learning
* [ ] Cluster

---

## 9. 模型评价

* [ ] Accuracy
* [ ] Precision
* [ ] Recall
* [ ] F1
* [ ] Confusion Matrix
* [ ] Regression Metrics

---

## 10. 泛化

* [ ] Overfitting
* [ ] Underfitting
* [ ] Generalization
* [ ] Regularization
* [ ] Cross Validation

---

## 11. Scikit-learn

* [ ] 数据预处理
* [ ] Model API
* [ ] Training
* [ ] Prediction
* [ ] Evaluation
* [ ] Pipeline

---

## 实践

* [ ] 回归项目
* [ ] 分类项目
* [ ] 聚类项目
* [ ] 综合机器学习项目

每个项目都要求能够解释：

* [ ] 数据从哪里来
* [ ] 数据如何处理
* [ ] Feature 是什么
* [ ] Label 是什么
* [ ] 为什么选择该模型
* [ ] 如何训练
* [ ] 如何评价
* [ ] 是否存在过拟合
* [ ] 如何改进

---

# 十二、阶段 8：数学重新激活

原则：

> **不提前完整重学三门数学，而是在机器学习、深度学习和 Transformer 学到哪里时补哪里。**

---

## 1. 高等数学

* [ ] 导数
* [ ] 偏导数
* [ ] 梯度
* [ ] 链式法则
* [ ] 极值
* [ ] 积分
* [ ] 多变量函数

主要服务：

```text
Loss
 ↓
Gradient
 ↓
Optimization
 ↓
Backpropagation
```

---

## 2. 线性代数

* [ ] 向量
* [ ] 矩阵
* [ ] 矩阵乘法
* [ ] 点积
* [ ] 向量空间
* [ ] 特征值
* [ ] 特征向量
* [ ] 张量基本概念

主要服务：

```text
Embedding
Attention
Neural Network
Transformer
```

---

## 3. 概率统计

* [ ] 随机变量
* [ ] 概率分布
* [ ] 条件概率
* [ ] 贝叶斯
* [ ] 期望
* [ ] 方差
* [ ] 最大似然
* [ ] 统计估计

主要服务：

```text
Machine Learning
Model Evaluation
LLM
```

---

# 十三、阶段 9：深度学习 + PyTorch

## 阶段目标

真正理解：

> **神经网络如何通过数据、Loss、反向传播和优化器不断更新参数。**

---

## 1. 神经网络

* [ ] Neuron
* [ ] Layer
* [ ] Weight
* [ ] Bias
* [ ] Activation Function
* [ ] Forward
* [ ] Loss

---

## 2. 训练

* [ ] Backward
* [ ] Gradient
* [ ] Gradient Descent
* [ ] Learning Rate
* [ ] Batch
* [ ] Epoch
* [ ] Optimizer
* [ ] SGD
* [ ] Adam

---

## 3. 泛化

* [ ] Overfitting
* [ ] Underfitting
* [ ] Regularization
* [ ] Dropout
* [ ] Early Stopping

---

## 4. PyTorch

* [ ] Tensor
* [ ] Tensor Shape
* [ ] Dataset
* [ ] DataLoader
* [ ] Module
* [ ] Loss Function
* [ ] Optimizer
* [ ] Training Loop
* [ ] GPU
* [ ] CUDA 基本概念

---

## 5. 自己实现训练流程

```text
数据
 ↓
Model
 ↓
Forward
 ↓
Loss
 ↓
Backward
 ↓
Optimizer
 ↓
更新参数
 ↓
重复
```

* [ ] 自己写简单训练循环
* [ ] 自己观察 Loss
* [ ] 理解参数更新
* [ ] 理解训练集与验证集变化

---

## 6. 神经网络发展路线

* [ ] 基础神经网络
* [ ] CNN
* [ ] RNN
* [ ] Attention
* [ ] Transformer

---

# 十四、阶段 10：Transformer / LLM 深入

这是第二遍真正深入 Transformer。

---

## 1. Self-Attention

* [ ] Self-Attention
* [ ] Q
* [ ] K
* [ ] V
* [ ] QKᵀ
* [ ] Scaling
* [ ] Softmax
* [ ] Attention Weight
* [ ] Weighted Sum
* [ ] Attention Output
* [ ] 理解矩阵维度
* [ ] 手算简单 Attention
* [ ] 使用 PyTorch 实现简化 Attention

---

## 2. Multi-Head Attention

* [ ] 为什么需要多个 Head
* [ ] Head 的作用
* [ ] 多组 Q/K/V
* [ ] 多组 Attention
* [ ] Concatenation
* [ ] Linear Projection
* [ ] Multi-Head Attention 的完整计算流程
* [ ] 使用 PyTorch 实现简化版本

---

## 3. Position

* [ ] 理解 Transformer 为什么需要位置信息
* [ ] Positional Encoding
* [ ] Position Embedding
* [ ] Sinusoidal Position Encoding
* [ ] RoPE
* [ ] 理解现代 LLM 中的位置编码思想

---

## 4. Transformer Block

* [ ] Attention
* [ ] Residual Connection
* [ ] LayerNorm
* [ ] FFN
* [ ] 完整 Transformer Block
* [ ] Pre-Norm
* [ ] Post-Norm
* [ ] 理解不同实现的结构差异

---

## 5. Encoder / Decoder

* [ ] Encoder
* [ ] Decoder
* [ ] Encoder Self-Attention
* [ ] Decoder Self-Attention
* [ ] Cross-Attention
* [ ] Causal Mask
* [ ] Encoder-only
* [ ] Decoder-only
* [ ] Encoder-Decoder
* [ ] 理解现代 LLM 为什么大量采用 Decoder-only 架构

---

## 6. LLM Training

* [ ] Dataset
* [ ] Tokenization
* [ ] Pre-training
* [ ] Next Token Prediction
* [ ] Loss
* [ ] Backpropagation
* [ ] Optimization
* [ ] Batch
* [ ] Epoch
* [ ] Scaling
* [ ] Context Length

---

## 7. Post-training

* [ ] Fine-tuning
* [ ] Instruction Tuning
* [ ] Alignment
* [ ] RLHF 基本概念
* [ ] DPO 基本概念

---

## 8. 参数高效微调

* [ ] LoRA
* [ ] PEFT
* [ ] Adapter 基本思想
* [ ] 理解为什么不一定需要更新整个模型

---

## 9. Inference

* [ ] Inference
* [ ] Generation
* [ ] Sampling
* [ ] Temperature
* [ ] Top-K
* [ ] Top-P
* [ ] KV Cache
* [ ] Batch
* [ ] Throughput
* [ ] Latency

---

## 10. Quantization

* [ ] FP32
* [ ] FP16
* [ ] BF16
* [ ] INT8
* [ ] INT4
* [ ] Quantization
* [ ] 显存占用
* [ ] 推理性能
* [ ] 精度影响

---

# 十五、阶段 11：LLM Engineering

## 阶段目标

从：

> “会使用模型”

进入：

> **“能够围绕 LLM 构建可靠 AI 应用。”**

---

## 1. Prompt Engineering

* [ ] Prompt Template
* [ ] Few-shot
* [ ] Structured Prompt
* [ ] Prompt Versioning
* [ ] Prompt Evaluation
* [ ] Prompt Regression Testing

---

## 2. RAG Engineering

* [ ] Retrieval
* [ ] Hybrid Search
* [ ] Reranking
* [ ] Query Rewrite
* [ ] Multi-query
* [ ] Metadata Filtering
* [ ] Context Management
* [ ] Context Compression
* [ ] RAG Evaluation

---

## 3. Tool / Agent Engineering

* [ ] Tool Schema
* [ ] Tool Reliability
* [ ] Tool Validation
* [ ] Agent Loop
* [ ] Error Recovery
* [ ] State
* [ ] Memory
* [ ] Workflow
* [ ] Agent Evaluation

---

## 4. Evaluation

* [ ] LLM Evaluation
* [ ] Prompt Evaluation
* [ ] RAG Evaluation
* [ ] Agent Evaluation
* [ ] Evaluation Dataset
* [ ] Benchmark
* [ ] Human Evaluation
* [ ] 自动评价的局限性
* [ ] 建立基础 Evaluation Pipeline

---

## 5. Cost / Performance

* [ ] Token Cost
* [ ] Latency
* [ ] Throughput
* [ ] Caching
* [ ] Context Optimization
* [ ] Model Selection
* [ ] Model Routing
* [ ] Batch Processing

---

# 十六、阶段 12：AI Engineering / Production AI

## 阶段目标

从：

> Demo

升级到：

> **能够构建真正可以运行、部署、监控和维护的 AI 系统。**

---

## 1. AI 系统架构

* [ ] AI Application
* [ ] LLM
* [ ] RAG
* [ ] Tool Calling
* [ ] Agent
* [ ] Memory
* [ ] Evaluation
* [ ] Monitoring
* [ ] Deployment

核心：

```text
User
 ↓
Frontend / API
 ↓
AI Application
 ↓
LLM
 ├── RAG
 ├── Tools
 ├── Agent
 └── Memory
 ↓
Evaluation
 ↓
Monitoring
 ↓
Deployment
 ↓
Production
```

---

## 2. LLM Serving

* [ ] Model Serving
* [ ] Inference Server
* [ ] API Server
* [ ] Batch Inference
* [ ] Online Inference
* [ ] 模型服务基本架构

---

## 3. 推理优化

* [ ] KV Cache
* [ ] Batching
* [ ] Quantization
* [ ] GPU Memory
* [ ] Latency
* [ ] Throughput
* [ ] 推理成本

---

## 4. GPU 基础

* [ ] CPU 与 GPU 区别
* [ ] GPU 并行计算基本思想
* [ ] VRAM
* [ ] CUDA 基础概念
* [ ] Tensor 运算
* [ ] GPU 推理

不以 GPU 底层研究为目标。

---

## 5. AI Observability

* [ ] Logs
* [ ] Metrics
* [ ] Traces
* [ ] Token Usage
* [ ] Latency
* [ ] Error Rate
* [ ] Tool Calls
* [ ] Retrieval Quality
* [ ] Model Quality Monitoring

---

## 6. AI 系统可靠性

* [ ] Timeout
* [ ] Retry
* [ ] Fallback
* [ ] Rate Limit
* [ ] Error Handling
* [ ] Tool Failure
* [ ] Model Failure
* [ ] Retrieval Failure
* [ ] Service Degradation
* [ ] 基础容灾思想

---

## 7. AI 应用安全

* [ ] Prompt Injection
* [ ] Data Leakage
* [ ] Tool Abuse
* [ ] Permission
* [ ] Input Validation
* [ ] Output Validation
* [ ] Sensitive Data Protection
* [ ] Tool 权限控制

---

## 8. 成本控制

* [ ] Token Cost
* [ ] Model Selection
* [ ] Model Routing
* [ ] Caching
* [ ] Context Optimization
* [ ] Batch
* [ ] Smaller Model
* [ ] 成本监控

---

## 9. Deployment

结合已有：

```text
Linux
Docker
Nginx
Spring Boot
Cloud Native
```

学习：

* [ ] AI Application Docker 化
* [ ] Python AI 服务部署
* [ ] Spring Boot AI API
* [ ] LLM API 服务
* [ ] RAG 服务部署
* [ ] Vector Database 部署
* [ ] Nginx
* [ ] Linux
* [ ] 基础服务监控

---

# 十七、最终综合项目

最终需要完成一个 **Production-oriented AI Application**。

---

## 核心功能

* [ ] LLM API
* [ ] Structured Output
* [ ] Embedding
* [ ] RAG
* [ ] Tool Calling
* [ ] Agent
* [ ] Memory
* [ ] Evaluation
* [ ] Logging
* [ ] Monitoring
* [ ] 基础安全
* [ ] Docker
* [ ] Deployment

---

## 推荐系统结构

```text
用户
 ↓
Web / API
 ↓
Spring Boot / Python
 ↓
LLM
 ├── RAG
 ├── Tool Calling
 ├── Agent
 └── Memory
 ↓
Evaluation
 ↓
Logging / Monitoring
 ↓
Docker
 ↓
Deployment
```

---

## 与已有后端能力结合

* [ ] Java / Spring Boot
* [ ] MySQL
* [ ] MyBatis
* [ ] Linux
* [ ] Docker
* [ ] Nginx
* [ ] Cloud Native

最终形成：

```text
Java / Backend
        +
Python / AI
        +
LLM
        +
RAG
        +
Agent
        +
Linux / Docker / Cloud Native
        ↓
AI Engineering
```

---

# 十八、学习时间安排

目前 AI 不额外增加一个巨大的每日学习负担。

采用：

* [ ] 每周约 2 次正式 AI 学习
* [ ] 尽量增加 1 次短复习
* [ ] 尽可能利用 Python 学习时间与 AI 学习结合
* [ ] AI 与后端主线并行，而不是挤压后端、数学等核心学习时间

---

# 十九、阶段切换标准

不是“看完知识点”就自动进入下一阶段。

必须逐渐满足：

## 理解

* [ ] 能用自己的话解释核心概念
* [ ] 不依赖死记硬背
* [ ] 能区分容易混淆的概念

## 操作

* [ ] 能独立完成简单代码
* [ ] 能修改已有代码
* [ ] 能观察程序运行结果

## 判断

* [ ] 遇到问题能够判断应该使用什么技术
* [ ] 理解为什么使用该技术
* [ ] 知道什么时候不应该使用该技术

## 调试

* [ ] 能阅读基本报错
* [ ] 能定位简单问题
* [ ] 能尝试修改并验证

## 实践

* [ ] 完成阶段项目
* [ ] 能解释项目的完整流程
* [ ] 能独立修改项目功能

---

# 二十、教学协议

以后 AI 教学必须优先遵循以下方式：

```text
讲解
 ↓
示例
 ↓
小任务
 ↓
用户回答 / 操作
 ↓
检查
 ↓
纠错
 ↓
下一步
```

---

## 原则 1：一次只学习一个主要概念

不要一次性塞入大量新知识。

例如：

```text
Attention
 ↓
确认理解
 ↓
Q/K/V
 ↓
确认理解
 ↓
Transformer
 ↓
确认理解
 ↓
FFN
 ↓
确认理解
 ↓
LayerNorm
```

---

## 原则 2：理解优先

目标：

> **真正理解 + 能够自己操作和使用**

而不是：

> 快速刷完知识点。

---

## 原则 3：错误立即纠正

如果用户出现概念混淆，应：

1. [ ] 明确指出错误
2. [ ] 给出正确概念
3. [ ] 解释为什么错
4. [ ] 给一个小题再次确认
5. [ ] 确认后再继续

---

## 原则 4：难度逐渐增加

推荐：

```text
概念理解
 ↓
概念判断
 ↓
简单示例
 ↓
手算
 ↓
代码实现
 ↓
综合应用
```

---

## 原则 5：不要为了显得深入而提前塞数学

第一次学习一个概念：

* [ ] 先理解直觉
* [ ] 再理解结构
* [ ] 再进行简单计算
* [ ] 后期再进入数学推导

例如第一次学习 Attention：

不需要立即学习：

* [ ] 复杂矩阵推导
* [ ] Scaling 的完整数学细节
* [ ] 梯度
* [ ] 反向传播

第二遍 Transformer 学习时再深入。

---

# 二十一、学习路线核心思想

这条路线不是：

> 看到什么热门就学什么。

也不是：

> Agent、机器学习、深度学习、具身智能全部一起学。

而是：

```text
先建立基础认知
        ↓
学会调用模型
        ↓
开发 AI 应用
        ↓
理解 Embedding / RAG
        ↓
理解 Tool Calling
        ↓
理解 Agent
        ↓
进入机器学习
        ↓
进入深度学习
        ↓
重新深入 Transformer / LLM
        ↓
进入 LLM Engineering
        ↓
进入 AI Engineering
```

核心原则：

> **先建立应用能力，再建立算法基础；先建立第一遍模型认知，再在机器学习和深度学习基础上进行第二遍深入。**

最终目标不是：

> “学过很多 AI 名词。”

而是逐渐做到：

> **能够解释、能够编程、能够构建、能够调试、能够部署，并最终能够参与优化真正的 AI 系统。**

---

# 二十二、新对话启动说明

如果未来切换到新的 AI 对话，可以直接把本计划书提供给 AI，并说明：

> **“这是我的 AI 学习计划书，请以此作为长期学习上下文。不要重新给我规划路线，先根据计划书中的复选框判断我当前阶段和进度，然后按照教学协议继续教学。”**

新的 AI 应：

1. [ ] 阅读整个计划书
2. [ ] 根据 `[x]` 与 `[ ]` 判断已完成和未完成内容
3. [ ] 确认当前所在阶段
4. [ ] 不重复已经掌握的基础内容
5. [ ] 从当前未完成的下一个知识点继续
6. [ ] 遵循“讲解 → 示例 → 小任务 → 用户回答 → 检查 → 纠错 → 下一步”
7. [ ] 每次只推进一个主要概念
8. [ ] 不擅自修改整体学习路线
9. [ ] 如果认为路线确实需要重大调整，应先与用户讨论，而不是直接改变
10. [ ] 每完成一个明确知识点，可以建议用户将对应的 `[ ]` 修改为 `[x]`

---

# 二十三、用户学习状态记录规则

本文件中的复选框用于长期记录学习进度。

```text
[ ] = 尚未完成
[x] = 已完成
```

需要注意：

> `[x]` 不代表“看过”，而应该代表**已经达到阶段要求的理解程度**。

如果只是听过但还不能独立解释：

```text
[ ]
```

如果已经能够：

* [ ] 自己解释
* [ ] 回答基础问题
* [ ] 完成简单练习

才逐渐认为该知识点完成：

```text
[x]
```

对于大型知识点，可以拆成多个子任务分别打勾，而不是一次全部标记完成。

---

# 二十四、最终能力目标

最终形成：

```text
                         AI Engineering
                              │
               ┌──────────────┴──────────────┐
               ↓                             ↓
          AI Application                AI Fundamentals
               │                             │
            LLM API                         ML
               │                             │
             RAG                            DL
               │                             │
        Tool Calling                      PyTorch
               │                             │
             Agent                       Transformer
               │                             │
               └──────────────┬──────────────┘
                              ↓
                             LLM
                              ↓
                      LLM Engineering
                              ↓
                       Production AI
```

结合已有技术：

```text
Java
Spring Boot
MySQL
MyBatis
Linux
Docker
Cloud Native
        +
Python
LLM
RAG
Agent
ML
DL
        ↓
AI × Backend × Cloud Native
        ↓
AI Engineering
```

最终目标：

> **不是只会调用 API，也不是只会数学公式，而是逐渐形成“懂原理 + 能开发 + 能使用模型 + 能构建 AI 系统”的完整能力结构。**
