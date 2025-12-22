# src/pdf_deskew_ui/main.py

import logging
import sys

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from . import __version__
from .ui import MainWindow


def attach_to_console():
    """在 Windows 上尝试附加到父进程的控制台，以便输出信息"""
    if sys.platform == "win32":
        import ctypes

        # ATTACH_PARENT_PROCESS = -1
        # Use getattr to avoid Mypy errors on non-Windows platforms
        kernel32 = getattr(ctypes, "WinDLL")("kernel32", use_last_error=True)  # noqa: B009
        if kernel32.AttachConsole(-1):
            # 重新定向标准流到附加的控制台
            # 使用 'CONOUT$' 和 'CONIN$' 是 Windows 特有的特殊文件
            try:
                sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
                sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
                sys.stdin = open("CONIN$", encoding="utf-8")
                return True
            except Exception:
                pass
    return False


def main():
    # 尝试附加到控制台并打印信息
    has_console = attach_to_console()
    if has_console:
        # 在输出前加一个换行，避免与 PowerShell 的提示符混在一起
        print(f"\n\nPDF Deskew Tool v{__version__}")
        print("Initializing GUI... (This may take a few seconds)")
        # 打印一个提示，告诉用户程序正在运行，因为控制台会立即返回提示符
        print("Note: The terminal prompt has returned, but the app is loading.\n")
        sys.stdout.flush()

    # 配置日志
    logging.basicConfig(
        filename="pdf_deskew.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.info(f"Application started (v{__version__})")

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")  # 可选的主题样式
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
