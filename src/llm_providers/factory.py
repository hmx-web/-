"""LLM 提供商工厂 - 根据配置创建对应提供商"""
import os
from typing import Optional
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider

# 各服务商的 base_url（兼容 OpenAI API 的）
DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
}


def _get_api_key(provider: str, api_key: Optional[str], api_keys_map: Optional[dict]) -> str:
    """从参数、api_keys_map 或环境变量获取 API Key"""
    if api_key:
        return api_key
    if api_keys_map and provider in api_keys_map:
        v = api_keys_map[provider]
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_name = v[2:-1]
            return os.getenv(env_name, "")
        return str(v) if v else ""
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "qwen": "DASHSCOPE_API_KEY",
        "zhipu": "ZHIPU_API_KEY",
    }
    return os.getenv(env_map.get(provider, ""), "") or os.getenv("OPENAI_API_KEY", "")


def get_provider(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    api_keys_map: Optional[dict] = None
) -> BaseLLMProvider:
    """根据 provider 名称创建 LLM 提供商"""
    provider = provider.lower().strip()
    key = _get_api_key(provider, api_key, api_keys_map)

    if provider == "openai":
        return OpenAIProvider(model=model, api_key=key, base_url=base_url)

    if provider == "anthropic":
        return AnthropicProvider(model=model, api_key=key)

    if provider == "ollama":
        return OllamaProvider(model=model, base_url=base_url or "http://localhost:11434")

    # 兼容 OpenAI API 的提供商
    if provider in ("deepseek", "qwen", "zhipu"):
        url = base_url or DEFAULT_BASE_URLS.get(provider)
        return OpenAIProvider(model=model, api_key=key, base_url=url)

    raise ValueError(f"不支持的 provider: {provider}")
