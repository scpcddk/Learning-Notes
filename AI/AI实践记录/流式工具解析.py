"""按索引合并流式工具请求，把完整调用交给上层校验和执行。"""

import json
import re

from 流式聊天 import iter_sse_data


class ToolStreamAssembler:
    def __init__(self, max_calls=8, max_chars=32_000):
        # 键是流内工具槽位 index；不同工具的名称和参数分别累积。
        self.calls = {}
        self.text = []
        self.reason = None
        self.max_calls = max_calls
        self.max_chars = max_chars
        self.chars = 0

    # 正文、工具名称和参数共用字符预算，限制整个组装过程的累积量。
    def add_text(self, value):
        if not isinstance(value, str):
            raise ValueError("流式字段必须是字符串")
        self.chars += len(value)
        if self.chars > self.max_chars:
            raise ValueError("增量内容超过预算")
        return value

    # 接收一条已解码的 SSE 事件。每个工具槽位按原到达顺序保留字符串片段。
    def feed(self, chunk):
        if not isinstance(chunk, dict) or chunk.get("error"):
            raise ValueError("无效流式对象或上游错误")
        choices = chunk.get("choices")
        if choices == []:  # 允许接口的独立 usage 事件。
            return
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError("本组装器只处理单 choice")
        choice = choices[0]
        if not isinstance(choice, dict) or choice.get("index", 0) != 0:
            raise ValueError("choice 类型或编号错误")
        delta = choice.get("delta")
        if delta is None:
            delta = {}
        if not isinstance(delta, dict):
            raise ValueError("delta 必须是对象")
        if self.reason is not None and (delta.get("content") or delta.get("tool_calls")):
            raise ValueError("业务结束后仍收到新增内容")
        content = delta.get("content")
        if content is not None:
            self.text.append(self.add_text(content))
        fragments = delta.get("tool_calls", [])
        if not isinstance(fragments, list):
            raise ValueError("tool_calls 增量必须是数组")
        for fragment in fragments:
            if not isinstance(fragment, dict):
                raise ValueError("工具增量必须是对象")
            index = fragment.get("index")
            if type(index) is not int or not 0 <= index < self.max_calls:
                raise ValueError("工具 index 超出范围")
            # 同一 index 的多次增量写入同一槽位，不把每个片段当成一次新调用。
            entry = self.calls.setdefault(index, {"id": None, "name": [], "arguments": []})
            call_id = fragment.get("id")
            # 后续增量可省略 ID。一旦给出 ID，当前槽位必须沿用它。
            if call_id is not None:
                if not isinstance(call_id, str) or not 1 <= len(call_id) <= 256:
                    raise ValueError("调用 ID 无效")
                if entry["id"] not in (None, call_id):
                    raise ValueError("同一 index 的调用 ID 发生变化")
                entry["id"] = call_id
            if fragment.get("type", "function") != "function":
                raise ValueError("不支持的工具类型")
            function = fragment.get("function", {})
            if not isinstance(function, dict):
                raise ValueError("function 增量必须是对象")
            for key in ("name", "arguments"):
                if key in function:
                    entry[key].append(self.add_text(function[key]))
        reason = choice.get("finish_reason")
        if reason is not None:
            if not isinstance(reason, str) or self.reason not in (None, reason):
                raise ValueError("结束原因冲突")
            self.reason = reason

    # 收齐传输结束信号后，按业务结束原因返回文本消息或完整工具请求。
    def finish(self, saw_done):
        if not saw_done:
            raise ValueError("流未完整结束，禁止执行工具")
        text = "".join(self.text)
        if not self.calls:
            if self.reason != "stop" or not text.strip():
                raise ValueError("没有完整最终文本")
            return {"role": "assistant", "content": text}, self.reason
        if self.reason != "tool_calls":
            raise ValueError("工具参数未以 tool_calls 状态结束")
        # 从 0 开始检查槽位是否连续，发现遗漏就拒绝整组调用。
        if sorted(self.calls) != list(range(len(self.calls))):
            raise ValueError("工具槽位缺失")
        result = []
        used_ids = set()
        for index in sorted(self.calls):
            entry = self.calls[index]
            name = "".join(entry["name"])
            # 等流完整结束后再拼接和解析参数，中间片段可能不是合法 JSON。
            raw = "".join(entry["arguments"])
            if not entry["id"] or entry["id"] in used_ids:
                raise ValueError("工具 ID 缺失或重复")
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", name):
                raise ValueError("工具名无效")
            if not isinstance(json.loads(raw), dict):
                raise ValueError("工具参数顶层必须是对象")
            used_ids.add(entry["id"])
            result.append({"id": entry["id"], "type": "function",
                           "function": {"name": name, "arguments": raw}})
        return {"role": "assistant", "content": text or None, "tool_calls": result}, self.reason


def message_from_lines(lines):
    assembler = ToolStreamAssembler()
    saw_done = False
    for data in iter_sse_data(lines):
        if data == "[DONE]":
            saw_done = True
            break
        assembler.feed(json.loads(data))
    return assembler.finish(saw_done)


def stream_message(client, messages, tools, **options):
    body = client.body(messages, stream=True, tools=tools, **options)
    # 响应读取和组装都在 with 内完成，中途报错也会关闭响应。
    with client.http.stream("POST", client.settings.url, json=body) as response:
        response.raise_for_status()
        if "text/event-stream" not in response.headers.get("content-type", "").lower():
            raise ValueError("未返回 SSE")
        return message_from_lines(response.iter_lines())
