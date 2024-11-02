# src/pdf_deskew_ui/ui.py

import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox, QSpinBox,
    QComboBox, QProgressBar, QColorDialog, QApplication
)
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QColor
from qt_material import apply_stylesheet

from .worker import WorkerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.init_translator()
        self.setWindowTitle(self.tr("PDF 校准工具"))
        self.setGeometry(100, 100, 700, 500)

        self.init_ui()

    def init_translator(self):
        # 自动检测系统语言
        locale = QLocale.system().name()
        translations_path = os.path.join(os.path.dirname(__file__), 'resources', 'translations')

        qm_file = os.path.join(translations_path, f"{locale}.qm")
        if os.path.exists(qm_file):
            self.translator.load(qm_file)
            app = QApplication.instance()
            app.installTranslator(self.translator)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 输入 PDF
        input_layout = QHBoxLayout()
        input_label = QLabel(self.tr("输入 PDF 文件:"))
        self.input_line = QLineEdit()
        self.input_browse = QPushButton(self.tr("浏览"))
        self.input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_browse)
        main_layout.addLayout(input_layout)

        # 输出 PDF
        output_layout = QHBoxLayout()
        output_label = QLabel(self.tr("输出 PDF 文件:"))
        self.output_line = QLineEdit()
        self.output_browse = QPushButton(self.tr("浏览"))
        self.output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_browse)
        main_layout.addLayout(output_layout)

        # 默认设置复选框
        self.default_checkbox = QCheckBox(self.tr("使用推荐设置 (DPI=300, 背景色=白色)"))
        self.default_checkbox.setChecked(True)
        self.default_checkbox.stateChanged.connect(self.toggle_settings)
        main_layout.addWidget(self.default_checkbox)

        # 自定义 DPI
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel(self.tr("渲染 DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setEnabled(False)
        dpi_layout.addWidget(dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        main_layout.addLayout(dpi_layout)

        # 背景颜色
        bg_layout = QHBoxLayout()
        bg_label = QLabel(self.tr("背景颜色:"))
        self.bg_combo = QComboBox()
        self.bg_combo.addItems([self.tr("白色"), self.tr("黑色"), self.tr("自定义")])
        self.bg_combo.setEnabled(False)
        self.bg_combo.currentIndexChanged.connect(self.bg_selection_changed)
        self.bg_button = QPushButton(self.tr("选择颜色"))
        self.bg_button.setEnabled(False)
        self.bg_button.clicked.connect(self.choose_color)
        self.selected_color = (255, 255, 255)  # 默认白色
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_combo)
        bg_layout.addWidget(self.bg_button)
        main_layout.addLayout(bg_layout)

        # 语言选择
        language_layout = QHBoxLayout()
        language_label = QLabel(self.tr("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        main_layout.addLayout(language_layout)

        # 帮助和退出按钮
        help_exit_layout = QHBoxLayout()
        self.help_button = QPushButton(self.tr("帮助"))
        self.help_button.clicked.connect(self.show_help)
        self.exit_button = QPushButton(self.tr("退出"))
        self.exit_button.clicked.connect(self.close)
        help_exit_layout.addWidget(self.help_button)
        help_exit_layout.addStretch()
        help_exit_layout.addWidget(self.exit_button)
        main_layout.addLayout(help_exit_layout)

        # 运行按钮
        self.run_button = QPushButton(self.tr("开始校准"))
        self.run_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.run_button)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 设置主窗口的中心部件
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.tr("选择输入 PDF 文件"), "", "PDF Files (*.pdf)")
        if file_path:
            self.input_line.setText(file_path)
            # 自动设置默认输出路径
            input_dir = os.path.dirname(file_path)
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            default_output = os.path.join(input_dir, f"{input_basename}_矫正.pdf")
            self.output_line.setText(default_output)

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(self, self.tr("选择输出 PDF 文件"), "", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            self.output_line.setText(file_path)

    def toggle_settings(self, state):
        if state == Qt.CheckState.Checked.value:
            self.dpi_spin.setEnabled(False)
            self.bg_combo.setEnabled(False)
            self.bg_button.setEnabled(False)
        else:
            self.dpi_spin.setEnabled(True)
            self.bg_combo.setEnabled(True)
            if self.bg_combo.currentText() == self.tr("自定义"):
                self.bg_button.setEnabled(True)
            else:
                self.bg_button.setEnabled(False)

    def bg_selection_changed(self, index):
        if self.bg_combo.currentText() == self.tr("自定义"):
            self.bg_button.setEnabled(True)
        else:
            self.bg_button.setEnabled(False)
            if self.bg_combo.currentText() == self.tr("白色"):
                self.selected_color = (255, 255, 255)
            elif self.bg_combo.currentText() == self.tr("黑色"):
                self.selected_color = (0, 0, 0)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = (color.red(), color.green(), color.blue())

    def show_help(self):
        help_text = f"""
        <h2>{self.tr('帮助信息')}</h2>
        <p>{self.tr('此工具用于校准 PDF 文件中的扫描图像。')}</p>
        <p>{self.tr('您可以选择文件、设置 DPI 以及背景颜色。')}</p>
        <p><b>{self.tr('使用步骤:')}</b></p>
        <ol>
            <li>{self.tr('点击“浏览”按钮选择输入的 PDF 文件。')}</li>
            <li>{self.tr('点击“浏览”按钮选择输出的 PDF 文件路径。默认情况下，输出文件将命名为“输入文件名_矫正.pdf”。')}</li>
            <li>{self.tr('选择是否使用推荐设置：')}</li>
            <ul>
                <li>{self.tr('如果勾选“使用推荐设置”，将使用 DPI=300 和白色背景。')}</li>
                <li>{self.tr('如果取消勾选，可以自定义 DPI 和背景颜色。')}</li>
            </ul>
            <li>{self.tr('点击“开始校准”按钮开始处理。')}</li>
            <li>{self.tr('处理过程中，您可以看到进度条显示进度。')}</li>
        </ol>
        """
        QMessageBox.information(self, self.tr("帮助"), help_text)

    def change_language(self, index):
        language = self.language_combo.currentText()
        translations_path = os.path.join(os.path.dirname(__file__), 'resources', 'translations')

        if language == "English":
            qm_file = os.path.join(translations_path, "en_US.qm")
        elif language == "中文":
            qm_file = os.path.join(translations_path, "zh_CN.qm")
        else:
            qm_file = ""

        if qm_file and os.path.exists(qm_file):
            self.translator.load(qm_file)
            app = QApplication.instance()
            app.installTranslator(self.translator)
            self.retranslate_ui()

    def retranslate_ui(self):
        # 更新所有UI文本
        self.setWindowTitle(self.tr("PDF 校准工具"))
        # 更新标签和按钮的文本
        input_label = self.findChildren(QLabel)[0]
        input_label.setText(self.tr("输入 PDF 文件:"))

        output_label = self.findChildren(QLabel)[1]
        output_label.setText(self.tr("输出 PDF 文件:"))

        self.default_checkbox.setText(self.tr("使用推荐设置 (DPI=300, 背景色=白色)"))

        dpi_label = self.findChildren(QLabel)[2]
        dpi_label.setText(self.tr("渲染 DPI:"))

        bg_label = self.findChildren(QLabel)[3]
        bg_label.setText(self.tr("背景颜色:"))

        self.bg_combo.clear()
        self.bg_combo.addItems([self.tr("白色"), self.tr("黑色"), self.tr("自定义")])

        language_label = self.findChildren(QLabel)[4]
        language_label.setText(self.tr("语言:"))

        self.help_button.setText(self.tr("帮助"))
        self.exit_button.setText(self.tr("退出"))
        self.run_button.setText(self.tr("开始校准"))

    def start_processing(self):
        input_pdf = self.input_line.text().strip()
        output_pdf = self.output_line.text().strip()

        if not input_pdf or not os.path.isfile(input_pdf):
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入有效的输入 PDF 文件路径。"))
            return

        if not output_pdf:
            QMessageBox.warning(self, self.tr("输出错误"), self.tr("请输入有效的输出 PDF 文件路径。"))
            return

        use_defaults = self.default_checkbox.isChecked()
        if use_defaults:
            dpi = 300
            background_color = (255, 255, 255)
        else:
            dpi = self.dpi_spin.value()
            bg_selection = self.bg_combo.currentText()
            if bg_selection == self.tr("白色"):
                background_color = (255, 255, 255)
            elif bg_selection == self.tr("黑色"):
                background_color = (0, 0, 0)
            elif bg_selection == self.tr("自定义"):
                background_color = self.selected_color
            else:
                background_color = (255, 255, 255)  # 默认白色

        # 确认设置
        confirm_text = f"""
        <h2>{self.tr('确认设置')}</h2>
        <p><b>{self.tr('输入 PDF 文件路径:')}</b> {input_pdf}</p>
        <p><b>{self.tr('输出 PDF 文件路径:')}</b> {output_pdf}</p>
        <p><b>{self.tr('渲染 DPI:')}</b> {dpi}</p>
        <p><b>{self.tr('背景颜色:')}</b> {background_color}</p>
        <p>{self.tr('请确认这些设置是否正确？')}</p>
        """
        reply = QMessageBox.question(
            self,
            self.tr("确认设置"),
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 禁用界面元素
        self.run_button.setEnabled(False)
        self.input_browse.setEnabled(False)
        self.output_browse.setEnabled(False)
        self.default_checkbox.setEnabled(False)
        self.dpi_spin.setEnabled(False)
        self.bg_combo.setEnabled(False)
        self.bg_button.setEnabled(False)
        self.help_button.setEnabled(False)
        self.exit_button.setEnabled(False)
        self.language_combo.setEnabled(False)

        # 重置进度条
        self.progress_bar.setValue(0)

        # 启动工作线程
        self.worker = WorkerThread(input_pdf, output_pdf, dpi, background_color)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_finished(self, output_pdf):
        self.progress_bar.setValue(100)
        QMessageBox.information(self, self.tr("完成"), f"{self.tr('校准后的 PDF 已保存到:')}\n{output_pdf}")

        # 重新启用界面元素
        self.run_button.setEnabled(True)
        self.input_browse.setEnabled(True)
        self.output_browse.setEnabled(True)
        self.default_checkbox.setEnabled(True)
        self.toggle_settings(self.default_checkbox.checkState())
        self.help_button.setEnabled(True)
        self.exit_button.setEnabled(True)
        self.language_combo.setEnabled(True)

    def processing_error(self, error_message):
        QMessageBox.critical(self, self.tr("错误"), f"{self.tr('处理过程中出现错误:')}\n{error_message}")

        # 重新启用界面元素
        self.run_button.setEnabled(True)
        self.input_browse.setEnabled(True)
        self.output_browse.setEnabled(True)
        self.default_checkbox.setEnabled(True)
        self.toggle_settings(self.default_checkbox.checkState())
        self.help_button.setEnabled(True)
        self.exit_button.setEnabled(True)
        self.language_combo.setEnabled(True)
