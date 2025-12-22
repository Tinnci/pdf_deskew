import json
import logging
import os
import tempfile
from pathlib import Path
from typing import cast

import cv2
import fitz
import numpy as np
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QWheelEvent
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

from deskew_tool.config import Language
from deskew_tool.deskew_pdf import process_single_page
from pdf_deskew_ui.styles import StyleManager
from pdf_deskew_ui.widgets import ConfigWidget, FileSelectionWidget, StatusWidget
from pdf_deskew_ui.worker import WorkerThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language: Language = Language.CHINESE
        self.translations: dict[str, dict[str, str]] = self.load_translations()

        # 预览状态
        self.zoom_factor = 1.0
        self.before_pixmap: QPixmap | None = None
        self.after_pixmap: QPixmap | None = None

        self.init_ui()

    def load_translations(self) -> dict[str, dict[str, str]]:
        try:
            trans_path = Path(__file__).parent / "translations.json"
            with open(trans_path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return cast(dict[str, dict[str, str]], data)
                return {}
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
        """初始化用户界面 - 使用侧边栏布局"""
        self.setAcceptDrops(True)
        self.setWindowTitle(self.get_translation()["window_title"])

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 使用 QSplitter 实现可调节的侧边栏
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- 左侧面板 (侧边栏) ---
        self.sidebar = QScrollArea()
        self.sidebar.setWidgetResizable(True)
        self.sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar.setMinimumWidth(0)  # 允许折叠到 0
        self.sidebar.setMaximumWidth(1000)  # 允许较大宽度

        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(20)

        # 1. 文件选择组件
        self.file_widget = FileSelectionWidget(self.get_translation())
        self.file_widget.input_browse.clicked.connect(self.browse_input)
        self.file_widget.output_browse.clicked.connect(self.browse_output)
        sidebar_layout.addWidget(self.file_widget)

        # 2. 配置组件
        self.config_widget = ConfigWidget(self.get_translation())
        sidebar_layout.addWidget(self.config_widget)

        # 3. 状态组件
        self.status_widget = StatusWidget(self.get_translation())
        sidebar_layout.addWidget(self.status_widget)

        # 4. 控制按钮与设置
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # 语言与主题行
        settings_row = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        lang_idx = 0 if self.current_language == Language.CHINESE else 1
        self.language_combo.setCurrentIndex(lang_idx)
        self.language_combo.currentIndexChanged.connect(self.change_language)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        settings_row.addWidget(QLabel("Lang:"))
        settings_row.addWidget(self.language_combo)
        settings_row.addWidget(QLabel("Theme:"))
        settings_row.addWidget(self.theme_combo)
        control_layout.addLayout(settings_row)

        # 操作按钮
        actions_row = QHBoxLayout()
        self.run_button = QPushButton()
        self.run_button.clicked.connect(self.start_processing)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_processing)

        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(30, 30)
        self.help_button.clicked.connect(self.show_help)

        actions_row.addWidget(self.run_button, 3)
        actions_row.addWidget(self.cancel_button, 1)
        actions_row.addWidget(self.help_button, 0)
        control_layout.addLayout(actions_row)

        sidebar_layout.addWidget(control_frame)
        sidebar_layout.addStretch()

        self.sidebar.setWidget(sidebar_content)
        self.splitter.addWidget(self.sidebar)

        # --- 右侧面板 (预览区域) ---
        self.preview_panel = QWidget()
        preview_layout = QVBoxLayout(self.preview_panel)

        # 预览控制
        preview_header = QHBoxLayout()
        preview_header.setContentsMargins(10, 10, 10, 10)

        self.toggle_sidebar_button = QPushButton("◀")
        self.toggle_sidebar_button.setFixedSize(30, 30)
        self.toggle_sidebar_button.setCheckable(True)
        self.toggle_sidebar_button.clicked.connect(self.toggle_sidebar)

        self.preview_page_label = QLabel()
        self.preview_page_spin = QSpinBox()
        self.preview_page_spin.setMinimum(1)
        self.preview_button = QPushButton()
        self.preview_button.clicked.connect(self.preview_current_page)

        # 缩放控制
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setFixedSize(30, 30)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedSize(30, 30)
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_reset_button = QPushButton("Reset")
        self.zoom_reset_button.clicked.connect(self.zoom_reset)

        preview_header.addWidget(self.toggle_sidebar_button)
        preview_header.addSpacing(10)
        preview_header.addWidget(self.preview_page_label)
        preview_header.addWidget(self.preview_page_spin)
        preview_header.addWidget(self.preview_button)
        preview_header.addSpacing(20)
        preview_header.addWidget(self.zoom_out_button)
        preview_header.addWidget(self.zoom_label)
        preview_header.addWidget(self.zoom_in_button)
        preview_header.addWidget(self.zoom_reset_button)
        preview_header.addStretch()
        preview_layout.addLayout(preview_header)

        # 预览滚动区域
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setFrameShape(QFrame.Shape.NoFrame)

        preview_container = QWidget()
        preview_images_layout = QHBoxLayout(preview_container)
        preview_images_layout.setSpacing(20)

        self.before_label = QLabel("Before")
        self.after_label = QLabel("After")
        for label in [self.before_label, self.after_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(400, 500)
            preview_images_layout.addWidget(label)

        self.preview_scroll.setWidget(preview_container)
        preview_layout.addWidget(self.preview_scroll)

        self.splitter.addWidget(self.preview_panel)

        # 设置初始比例
        self.splitter.setSizes([400, 800])
        main_layout.addWidget(self.splitter)

        self.update_ui_styles()
        self.init_ui_texts()
        self.resize(1200, 800)

    def update_ui_styles(self):
        """更新全局 UI 样式"""
        theme = StyleManager.get_theme()
        self.setStyleSheet(StyleManager.get_main_style())
        self.sidebar.setStyleSheet(StyleManager.get_sidebar_style())
        self.preview_panel.setStyleSheet(StyleManager.get_preview_panel_style())

        for label in [self.before_label, self.after_label]:
            label.setStyleSheet(StyleManager.get_preview_label_style())

        self.run_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.primary};
                color: {theme.surface};
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme.primary};
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background-color: {theme.border};
            }}
        """)

        # 通知子组件更新样式
        self.file_widget.update_style()
        self.config_widget.update_style()
        self.status_widget.update_style()

    def init_ui_texts(self):
        """根据当前语言设置所有UI文本"""
        t = self.get_translation()
        self.setWindowTitle(t["window_title"])

        self.file_widget.update_translations(t)
        self.config_widget.update_translations(t)
        self.status_widget.update_translations(t)

        self.run_button.setText(t["start_deskew"])
        self.cancel_button.setText(t.get("cancel", "Cancel"))
        self.preview_page_label.setText(t.get("page", "Page:"))
        self.preview_button.setText(t.get("preview", "Preview Page"))
        self.zoom_reset_button.setText(t.get("zoom_reset", "Reset Zoom"))
        self.before_label.setText("Before")
        self.after_label.setText("After")

    def change_language(self, index):
        """切换语言"""
        self.current_language = Language.CHINESE if index == 0 else Language.ENGLISH
        self.init_ui_texts()

    def change_theme(self, index):
        """切换主题"""
        theme_names = ["light", "dark", "blue"]
        selected_name = theme_names[index] if index < len(theme_names) else "light"

        # 更新 StyleManager
        StyleManager.set_theme(selected_name)

        # 应用 qt-material 主题
        themes = ["light_blue.xml", "dark_teal.xml", "blue.xml"]
        selected_theme = themes[index] if index < len(themes) else "light_blue.xml"
        apply_stylesheet(QApplication.instance(), theme=selected_theme)

        # 更新自定义样式
        self.update_ui_styles()

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
        self.before_pixmap = QPixmap(before_path)
        self.after_pixmap = QPixmap(after_path)

        # 自动重置缩放以适应窗口
        self.zoom_factor = 1.0
        self.update_preview_images()

        # 添加淡入动画
        for label in [self.before_label, self.after_label]:
            opacity_effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(opacity_effect)

            anim = QPropertyAnimation(opacity_effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InQuad)
            anim.start()
            # 保持引用防止被垃圾回收
            if not hasattr(self, "_animations"):
                self._animations = []
            self._animations.append(anim)

        try:
            os.remove(before_path)
            os.remove(after_path)
        except Exception:
            pass

    def update_preview_images(self):
        """根据当前缩放比例更新预览图"""
        if not self.before_pixmap or not self.after_pixmap:
            return

        self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")

        for label, pixmap in [
            (self.before_label, self.before_pixmap),
            (self.after_label, self.after_pixmap),
        ]:
            if pixmap.isNull():
                continue

            scaled_pixmap = pixmap.scaled(
                pixmap.size() * self.zoom_factor,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(scaled_pixmap)
            # 调整 label 大小以适应缩放后的图片，这样 ScrollArea 才能工作
            label.setFixedSize(scaled_pixmap.size())

    def zoom_in(self):
        self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        self.update_preview_images()

    def zoom_out(self):
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.1)
        self.update_preview_images()

    def zoom_reset(self):
        self.zoom_factor = 1.0
        self.update_preview_images()

    def toggle_sidebar(self, checked):
        """切换侧边栏显示/隐藏，带动画效果"""
        start_width = self.sidebar.width()
        end_width = 0 if checked else 400

        self.toggle_sidebar_button.setText("▶" if checked else "◀")

        self.sidebar_animation = QPropertyAnimation(self, b"sidebar_width")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if not checked:
            self.sidebar.show()

        self.sidebar_animation.finished.connect(
            lambda: self.on_sidebar_animation_finished(checked)
        )
        self.sidebar_animation.start()

    def on_sidebar_animation_finished(self, checked):
        if checked:
            self.sidebar.hide()
        else:
            # 动画结束后，恢复弹性宽度，允许用户手动调整
            self.sidebar.setMinimumWidth(0)
            self.sidebar.setMaximumWidth(1000)
            self.sidebar.setFixedWidth(16777215)  # QWIDGETSIZE_MAX

    @pyqtProperty(int)
    def sidebar_width(self):
        return self.sidebar.width()

    @sidebar_width.setter
    def sidebar_width(self, width):
        self.sidebar.setFixedWidth(width)
        # 强制刷新布局
        self.splitter.setSizes([width, self.width() - width])

    def set_ui_enabled(self, enabled):
        self.file_widget.setEnabled(enabled)
        self.config_widget.setEnabled(enabled)
        self.run_button.setEnabled(enabled)
        self.cancel_button.setEnabled(not enabled)

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event:
            mime_data = event.mimeData()
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None):
        if event:
            mime_data = event.mimeData()
            if mime_data:
                for url in mime_data.urls():
                    path = url.toLocalFile()
                    if path.lower().endswith(".pdf"):
                        self.file_widget.input_line.setText(path)
                        self.browse_input_path(path)
                        break

    def wheelEvent(self, event: QWheelEvent | None):
        """处理鼠标滚轮缩放 (Ctrl + Wheel)"""
        if event and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event) if event else None
