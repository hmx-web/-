"""纠正/审查智能体：检查主题偏差与字数，并给出重生成建议。"""
import json
import re
from .base import BaseAgent, PaperContext


class CorrectorAgent(BaseAgent):
    """审查各章节质量并输出结构化建议。"""

    def __init__(self, llm, name: str = "纠正审查", min_lengths: dict | None = None):
        super().__init__(llm, name)
        self.min_lengths = min_lengths or {
            "abstract": 180,
            "introduction": 450,
            "content": 1800,
            "conclusion": 280,
        }

    def get_system_prompt(self) -> str:
        return """你是一位中文学术论文质量审稿专家。你的任务是：
1) 判断各部分是否偏离主题中心思想
2) 判断各部分字数是否达标
3) 给出是否需要重生成的章节建议

你必须只输出 JSON，不要输出额外文本，格式如下：
{
  "center_idea": "一句话概括论文中心思想",
  "sections": {
    "abstract": {"off_topic": false, "too_short": false, "reason": "简短原因"},
    "introduction": {"off_topic": false, "too_short": false, "reason": "简短原因"},
    "content": {"off_topic": false, "too_short": false, "reason": "简短原因"},
    "conclusion": {"off_topic": false, "too_short": false, "reason": "简短原因"}
  },
  "regenerate": ["content"],
  "global_suggestion": "整体修改建议"
}

规则：
- 若章节与主题偏差明显，off_topic=true
- 若章节字数不足最低要求，too_short=true
- regenerate 包含所有 off_topic=true 或 too_short=true 的章节
- 若均合格，regenerate 返回空数组 []
"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        return (
            f"主题：{ctx.topic}\n"
            f"关键词：{', '.join(ctx.keywords) if ctx.keywords else '无'}\n\n"
            f"最低字数要求：\n"
            f"- abstract >= {self.min_lengths['abstract']}\n"
            f"- introduction >= {self.min_lengths['introduction']}\n"
            f"- content >= {self.min_lengths['content']}\n"
            f"- conclusion >= {self.min_lengths['conclusion']}\n\n"
            f"【摘要】\n{ctx.abstract}\n\n"
            f"【引言】\n{ctx.introduction}\n\n"
            f"【正文】\n{ctx.content}\n\n"
            f"【结论】\n{ctx.conclusion}\n"
        )

    def review(self, ctx: PaperContext) -> dict:
        """返回结构化审查结果。"""
        raw = self.run(ctx)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # 模型偶尔会夹带文本，这里做兜底提取
            match = re.search(r"\{[\s\S]*\}", raw)
            if not match:
                return {
                    "center_idea": "",
                    "sections": {},
                    "regenerate": [],
                    "global_suggestion": "审查结果解析失败，跳过自动重生成。",
                }
            data = json.loads(match.group(0))
        if "regenerate" not in data or not isinstance(data.get("regenerate"), list):
            data["regenerate"] = []
        return data
