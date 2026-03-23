"""LLM 提供商基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    usage: Optional[dict] = None


class BaseLLMProvider(ABC):
    """LLM 提供商基类"""

    @abstractmethod
    def complete(self, messages: list[dict], **kwargs) -> LLMResponse:
        """完成对话补全"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
