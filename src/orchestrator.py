"""论文生成流程编排器"""
from dataclasses import dataclass
from typing import Optional
from .agents import (
    AbstractAgent,
    IntroductionAgent,
    ContentAgent,
    ConclusionAgent,
    ReferencesAgent,
    CorrectorAgent,
)
from .agents.base import PaperContext
from .llm_providers import get_provider
from .llm_providers.base import BaseLLMProvider


@dataclass
class AgentConfig:
    """单个智能体的模型配置"""
    provider: str
    name: str


def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    import os
    import yaml
    path = config_path
    if not os.path.exists(path):
        path = "config.example.yaml"
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # 解析 ${ENV} 形式的 API Key
    api_keys = data.get("api_keys") or {}
    resolved = {}
    for k, v in api_keys.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            resolved[k] = os.getenv(v[2:-1], "")
        else:
            resolved[k] = v
    data["api_keys"] = resolved
    return data


def build_agent_config(agent_name: str, default_provider: str, default_model: str, config: dict) -> AgentConfig:
    """从配置构建智能体模型配置"""
    agents_cfg = config.get("agents") or {}
    agent_cfg = agents_cfg.get(agent_name) or {}
    return AgentConfig(
        provider=agent_cfg.get("provider") or default_provider,
        name=agent_cfg.get("name") or default_model
    )


class PaperOrchestrator:
    """论文生成流程编排"""

    def __init__(self, config: Optional[dict] = None, config_path: str = "config.yaml"):
        self.config = config or load_config(config_path)
        self.api_keys = self.config.get("api_keys") or {}
        model_cfg = self.config.get("model") or {}
        self.default_provider = model_cfg.get("provider") or "openai"
        self.default_model = model_cfg.get("name") or "gpt-4o"
        quality_cfg = self.config.get("quality") or {}
        self.max_regen_rounds = int(quality_cfg.get("max_regen_rounds", 1))
        self.min_lengths = {
            "abstract": int(quality_cfg.get("min_abstract", 180)),
            "introduction": int(quality_cfg.get("min_introduction", 450)),
            "content": int(quality_cfg.get("min_content", 1800)),
            "conclusion": int(quality_cfg.get("min_conclusion", 280)),
        }

    def _get_llm(self, agent_name: str) -> BaseLLMProvider:
        """为指定智能体获取 LLM"""
        ac = build_agent_config(agent_name, self.default_provider, self.default_model, self.config)
        return get_provider(
            provider=ac.provider,
            model=ac.name,
            api_keys_map=self.api_keys
        )

    def _create_agents(self) -> tuple:
        """创建所有智能体"""
        llm_abstract = self._get_llm("abstract")
        llm_intro = self._get_llm("introduction")
        llm_content = self._get_llm("content")
        llm_conclusion = self._get_llm("conclusion")
        llm_refs = self._get_llm("references")
        llm_corrector = self._get_llm("corrector")
        return (
            AbstractAgent(llm_abstract, "摘要"),
            IntroductionAgent(llm_intro, "引言"),
            ContentAgent(llm_content, "正文"),
            ConclusionAgent(llm_conclusion, "总结"),
            ReferencesAgent(llm_refs, "参考文献"),
            CorrectorAgent(llm_corrector, "纠正审查", min_lengths=self.min_lengths),
        )

    @staticmethod
    def _char_count(text: str) -> int:
        return len((text or "").strip())

    def _fallback_length_check(self, ctx: PaperContext) -> list[str]:
        """当纠正智能体失败时，至少做字数兜底检查。"""
        regenerate = []
        mapping = {
            "abstract": ctx.abstract,
            "introduction": ctx.introduction,
            "content": ctx.content,
            "conclusion": ctx.conclusion,
        }
        for sec, text in mapping.items():
            if self._char_count(text) < self.min_lengths[sec]:
                regenerate.append(sec)
        return regenerate

    def _regenerate_section(self, section: str, agents: tuple, ctx: PaperContext, report) -> None:
        alias = {
            "abstract": ("摘要", 0, "abstract"),
            "introduction": ("引言", 1, "introduction"),
            "content": ("正文", 2, "content"),
            "conclusion": ("总结", 3, "conclusion"),
        }
        if section not in alias:
            return
        cn_name, idx, attr = alias[section]
        report(f"{cn_name}-重生成", "running")
        setattr(ctx, attr, agents[idx].run(ctx))
        report(f"{cn_name}-重生成", "done", getattr(ctx, attr))

    def generate(
        self,
        topic: str,
        keywords: Optional[list[str]] = None,
        extra_instructions: str = "",
        callback=None
    ) -> PaperContext:
        """
        生成完整论文
        :param topic: 论文主题
        :param keywords: 关键词列表
        :param extra_instructions: 额外要求
        :param callback: 进度回调 (agent_name, status, result) -> None
        """
        ctx = PaperContext(
            topic=topic,
            keywords=keywords or [],
            extra_instructions=extra_instructions
        )
        agents = self._create_agents()

        def report(name: str, status: str, result: str = ""):
            if callback:
                callback(name, status, result)

        # 1. 摘要
        report("摘要", "running")
        ctx.abstract = agents[0].run(ctx)
        report("摘要", "done", ctx.abstract)

        # 2. 引言
        report("引言", "running")
        ctx.introduction = agents[1].run(ctx)
        report("引言", "done", ctx.introduction)

        # 3. 正文
        report("正文", "running")
        ctx.content = agents[2].run(ctx)
        report("正文", "done", ctx.content)

        # 4. 总结
        report("总结", "running")
        ctx.conclusion = agents[3].run(ctx)
        report("总结", "done", ctx.conclusion)

        # 5. 参考文献
        report("参考文献", "running")
        refs_text = agents[4].run(ctx)
        ctx.references = [line.strip() for line in refs_text.split("\n") if line.strip()]
        report("参考文献", "done", refs_text)

        # 6. 纠正审查 + 有条件重生成
        for round_idx in range(self.max_regen_rounds):
            report("纠正审查", "running", f"第 {round_idx + 1} 轮")
            review = agents[5].review(ctx)
            regenerate_list = review.get("regenerate", [])
            if not regenerate_list:
                regenerate_list = self._fallback_length_check(ctx)
            report("纠正审查", "done", str(review))
            if not regenerate_list:
                break
            for sec in regenerate_list:
                self._regenerate_section(sec, agents, ctx, report)

        # 重生成后再次更新参考文献，保证编号与正文一致
        report("参考文献-复核", "running")
        refs_text = agents[4].run(ctx)
        ctx.references = [line.strip() for line in refs_text.split("\n") if line.strip()]
        report("参考文献-复核", "done", refs_text)

        return ctx
