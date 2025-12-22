import json
import logging
import os
import tempfile
from pathlib import Path

import cv2
import fitz
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

from deskew_tool.config import Language
from deskew_tool.deskew_pdf import process_single_page
from pdf_deskew_ui.widgets import ConfigWidget, FileSelectionWidget, StatusWidget
from pdf_deskew_ui.worker import WorkerThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = Language.CHINESE
        self.translations = self.load_translations()
        self.init_ui()

    def load_translations(self) -> dict:
        try:
            trans_path = Path(__file__).parent / "translations.json"
            with open(trans_path, encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            logging.error(f"Failed to load translations: {e}")
            return {
                "en_US": {"window_title": "PDF Deskew Tool"},
                "zh_CN": {"window_title": "PDF 校准工具"},
            }

    def get_translation(self) -> dict[str, str]:
        """获取当前语言的翻译字典"""
        lang = self.current_language.value
        return self.translations.get(lang, self.translations[Language.CHINESE.value])

    def init_ui(self):
        """初始化用户界面 - 使用组件化布局"""
        self.setAcceptDrops(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. 文件选择组件
        self.file_widget = FileSelectionWidget(self.get_translation())
        self.file_widget.input_browse.clicked.connect(self.browse_input)
        self.file_widget.output_browse.clicked.connect(self.browse_output)
        main_layout.addWidget(self.file_widget)

        # 2. 配置组件
        self.config_widget = ConfigWidget(self.get_translation())
        main_layout.addWidget(self.config_widget)

        # 3. 状态组件
        self.status_widget = StatusWidget(self.get_translation())
        main_layout.addWidget(self.status_widget)

        # 4. 控制按钮
        control_layout = QHBoxLayout()

        # 语言切换
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        self.language_combo.setCurrentIndex(
            0 if self.current_language == Language.CHINESE else 1
        )
        self.language_combo.currentIndexChanged.connect(self.change_language)
        control_layout.addWidget(self.language_label)
        control_layout.addWidget(self.language_combo)

        # 主题切换
        self.theme_label = QLabel()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        control_layout.addWidget(self.theme_label)
        control_layout.addWidget(self.theme_combo)

        control_layout.addStretch()

        self.help_button = QPushButton()
        self.help_button.clicked.connect(self.show_help)
        control_layout.addWidget(self.help_button)

        self.run_button = QPushButton()
        self.run_button.clicked.connect(self.start_processing)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_processing)

        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.cancel_button)
        main_layout.addLayout(control_layout)

        # 5. 预览控制
        preview_control_layout = QHBoxLayout()
        self.preview_page_label = QLabel()
        self.preview_page_spin = QSpinBox()
        self.preview_page_spin.setMinimum(1)
        self.preview_button = QPushButton()
        self.preview_button.clicked.connect(self.preview_current_page)

        preview_control_layout.addWidget(self.preview_page_label)
        preview_control_layout.addWidget(self.preview_page_spin)
        preview_control_layout.addWidget(self.preview_button)
        preview_control_layout.addStretch()
        main_layout.addLayout(preview_control_layout)

        # 6. 预览区域
        preview_layout = QHBoxLayout()
        self.before_label = QLabel()
        self.after_label = QLabel()
        self.before_label.setMinimumSize(200, 200)
        self.after_label.setMinimumSize(200, 200)
        self.before_label.setStyleSheet("border: 1px solid #555;")
        self.after_label.setStyleSheet("border: 1px solid #555;")
        self.before_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.after_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.before_label)
        preview_layout.addWidget(self.after_label)
        main_layout.addLayout(preview_layout)

        self.init_ui_texts()
        self.resize(900, 800)

    def init_ui_texts(self):
        """根据当前语言设置所有UI文本"""
        t = self.get_translation()
        self.setWindowTitle(t["window_title"])

        self.file_widget.update_translations(t)
        self.config_widget.update_translations(t)
        self.status_widget.update_translations(t)

        self.language_label.setText(t["language"])
        self.theme_label.setText(t.get("theme", "Theme:"))
        self.run_button.setText(t["start_deskew"])
        self.cancel_button.setText(t.get("cancel", "Cancel"))
        self.help_button.setText(t.get("help", "Help"))
        self.preview_page_label.setText(t.get("page", "Page:"))
        self.preview_button.setText(t.get("preview", "Preview Page"))

    def change_language(self, index):
        """切换语言"""
        self.current_language = Language.CHINESE if index == 0 else Language.ENGLISH
        self.init_ui_texts()

    def change_theme(self, index):
        """切换主题"""
        themes = ["light_blue.xml", "dark_teal.xml", "blue.xml"]
        selected_theme = themes[index] if index < len(themes) else "light_blue.xml"
        apply_stylesheet(QApplication.instance(), theme=selected_theme)

    def show_help(self):
        """显示帮助信息"""
        t = self.get_translation()
        QMessageBox.information(self, t["help_info_title"], t["help_info_text"])

    def preview_current_page(self):
        """预览当前选定页面的处理效果"""
        input_pdf = self.file_widget.input_line.text().strip()
        if not input_pdf or not os.path.isfile(input_pdf):
            t = self.get_translation()
            QMessageBox.warning(self, t["input_error_title"], t["input_error_text"])
            return

        page_num = self.preview_page_spin.value() - 1
        config = self.config_widget.get_config()

        self.preview_button.setEnabled(False)
        self.preview_button.setText("Processing...")
        QApplication.processEvents()

        try:
            temp_dir = tempfile.mkdtemp(prefix="pdf_preview_")

            # 获取处理前的图像
            doc = fitz.open(input_pdf)
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=config.dpi)
            img_before = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )
            if img_before.ndim == 2:
                img_before = cv2.cvtColor(img_before, cv2.COLOR_GRAY2BGR)

            before_path = os.path.join(temp_dir, "before.png")
            cv2.imwrite(before_path, img_before)
            doc.close()

            # 获取处理后的图像
            _, after_path = process_single_page(page_num, input_pdf, config, temp_dir)

            if after_path:
                self.display_before_after(before_path, after_path)

            # 注意：display_before_after 会删除文件，但不会删除文件夹
            # 我们在这里不删除文件夹，因为 display_before_after 可能还在使用它
            # （虽然目前是同步的）。实际生产中应该有更好的清理机制。
        except Exception as e:
            logging.error(f"Preview failed: {e}")
            QMessageBox.warning(self, "Preview Error", f"Failed to preview page: {e}")
        finally:
            self.preview_button.setEnabled(True)
            self.init_ui_texts()  # 恢复按钮文本

    def browse_input(self):
        """浏览选择输入PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getOpenFileName(
            self, t["input_pdf"], "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.file_widget.input_line.setText(file_path)
            self.browse_input_path(file_path)

    def browse_input_path(self, file_path):
        input_dir = os.path.dirname(file_path)
        input_basename = os.path.splitext(os.path.basename(file_path))[0]
        suffix = (
            "_deskewed.pdf"
            if self.current_language == Language.ENGLISH
            else "_校准.pdf"
        )
        self.file_widget.output_line.setText(
            os.path.join(input_dir, f"{input_basename}{suffix}")
        )
        self.update_page_count(file_path)

    def update_page_count(self, file_path):
        try:
            doc = fitz.open(file_path)
            self.preview_page_spin.setMaximum(len(doc))
            doc.close()
        except Exception as e:
            logging.error(f"Failed to get page count: {e}")

    def browse_output(self):
        """浏览选择输出PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getSaveFileName(
            self, t["output_pdf"], "", "PDF Files (*.pdf)"
        )
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            self.file_widget.output_line.setText(file_path)

    def start_processing(self):
        """开始PDF校准处理"""
        t = self.get_translation()
        input_pdf = self.file_widget.input_line.text().strip()
        output_pdf = self.file_widget.output_line.text().strip()

        if not input_pdf or not os.path.isfile(input_pdf):
            QMessageBox.warning(self, t["input_error_title"], t["input_error_text"])
            return

        if not output_pdf:
            QMessageBox.warning(self, t["output_error_title"], t["output_error_text"])
            return

        config = self.config_widget.get_config()

        # 禁用界面
        self.set_ui_enabled(False)
        self.status_widget.progress_bar.setValue(0)
        self.status_widget.log_text.clear()

        # 启动工作线程
        self.worker = WorkerThread(input_pdf, output_pdf, config)
        self.worker.progress.connect(self.status_widget.progress_bar.setValue)
        self.worker.progress.connect(
            lambda v: self.status_widget.progress_label.setText(f"{v}%")
        )
        self.worker.status.connect(self.status_widget.status_text.setText)
        self.worker.status.connect(self.status_widget.log_text.append)
        self.worker.before_after.connect(self.display_before_after)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()

        self.cancel_button.setEnabled(True)

    def cancel_processing(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.status_widget.log_text.append("Cancelled by user.")
            self.set_ui_enabled(True)

    def processing_finished(self, output_pdf):
        t = self.get_translation()
        self.status_widget.progress_bar.setValue(100)
        QMessageBox.information(
            self,
            t["processing_complete_title"],
            f"{t['processing_complete_text']}\n{output_pdf}",
        )
        self.set_ui_enabled(True)

    def processing_error(self, error_message):
        t = self.get_translation()
        QMessageBox.critical(
            self,
            t["processing_error_title"],
            f"{t['processing_error_text']}\n{error_message}",
        )
        self.set_ui_enabled(True)

    def display_before_after(self, before_path, after_path):
        for label, path in [
            (self.before_label, before_path),
            (self.after_label, after_path),
        ]:
            pix = QPixmap(path)
            label.setPixmap(
                pix.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            try:
                os.remove(path)
            except Exception:
                pass

    def set_ui_enabled(self, enabled):
        self.file_widget.setEnabled(enabled)
        self.config_widget.setEnabled(enabled)
        self.run_button.setEnabled(enabled)
        self.cancel_button.setEnabled(not enabled)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self.file_widget.input_line.setText(path)
                self.browse_input_path(path)
                break
