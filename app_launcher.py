"""桌面启动器：后台启动 Streamlit，用原生窗口（pywebview）嵌入，无需打开系统浏览器。"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
from pathlib import Path

# 设为 1 或 true 则仍用系统浏览器打开（调试用）
_USE_EXTERNAL_BROWSER = os.environ.get("PAPER_USE_BROWSER", "").lower() in ("1", "true", "yes")


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def _find_free_port(start: int = 8501, end: int = 8599) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("未找到可用端口（8501-8599）")


def _wait_port_open(port: int, timeout: float = 90.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _run_streamlit(web_app: Path, port: int) -> None:
    """在子线程中运行 Streamlit（主线程留给桌面窗口）。"""
    sys.argv = [
        "streamlit",
        "run",
        str(web_app),
        "--server.headless=true",
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    try:
        from streamlit.web.cli import main as streamlit_main

        streamlit_main()
    except Exception as e:
        print("Streamlit 启动失败：", e)


def _open_external_browser_when_ready(url: str, port: int) -> None:
    import webbrowser

    if _wait_port_open(port):
        webbrowser.open(url)
    else:
        print("警告：服务未在预期时间内启动，请手动在浏览器打开：", url)


def _open_native_window(url: str) -> None:
    """Windows 下使用 Edge WebView2 内嵌页面，外观类似独立应用。"""
    import webview

    webview.create_window(
        "中文论文生成器",
        url,
        width=1280,
        height=840,
        resizable=True,
        text_select=True,
    )
    webview.start(debug=False)


def main() -> int:
    base_dir = _get_base_dir()
    web_app = base_dir / "web_app.py"
    if not web_app.exists():
        print(f"未找到 web_app.py: {web_app}")
        input("按回车退出...")
        return 1

    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    # 后台线程启动 Streamlit
    st_thread = threading.Thread(
        target=_run_streamlit,
        args=(web_app, port),
        daemon=True,
        name="streamlit-server",
    )
    st_thread.start()

    print("正在启动中文论文生成器...")
    if not _wait_port_open(port):
        print("错误：本地服务未启动成功，请查看上方报错。")
        input("按回车退出...")
        return 1

    try:
        if _USE_EXTERNAL_BROWSER:
            print("已启用外部浏览器模式：", url)
            import webbrowser

            webbrowser.open(url)
            # 阻塞直到用户 Ctrl+C（简单起见）
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                return 0
        else:
            print("正在打开应用窗口（非系统浏览器标签页）…")
            _open_native_window(url)
    except ImportError as e:
        print("无法加载桌面窗口组件（pywebview）：", e)
        print("将改用系统浏览器打开：", url)
        import webbrowser

        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return 0
    except Exception as e:
        print("打开窗口失败：", e)
        print("请手动在浏览器访问：", url)
        input("按回车退出...")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
