"""正文内容智能体"""
from .base import BaseAgent, PaperContext


class ContentAgent(BaseAgent):
    """负责生成论文正文主体内容"""

    def get_system_prompt(self) -> str:
        return """你是一位资深中文学术论文写作专家。你的任务是撰写论文正文主体部分。

正文应包含：
1. 理论分析或方法阐述
2. 实证研究/案例分析（如适用）
3. 数据与结果讨论
4. 分章节、分小节组织，层次清晰

要求：
- 论证充分，有理有据
- 篇幅约2000-4000字
- 使用小标题划分章节（如：一、二、三 或 1、2、3）
- 可适当使用【引用】占位，格式如 [1]、[2]
- 学术规范，逻辑严密"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        parts = [
            f"请为以下主题撰写论文正文主体：\n\n主题：{ctx.topic}\n",
            f"\n摘要：\n{ctx.abstract}\n" if ctx.abstract else "",
            f"\n引言：\n{ctx.introduction}\n" if ctx.introduction else "",
        ]
        if ctx.keywords:
            parts.append(f"\n关键词：{', '.join(ctx.keywords)}")
        if ctx.extra_instructions:
            parts.append(f"\n附加要求：{ctx.extra_instructions}")
        return "".join(parts)
