# src/pdf_deskew_ui/main.py

import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from .ui import MainWindow

def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')  # 选择一个 pyqt-material 主题
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
