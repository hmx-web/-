#!/usr/bin/env python3
"""中文论文多智能体生成器 - 主入口"""
import argparse
import os
import sys

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="中文论文多智能体生成器")
    parser.add_argument("topic", nargs="?", help="论文主题")
    parser.add_argument("-k", "--keywords", nargs="+", help="关键词，空格分隔")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("-e", "--extra", default="", help="额外写作要求")
    parser.add_argument("--no-save", action="store_true", help="不保存到文件，仅打印")
    args = parser.parse_args()

    topic = args.topic
    if not topic:
        topic = input("请输入论文主题：").strip()
    if not topic:
        print("错误：未指定主题")
        sys.exit(1)

    def progress(agent_name: str, status: str, result: str = ""):
        if status == "running":
            print(f"[进行中] {agent_name}...")
        else:
            print(f"[完成] {agent_name}")

    from src.orchestrator import PaperOrchestrator
    from src.paper_formatter import format_paper

    print("正在初始化...")
    orch = PaperOrchestrator(config_path=args.config)
    print("开始生成论文...\n")

    ctx = orch.generate(
        topic=topic,
        keywords=args.keywords,
        extra_instructions=args.extra,
        callback=progress
    )

    paper_text = format_paper(ctx, title=topic)
    print("\n" + "=" * 60)
    print("论文生成完成！")
    print("=" * 60)

    if args.no_save:
        print(paper_text)
    else:
        out_path = args.output or f"论文_{topic[:20].replace(' ', '_')}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(paper_text)
        print(f"已保存到：{out_path}")


if __name__ == "__main__":
    main()
