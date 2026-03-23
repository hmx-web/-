"""智能体基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from ..llm_providers import BaseLLMProvider


@dataclass
class PaperContext:
    """论文上下文 - 在智能体间传递"""
    topic: str
    keywords: list[str] = field(default_factory=list)
    abstract: str = ""
    introduction: str = ""
    content: str = ""
    conclusion: str = ""
    references: list[str] = field(default_factory=list)
    extra_instructions: str = ""


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, llm: BaseLLMProvider, name: str = ""):
        self.llm = llm
        self.name = name or self.__class__.__name__

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass

    @abstractmethod
    def get_user_prompt(self, ctx: PaperContext) -> str:
        """根据上下文生成用户提示"""
        pass

    def run(self, ctx: PaperContext) -> str:
        """执行智能体任务，返回生成内容"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_user_prompt(ctx)}
        ]
        resp = self.llm.complete(messages, max_tokens=4096)
        return resp.content.strip()
