"""离线检查流式完整性、失败回滚与 429 重试，不发送真实 API 请求。"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import httpx


spec = importlib.util.spec_from_file_location(
    "error_handling_practice", Path(__file__).with_name("错误处理.py")
)
main = importlib.util.module_from_spec(spec)
with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key", "DEEPSEEK_MODEL": "test-model"}):
    spec.loader.exec_module(main)


def event(content=None, reason=None, prefix="data: "):
    # 每个事件必须由空行结束；content=null 是协议允许的无文本片段。
    payload = {"choices": [{"delta": {"content": content}, "finish_reason": reason}]}
    return [prefix + json.dumps(payload, ensure_ascii=False), ""]


def response_context(lines=(), status=200, headers=None):
    response = MagicMock()
    real_response = httpx.Response(status, request=httpx.Request("POST", "https://example.com/chat"))
    # 直接注入响应头字典，以便同时覆盖异常非 ASCII 值的兜底处理。
    if headers:
        real_response.headers = headers
    response.raise_for_status.side_effect = real_response.raise_for_status
    response.iter_lines.return_value = iter(lines)
    context = MagicMock()
    context.__enter__.return_value = response
    context.__exit__.return_value = False
    return context


class StreamingPracticeTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            {"role": "user", "content": "旧问题"},
            {"role": "assistant", "content": "旧回答"},
        ]
        main.messages = self.history.copy()

    def call(self, contexts):
        with patch.object(main.httpx, "stream", side_effect=contexts) as stream:
            with patch.object(main.time, "sleep") as sleep:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    result = main.ask_ai("新问题")
        return result, stream, sleep, output.getvalue()

    def complete_lines(self):
        return event("完整回答") + event(reason="stop") + ["data: [DONE]", ""]

    def test_valid_response_without_optional_space_and_with_null_content(self):
        lines = event(prefix="data:") + event("完整回答", prefix="data:")
        lines += event(reason="stop", prefix="data:") + ["data:[DONE]", ""]
        context = response_context(lines)
        result, stream, sleep, _ = self.call([context])
        self.assertEqual(result, "完整回答")
        self.assertEqual(main.messages, self.history + [
            {"role": "user", "content": "新问题"},
            {"role": "assistant", "content": "完整回答"},
        ])
        self.assertEqual(stream.call_args.kwargs["json"]["model"], "test-model")
        self.assertEqual(stream.call_args.kwargs["json"]["thinking"], {"type": "disabled"})
        context.__exit__.assert_called_once()
        sleep.assert_not_called()

    def test_multiline_sse_event_bom_comment_and_unknown_fields(self):
        lines = [
            "\ufeff: keep-alive", "event: message", "id: 1",
            'data: {"choices":',
            'data:[{"delta":{"content":"完整回答"},"finish_reason":"stop"}]}',
            "", "data: [DONE]", "",
        ]
        result, _, _, _ = self.call([response_context(lines)])
        self.assertEqual(result, "完整回答")

    def test_parser_preserves_spaces_and_discards_unterminated_event(self):
        self.assertEqual(list(main.iter_sse_data([
            "data:  开头有空格", "data: 第二行 ", "", "data: 未结束"
        ])), [" 开头有空格\n第二行 "])

    def test_done_alone_or_missing_stop_or_truncated_answer_rolls_back(self):
        for reason in (None, "length", "tool_calls", "content_filter", "insufficient_system_resource"):
            with self.subTest(reason=reason):
                lines = event("部分回答", reason) + ["data: [DONE]", ""]
                result, stream, sleep, _ = self.call([response_context(lines)])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)
                stream.assert_called_once()
                sleep.assert_not_called()
        result, _, _, _ = self.call([response_context(["data: [DONE]", ""])])
        self.assertIsNone(result)
        self.assertEqual(main.messages, self.history)

    def test_missing_done_or_unterminated_done_rolls_back(self):
        for ending in ([], ["data: [DONE]"]):
            with self.subTest(ending=ending):
                result, _, _, _ = self.call([response_context(event("回答", "stop") + ending)])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)

    def test_empty_or_whitespace_answer_rolls_back(self):
        for content in (None, "", " \n\t"):
            with self.subTest(content=content):
                lines = event(content, "stop") + ["data: [DONE]", ""]
                result, _, _, _ = self.call([response_context(lines)])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)

    def test_invalid_json_and_nested_types_roll_back(self):
        payloads = [
            "not json", "null", "[]", '{}', '{"choices":[]}',
            '{"choices":[null]}', '{"choices":[{"delta":null}]}',
            '{"choices":[{"delta":{"content":42}}]}',
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                lines = ["data: " + payload, "", "data: [DONE]", ""]
                result, _, _, _ = self.call([response_context(lines)])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)

    def test_partial_output_then_read_timeout_rolls_back_without_retry(self):
        def interrupted():
            yield from event("部分回答")
            raise httpx.ReadTimeout("模拟读取超时")

        result, stream, sleep, output = self.call([response_context(interrupted())])
        self.assertIsNone(result)
        self.assertIn("部分回答", output)
        self.assertIn("本轮对话未保存", output)
        self.assertEqual(main.messages, self.history)
        stream.assert_called_once()
        sleep.assert_not_called()

    def test_non_retryable_http_and_transport_errors_roll_back(self):
        contexts = [response_context(status=status) for status in (302, 401, 500)]
        contexts += [httpx.ConnectTimeout("超时"), httpx.ConnectError("连接失败")]
        for context in contexts:
            with self.subTest(context=context):
                result, stream, sleep, _ = self.call([context])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)
                stream.assert_called_once()
                sleep.assert_not_called()

    def test_429_retries_twice_and_does_not_duplicate_question(self):
        result, stream, sleep, _ = self.call([
            response_context(status=429), response_context(status=429),
            response_context(self.complete_lines()),
        ])
        self.assertEqual(result, "完整回答")
        self.assertEqual(stream.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 4])
        self.assertEqual(sum(m["content"] == "新问题" for m in main.messages), 1)

    def test_429_exhaustion_restores_history_after_trimming(self):
        self.history = self.history * 5
        main.messages = self.history.copy()
        result, stream, sleep, _ = self.call([response_context(status=429) for _ in range(3)])
        self.assertIsNone(result)
        self.assertEqual(main.messages, self.history)
        self.assertEqual(stream.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_retry_after_seconds_or_invalid_value(self):
        for value, expected in (("0003", 3), ("0", 0), ("30", 30), ("invalid", 2), ("٣", 2)):
            with self.subTest(value=value):
                main.messages = self.history.copy()
                result, _, sleep, _ = self.call([
                    response_context(status=429, headers={"Retry-After": value}),
                    response_context(self.complete_lines()),
                ])
                self.assertEqual(result, "完整回答")
                sleep.assert_called_once_with(expected)

    def test_retry_after_over_limit_including_very_long_digits_stops(self):
        for value in ("31", "9" * 5000):
            with self.subTest(length=len(value)):
                result, stream, sleep, _ = self.call([
                    response_context(status=429, headers={"Retry-After": value})
                ])
                self.assertIsNone(result)
                self.assertEqual(main.messages, self.history)
                stream.assert_called_once()
                sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
