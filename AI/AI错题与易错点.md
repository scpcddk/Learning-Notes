# AI错题与易错点

> 只记录容易混淆、曾经理解错误、以后需要重点避免的知识点。
> 不重复记录完整知识讲解。

---

## 1. LLM ≠ 数据库

❌ 错误理解：

> LLM 主要通过查询内部数据库来回答问题。

✅ 正确理解：

> LLM 通过训练调整大量模型参数，学习数据中的规律；推理时利用这些参数进行计算和生成。

**易错点：**

模型中的知识不是简单地以“一条条文本记录”的形式存储。

---

## 2. Token ≠ 字符 / 单词

❌ 错误理解：

> 一个 Token 就是一个汉字，或者一个完整单词。

✅ 正确理解：

> Token 是模型处理文本的基本单位，具体如何切分由 Tokenizer 决定。

**易错点：**

```text
一个汉字 ≠ 必然一个 Token
一个单词 ≠ 必然一个 Token
```

---

## 3. Token ID 没有语义

❌ 错误理解：

> Token ID 越接近，Token 的语义越接近。

✅ 正确理解：

> Token ID 只是 Vocabulary 中 Token 的编号，本身没有语义。

例如：

```text
苹果 → 100
香蕉 → 101
汽车 → 102
```

不能因为 ID 接近，就认为苹果和香蕉的语义比苹果和汽车更接近。

---

## 4. Token ID ≠ K

❌ 错误理解：

> Attention 中的 K 就是 Token 的编号。

✅ 正确理解：

* Token ID：Vocabulary 中 Token 的编号
* K：Attention 中用于与 Q 匹配的向量

两者完全不是同一个东西。

---

## 5. Embedding ≠ 上下文关系

❌ 错误理解：

> Embedding 可以直接判断一句话中 Token 之间的关系。

✅ 正确理解：

> Embedding 提供 Token 的向量表示；Attention 根据上下文动态计算 Token 之间的关系。

简单记：

```text
Embedding → “你用什么向量表示？”
Attention → “你应该关注谁？”
```

---

## 6. Attention 权重高 ≠ V 离输出更近

❌ 错误理解：

> 最终输出更接近 V1，是因为输出与 V1 的距离更近。

✅ 正确理解：

> V1 的 Attention Weight 更高，所以 V1 对最终结果的贡献更大。

核心：

```text
Weight 越大
→ 对最终结果贡献越大
```

不要用“距离”解释 Attention Weight。

---

## 7. Residual 保存的不是“最初输入”

❌ 错误理解：

> Transformer 中的 Residual 永远保存最开始的 Embedding。

✅ 正确理解：

> 每个子层都有自己的当前输入 X，Residual 保存的是当前子层的输入。

例如：

```text
X₀
 ↓
Attention
 ↓
X₀ + Attention(X₀)
 ↓
X₁
 ↓
FFN
 ↓
X₁ + FFN(X₁)
 ↓
X₂
```

**易错点：**

> Residual 的“原输入”是当前子层的输入，不是整个 Transformer 最开始的输入。

---

## 8. LayerNorm ≠ “把数字变小”

❌ 错误理解：

> LayerNorm 的作用就是把数字缩小。

✅ 正确理解：

> LayerNorm 对每个 Token 的表示向量，在特征维度上进行归一化，使数值分布更加稳定。

它不是简单地“除以一个固定数字”。

---

## 9. LayerNorm ≠ 看到数据就随便使用

❌ 错误理解：

> 只要有数据，LayerNorm 就应该使用，不管是在输入还是输出。

✅ 正确理解：

> LayerNorm 是 Transformer 架构中按照特定结构放置的计算模块。

在我们当前学习的 Pre-Norm 结构中：

```text
X
↓
LayerNorm
↓
Attention
↓
Residual
↓
X₁
↓
LayerNorm
↓
FFN
↓
Residual
```

**易错点：**

LayerNorm 通常是在进入后续子层之前，对当前表示进行归一化，而不是“只要有数据就进行归一化”。

---

## 10. 模型知识 ≠ 某个参数直接对应某条知识

❌ 错误理解：

> “苹果是一种水果”被直接存储在某一个参数里。

✅ 正确理解：

> 模型通过大量参数之间复杂的数值关系，共同表达从训练数据中学习到的知识和规律。

**易错点：**

不要把模型参数理解成：

```text
参数 1 → 苹果
参数 2 → 水果
参数 3 → 苹果是一种水果
```

实际情况是大量参数共同参与计算。

---

## 11. Scaled Attention 与 LayerNorm 的稳定机制不同

两者都与**数值稳定**有关，但不是同一种操作。

### Scaled Dot-Product Attention

```text
QKᵀ
 ↓
除以 √dₖ
 ↓
Softmax
```

作用：

> 控制 Attention Score 的尺度，避免进入 Softmax 的数值过大。

### LayerNorm

对每个 Token 的表示向量，在特征维度上进行归一化。

作用：

> 使表示的数值分布更加稳定。

**易错点：**

> 两者都与“稳定数值”有关，但处理对象、计算方式和作用位置不同。

---

## 12. Position ≠ Context

❌ **错误理解：**

> Position 提供上下文信息，辅助 Attention。

✅ **正确理解：**

