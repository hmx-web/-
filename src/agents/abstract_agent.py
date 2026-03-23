"""摘要智能体"""
from .base import BaseAgent, PaperContext


class AbstractAgent(BaseAgent):
    """负责生成论文摘要"""

    def get_system_prompt(self) -> str:
        return """你是一位资深中文学术论文写作专家。你的任务是撰写高质量的中文学术论文摘要。

摘要应包含：
1. 研究背景与目的（1-2句）
2. 研究方法（1-2句）
3. 主要结果与发现（2-3句）
4. 结论与意义（1句）

要求：
- 语言严谨、学术规范
- 篇幅约200-300字
- 使用第三人称
- 不出现"本文"、"笔者"等第一人称表述"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        parts = [f"请为以下主题撰写论文摘要：\n\n主题：{ctx.topic}"]
        if ctx.keywords:
            parts.append(f"\n关键词：{', '.join(ctx.keywords)}")
        if ctx.extra_instructions:
            parts.append(f"\n附加要求：{ctx.extra_instructions}")
        return "".join(parts)
