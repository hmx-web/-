"""结论/总结智能体"""
from .base import BaseAgent, PaperContext


class ConclusionAgent(BaseAgent):
    """负责生成论文总结/结论部分"""

    def get_system_prompt(self) -> str:
        return """你是一位资深中文学术论文写作专家。你的任务是撰写论文总结与结论部分。

总结/结论应包含：
1. 主要研究结论回顾
2. 理论或实践贡献
3. 研究局限与不足
4. 未来研究方向或建议

要求：
- 与摘要、正文呼应
- 篇幅约300-500字
- 语言精炼，避免重复
- 学术规范"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        parts = [
            f"请为以下主题撰写论文总结与结论：\n\n主题：{ctx.topic}\n",
            f"\n摘要：\n{ctx.abstract}\n" if ctx.abstract else "",
            f"\n引言：\n{ctx.introduction}\n" if ctx.introduction else "",
            f"\n正文要点：\n{ctx.content[:2000]}...\n" if len(ctx.content) > 2000 else f"\n正文：\n{ctx.content}\n" if ctx.content else "",
        ]
        if ctx.extra_instructions:
            parts.append(f"\n附加要求：{ctx.extra_instructions}")
        return "".join(parts)
