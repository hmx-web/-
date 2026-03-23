"""引用文献汇总智能体"""
import re
from .base import BaseAgent, PaperContext


class ReferencesAgent(BaseAgent):
    """负责汇总并格式化引用文献"""

    def get_system_prompt(self) -> str:
        return """你是一位资深中文学术论文写作专家。你的任务是根据正文中的引用占位，生成规范的参考文献列表。

要求：
1. 使用国标 GB/T 7714 格式（或常用学术期刊格式）
2. 中英文文献分开，中文在前、英文在后
3. 按在正文中出现顺序编号 [1]、[2]、[3]...
4. 若正文中有 [1]、[2] 等占位，请生成对应数量的合理文献条目
5. 文献信息需真实可信（作者、年份、题目、出版信息等格式正确）
6. 每条文献独立一行"""

    def get_user_prompt(self, ctx: PaperContext) -> str:
        parts = [
            f"请根据以下论文内容，生成规范的参考文献列表：\n\n主题：{ctx.topic}\n",
        ]
        if ctx.content:
            parts.append(f"\n正文（含引用占位）：\n{ctx.content}\n")
        if ctx.introduction:
            parts.append(f"\n引言（供参考）：\n{ctx.introduction[:500]}...\n")
        # 估算引用数量：简单按 [数字] 占位
        combined = (ctx.content or "") + (ctx.introduction or "")
        refs = re.findall(r'\[(\d+)\]', combined)
        if refs:
            max_ref = max(int(x) for x in refs)
            parts.append(f"\n正文中引用编号至 [{max_ref}]，请生成 {max_ref} 条参考文献。")
        else:
            parts.append("\n若正文无明确引用占位，请根据主题生成 5-8 条相关的典型参考文献。")
        if ctx.extra_instructions:
            parts.append(f"\n附加要求：{ctx.extra_instructions}")
        return "".join(parts)
