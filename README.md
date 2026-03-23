# 中文论文多智能体生成器

基于多智能体架构的中文学术论文生成器，支持接入多种大模型（OpenAI、Claude、Ollama、DeepSeek、通义千问、智谱等）。

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      PaperOrchestrator                            │
│  (流程编排：按顺序调用各智能体，传递上下文)                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ├──► AbstractAgent      (摘要)
         ├──► IntroductionAgent  (引言)
         ├──► ContentAgent       (正文)
         ├──► ConclusionAgent    (总结/结论)
        ├──► ReferencesAgent    (参考文献)
        └──► CorrectorAgent     (纠正审查/重生成)
                    │
                    ▼
         ┌──────────────────────┐
         │   LLM Provider 层     │  ← 可配置不同模型
         │ OpenAI / Claude /    │
         │ Ollama / DeepSeek…   │
         └──────────────────────┘
```

## 安装

```bash
cd f:\new
pip install -r requirements.txt
```

## 配置

1. 复制 `config.example.yaml` 为 `config.yaml`
2. 在 `config.yaml` 中配置模型与 API Key，或在 `.env` 中设置环境变量：

```env
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
DEEPSEEK_API_KEY=xxx
DASHSCOPE_API_KEY=xxx   # 通义千问
ZHIPU_API_KEY=xxx       # 智谱
```

3. 可为不同智能体指定不同模型（如摘要用轻量模型、正文用大模型）

## 使用

```bash
# 交互式输入主题
python main.py

# 直接指定主题
python main.py "人工智能在医疗诊断中的应用"

# 带关键词
python main.py "大语言模型的 Few-shot 学习" -k 大语言模型 少样本学习 提示工程

# 指定输出文件
python main.py "区块链技术综述" -o 论文_区块链.txt

# 额外要求
python main.py "深度学习综述" -e "偏重计算机视觉方向，引用近三年文献"
```

## 在线编辑 + Word/PDF 导出

```bash
streamlit run web_app.py
```

或开发环境直接运行：

```bash
python -m streamlit run web_app.py
```

打包后的 EXE：双击 `dist\ChinesePaperGenerator\ChinesePaperGenerator.exe`，会自动打开**系统默认浏览器**访问本地页面。

功能：
- 多智能体生成后可在网页中逐段在线修改
- 支持上传插图并导出到 Word/PDF
- 一键下载 `.docx` 与 `.pdf`
- 支持在页面侧边栏直接填写 API Key，或上传 `.env/.txt/.yaml/.json` 密钥文件即用
- API Key 仅保存在当前会话内存，不写入本地配置文件

## 打包为 EXE 安装包（Windows）

### 1) 先打包 EXE

```bash
build_exe.bat
```

产物：
- `dist/ChinesePaperGenerator/ChinesePaperGenerator.exe`

### 2) 再生成安装程序

先安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)，然后执行：

```bash
build_installer.bat
```

安装包产物：
- `dist_installer/ChinesePaperGeneratorSetup.exe`

说明：
- 安装后双击“中文论文生成器”即可启动本地 Web 界面
- 用户在界面侧边栏上传/填写 API Key 即可使用
- 若只需免安装版本，可直接分发 `dist/ChinesePaperGenerator/` 整个目录

### EXE 打开后浏览器提示「拒绝连接 / ERR_CONNECTION_REFUSED」

- **原因**：旧版启动器用子进程再启动一次 EXE，无法加载 `streamlit`，服务未起来。
- **处理**：请重新执行 `build_exe.bat` 用最新代码打包；启动器已改为**同进程**启动 Streamlit。
- **仍失败时**：查看黑色控制台窗口是否有报错；确认防火墙未拦截本机 `127.0.0.1`（一般本机访问不需要放行）。

### 打包运行报错 `ModuleNotFoundError: No module named 'httpx'`

- **原因**：`httpx` 由 `OllamaProvider` 等模块使用，PyInstaller 有时不会自动打进包。
- **处理**：使用最新 `build_exe.bat`（已包含 `--collect-all httpx`），删除 `build/`、`dist/` 后重新打包。

### EXE 双击后窗口一闪就关

- **常见原因**：Streamlit 在打包环境下启用**文件监视**会拉起子进程，容易导致进程立刻退出。
- **处理**：请用最新 `app_launcher.py` 重新执行 `build_exe.bat`（已加 `--server.fileWatcherType=none` 与 `multiprocessing.freeze_support()`）。
- **排查**：在项目根目录双击 `debug_run_exe.bat`，或在命令行运行 exe，便于看到报错；同目录会生成 `launcher_error.log`。

## 支持的模型

| Provider   | 说明          | 环境变量 / 配置   |
|-----------|---------------|-------------------|
| openai    | GPT 系列      | OPENAI_API_KEY    |
| anthropic | Claude        | ANTHROPIC_API_KEY |
| ollama    | 本地 Ollama   | 无需 Key          |
| deepseek  | DeepSeek      | DEEPSEEK_API_KEY  |
| qwen      | 通义千问      | DASHSCOPE_API_KEY |
| zhipu     | 智谱 GLM      | ZHIPU_API_KEY     |

## 项目结构

```
f:\new\
├── main.py              # CLI 主入口
├── web_app.py           # 在线编辑页面（Streamlit）
├── config.yaml          # 配置文件
├── config.example.yaml
├── requirements.txt
├── src/
│   ├── orchestrator.py  # 流程编排
│   ├── paper_formatter.py
│   ├── exporters.py     # Word/PDF 导出
│   ├── agents/          # 各智能体
│   │   ├── abstract_agent.py
│   │   ├── introduction_agent.py
│   │   ├── content_agent.py
│   │   ├── conclusion_agent.py
│   │   ├── references_agent.py
│   │   └── corrector_agent.py
│   └── llm_providers/   # 多模型接入
│       ├── base.py
│       ├── factory.py
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       └── ollama_provider.py
```

## 纠正智能体说明

- `CorrectorAgent` 会根据题目提炼中心思想，审查摘要/引言/正文/结论是否偏题
- 同时按 `quality` 配置检查最小字数（默认正文至少 1800 字）
- 若发现偏题或字数不足，会触发对应章节自动重生成
- 重生成后会再次刷新参考文献，避免编号不一致
