# 个人 AI 学习路线计划书

## 一、最终目标

不是以“成为 AI 算法研究员”为目标，而是逐步形成：

> **AI 应用开发 → AI Engineering → LLM / Agent → 机器学习 / 深度学习 → AI 系统**

最终具备独立理解、开发和部署 AI 应用的能力。

---

# 二、总体路线

```text
AI 使用
  ↓
Python
  ↓
LLM 基础
  ↓
LLM API
  ↓
AI 应用开发
  ↓
Embedding / RAG
  ↓
Tool Calling
  ↓
Agent
  ↓
机器学习
  ↓
深度学习
  ↓
PyTorch
  ↓
Transformer / LLM
  ↓
LLM Engineering
  ↓
AI Engineering
```

不是所有内容同时学习，而是**逐层深入**。

---

# 三、阶段 0：AI 基础使用

### 当前阶段

你已经：

* 日常使用 AI
* 用 AI 辅助学习
* 调用过 DeepSeek API
* 完成过 `hello`

因此不需要重新学习“什么是 ChatGPT”这种内容。

重点是从：

```text
使用 AI
```

逐渐变成：

```text
理解 AI
```

学习：

* LLM 是什么
* Token
* Context Window
* Prompt
* System / User / Assistant
* Temperature
* Embedding
* 推理
* Hallucination
* Model / API 的基本关系

### 阶段目标

能够解释：

> **LLM 到底是什么，以及一次 API 调用背后发生了什么。**

---

# 四、阶段 1：Python + LLM API

### 现在最适合你的 AI 学习阶段

利用正在学习的 Python，逐渐把：

```text
DeepSeek API
 ↓
hello
```

升级成真正的程序。

学习：

* HTTP / API 基础
* Python 请求 API
* JSON
* API Key
* 参数
* 错误处理
* 多轮对话
* 流式输出
* Structured Output

### 实践顺序

```text
hello
 ↓
简单问答
 ↓
多轮聊天
 ↓
流式输出
 ↓
结构化 JSON
 ↓
文件分析
 ↓
自己的小工具
```

### 阶段目标

> **能够独立使用 Python 调用 LLM API，并完成一个小型 AI 程序。**

---

# 五、阶段 2：AI 应用开发

开始理解：

> **LLM 不只是聊天机器人。**

学习：

### Prompt Engineering

* Role
* Context
* Constraints
* Examples
* Output Format
* Few-shot
* Prompt 调试

### Embedding

理解：

```text
文本
 ↓
Embedding
 ↓
向量
 ↓
相似度
```

理解它为什么能够用于知识检索。

---

# 六、阶段 3：RAG

这是你 AI 应用开发的第一个重点。

学习：

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
相关内容
 ↓
LLM
 ↓
答案
```

重点理解：

* 为什么需要 RAG
* Chunk
* Embedding
* Vector Database
* Similarity Search
* Retrieval
* Context
* RAG 的基本评价方式

### 实践

做一个：

> **个人知识库 AI**

例如：

```text
自己的学习笔记
       ↓
      RAG
       ↓
      LLM
       ↓
“问我的 MySQL 笔记”
```

这会非常适合你的学习方式。

---

# 七、阶段 4：Tool Calling

RAG 之后进入 Tool Calling。

理解：

```text
用户
 ↓
LLM
 ↓
判断是否需要工具
 ↓
调用工具
 ↓
获得结果
 ↓
LLM
 ↓
最终回答
```

例如：

```text
用户：
帮我计算这个数据

LLM
 ↓
调用 Python Calculator
 ↓
得到结果
 ↓
LLM
 ↓
回答
```

进一步：

```text
LLM
 ↓
调用天气 API
 ↓
调用搜索 API
 ↓
调用自己的程序
```

### 阶段目标

> **让 AI 从“回答问题”变成“可以执行任务”。**

---

# 八、阶段 5：Agent

Tool Calling 理解之后再学习 Agent。

学习：

* Agent 是什么
* Workflow
* Planning
* Tool Use
* Memory
* Reflection
* ReAct
* Agent Loop
* Multi-Agent 基本概念

核心理解：

```text
观察
 ↓
思考
 ↓
选择工具
 ↓
执行
 ↓
获得结果
 ↓
继续判断
 ↓
