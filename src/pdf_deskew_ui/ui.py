# src/pdf_deskew_ui/ui.py

import sys
import os
import json
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Tuple

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox, QSpinBox,
    QComboBox, QProgressBar, QColorDialog, QApplication
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent, QIcon

from .worker import WorkerThread
from deskew_tool.deskew_pdf import deskew_pdf  # Ensure correct import path
from qt_material import apply_stylesheet

# 定义语言枚举
class Language(Enum):
    ENGLISH = 'en_US'
    CHINESE = 'zh_CN'

# 数据类存储背景颜色
@dataclass
class BackgroundColor:
    name: str
    rgb: Tuple[int, int, int]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = Language.CHINESE  # 默认语言为中文

        self.background_colors = {
            "White": BackgroundColor("White", (255, 255, 255)),
            "Black": BackgroundColor("Black", (0, 0, 0)),
            "Custom": BackgroundColor("Custom", (255, 255, 255))
        }

        self.selected_color = self.background_colors["White"].rgb  # 默认白色

        self.translations = self.load_translations()
        self.init_ui()

    def load_translations(self) -> Dict[str, Dict[str, str]]:
        """加载翻译字典，可以扩展为从外部JSON文件加载"""
        return {
            'en_US': {
                "window_title": "PDF Deskew Tool",
                "input_pdf": "Input PDF File:",
                "browse": "Browse",
                "output_pdf": "Output PDF File:",
                "use_defaults": "Use Recommended Settings (DPI=300, Background=White)",
                "render_dpi": "Render DPI:",
                "background_color": "Background Color:",
                "white": "White",
                "black": "Black",
                "custom": "Custom",
                "language": "Language:",
                "help": "Help",
                "exit": "Exit",
                "start_deskew": "Start Deskew",
                "help_info_title": "Help Information",
                "help_info_text": (
                    "<h2>Help Information</h2>"
                    "<p>This tool is used to deskew scanned images in PDF files.</p>"
                    "<p>You can select files, set DPI, and choose background color.</p>"
                    "<p><b>Steps to Use:</b></p>"
                    "<ol>"
                    "<li>Click the 'Browse' button to select the input PDF file.</li>"
                    "<li>Click the 'Browse' button to choose the output PDF file path. By default, the output file will be named 'input_filename_deskewed.pdf'.</li>"
                    "<li>Select whether to use recommended settings:</li>"
                    "<ul>"
                    "<li>If 'Use Recommended Settings' is checked, DPI=300 and background color will be white.</li>"
                    "<li>If unchecked, you can customize DPI and background color.</li>"
                    "</ul>"
                    "<li>Click the 'Start Deskew' button to begin processing.</li>"
                    "<li>During processing, you can see the progress bar indicating the progress.</li>"
                    "</ol>"
                ),
                "confirm_settings_title": "Confirm Settings",
                "confirm_settings_text": "Please confirm if these settings are correct:",
                "input_path": "Input PDF File Path:",
                "output_path": "Output PDF File Path:",
                "dpi": "Render DPI:",
                "bg_color": "Background Color:",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "input_error_title": "Input Error",
                "input_error_text": "Please enter a valid input PDF file path.",
                "output_error_title": "Output Error",
                "output_error_text": "Please enter a valid output PDF file path.",
                "processing_complete_title": "Completed",
                "processing_complete_text": "The deskewed PDF has been saved to:",
                "processing_error_title": "Error",
                "processing_error_text": "An error occurred during processing:",
                "browse_tooltip": "Click to browse and select a PDF file",
                "start_deskew_tooltip": "Click to start the deskew process",
                "theme": "Theme:",
                "theme_tooltip": "Select a theme for the application"
            },
            'zh_CN': {
                "window_title": "PDF 校准工具",
                "input_pdf": "输入 PDF 文件:",
                "browse": "浏览",
                "output_pdf": "输出 PDF 文件:",
                "use_defaults": "使用推荐设置 (DPI=300, 背景色=白色)",
                "render_dpi": "渲染 DPI:",
                "background_color": "背景颜色:",
                "white": "白色",
                "black": "黑色",
                "custom": "自定义",
                "language": "语言:",
                "help": "帮助",
                "exit": "退出",
                "start_deskew": "开始校准",
                "help_info_title": "帮助信息",
                "help_info_text": (
                    "<h2>帮助信息</h2>"
                    "<p>此工具用于校准 PDF 文件中的扫描图像。</p>"
                    "<p>您可以选择文件、设置 DPI 以及背景颜色。</p>"
                    "<p><b>使用步骤:</b></p>"
                    "<ol>"
                    "<li>点击“浏览”按钮选择输入的 PDF 文件。</li>"
                    "<li>点击“浏览”按钮选择输出的 PDF 文件路径。默认情况下，输出文件将命名为“输入文件名_校准.pdf”。</li>"
                    "<li>选择是否使用推荐设置：</li>"
                    "<ul>"
                    "<li>如果勾选“使用推荐设置”，将使用 DPI=300 和白色背景。</li>"
                    "<li>如果取消勾选，可以自定义 DPI 和背景颜色。</li>"
                    "</ul>"
                    "<li>点击“开始校准”按钮开始处理。</li>"
                    "<li>处理过程中，您可以看到进度条显示进度。</li>"
                    "</ol>"
                ),
                "confirm_settings_title": "确认设置",
                "confirm_settings_text": "请确认这些设置是否正确：",
                "input_path": "输入 PDF 文件路径:",
                "output_path": "输出 PDF 文件路径:",
                "dpi": "渲染 DPI:",
                "bg_color": "背景颜色:",
                "confirm": "确认",
                "cancel": "取消",
                "input_error_title": "输入错误",
                "input_error_text": "请输入有效的输入 PDF 文件路径。",
                "output_error_title": "输出错误",
                "output_error_text": "请输入有效的输出 PDF 文件路径。",
                "processing_complete_title": "完成",
                "processing_complete_text": "校准后的 PDF 已保存到:",
                "processing_error_title": "错误",
                "processing_error_text": "处理过程中出现错误:",
                "browse_tooltip": "点击浏览并选择一个PDF文件",
                "start_deskew_tooltip": "点击开始校准过程",
                "theme": "主题:",
                "theme_tooltip": "选择应用程序的主题"
            }
        }

    def init_ui_texts(self):
        """根据当前语言设置所有UI文本"""
        lang = self.current_language.value
        t = self.translations.get(lang, self.translations[Language.CHINESE.value])

        self.setWindowTitle(t["window_title"])

        # 更新所有标签和按钮的文本
        self.input_label.setText(t["input_pdf"])
        self.input_browse.setText(t["browse"])
        self.input_browse.setToolTip(t["browse_tooltip"])
        self.output_label.setText(t["output_pdf"])
        self.output_browse.setText(t["browse"])
        self.output_browse.setToolTip(t["browse_tooltip"])
        self.default_checkbox.setText(t["use_defaults"])
        self.dpi_label.setText(t["render_dpi"])
        self.bg_label.setText(t["background_color"])
        self.bg_combo.clear()
        self.bg_combo.addItems([t["white"], t["black"], t["custom"]])
        self.bg_combo.setToolTip(t["background_color"])
        self.bg_button.setToolTip(t["choose_color_tooltip"] if "choose_color_tooltip" in t else "Choose custom color")
        self.language_label.setText(t["language"])
        self.help_button.setText(t["help"])
        self.help_button.setToolTip(t["help_tooltip"] if "help_tooltip" in t else "Click for help")
        self.exit_button.setText(t["exit"])
        self.exit_button.setToolTip(t["exit_tooltip"] if "exit_tooltip" in t else "Exit the application")
        self.run_button.setText(t["start_deskew"])
        self.run_button.setToolTip(t["start_deskew_tooltip"])
        self.theme_label.setText(t["theme"])
        self.theme_combo.setToolTip(t["theme_tooltip"])

        # 更新帮助信息标题和内容
        self.help_info_title = t["help_info_title"]
        self.help_info_text = t["help_info_text"]

    def init_ui(self):
        """初始化用户界面"""
        # 设置允许拖放
        self.setAcceptDrops(True)

        # 主布局
        main_layout = QVBoxLayout()

        # 拖放提示
        self.drag_drop_label = QLabel()
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        main_layout.addWidget(self.drag_drop_label)

        # 输入 PDF
        input_layout = QHBoxLayout()
        self.input_label = QLabel()
        self.input_line = QLineEdit()
        self.input_browse = QPushButton()
        self.input_browse.setIcon(QIcon.fromTheme("document-open"))  # 添加图标
        self.input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_browse)
        main_layout.addLayout(input_layout)

        # 输出 PDF
        output_layout = QHBoxLayout()
        self.output_label = QLabel()
        self.output_line = QLineEdit()
        self.output_browse = QPushButton()
        self.output_browse.setIcon(QIcon.fromTheme("document-save"))  # 添加图标
        self.output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_browse)
        main_layout.addLayout(output_layout)

        # 默认设置复选框
        self.default_checkbox = QCheckBox()
        self.default_checkbox.setChecked(True)
        self.default_checkbox.stateChanged.connect(self.toggle_settings)
        main_layout.addWidget(self.default_checkbox)

        # 自定义 DPI
        dpi_layout = QHBoxLayout()
        self.dpi_label = QLabel()
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setEnabled(False)
        dpi_layout.addWidget(self.dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        main_layout.addLayout(dpi_layout)

        # 背景颜色
        bg_layout = QHBoxLayout()
        self.bg_label = QLabel()
        self.bg_combo = QComboBox()
        self.bg_combo.setEnabled(False)
        self.bg_combo.currentIndexChanged.connect(self.bg_selection_changed)
        self.bg_button = QPushButton()
        self.bg_button.setIcon(QIcon.fromTheme("color-picker"))  # 添加图标
        self.bg_button.setEnabled(False)
        self.bg_button.clicked.connect(self.choose_color)
        bg_layout.addWidget(self.bg_label)
        bg_layout.addWidget(self.bg_combo)
        bg_layout.addWidget(self.bg_button)
        main_layout.addLayout(bg_layout)

        # 语言选择
        language_layout = QHBoxLayout()
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        main_layout.addLayout(language_layout)

        # 主题选择
        theme_layout = QHBoxLayout()
        self.theme_label = QLabel()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_combo)
        main_layout.addLayout(theme_layout)

        # 帮助和退出按钮
        help_exit_layout = QHBoxLayout()
        self.help_button = QPushButton()
        self.help_button.setIcon(QIcon.fromTheme("help-browser"))  # 添加图标
        self.help_button.clicked.connect(self.show_help)
        self.exit_button = QPushButton()
        self.exit_button.setIcon(QIcon.fromTheme("application-exit"))  # 添加图标
        self.exit_button.clicked.connect(self.close)
        help_exit_layout.addWidget(self.help_button)
        help_exit_layout.addStretch()
        help_exit_layout.addWidget(self.exit_button)
        main_layout.addLayout(help_exit_layout)

        # 运行按钮
        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon.fromTheme("media-playback-start"))  # 添加图标
        self.run_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.run_button)

        # 进度条和百分比标签
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_label = QLabel("0%")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        main_layout.addLayout(progress_layout)

        # 设置主窗口的中心部件
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 初始化所有UI文本
        self.init_ui_texts()

    def change_language(self, index):
        """切换语言"""
        if index == 0:
            self.current_language = Language.ENGLISH
        elif index == 1:
            self.current_language = Language.CHINESE
        else:
            self.current_language = Language.CHINESE  # 默认中文

        self.init_ui_texts()

    def change_theme(self, index):
        """切换主题"""
        themes = ['light_blue.xml', 'dark_teal.xml', 'blue.xml']
        selected_theme = themes[index] if index < len(themes) else 'light_blue.xml'
        apply_stylesheet(QApplication.instance(), theme=selected_theme)

    def browse_input(self):
        """浏览选择输入PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getOpenFileName(self, t["input_pdf"], "", "PDF Files (*.pdf)")
        if file_path:
            self.input_line.setText(file_path)
            # 自动设置默认输出路径
            input_dir = os.path.dirname(file_path)
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            if self.current_language == Language.ENGLISH:
                default_output = os.path.join(input_dir, f"{input_basename}_deskewed.pdf")
            else:
                default_output = os.path.join(input_dir, f"{input_basename}_校准.pdf")
            self.output_line.setText(default_output)

    def browse_output(self):
        """浏览选择输出PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getSaveFileName(self, t["output_pdf"], "", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            self.output_line.setText(file_path)

    def toggle_settings(self, state):
        """切换默认设置"""
        t = self.get_translation()
        if state == Qt.CheckState.Checked.value:
            self.dpi_spin.setEnabled(False)
            self.bg_combo.setEnabled(False)
            self.bg_button.setEnabled(False)
        else:
            self.dpi_spin.setEnabled(True)
            self.bg_combo.setEnabled(True)
            if self.bg_combo.currentText() == t["custom"]:
                self.bg_button.setEnabled(True)
            else:
                self.bg_button.setEnabled(False)

    def bg_selection_changed(self, index):
        """背景颜色选择变化"""
        t = self.get_translation()
        if self.bg_combo.currentText() == t["custom"]:
            self.bg_button.setEnabled(True)
        else:
            self.bg_button.setEnabled(False)
            if self.bg_combo.currentText() == t["white"]:
                self.selected_color = self.background_colors["White"].rgb
            elif self.bg_combo.currentText() == t["black"]:
                self.selected_color = self.background_colors["Black"].rgb

    def choose_color(self):
        """选择自定义背景颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = (color.red(), color.green(), color.blue())

    def show_help(self):
        """显示帮助信息"""
        t = self.get_translation()
        QMessageBox.information(self, t["help_info_title"], t["help_info_text"])

    def start_processing(self):
        """开始PDF校准处理"""
        try:
            t = self.get_translation()

            input_pdf = self.input_line.text().strip()
            output_pdf = self.output_line.text().strip()

            if not input_pdf or not os.path.isfile(input_pdf):
                QMessageBox.warning(self, t["input_error_title"], t["input_error_text"])
                return

            if not output_pdf:
                QMessageBox.warning(self, t["output_error_title"], t["output_error_text"])
                return

            use_defaults = self.default_checkbox.isChecked()
            if use_defaults:
                dpi = 300
                background_color = self.background_colors["White"].rgb
            else:
                dpi = self.dpi_spin.value()
                bg_selection = self.bg_combo.currentText()
                if bg_selection == t["white"]:
                    background_color = self.background_colors["White"].rgb
                elif bg_selection == t["black"]:
                    background_color = self.background_colors["Black"].rgb
                elif bg_selection == t["custom"]:
                    background_color = self.selected_color
                else:
                    background_color = self.background_colors["White"].rgb  # 默认白色

            # 确认设置
            confirm_text = (
                f"<h2>{t['confirm_settings_title']}</h2>"
                f"<p><b>{t['input_path']}</b> {input_pdf}</p>"
                f"<p><b>{t['output_path']}</b> {output_pdf}</p>"
                f"<p><b>{t['dpi']}</b> {dpi}</p>"
                f"<p><b>{t['bg_color']}</b> {background_color}</p>"
                f"<p>{t['confirm_settings_text']}</p>"
            )

            reply = QMessageBox.question(
                self,
                t["confirm_settings_title"],
                confirm_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            # 禁用界面元素
            self.set_ui_enabled(False)

            # 重置进度条
            self.progress_bar.setValue(0)
            self.progress_label.setText("0%")

            # 启动工作线程
            self.worker = WorkerThread(input_pdf, output_pdf, dpi, background_color)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.processing_finished)
            self.worker.error.connect(self.processing_error)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")
            logging.exception("An unexpected error occurred in start_processing")
            self.set_ui_enabled(True)

    def update_progress(self, value):
        """更新进度条和标签"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")

    def processing_finished(self, output_pdf):
        """处理完成"""
        t = self.get_translation()
        self.progress_bar.setValue(100)
        self.progress_label.setText("100%")
        QMessageBox.information(self, t["processing_complete_title"], f"{t['processing_complete_text']}\n{output_pdf}")

        # 重新启用界面元素
        self.set_ui_enabled(True)

    def processing_error(self, error_message):
        """处理错误"""
        t = self.get_translation()
        QMessageBox.critical(self, t["processing_error_title"], f"{t['processing_error_text']}\n{error_message}")

        # 重新启用界面元素
        self.set_ui_enabled(True)

    def set_ui_enabled(self, enabled: bool):
        """启用或禁用所有UI元素"""
        self.run_button.setEnabled(enabled)
        self.input_browse.setEnabled(enabled)
        self.output_browse.setEnabled(enabled)
        self.default_checkbox.setEnabled(enabled)
        self.dpi_spin.setEnabled(enabled and not self.default_checkbox.isChecked())
        self.bg_combo.setEnabled(enabled and not self.default_checkbox.isChecked())
        self.bg_button.setEnabled(enabled and not self.default_checkbox.isChecked() and self.bg_combo.currentText() == self.get_translation()["custom"])
        self.help_button.setEnabled(enabled)
        self.exit_button.setEnabled(enabled)
        self.language_combo.setEnabled(enabled)
        self.theme_combo.setEnabled(enabled)

    def get_translation(self) -> Dict[str, str]:
        """获取当前语言的翻译字典"""
        lang = self.current_language.value
        return self.translations.get(lang, self.translations[Language.CHINESE.value])

    # 文件拖放事件
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """处理拖放事件"""
        t = self.get_translation()
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".pdf"):
                self.input_line.setText(file_path)
                # 自动设置默认输出路径
                input_dir = os.path.dirname(file_path)
                input_basename = os.path.splitext(os.path.basename(file_path))[0]
                if self.current_language == Language.ENGLISH:
                    default_output = os.path.join(input_dir, f"{input_basename}_deskewed.pdf")
                else:
                    default_output = os.path.join(input_dir, f"{input_basename}_校准.pdf")
                self.output_line.setText(default_output)
                break  # 仅处理第一个PDF文件

