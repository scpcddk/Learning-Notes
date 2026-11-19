"""支持多轮历史和 SSE 增量的命令行聊天。包含可复用的 SSE 解析与 Token 预算函数。"""

import json
import sys
import time

import httpx

from 聊天客户端 import ChatClient, ResponseFormatError, Settings


def iter_sse_data(lines):
    data_lines = []
    event_size = 0
    first = True
    for line in lines:
        if first:
            line = line.removeprefix("\ufeff")  # 兼容流开头 BOM。
            first = False
        # 空行才是事件边界；在此之前，多个 data 行属于同一个事件。
        if line == "":
            if data_lines:
                yield "\n".join(data_lines)
            data_lines = []
            event_size = 0
            continue
        # 冒号开头的是 SSE 注释，例如服务端发送的心跳。
        if line.startswith(":"):
            continue
        field, sep, value = line.partition(":")
        if sep and value.startswith(" "):
            value = value[1:]  # 按协议只去掉一个可选空格。
        if field == "data":
            event_size += len(value) + 1
            # 按字符数限制单个事件，避免一直没有空行时累积过多数据。
            if event_size > 1_000_000:
                raise ValueError("SSE 单事件过大")
            data_lines.append(value)
    # EOF 时没有空行结尾的未完成事件不派发；调用方另查结束标志。


# 供进阶练习使用。默认 CLI 仍按最近轮次及字符数裁剪。
def fit_history(system, turns, question, counter, context_limit,
                output_budget, reserve=0):
    # turns 存放已经确认的问题与回答对，counter 负责按模型统计候选消息的 Token 数。
    limits = (context_limit, output_budget, reserve)
    if any(type(value) is not int or value < 0 for value in limits):
        raise ValueError("预算必须为非负整数")
    # 上下文同时容纳输入与输出；先给回答和额外开销留出空间。
    available = context_limit - output_budget - reserve
    if available <= 0:
        raise ValueError("没有剩余输入预算")
    selected = list(turns)  # 不修改已确认历史。

    # 无论保留几轮历史，系统指令和当前问题都要进入候选请求。
    def build(items):
        result = [{"role": "system", "content": system}]
        for user, assistant in items:
            result.extend([
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ])
        result.append({"role": "user", "content": question})
        return result

    def count(messages):
        value = counter(messages)
        if type(value) is not int or value < 0:
            raise ValueError("计数器必须返回非负整数")
        return value

    # 先确认本次问题自身能放下，避免无意义地删光历史。
    if count(build([])) > available:
        raise ValueError("指令与本次问题已超过预算，需要缩短或分段")
    while True:
        candidate = build(selected)
        used = count(candidate)
        if used <= available:
            return candidate, {"input_tokens": used, "dropped_turns": len(turns) - len(selected)}
        # 每次删除最早的一整轮，保留 user/assistant 的配对关系。
        selected.pop(0)


def stream_text(client, messages):
    # 边显示边收集正文片段；只有确认完整结束，才把拼接结果返回给调用方。
    pieces = []
    total_chars = 0
    done = False
    finish_reason = None
    usage = None
    deadline = time.monotonic() + 120
    body = client.body(messages, stream=True)
    with client.http.stream("POST", client.settings.url, json=body) as response:
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" not in content_type.lower():
            raise ResponseFormatError("服务器未返回预期 SSE 格式")
        for data in iter_sse_data(response.iter_lines()):
            # 这是收到事件时检查的软预算，不是硬性 120 秒中断器。
            if time.monotonic() > deadline:
                raise ResponseFormatError("本轮超过时间预算")
            # 先识别协议结束标记，再对普通 data 事件做 JSON 解析。
            if data == "[DONE]":
                done = True
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError as exc:
                raise ResponseFormatError("SSE data 不是合法 JSON") from exc
            if not isinstance(obj, dict) or obj.get("error"):
                raise ResponseFormatError("流中包含错误或非法对象")
            # 用量有时单独发送，先记录它，再判断这一事件是否有候选内容。
            if isinstance(obj.get("usage"), dict):
                usage = obj["usage"]
            choices = obj.get("choices")
            if choices == []:  # 某些兼容接口有独立 usage 事件。
                continue
            if not isinstance(choices, list) or not choices:
                raise ResponseFormatError("流事件缺少 choices 数组")
            choice = choices[0]
            if not isinstance(choice, dict):
                raise ResponseFormatError("choice 类型错误")
            delta = choice.get("delta")
            if delta is None:
                delta = {}
            if not isinstance(delta, dict):
                raise ResponseFormatError("delta 必须是对象")
            if delta.get("tool_calls"):
                raise ResponseFormatError("文本 CLI 不执行工具调用")
            text = delta.get("content")
            if text is not None and not isinstance(text, str):
                raise ResponseFormatError("content 类型错误")
            if text:
                total_chars += len(text)
                if total_chars > 50_000:
                    raise ResponseFormatError("输出超过本程序限制")
                pieces.append(text)
                sys.stdout.write(text)
                sys.stdout.flush()
            reason = choice.get("finish_reason")
            if reason is not None:
                finish_reason = reason
    answer = "".join(pieces)
    # 协议结束标记、模型正常停止和非空正文缺一不可。
    if not done or finish_reason != "stop" or not answer.strip():
        raise ResponseFormatError(
            f"本轮未获得完整文本：done={done}, finish_reason={finish_reason!r}"
        )
    return answer, usage


def candidate_messages(system, turns, question):
    # 只裁剪本轮要发给模型的副本，已确认的历史由主循环管理。
    selected = list(turns[-5:])
    # 字符预算只用于教学；真实 Token 预算须按模型计数。
    def count_chars(items):
        return len(system) + len(question) + sum(len(q) + len(a) for q, a in items)
    while selected and count_chars(selected) > 12_000:
        selected.pop(0)
    if count_chars(selected) > 12_000:
        raise ValueError("单次问题过长，请先缩短或分段")
    messages = [{"role": "system", "content": system}]
    for q, a in selected:
        messages.extend([
            {"role": "user", "content": q},
            {"role": "assistant", "content": a},
        ])
    messages.append({"role": "user", "content": question})
    return messages


def main():
    system = "你是学习助手。先清楚解释当前问题，再给一个具体例子。"
    turns = []
    with ChatClient(Settings.from_env()) as client:
        print("输入 exit 退出，clear 清空历史，Ctrl+C 取消当前轮。")
        while True:
            try:
                question = input("你：").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n聊天结束")
                break
            if question.lower() == "exit":
                break
            if question.lower() == "clear":
                turns.clear()
                print("历史已清空")
                continue
            if not question:
                continue
            try:
                # 本轮先使用候选历史，请求失败时保留之前已确认的对话。
                candidate = candidate_messages(system, turns, question)
                print("AI：", end="", flush=True)
                answer, _ = stream_text(client, candidate)
            except httpx.TimeoutException:
                print("\n[请求超时，本轮未写入历史]")
            except httpx.HTTPStatusError as exc:
                print(f"\n[HTTP {exc.response.status_code}，本轮未写入历史]")
            except httpx.RequestError:
                print("\n[网络请求失败，本轮未写入历史]")
            except (ResponseFormatError, ValueError) as exc:
                print(f"\n[{exc}；本轮未写入历史]")
            except KeyboardInterrupt:
                print("\n[已取消，本轮未写入历史]")
            else:
                # 只在全部验证通过后提交一个完整轮次。
                turns = (turns + [(question, answer)])[-5:]
                print()


if __name__ == "__main__":
    main()
