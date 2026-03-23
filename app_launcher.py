"""桌面启动器：在同进程内启动 Streamlit，并自动打开系统浏览器（打包 EXE 推荐方式）。"""
from __future__ import annotations

import multiprocessing
import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path


def _exe_dir() -> Path:
    """EXE 所在目录（用于写日志；与 _MEIPASS 不同）。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _log_error(msg: str) -> None:
    try:
        log_path = _exe_dir() / "launcher_error.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


def _get_base_dir() -> Path:
    """打包资源目录（web_app.py、src 等）。"""
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


def _open_browser_when_ready(url: str, port: int) -> None:
    if _wait_port_open(port):
        webbrowser.open(url)
    else:
        print("警告：服务未在预期时间内启动，请手动在浏览器打开：", url)


def main() -> int:
    base_dir = _get_base_dir()
    web_app = base_dir / "web_app.py"
    if not web_app.exists():
        print(f"未找到 web_app.py: {web_app}")
        print(f"资源目录应为: {base_dir}")
        _log_error(f"缺少 web_app.py, base_dir={base_dir}")
        return 1

    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    # 打包 EXE 时务必关闭文件监视器，否则会再起子进程/监视器导致秒退
    sys.argv = [
        "streamlit",
        "run",
        str(web_app),
        "--server.headless=true",
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
        "--server.fileWatcherType=none",
        "--server.runOnSave=false",
    ]

    threading.Thread(
        target=_open_browser_when_ready,
        args=(url, port),
        daemon=True,
    ).start()

    print("正在启动中文论文生成器...")
    print("将自动打开系统浏览器，若未打开请访问：", url)
    print("关闭本窗口将停止服务。")

    try:
        from streamlit.web.cli import main as streamlit_main

        streamlit_main()
        return 0
    except SystemExit as e:
        code = e.code
        if isinstance(code, int):
            if code != 0:
                print("Streamlit 异常退出，代码：", code)
                _log_error(f"SystemExit code={code}")
            return code
        if code is None:
            return 0
        print("Streamlit 退出：", code)
        _log_error(f"SystemExit code={code!r}")
        return 1
    except Exception as e:
        print("启动失败：", e)
        traceback.print_exc()
        _log_error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    # Windows 下打包 EXE 时，避免 multiprocessing spawn 子进程异常退出
    multiprocessing.freeze_support()

    try:
        raise SystemExit(main())
    except SystemExit as e:
        code = e.code
        icode = code if isinstance(code, int) else 1
        if icode != 0:
            _log_error(f"顶层 SystemExit code={code!r}")
            print("\n启动失败（退出码 %s）。请查看 EXE 同目录下的 launcher_error.log" % icode)
            input("按回车退出...")
        raise SystemExit(icode) from None
    except BaseException:
        traceback.print_exc()
        _log_error(traceback.format_exc())
        print("\n若窗口即将关闭，请查看同目录下的 launcher_error.log")
        input("按回车退出...")
        raise SystemExit(1) from None
