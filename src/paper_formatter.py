"""论文格式化输出"""
from .agents.base import PaperContext


def format_paper(ctx: PaperContext, title: str = "") -> str:
    """将 PaperContext 格式化为完整论文文本"""
    title = title or ctx.topic
    lines = [
        "=" * 60,
        title,
        "=" * 60,
        "",
        "【摘要】",
        ctx.abstract,
        "",
        "关键词：" + "；".join(ctx.keywords) if ctx.keywords else "",
        "",
        "-" * 60,
        "",
        "【引言】",
        ctx.introduction,
        "",
        "-" * 60,
        "",
        "【正文】",
        ctx.content,
        "",
        "-" * 60,
        "",
        "【总结与结论】",
        ctx.conclusion,
        "",
        "-" * 60,
        "",
        "【参考文献】",
        "",
    ]
    for r in ctx.references:
        lines.append(r)
    lines.append("")
    return "\n".join(lines)
