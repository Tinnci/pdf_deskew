# src/pdf_deskew_ui/main.py

import logging
import sys

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from .ui import MainWindow


def main():
    # 配置日志
    logging.basicConfig(
        filename="pdf_deskew.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.info("Application started")

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")  # 可选的主题样式
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
