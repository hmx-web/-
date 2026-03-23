"""OpenAI / 兼容 OpenAI API 的提供商 (DeepSeek, Qwen 等)"""
from typing import Optional
from .base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 及兼容 API"""

    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"

    def complete(self, messages: list[dict], **kwargs) -> LLMResponse:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        choice = resp.choices[0]
        usage = None
        if resp.usage:
            usage = {"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens}
        return LLMResponse(
            content=choice.message.content or "",
            model=resp.model,
            usage=usage
        )

    def get_model_name(self) -> str:
        return self.model
