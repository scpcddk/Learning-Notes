"""从环境读取聊天接口配置，封装请求、响应校验和客户端生命周期。"""

import json
import os
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


class ResponseFormatError(RuntimeError):
    """HTTP 成功，但返回结构不符合本程序的约定。"""


@dataclass(frozen=True)
class Settings:
    url: str
    model: str
    # 实例包含认证密钥，展示配置时只输出所需的非敏感字段。
    key: str

    @classmethod
    def from_env(cls):
        url = os.environ.get("LLM_API_URL", "").strip()
        model = os.environ.get("LLM_MODEL", "").strip()
        # 通用变量优先，兼容此前的 DeepSeek 环境变量。
        key = os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        if not url or not model or not key:
            raise RuntimeError("请配置 LLM_API_URL、LLM_MODEL 和 API Key")
        parsed = urlparse(url)
        local_hosts = {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and parsed.hostname in local_hosts
        ):
            raise RuntimeError("远程 Endpoint 请使用 HTTPS；本地服务允许 HTTP")
        return cls(url, model, key)


# 普通聊天和 Web 示例复用这层结构检查，调用方再按各自需求读取 message。
def first_choice(payload):
    if not isinstance(payload, dict):
        raise ResponseFormatError("响应顶层必须是对象")
    if payload.get("error"):
        raise ResponseFormatError("响应包含 API error，请检查脱敏后的错误记录")
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ResponseFormatError("缺少有效的 choices[0]")
    return choices[0]


class ChatClient:
    def __init__(self, settings):
        self.settings = settings
        # HTTPX 区分连接、读取、写入、连接池超时，不是整个任务总时长。
        self.http = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=10.0, write=20.0, pool=10.0),
            headers={"Authorization": f"Bearer {settings.key}"},
        )

    def body(self, messages, **options):
        # 固定配置与调用选项分开，避免业务代码覆盖模型和消息。
        reserved = {"model", "messages"}
        if reserved.intersection(options):
            raise ValueError("model/messages 由客户端统一设置")
        return {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": 1024,
            **options,
        }

    # 返回首个候选和可选的用量数据，方便调用方处理文本或工具请求。
    def complete(self, messages, **options):
        if options.get("stream"):
            raise ValueError("complete() 只处理普通响应")
        # json= 接收 Python 对象，由 HTTPX 完成 JSON 编码。
        response = self.http.post(self.settings.url, json=self.body(messages, **options))
        response.raise_for_status()  # HTTP 错误与 JSON/结构错误分开。
        try:
            payload = response.json()
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ResponseFormatError("响应不是可解码的 JSON") from exc
        choice = first_choice(payload)
        if not isinstance(choice.get("message"), dict):
            raise ResponseFormatError("缺少 message 对象")
        return choice, payload.get("usage")

    # 只取完整的普通文本，可直接作为展示内容或保存为一轮回答。
    def text(self, messages, **options):
        choice, _ = self.complete(messages, **options)
        # 拿到 content 不代表回答完整，还要检查业务结束原因。
        reason = choice.get("finish_reason")
        text = choice["message"].get("content")
        if reason != "stop" or not isinstance(text, str) or not text.strip():
            raise ResponseFormatError(f"未收到完整文本回答，finish_reason={reason!r}")
        return text

    def close(self):
        self.http.close()

    def __enter__(self):
        return self

    # 离开 with 时关闭连接池，异常继续交给调用方处理。
    def __exit__(self, exc_type, exc, tb):
        self.close()


if __name__ == "__main__":
    with ChatClient(Settings.from_env()) as client:
        answer = client.text([{"role": "user", "content": "用一句话解释 API。"}])
        print(answer)
