"""引言智能体"""
from .base import BaseAgent, PaperContext


class IntroductionAgent(BaseAgent):
    """负责生成论文引言"""

    def get_system_prompt(self) -> str:
        return """你是一位资深中文学术论文写作专家。你的任务是撰写论文引言部分。

引言应包含：
1. 研究背景与问题提出
2. 国内外研究现状（简要综述）
3. 研究目的与意义
4. 论文结构安排

要求：
- 逻辑清晰，层层递进
- 篇幅约500-800字
- 学术规范，引用得当
- 自然过渡到正文"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        parts = [
            f"请为以下主题撰写论文引言：\n\n主题：{ctx.topic}\n",
            f"\n摘要（供参考）：\n{ctx.abstract}\n" if ctx.abstract else "",
        ]
        if ctx.keywords:
            parts.append(f"\n关键词：{', '.join(ctx.keywords)}")
        if ctx.extra_instructions:
            parts.append(f"\n附加要求：{ctx.extra_instructions}")
        return "".join(parts)
