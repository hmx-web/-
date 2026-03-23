"""Anthropic Claude 提供商"""
from .base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude"""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def complete(self, messages: list[dict], **kwargs) -> LLMResponse:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        # 转换 messages 格式：anthropic 需要 system 单独传
        system = ""
        anthropic_messages = []
        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                system = content
            else:
                anthropic_messages.append({"role": role, "content": content})
        resp = client.messages.create(
            model=self.model,
            system=system or None,
            messages=anthropic_messages,
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        text = resp.content[0].text if resp.content else ""
        usage = None
        if resp.usage:
            usage = {"prompt_tokens": resp.usage.input_tokens, "completion_tokens": resp.usage.output_tokens}
        return LLMResponse(content=text, model=self.model, usage=usage)

    def get_model_name(self) -> str:
        return self.model
