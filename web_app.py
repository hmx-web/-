"""在线论文生成与编辑页面（Streamlit）。"""
import json
import tempfile
from pathlib import Path

import streamlit as st
import yaml

from src.agents.base import PaperContext
from src.exporters import export_docx_bytes, export_pdf_bytes
from src.orchestrator import PaperOrchestrator


st.set_page_config(page_title="中文论文生成器", layout="wide")
st.title("中文论文多智能体生成器")
st.caption("应用模式：用户填写/上传 API Key 即可使用（密钥仅保存在当前会话内存，不落盘）")

if "ctx" not in st.session_state:
    st.session_state.ctx = None
if "images" not in st.session_state:
    st.session_state.images = []


def _build_runtime_config(
    provider: str,
    model: str,
    api_keys_map: dict,
    max_regen_rounds: int,
    min_content_len: int,
):
    agents = {}
    for name in ["abstract", "introduction", "content", "conclusion", "references", "corrector"]:
        agents[name] = {"provider": provider, "name": model}
    return {
        "model": {"provider": provider, "name": model},
        "agents": agents,
        "api_keys": api_keys_map,
        "quality": {
            "min_abstract": 180,
            "min_introduction": 450,
            "min_content": min_content_len,
            "min_conclusion": 280,
            "max_regen_rounds": max_regen_rounds,
        },
    }


def _parse_uploaded_keys(uploaded_file) -> dict:
    if uploaded_file is None:
        return {}
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    suffix = Path(uploaded_file.name).suffix.lower()
    parsed = {}
    if suffix in (".yml", ".yaml"):
        data = yaml.safe_load(text) or {}
        parsed = data.get("api_keys", data) if isinstance(data, dict) else {}
    elif suffix == ".json":
        data = json.loads(text or "{}")
        parsed = data.get("api_keys", data) if isinstance(data, dict) else {}
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            parsed[k.strip()] = v.strip()
    return {str(k).lower().replace("_api_key", ""): str(v) for k, v in parsed.items() if v}


with st.sidebar:
    st.header("应用设置")
    provider = st.selectbox(
        "模型提供商",
        ["openai", "anthropic", "deepseek", "qwen", "zhipu", "ollama"],
        index=0,
    )
    default_model_map = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "deepseek": "deepseek-chat",
        "qwen": "qwen-plus",
        "zhipu": "glm-4",
        "ollama": "qwen2.5:7b",
    }
    model_name = st.text_input("模型名称", value=default_model_map[provider])
    max_regen_rounds = st.slider("纠正重生成轮数", min_value=0, max_value=3, value=1)
    min_content_len = st.slider("正文最小字数", min_value=1200, max_value=5000, value=1800, step=100)

    st.subheader("API Key（可手填）")
    openai_key = st.text_input("OPENAI API Key", type="password")
    anthropic_key = st.text_input("ANTHROPIC API Key", type="password")
    deepseek_key = st.text_input("DEEPSEEK API Key", type="password")
    qwen_key = st.text_input("DASHSCOPE API Key (Qwen)", type="password")
    zhipu_key = st.text_input("ZHIPU API Key", type="password")

    st.subheader("或上传密钥文件")
    uploaded_keys = st.file_uploader("支持 .env / .txt / .yaml / .json", type=["env", "txt", "yaml", "yml", "json"])
    parsed_keys = _parse_uploaded_keys(uploaded_keys)

    manual_keys = {
        "openai": openai_key,
        "anthropic": anthropic_key,
        "deepseek": deepseek_key,
        "qwen": qwen_key,
        "zhipu": zhipu_key,
    }
    runtime_keys = {**parsed_keys, **{k: v for k, v in manual_keys.items() if v}}
    st.caption("说明：手动输入优先级高于上传文件；密钥仅用于当前会话。")

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("生成参数")
    topic = st.text_input("论文题目", value="人工智能在教育中的应用研究")
    keywords_text = st.text_input("关键词（用逗号分隔）", value="人工智能,教育技术,个性化学习")
    extra = st.text_area("额外要求", value="语言正式，正文不少于2000字。")
    use_local_config = st.checkbox("使用本地 config.yaml（否则使用侧边栏应用设置）", value=False)
    config_path = st.text_input("配置文件路径", value="config.yaml", disabled=not use_local_config)

    if st.button("开始生成", type="primary", use_container_width=True):
        kws = [x.strip() for x in keywords_text.split(",") if x.strip()]
        progress = st.progress(0.0)
        status = st.empty()

        steps = {"摘要": 0.15, "引言": 0.35, "正文": 0.6, "总结": 0.75, "参考文献": 0.85, "纠正审查": 1.0}

        def cb(name: str, state: str, _result: str = ""):
            if state == "running":
                status.info(f"正在处理：{name}")
            else:
                status.success(f"完成：{name}")
                for key, p in steps.items():
                    if key in name:
                        progress.progress(p)
                        break

        with st.spinner("多智能体生成中，请稍候..."):
            if use_local_config:
                orchestrator = PaperOrchestrator(config_path=config_path)
            else:
                runtime_config = _build_runtime_config(
                    provider=provider,
                    model=model_name,
                    api_keys_map=runtime_keys,
                    max_regen_rounds=max_regen_rounds,
                    min_content_len=min_content_len,
                )
                orchestrator = PaperOrchestrator(config=runtime_config)
            st.session_state.ctx = orchestrator.generate(
                topic=topic,
                keywords=kws,
                extra_instructions=extra,
                callback=cb,
            )
            progress.progress(1.0)
            status.success("全部完成，可在线编辑并导出。")

    st.divider()
    st.subheader("插图上传")
    uploaded = st.file_uploader(
        "上传插图（可多选，导出到 Word/PDF）",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    if uploaded:
        img_paths = []
        for f in uploaded:
            suffix = Path(f.name).suffix or ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(f.read())
            tmp.flush()
            tmp.close()
            img_paths.append(tmp.name)
        st.session_state.images = img_paths
        st.success(f"已加载 {len(img_paths)} 张插图。")

with right:
    st.subheader("在线编辑")
    ctx = st.session_state.ctx
    if not ctx:
        st.info("先在左侧填写参数并点击“开始生成”。")
    else:
        title = st.text_input("标题", value=ctx.topic)
        abstract = st.text_area("摘要", value=ctx.abstract, height=180)
        introduction = st.text_area("引言", value=ctx.introduction, height=220)
        content = st.text_area("正文", value=ctx.content, height=420)
        conclusion = st.text_area("总结与结论", value=ctx.conclusion, height=180)
        refs = st.text_area("参考文献（每行一条）", value="\n".join(ctx.references), height=180)

        edited_ctx = PaperContext(
            topic=title,
            keywords=ctx.keywords,
            abstract=abstract,
            introduction=introduction,
            content=content,
            conclusion=conclusion,
            references=[x.strip() for x in refs.split("\n") if x.strip()],
            extra_instructions=ctx.extra_instructions,
        )
        st.session_state.ctx = edited_ctx

        docx_bytes = export_docx_bytes(edited_ctx, st.session_state.images)
        pdf_bytes = export_pdf_bytes(edited_ctx, st.session_state.images)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "下载 Word (.docx)",
                data=docx_bytes,
                file_name=f"{edited_ctx.topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "下载 PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"{edited_ctx.topic}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
