"""通过聊天接口演示计算器与日期工具。程序校验工具请求，并限制调用次数和耗时。"""

import json
import math
import time
from datetime import datetime, timedelta, timezone
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from 聊天客户端 import ChatClient, ResponseFormatError, Settings


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    op: Literal["add", "subtract", "multiply", "divide"]
    a: float = Field(ge=-1e9, le=1e9, allow_inf_nan=False)
    b: float = Field(ge=-1e9, le=1e9, allow_inf_nan=False)


# 日期工具无需参数，参数对象只接受空字典。
class DateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def calculate(args):
    if args.op == "add":
        result = args.a + args.b
    elif args.op == "subtract":
        result = args.a - args.b
    elif args.op == "multiply":
        result = args.a * args.b
    else:
        if args.b == 0:
            raise ValueError("除数不能为零")
        result = args.a / args.b
    if not math.isfinite(result):
        raise ValueError("结果不是有限数")
    return {"value": result}


def today(args):
    # 当前业务固定 Asia/Shanghai（UTC+8）；多时区系统需单独配置。
    return {"date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
            "timezone": "Asia/Shanghai"}


# 注册表同时绑定参数 Schema 与执行函数，只允许调用明确登记的工具。
REGISTRY = {
    "calculate": (CalculateArgs, calculate, "执行有界的四则计算，不接受表达式字符串"),
    "today": (DateArgs, today, "获取 Asia/Shanghai 时区今天的日期"),
}
# 从执行注册表生成发给模型的工具描述，使声明和实际校验使用同一份 Schema。
TOOLS = [
    {"type":"function", "function":{
        "name": name, "description": entry[2], "parameters": entry[0].model_json_schema()
    }} for name, entry in REGISTRY.items()
]


# 将参数错误和工具执行错误整理成结果，供下一轮模型判断如何继续。
def execute_call(call):
    function = call.get("function")
    if not isinstance(function, dict):
        return {"ok": False, "error": "invalid_function"}
    name = function.get("name")
    if not isinstance(name, str):
        return {"ok": False, "error": "invalid_tool_name"}
    entry = REGISTRY.get(name)
    if entry is None:
        return {"ok": False, "error": "unknown_tool"}
    raw = function.get("arguments")
    if not isinstance(raw, str) or len(raw) > 4000:
        return {"ok": False, "error": "invalid_arguments"}
    schema, handler, _ = entry
    try:
        # 先将参数字符串解析为已校验对象，再进入真实函数。
        args = schema.model_validate_json(raw)
        return {"ok": True, "data": handler(args)}
    except ValidationError:
        return {"ok": False, "error": "arguments_do_not_match_schema"}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}


def run_agent(client, task):
    messages = [
        {"role":"system", "content":(
            "你是计算与日期助手。需要精确计算或日期时使用工具。"
            "工具出错要明确说明或修正参数，不能编造工具结果。"
        )},
        {"role":"user", "content":task},
    ]
    options = {}
    if urlparse(client.settings.url).hostname == "api.deepseek.com":
        options["thinking"] = {"type": "disabled"}
    # 在调用前后检查时间预算。请求本身的网络等待由 HTTPX 超时约束。
    deadline = time.monotonic() + 120
    seen = set()
    total_calls = 0
    for step in range(6):
        if time.monotonic() > deadline:
            raise RuntimeError("Agent 超过软时间预算")
        choice, usage = client.complete(messages, tools=TOOLS, **options)
        if time.monotonic() > deadline:
            raise RuntimeError("模型请求返回时已超过预算")
        message = choice["message"]
        calls = message.get("tool_calls") or []
        if not isinstance(calls, list):
            raise ResponseFormatError("tool_calls 类型错误")
        if not calls:
            answer = message.get("content")
            if choice.get("finish_reason") != "stop" or not isinstance(answer, str) or not answer.strip():
                raise ResponseFormatError("Agent 未产生完整最终文本")
            return answer
        if choice.get("finish_reason") != "tool_calls":
            raise ResponseFormatError("工具请求结束原因不符合约定")
        # 分别限制本轮工具数量和整个任务的累计数量，本批超限时一项也不执行。
        if len(calls) > 3 or total_calls + len(calls) > 8:
            raise RuntimeError("工具次数超过预算")
        call_ids = []
        for call in calls:
            if not isinstance(call, dict) or not isinstance(call.get("id"), str) or not call["id"]:
                raise ResponseFormatError("工具调用缺少有效 ID")
            call_ids.append(call["id"])
        # 先校验整批 ID，保证每个工具结果都能对应到唯一的请求。
        if len(set(call_ids)) != len(call_ids):
            raise ResponseFormatError("工具调用 ID 重复")
        # 先记录模型提出的工具请求，再按 tool_call_id 回传各自的执行结果。
        messages.append({"role":"assistant", "content":message.get("content"), "tool_calls":calls})
        for call in calls:
            if time.monotonic() > deadline:
                raise RuntimeError("执行工具前预算已耗尽")
            # 按函数名与参数识别重复请求，防止换了调用 ID 仍反复执行相同操作。
            signature = json.dumps(call.get("function"), ensure_ascii=False, sort_keys=True)
            if signature in seen:
                raise RuntimeError("重复相同工具请求，停止无进展循环")
            seen.add(signature)
            result = execute_call(call)
            total_calls += 1
            messages.append({"role":"tool", "tool_call_id":call["id"],
                             "content":json.dumps(result, ensure_ascii=False, allow_nan=False)})
    raise RuntimeError("达到最大模型决策轮数，任务未确认完成")


if __name__ == "__main__":
    with ChatClient(Settings.from_env()) as client:
        print(run_agent(client, "今天是什么日期？再算一下 (18+24)÷6。"))