完成任务
```

不要一开始就疯狂学习各种 Agent Framework。

先理解：

> **Agent 的本质是什么。**

然后再接触框架。

---

# 九、阶段 6：机器学习

### 时间：大三开始重点学习

此时再系统进入传统机器学习。

Python 基础已经有了，数学也有基础。

学习：

* NumPy
* Pandas
* Matplotlib
* Scikit-learn
* 数据预处理
* 特征工程
* 训练集 / 验证集 / 测试集
* 回归
* 分类
* 聚类
* 决策树
* 集成学习
* 模型评估
* 过拟合
* 正则化

### 重点

不要变成：

> “会调用 sklearn。”

而要理解：

> **机器学习到底是在解决什么问题。**

---

# 十、阶段 7：数学重新激活

进入机器学习之后，再系统复习数学。

### 高数

重点：

* 导数
* 偏导数
* 梯度
* 链式法则
* 极值
* 积分

### 线性代数

重点：

* 向量
* 矩阵
* 矩阵乘法
* 向量空间
* 特征值
* 特征向量

### 概率统计

重点：

* 随机变量
* 概率分布
* 条件概率
* 贝叶斯
* 期望
* 方差
* 最大似然
* 统计估计

你的策略不是：

> **现在把三门数学全部重新学一遍。**

而是：

> **机器学习学到哪里，就复习对应数学。**

这样效率最高。

---

# 十一、阶段 8：深度学习

进入：

```text
机器学习
 ↓
神经网络
 ↓
反向传播
 ↓
梯度下降
 ↓
PyTorch
```

学习：

* 神经网络
* 激活函数
* Loss
* Forward
* Backward
* Gradient Descent
* Optimizer
* Batch
* Epoch
* Overfitting
* Regularization

然后：

```text
CNN
 ↓
RNN
 ↓
Attention
 ↓
Transformer
```

---

# 十二、阶段 9：LLM 深入

这时候重新回到大语言模型。

学习：

### Transformer

* Self-Attention
* Multi-Head Attention
* Positional Encoding
* Encoder
* Decoder

### LLM

* Tokenization
* Pre-training
* Fine-tuning
* Instruction Tuning
* RLHF / Alignment 基本概念
* LoRA
* PEFT
* Quantization
* Inference

这时候你对 LLM 的理解会从：

> “我会调用 API。”

升级成：

> **“我知道模型大概是怎么工作的。”**

---

# 十三、阶段 10：AI Engineering

最终进入工程层。

```text
模型
 ↓
Inference
 ↓
API
 ↓
RAG
 ↓
Agent
 ↓
Evaluation
 ↓
Monitoring
 ↓
Deployment
 ↓
Production
```

学习：

* LLM Serving
* 推理优化
* 模型量化
* GPU 基础
* Prompt Evaluation
* RAG Evaluation
* Agent Evaluation
* AI Observability
* AI 系统可靠性
* AI 应用安全
* 成本与性能优化

最终目标：

> **不仅会做 Demo，还能构建真正可运行的 AI 系统。**

---

# 十四、你的时间安排

## 现在～大二

AI 只占整体学习的一部分。

但 AI 内部优先：

```text
Python
 ↓
LLM 基础
 ↓
API
 ↓
RAG
 ↓
Tool Calling
 ↓
Agent
```

暂时不重点学习：

```text
机器学习
深度学习
模型训练
具身智能
复杂数学推导
```

---

# 十五、大二暑假之后

开始提高 AI 比重。

```text
大二前期
AI 应用基础
      ↓
大二后期
RAG / Tool / Agent
      ↓
大二暑假
真实业务经验
      ↓
大三
机器学习 + 深度学习
      ↓
LLM 深入
      ↓
AI Engineering
```

---

# 十六、你目前最应该做的事情

不是：

> “我要不要开始学机器学习？”

而是：

### 第一件

继续 Python。

### 第二件

把 DeepSeek 的：

```text
hello
```

升级成一个真正的小程序。

### 第三件

依次学习：

```text
LLM 基础
 ↓
API
 ↓
Structured Output
 ↓
Embedding
 ↓
RAG
 ↓
Tool Calling
 ↓
Agent
```

### 第四件

等这些东西真正做过几个项目之后，再进入机器学习。

---

# 十七、最终路线

```text
                 AI
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
    AI 应用方向          AI 算法方向
        │                   │
      LLM API            机器学习
        │                   │
       RAG               深度学习
        │                   │
  Tool Calling          PyTorch
        │                   │
      Agent            Transformer
        │                   │
        └─────────┬─────────┘
                  ↓
                 LLM
                  ↓
           AI Engineering
                  ↓
          Production AI
```

你的路线不是“现在就冲最前沿”。

而是：

> **先把 AI 应用能力建立起来 → 再补机器学习和深度学习 → 再深入 LLM → 最后进入 AI Engineering。**

这样到大三的时候，你既不是只会调用 API 的“AI 使用者”，也不是只会数学公式却不会做应用的人，而是逐渐形成：

> **懂原理 + 能开发 + 能使用模型 + 能构建 AI 系统**

的能力结构。

**你现在的 `DeepSeek API → hello`，就把它当成这条路线的起点，而不是能力不足的证明。**

---
