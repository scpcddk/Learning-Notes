"""离线验证应用笔记中的协议、会话、持久化和检索评价示例。"""

import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import httpx
import 流式聊天 as cli
from 流式聊天 import fit_history
from 聊天客户端 import ChatClient, ResponseFormatError, Settings
from 检索评估 import evaluate, regressions, score_query
from 会话存储 import StateConflict, StateStore
from 流式工具解析 import ToolStreamAssembler, message_from_lines


def event(delta, reason=None):
    return {"choices": [{"index": 0, "delta": delta, "finish_reason": reason}]}


# 每条 SSE 事件用空行结束，省略 [DONE] 可模拟流提前断开。
def sse(*objects, done=True):
    text = "".join("data: " + json.dumps(obj, ensure_ascii=False) + "\n\n" for obj in objects)
    return text + ("data: [DONE]\n\n" if done else "")


class ExampleTests(unittest.TestCase):
    def client(self, handler):
        client = ChatClient(Settings("https://offline.invalid/chat", "fake-model", "fake-key"))
        client.http.close()
        # 把真实网络替换成可控的响应函数，便于稳定复现错误。
        client.http = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(client.close)
        return client

    def test_text_response_and_body(self):
        def handler(request):
            body = json.loads(request.content)
            self.assertEqual(body["model"], "fake-model")
            self.assertEqual(body["messages"][0]["content"], "测试")
            return httpx.Response(200, json={"choices": [{"finish_reason": "stop",
                "message": {"role": "assistant", "content": "收到"}}]})
        self.assertEqual(self.client(handler).text([{"role": "user", "content": "测试"}]), "收到")

    def test_http_and_format_failures(self):
        factories = [
            (lambda: httpx.Response(401, json={"error": "unauthorized"}), httpx.HTTPStatusError),
            (lambda: httpx.Response(200, text="not JSON"), ResponseFormatError),
            (lambda: httpx.Response(200, json={"choices": []}), ResponseFormatError),
            (lambda: httpx.Response(200, json={"choices": [{"finish_reason": "length",
                "message": {"content": "一半"}}]}), ResponseFormatError),
        ]
        for factory, error in factories:
            with self.subTest(error=error.__name__), self.assertRaises(error):
                self.client(lambda request: factory()).text([])

    def test_network_timeout(self):
        def handler(request):
            raise httpx.ReadTimeout("offline simulated timeout", request=request)
        with self.assertRaises(httpx.ReadTimeout):
            self.client(handler).text([])

    def test_sse_event_boundaries(self):
        lines = ["\ufeff: heartbeat", "data: {", 'data: "x": 1}', "", "data: incomplete"]
        self.assertEqual(list(cli.iter_sse_data(lines)), ['{\n"x": 1}'])

    # 让模拟响应经过真实的 SSE 解析入口，捕获交互输出以便检查函数返回值。
    def stream(self, text):
        client = self.client(lambda request: httpx.Response(
            200, text=text, headers={"content-type": "text/event-stream; charset=utf-8"}))
        with contextlib.redirect_stdout(io.StringIO()):
            return cli.stream_text(client, [])

    def test_sse_unicode_and_usage(self):
        text = sse(event({"role": "assistant", "content": None}),
                   event({"content": "你好"}), event({}, "stop"),
                   {"choices": [], "usage": {"total_tokens": 7}})
        answer, usage = self.stream(text)
        self.assertEqual(answer, "你好")
        self.assertEqual(usage["total_tokens"], 7)

    def test_sse_truncation_and_bad_json(self):
        cases = [sse(event({"content": "半句"}), done=False),
                 sse(event({"content": "截断"}, "length")),
                 sse(event({"content": "缺少结束状态"})),
                 "data: broken\n\ndata: [DONE]\n\n"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ResponseFormatError):
                self.stream(text)

    def test_failed_turn_not_committed(self):
        snapshots = []
        original = cli.candidate_messages
        def record(system, turns, question):
            snapshots.append(copy.deepcopy(turns))
            return original(system, turns, question)
        settings = Settings("https://offline.invalid/chat", "fake-model", "fake-key")
        client = self.client(lambda request: httpx.Response(500))
        # 按顺序模拟两轮输入及一次断流，再检查下一轮看到的历史。
        with patch("builtins.input", side_effect=["坏请求", "下一轮", "exit"]), \
             patch.object(cli.Settings, "from_env", return_value=settings), \
             patch.object(cli, "ChatClient", return_value=client), \
             patch.object(cli, "candidate_messages", side_effect=record), \
             patch.object(cli, "stream_text", side_effect=[ResponseFormatError("断流"), ("成功", None)]), \
             contextlib.redirect_stdout(io.StringIO()):
            cli.main()
        self.assertEqual(snapshots, [[], []])

    def test_token_budget_removes_whole_turns(self):
        turns = [("old", "answer"), ("new", "reply")]
        counter = lambda messages: len(messages)  # 确定性的假计数器，不代表真实 Token。
        messages, info = fit_history("s", turns, "q", counter, 5, 1)
        self.assertEqual([m["role"] for m in messages], ["system", "user", "assistant", "user"])
        self.assertEqual(messages[1]["content"], "new")
        self.assertEqual(info["dropped_turns"], 1)
        self.assertEqual(turns, [("old", "answer"), ("new", "reply")])
        with self.assertRaises(ValueError):
            fit_history("s", turns, "q", counter, 2, 1)
        with self.assertRaises(ValueError):
            fit_history("s", turns, "q", lambda messages: -1, 10, 1)

    def test_interleaved_tool_fragments(self):
        # 故意让两个工具的片段交错到达，验证组装依据 index，而不是到达顺序。
        objects = [
            event({"tool_calls": [{"index": 1, "id": "c1", "type": "function",
                "function": {"name": "today", "arguments": "{"}},
                {"index": 0, "id": "c0", "type": "function",
                 "function": {"name": "cal", "arguments": '{"expression":'}}]}),
            event({"tool_calls": [{"index": 0, "function": {"name": "culate", "arguments": '"1+1"}'}},
                                   {"index": 1, "function": {"arguments": "}"}}]}),
            event({}, "tool_calls"),
        ]
        assembler = ToolStreamAssembler()
        for obj in objects:
            assembler.feed(obj)
        with self.assertRaises(ValueError):
            assembler.finish(False)  # 即使参数完整，也必须等流完整结束。
        message, reason = message_from_lines(sse(*objects).splitlines())
        self.assertEqual(reason, "tool_calls")
        self.assertEqual([call["id"] for call in message["tool_calls"]], ["c0", "c1"])
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "calculate")
        self.assertEqual(json.loads(message["tool_calls"][0]["function"]["arguments"]),
                         {"expression": "1+1"})

    # 分别模拟缺失 JSON 尾部、参数类型错误和模型输出被截断。
    def test_invalid_tools_never_become_ready(self):
        for raw, reason in [("{", "tool_calls"), ("[]", "tool_calls"), ("{}", "length")]:
            text = sse(event({"tool_calls": [{"index": 0, "id": "c0",
                "function": {"name": "today", "arguments": raw}}]}, reason))
            with self.subTest(raw=raw, reason=reason), self.assertRaises(ValueError):
                message_from_lines(text.splitlines())

    def test_sqlite_restart_conflict_and_owner(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path = Path(folder) / "state.sqlite3"
            store = StateStore(path)
            store.create("chat:1", "u1", {"turns": []})
            revision = store.save("chat:1", "u1", 0, {"turns": [["问题", "回答"]]})
            # 新 Python 进程读取已提交状态，验证不依赖原实例的内存。
            code = ("from 会话存储 import StateStore; import json,sys; "
                    "print(json.dumps(StateStore(sys.argv[1]).load('chat:1','u1')))" )
            result = subprocess.run([sys.executable, "-X", "utf8", "-c", code, str(path)],
                                    cwd=Path(__file__).resolve().parent,
                                    check=True, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(json.loads(result.stdout)["revision"], revision)
            with self.assertRaises(StateConflict):
                store.save("chat:1", "u1", 0, {"turns": []})
            with self.assertRaises(LookupError):
                store.load("chat:1", "u2")
            with self.assertRaises(StateConflict):
                store.delete("chat:1", "u2", revision)
            store.delete("chat:1", "u1", revision)
            with self.assertRaises(LookupError):
                store.load("chat:1", "u1")

    def test_retrieval_metrics_and_no_answer(self):
        scores = score_query({"A": 3, "C": 1}, ["B", "A", "C"], 3)
        self.assertAlmostEqual(scores["precision"], 2 / 3)
        self.assertEqual(scores["recall"], 1)
        self.assertEqual(scores["mrr"], 0.5)
        self.assertAlmostEqual(scores["ndcg"], 0.6442869262030828)
        self.assertTrue(all(value is None for value in score_query({}, [], 3).values()))
        with self.assertRaises(ValueError):
            score_query({"A": 1}, ["A", "A"], 3)

    def test_evaluation_baseline_gate(self):
        cases = [{"id": "q1", "question": "问题", "corpus_version": "v1",
                  "relevant": {"A": 3}, "ranked_ids": ["A"]}]
        old = evaluate(cases, 3)
        changed = copy.deepcopy(cases)
        changed[0]["ranked_ids"] = ["B", "A"]
        new = evaluate(changed, 3)
        self.assertIn("mrr", regressions(old, new))
        self.assertEqual(regressions(old, old), {})
        # 更换语料版本后应拒绝比较，即使查询 ID 与标注保持原样。
        changed[0]["corpus_version"] = "v2"
        with self.assertRaises(ValueError):
            regressions(old, evaluate(changed, 3))


if __name__ == "__main__":
    unittest.main()
