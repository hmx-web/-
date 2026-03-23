"""Ollama 本地模型提供商"""
import httpx
from .base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """Ollama 本地部署"""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, messages: list[dict], **kwargs) -> LLMResponse:
        with httpx.Client(timeout=300) as client:
            resp = client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False}
            )
            resp.raise_for_status()
            data = resp.json()
        content = data.get("message", {}).get("content", "")
        return LLMResponse(content=content, model=self.model)

    def get_model_name(self) -> str:
        return self.model
