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

**例**：`playing = play + ing`

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

**易错理解：** 把 HTTP、POST、`httpx.post()` 当成同一层面的概念。

| 名称 | 是什么 | 所属层次 |
|---|---|---|
| HTTP | 应用层通信协议，规定通信规则 | 协议 |
| POST | HTTP 定义的一种请求方法 | 协议中的概念 |
| `httpx.post()` | Python HTTPX 库中发起 POST 请求的方法 | 程序实现 / 工具层 |

```python
httpx.post(url, headers=headers, json=data)
```

这段 Python 代码通过 HTTPX 发起 HTTP 请求，使用的请求方法是 POST。

---

## 错题14：API 调试与 API Key 环境变量问题

**错误表现：** 访问 `result["choices"][0]["message"]["content"]` 时出现 `KeyError: 'choices'`，实际响应却是：

```text
api key: None is invalid
```

**原因：** 当前 Python 进程执行 `os.environ.get("DEEPSEEK_API_KEY")` 得到 `None`，请求认证失败，返回的错误对象自然没有正常响应中的 `choices` 字段。

此前只在某个 PowerShell 会话中设置：

```powershell
$env:DEEPSEEK_API_KEY="你的API Key"
```

这种设置作用于当前会话及其后启动的子进程，换终端或使用其他运行配置时，不应假定仍能读到。

**排查顺序：**

1. 查看 `response.status_code` 和实际响应，先区分错误响应与正常结果。
2. 若提示认证错误，在实际运行的 Python 进程中检查变量是否读取成功：

   ```python
   api_key = os.environ.get("DEEPSEEK_API_KEY")
   print("已读取 API Key:", bool(api_key))  # 检查存在性，不打印密钥本身
   ```

3. 若没有读取到，在启动该进程的终端或运行配置中设置变量，再重试。
4. 若变量存在，继续检查密钥是否正确，以及错误信息指向的权限、额度或请求参数。
5. 只有正常响应仍无法取值时，再核对字段路径。

---

## 错题15：请求与响应格式混淆

**错误理解：** 请求头设置 `Content-Type: application/json`，服务器就一定返回 JSON。

**正确区分：**

- 请求头 `Content-Type` 说明发送的请求体格式，不保证响应格式。
- 响应格式应结合响应头 `Content-Type` 与实际响应体判断。
- `response.json()` 尝试把响应体解析成 Python 对象；它不负责判断 API 是否调用成功。

```python
response = httpx.post(url, headers=headers, json=data)

print(response.status_code)
print(response.headers.get("content-type"))
print(response.text)  # 先查看实际内容，再决定如何解析
result = response.json()  # 响应不是合法 JSON 时会抛出解析异常
```

例如，普通文本 `OK` 不是合法 JSON，解析会失败；带双引号的 `"OK"` 则是合法 JSON 字符串。认证等错误响应的排查见错题 14。

---

## 错题16：SSE 流式响应与 JSON 解析混淆

**错误理解：** `iter_lines()` 返回的每一行都能直接传给 `json.loads()`。

例如，下面一行是 SSE 的 `data` 字段，整行并不是 JSON：

```text
data: {"choices":[{"delta":{"content":"你好"}}]}
```

`iter_lines()` 只读取行，不会去掉 `data:` 前缀或解析 JSON。对于每个 `data:` 行承载一份完整 JSON、用 `[DONE]` 结束的 LLM 接口，可按以下方式处理：

```python
import json

for line in response.iter_lines():
    if not line or not line.startswith("data:"):
        continue

    content = line.removeprefix("data:").strip()
    if content == "[DONE]":  # 结束标记不是 JSON，必须先判断
        break

    data = json.loads(content)
    text = data["choices"][0]["delta"].get("content")
    if text:
        print(text, end="", flush=True)
```

**不要混淆这些层次：**

| 概念 | 含义 |
|---|---|
| `line` | `iter_lines()` 读取的一行文本 |
| SSE Event | 按 SSE 规则组织的事件，通常由空行结束 |
| `data:` | SSE 中承载事件数据的字段 |
| JSON 文本 | `data:` 后可能携带的数据格式 |
| Streaming Chunk | LLM API 的一个流式数据单元 |
| `delta.content` | 当前数据单元中的新增文本 |

网络数据块、SSE Event 与 LLM Streaming Chunk 不一定一一对应；一行也不保证构成完整事件。上例按接口约定处理单行数据，不是通用的多行 SSE 事件解析器。`delta` 缺少文本字段的情况见错题 17。

---

## 错题17：`delta` 字典不一定只有 `content` 键

**错误理解：** `delta` 字典只有 `content` 这一个键。

**正确理解：** `delta` 表示本次新增的字段或内容，也可能包含角色或没有文本：

```json
{"choices": [{"delta": {"role": "assistant"}}]}
{"choices": [{"delta": {"content": "你"}}]}
{"choices": [{"delta": {"content": "好"}}]}
{"choices": [{"delta": {}}]}
```

上面每行代表一个独立的数据单元，并非一份完整 JSON 文档。

```python
text = data["choices"][0]["delta"].get("content")
```

`.get("content")` 只读取指定键；缺键时返回 `None`，不代表 `delta` 只有这个键。它也不会保护前面 `choices[0]` 等访问，相关默认值与异常类型见错题 19。

---

## 错题18：浅拷贝与列表结构修改混淆

**错误理解：** `messages.copy()` 与原列表共享内部字典，所以执行 `messages.pop()` 也会删除副本中的消息。

**正确理解：** 浅拷贝创建新列表，但不复制内部字典；**列表结构独立，内部可变对象共享**。

```python
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
]
old_messages = messages.copy()

messages.pop()
print(len(messages))      # 1
print(len(old_messages))  # 2：删除原列表元素，不会删除副本中的引用

messages[0]["content"] = "修改后的内容"
print(old_messages[0]["content"])  # 修改后的内容：第一个字典仍然共享
```

**与当前项目的联系：** 在 `ask_ai()` 中先用 `old_messages = messages.copy()` 备份，请求失败后执行 `messages = old_messages`，可以恢复此前被追加、删除或裁剪的列表结构。

当前代码不修改已有消息字典，因此浅拷贝足够；如果后续要修改已有字典且保留修改前的完整状态，再考虑 `copy.deepcopy()`。

---

## 错题19：`dict.get()` 默认值与异常类型判断

1\. 错误理解

- 认为 `chunk.get("choices", [{}])[0].get("delta", {})` 在 `choices` 为空列表时会得到 `{}`。
- 认为 `choices = [None]` 时会触发 `IndexError`。

2\. 正确理解

`dict.get(key, default)` 只有在键不存在时才返回默认值，不会因为键对应的值为空而使用默认值。

```
{}.get("choices", [{}])                       # [{}]{"choices": []}.get("choices", [{}])          # []{"choices": [None]}.get("choices", [{}])[0]   # None
```

- 空列表访问 `[0]`：触发 `IndexError`。
- `None.get("delta", {})`：触发 `AttributeError`。

3\. 项目中的联系

AI API 项目通过 `json.loads(content)` 解析流式响应，再从 `choices → delta → content` 提取文本。

当前 `except` 捕获了 `IndexError`，但没有捕获 `AttributeError`。如果出现 `AttributeError`，当前异常处理分支不会执行，因而无法通过该分支恢复 `messages`。

4\. 核心记忆

> 键不存在才用默认值；空列表取 `[0]` 是 `IndexError`；`None` 调用 `.get()` 是 `AttributeError`。

---