> **Position 提供 Token 的位置信息，让模型知道 Token 的顺序。**

三者要区分：

```text
Position
→ 你在第几个位置？

Context
→ 当前有哪些信息可以作为上下文？

Attention
→ 根据这些信息，应该关注谁、关注多少？
```

例如：

> 我喜欢苹果

Position 帮助模型区分：

```text
我     → 位置1
喜欢   → 位置2
苹果   → 位置3
```

然后 Attention 才能结合这些信息进行关系计算。

---


## 错题13：HTTP / POST / `httpx.post()` 层级混淆

**易错理解：**
把 `HTTP`、`POST`、`httpx.post()` 看成同一个层面的东西。

**正确区分：**

| 名称             | 是什么                   | 所属层次            |
| -------------- | --------------------- | --------------- |
| `HTTP`         | 应用层通信协议               | 协议              |
| `POST`         | HTTP 定义的请求方法          | HTTP 协议中的概念     |
| `httpx.post()` | Python HTTPX 库提供的调用方法 | Python 实现 / 工具层 |

三者关系可以记成：

```text
HTTP
 ↓
规定通信规则
 ↓
POST
 ↓
HTTP 协议定义的一种请求方法
 ↓
httpx.post()
 ↓
Python 程序调用 HTTPX 来实际发起 POST 请求
```

例如：

```python
httpx.post(
    url,
    headers=headers,
    json=data
)
```

这里：

* `POST` → **真正的 HTTP Method**
* `httpx.post()` → **Python 中调用 POST 请求的方式**
* HTTP → **底层遵循的应用层通信协议**

### 一句话记忆

> **HTTP = 规则，POST = 规则中的请求方法，`httpx.post()` = Python 调用这个方法的工具。**

---

## 错题14：API 调试与 API Key 环境变量问题

**错误表现：**

直接执行：

```python
answer = result["choices"][0]["message"]["content"]
```

出现：

```text
KeyError: 'choices'
```

**排查过程：**

1. 打印 `result`
2. 发现 API 返回的是错误信息，而不是正常的 `choices`
3. 错误信息显示：

```text
api key: None is invalid
```

4. 说明：

```python
api_key = os.environ.get("DEEPSEEK_API_KEY")
```

得到的是：

```python
None
```

也就是**当前 Python 进程没有读取到 `DEEPSEEK_API_KEY` 环境变量**。

**为什么会读取不到？**

之前是在 PowerShell 中通过：

```powershell
$env:DEEPSEEK_API_KEY="你的API Key"
```

设置的。

这种 `$env:` 设置通常只对**当前 PowerShell 会话**有效。关闭终端、换终端或重新打开终端后，可能就不存在了，因此：

```python
os.environ.get("DEEPSEEK_API_KEY")
```

就会得到 `None`。

**正确排查：**

PowerShell：

```powershell
echo $env:DEEPSEEK_API_KEY
```

Python：

```python
api_key = os.environ.get("DEEPSEEK_API_KEY")
print(api_key)
```

如果是 `None`，说明环境变量没有被当前 Python 进程读取到。

**核心记忆：**

> API 出现 `KeyError: 'choices'` 时，不要直接怀疑 JSON 路径；先看实际 Response。
> 如果 Response 是认证错误，再检查 API Key 是否存在、是否正确，以及当前进程能否读取环境变量。

> [!note]
> **排错顺序**：
> 
> 1. 查看 response.status_code。
> 2. 查看 result 的实际内容。
> 3. 如果是错误响应，检查错误信息。
> 4. 根据错误信息排查 API Key、请求参数、权限、额度等问题。
> 5. 如果响应是成功的，再核对代码访问的字段路径。

---

## 错题15：请求与响应格式混淆

**错误表现：**
认为请求头设置了 `Content-Type: application/json`，服务器就一定会返回 JSON；不清楚响应体是普通文本时调用 `response.json()` 会发生什么。

**正确理解：**

请求与响应是两个独立的方向。

* 请求头 `Content-Type: application/json`：表示客户端发送的请求体采用 JSON 格式。
* 响应体格式：由服务器实际返回的内容决定，不一定是 JSON，也可能是普通文本。
* `response.json()`：尝试将响应体解析为 JSON，并转换成 Python 对象；如果响应体不是合法 JSON，通常会抛出 JSON 解析异常。

**示例：**

```python
response = httpx.post(url, headers=headers, json=data)

print(response.status_code)
print(response.text)  # 查看响应体原始文本

result = response.json()  # 尝试解析 JSON
```

假设服务器返回普通文本 `OK`：

```text
OK
```

调用 `response.json()` 通常会报 JSON 解析异常，因为 `OK` 不是合法 JSON。

但如果返回的是带双引号的 `"OK"`，它就是合法 JSON 字符串。

**排查方法：**

1. 查看 `response.status_code`，确认 HTTP 状态。
2. 查看响应头 `Content-Type`，了解服务器声明的响应格式。
3. 查看 `response.text`，检查实际响应内容。
4. 确认响应体是合法 JSON 后，再调用 `response.json()`。

**记忆口诀：**

请求的 `Content-Type` 管发送格式，不保证响应格式；`response.json()` 负责解析 JSON，不负责判断 API 是否调用成功。

---
