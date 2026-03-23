"""LLM 提供商抽象层 - 支持多种大模型接入"""
from .base import BaseLLMProvider, LLMResponse
from .factory import get_provider

__all__ = ["BaseLLMProvider", "LLMResponse", "get_provider"]
