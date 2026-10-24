import os
import json
import httpx
import time

# 从环境变量读取密钥，避免把 API Key 直接写入代码。
api_key = os.environ.get("DEEPSEEK_API_KEY")

# 缺少密钥时立即停止，避免发送无法通过认证的请求。
if not api_key:
    raise RuntimeError("未设置 DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/chat/completions"
model = "deepseek-chat"

# Bearer 认证通过请求头传递密钥；请求正文使用 JSON 格式。
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 分别设置连接、读取、写入和等待连接池的超时，单位为秒。
# read 限制等待下一批响应数据的时间，不是整次回答的总耗时。
timeout = httpx.Timeout(
    connect=5.0,
    read=60.0,
    write=10.0,
    pool=5.0
)

# 保存多轮对话，每条消息包含 role（角色）和 content（内容）。
messages = []

def trim_messages(messages):
    # 只保留最近的消息，限制发送给模型的上下文长度。
    if len(messages) > 6:
        messages = messages[-6:]
        # 如果截断后以模型回答开头，再移除它，让上下文从用户问题开始。
        if messages[0]["role"] == "assistant":
            messages = messages[-5:]
    return messages

def ask_ai(question):
    # 函数中会重新赋值 messages，因此需要声明使用全局变量。
    global messages

    # 在加入新问题前保存历史；请求失败时恢复，避免留下未完成的对话。
    # 这里只追加消息或切片，不修改已有消息字典，浅拷贝即可满足需要。
    old_messages = messages.copy()

    # 先加入当前问题，再裁剪历史，确保请求中包含本轮提问。
    messages.append({
        "role": "user",
        "content": question
    })
    messages = trim_messages(messages)

    # stream=True 启用流式响应；max_tokens 限制生成回答的 token 数。
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 500,
        "stream": True
    }

    # 最多重试两次，加上首次请求，总共最多发送三次；这里只重试 429。
    max_retries = 2


    for attempt in range(max_retries + 1):
        # 每次尝试都重新记录结束状态和回答内容。
        completed = False
        answer = ""
        try:
            # 使用上下文管理器，退出时会关闭响应并释放连接资源。
            with httpx.stream(
                "POST",
                url,
                headers=headers,
                json=data,
                timeout=timeout
            ) as response:
                # 遇到 4xx 或 5xx 状态码时抛出 HTTPStatusError，交给下方处理。
                response.raise_for_status()
    
                for line in response.iter_lines():
                    # 按行读取 SSE（服务器发送事件），忽略空行等非数据行。
                    if not line.startswith("data: "):
                        continue
    
                    # 去掉 "data: " 前缀，取得事件正文。
                    content = line[6:]
    
                    # [DONE] 是流式响应的结束标记，不是 JSON 数据。
                    if content == "[DONE]":
                        completed = True
                        break
    
                    # 将事件正文解析为 JSON，并逐层检查结构，避免直接取值出错。
                    chunk = json.loads(content)
                    if not isinstance(chunk, dict):
                      raise ValueError("API 响应不是字典")
                    choices = chunk.get("choices")
    
                    if not isinstance(choices, list) or not choices:
                        raise ValueError("choices 缺失、类型错误或为空")
                    
                    if not isinstance(choices[0], dict):
                        raise ValueError("choices[0] 不是字典")
                    
                    # delta 表示这一块新增的内容，而非整段回答。
                    delta = choices[0].get("delta")
                    
                    if not isinstance(delta, dict):
                        raise ValueError("delta 不是字典")
                    
                    # 部分数据块仅包含角色或结束信息，没有 content 时按空文本处理。
                    text = delta.get("content", "")
                    
                    if not isinstance(text, str):
                        raise ValueError("content 不是字符串")
                    
                    if text:
                        # 立即显示新文本，同时拼接出用于保存到历史中的完整回答。
                        print(text, end="", flush=True)
                        answer += text
                    
            print()
    
            # 只有收到结束标记才保存回答；流提前关闭时恢复原历史。
            if completed:
               messages.append({
                   "role": "assistant",
                   "content": answer
               })
            else:
                print("流式响应未正常结束：未收到结束标记，本轮对话未保存")
                messages = old_messages
                return None
    
            return answer
    
        except httpx.HTTPStatusError as e:
            # HTTP 响应已收到，但状态码表示请求失败。
            status = e.response.status_code
    
            if status == 401:
                print("API 身份认证失败（401），请检查 API Key 和认证配置")
        
            elif status == 429:
                # 限流时优先使用服务器建议的等待秒数，否则采用指数退避。
                if attempt < max_retries:
                     max_wait_seconds = 30
                     retry_after = e.response.headers.get("Retry-After")
                     # 此处只接受 ASCII 数字形式的秒数；日期等其他格式使用退避时间。
                     if isinstance(retry_after, str) and retry_after.isascii() and retry_after.isdigit():
                         # 先去掉前导零，再按长度和字典序与上限比较。
                         # 这样不用把可能很长的数字字符串直接转换为整数。
                         normalized = retry_after.lstrip("0") or "0"
                         limit = str(max_wait_seconds)
                         too_long = (
                             len(normalized) > len(limit)
                             or (
                                 len(normalized) == len(limit)
                                 and normalized > limit
                             )
                         )
                         if too_long:
                             # 等待建议超过上限时结束本轮，不缩短服务器要求的等待时间。
                             print("服务器建议等待时间超过 30 秒，请稍后再试")
                             messages = old_messages
                             return None
                         wait_seconds = int(normalized)
                     else:
                         # attempt 从 0 开始，两次重试分别等待 2 秒、4 秒。
                         wait_seconds = 2 ** (attempt + 1)
                     if wait_seconds > max_wait_seconds:
                         print("等待时间过长")
                         messages = old_messages
                         return None
                     print(f"等待 {wait_seconds} 秒后重试")
                     time.sleep(wait_seconds)
                     # 进入下一次尝试，复用当前问题和同一份请求数据。
                     continue
                else:
                    print("API 请求受到限流（429），重试次数已用完，请稍后再试")
        
            elif status == 500:
                print("API 服务器处理请求时发生内部错误（500），请稍后重试")
            else:
                print(f"HTTP 请求失败，状态码：{status}")
            # 不再重试的 HTTP 错误统一恢复历史并返回 None。
            messages = old_messages
            return None
    
        # 先捕获具体超时类型，再捕获它们的父类 TimeoutException。
        except httpx.ReadTimeout:
            messages = old_messages
            print("\n读取超时：模型响应中断，本轮对话未保存")
            return None
        
        except httpx.ConnectTimeout:
            messages = old_messages
            print("\n连接超时：无法及时连接 API 服务器，本轮对话未保存")
            return None
        
        except httpx.TimeoutException:
            messages = old_messages
            print("\n其他超时")
            return None
        
        except httpx.RequestError as e:
            # 处理超时以外的请求异常，例如连接失败、连接中断等。
            messages = old_messages
            print(f"\n网络请求异常：{type(e).__name__}")
            return None   
                 
        except (
            json.JSONDecodeError,
            KeyError,
            IndexError,
            ValueError
        ) as e:
            # JSON 解析或响应结构校验失败时，不把部分回答保存到对话历史。
            messages = old_messages
            print(f"\n请求或解析失败：{e}")
            return None

# 直接运行本文件时进入交互循环；被其他模块导入时不执行此循环。
if __name__ == "__main__":
    while True:
        question = input("请输入问题：")
    
        # 忽略首尾空白和大小写，方便输入退出指令。
        if question.strip().lower() == "exit":
            print("聊天结束")
            break
    
        # 跳过空输入，避免发送无意义的请求。
        if not question.strip():
            continue
    
        # 回答已在函数内流式打印；返回值为完整回答，失败时为 None。
        answer = ask_ai(question)
