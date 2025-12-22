# src/pdf_deskew_ui/ui.py

import logging
import os
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

from .worker import WorkerThread


# 定义语言枚举
class Language(Enum):
    ENGLISH = "en_US"
    CHINESE = "zh_CN"


# 数据类存储背景颜色
@dataclass
class BackgroundColor:
    name: str
    rgb: tuple[int, int, int]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = Language.CHINESE  # 默认语言为中文

        self.background_colors = {
            "White": BackgroundColor("White", (255, 255, 255)),
            "Black": BackgroundColor("Black", (0, 0, 0)),
            "Custom": BackgroundColor("Custom", (255, 255, 255)),
        }

        self.selected_color = self.background_colors["White"].rgb  # 默认白色

        self.translations = self.load_translations()
        self.init_ui()

    def load_translations(self) -> dict[str, dict[str, str]]:
        """加载翻译字典，可以扩展为从外部JSON文件加载"""
        return {
            "en_US": {
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
                    "<li>Click the 'Browse' button to choose the output PDF file path. "
                    "By default, the output file will be named "
                    "'input_filename_deskewed.pdf'.</li>"
                    "<li>Select whether to use recommended settings:</li>"
                    "<ul>"
                    "<li>If 'Use Recommended Settings' is checked, DPI=300 and "
                    "background color will be white.</li>"
                    "<li>If unchecked, you can customize DPI and background color.</li>"
                    "</ul>"
                    "<li>Click the 'Start Deskew' button to begin processing.</li>"
                    "<li>During processing, you can see the progress bar indicating "
                    "the progress.</li>"
                    "</ol>"
                ),
                "confirm_settings_title": "Confirm Settings",
                "confirm_settings_text": (
                    "Please confirm if these settings are correct:"
                ),
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
                "theme_tooltip": "Select a theme for the application",
                "choose_color_tooltip": "Choose a custom background color",
                "help_tooltip": "Click for help",
                "exit_tooltip": "Exit the application",
                "status_label": "Status:",
                "total_pages_label": "Total Pages:",
                "current_page_label": "Current Page:",
                "image_processing": "Image Processing Options:",
                "remove_watermark": "Remove Watermark",
                "enhance_image": "Enhance Image",
                "convert_grayscale": "Convert to Grayscale",
                "log_label": "Log:",
                # Tab页标签
                "tab_basic": "Basic Settings",
                "tab_watermark": "Watermark Removal",
                "tab_enhance": "Image Enhancement",
                "tab_grayscale": "Grayscale Conversion",
                # 新增翻译键
                "watermark_removal_method": "Watermark Removal Method:",
                "inpainting_algorithm": "Inpainting Algorithm:",
                "telea": "Telea",
                "navier_stokes": "Navier-Stokes",
                "watermark_mask_threshold": "Watermark Mask Threshold:",
                "contrast_enhancement": "Contrast Enhancement:",
                "contrast_level": "Contrast Level:",
                "denoising_method": "Denoising Method:",
                "denoising_kernel_size": "Denoising Kernel Size:",
                "sharpening": "Sharpening:",
                "sharpening_strength": "Sharpening Strength:",
                "grayscale_quantization": "Grayscale Quantization Levels:",
                "grayscale_quant_levels": "Quantization Levels:",
                "grayscale_scaling": "Grayscale Scaling:",
                "grayscale_scale_factor": "Scale Factor:",
                "grayscale_smoothing_method": "Grayscale Smoothing Method:",
                "grayscale_smoothing_kernel": "Smoothing Kernel Size:",
            },
            "zh_CN": {
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
                    "<li>点击“浏览”按钮选择输出的 PDF 文件路径。默认情况下，"
                    "输出文件将命名为“输入文件名_校准.pdf”。</li>"
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
                "theme_tooltip": "选择应用程序的主题",
                "choose_color_tooltip": "选择自定义背景颜色",
                "help_tooltip": "点击获取帮助",
                "exit_tooltip": "退出应用程序",
                "status_label": "状态:",
                "total_pages_label": "总页数:",
                "current_page_label": "当前页数:",
                "image_processing": "图像处理选项:",
                "remove_watermark": "移除水印",
                "enhance_image": "增强图像",
                "convert_grayscale": "转换为灰度图像",
                "log_label": "日志:",
                # Tab页标签
                "tab_basic": "基础设置",
                "tab_watermark": "水印移除",
                "tab_enhance": "图像增强",
                "tab_grayscale": "灰度转换",
                # 新增翻译键
                "watermark_removal_method": "水印移除方法:",
                "inpainting_algorithm": "修复算法:",
                "telea": "Telea",
                "navier_stokes": "Navier-Stokes",
                "watermark_mask_threshold": "水印掩码阈值:",
                "contrast_enhancement": "对比度增强:",
                "contrast_level": "对比度等级:",
                "denoising_method": "去噪方法:",
                "denoising_kernel_size": "去噪内核大小:",
                "sharpening": "锐化:",
                "sharpening_strength": "锐化强度:",
                "grayscale_quantization": "灰度量化等级:",
                "grayscale_quant_levels": "量化等级:",
                "grayscale_scaling": "灰度缩放:",
                "grayscale_scale_factor": "缩放比例:",
                "grayscale_smoothing_method": "灰度平滑方法:",
                "grayscale_smoothing_kernel": "平滑内核大小:",
            },
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
        self.bg_button.setToolTip(
            t["choose_color_tooltip"]
            if "choose_color_tooltip" in t
            else "Choose custom color"
        )
        self.language_label.setText(t["language"])
        self.help_button.setText(t["help"])
        self.help_button.setToolTip(
            t["help_tooltip"] if "help_tooltip" in t else "Click for help"
        )
        self.exit_button.setText(t["exit"])
        self.exit_button.setToolTip(
            t["exit_tooltip"] if "exit_tooltip" in t else "Exit the application"
        )
        self.run_button.setText(t["start_deskew"])
        self.run_button.setToolTip(t["start_deskew_tooltip"])
        self.theme_label.setText(t["theme"])
        self.theme_combo.setToolTip(t["theme_tooltip"])

        # 更新帮助信息标题和内容
        self.help_info_title = t["help_info_title"]
        self.help_info_text = t["help_info_text"]

        # 更新状态标签
        self.status_label.setText(t.get("status_label", "Status:"))
        self.total_pages_label.setText(t.get("total_pages_label", "Total Pages:"))
        self.current_page_label.setText(t.get("current_page_label", "Current Page:"))

        # 更新图像处理选项复选框文本
        self.remove_watermark_checkbox.setText(
            t.get("remove_watermark", "Remove Watermark")
        )
        self.enhance_image_checkbox.setText(t.get("enhance_image", "Enhance Image"))
        self.contrast_enhancement_checkbox.setText(
            t.get("contrast_enhancement", "Contrast Enhancement:")
        )
        self.convert_grayscale_checkbox.setText(
            t.get("convert_grayscale", "Convert to Grayscale")
        )

        # 更新日志标签
        self.log_label.setText(t.get("log_label", "Log:"))

        # 更新标签页标题
        if hasattr(self, "tabs"):
            self.tabs.setTabText(0, t.get("tab_basic", "Basic Settings"))
            self.tabs.setTabText(1, t.get("tab_watermark", "Watermark Removal"))
            self.tabs.setTabText(2, t.get("tab_enhance", "Image Enhancement"))
            self.tabs.setTabText(3, t.get("tab_grayscale", "Grayscale Conversion"))

        # 更新水印移除参数
        self.watermark_removal_method_label.setText(
            t.get("watermark_removal_method", "Watermark Removal Method:")
        )
        self.inpainting_algorithm_label.setText(
            t.get("inpainting_algorithm", "Inpainting Algorithm:")
        )
        self.watermark_mask_threshold_label.setText(
            t.get("watermark_mask_threshold", "Watermark Mask Threshold:")
        )

        # 更新图像增强参数
        self.contrast_level_label.setText(t.get("contrast_level", "Contrast Level:"))
        self.denoising_method_label.setText(
            t.get("denoising_method", "Denoising Method:")
        )
        self.denoising_kernel_label.setText(
            t.get("denoising_kernel_size", "Denoising Kernel Size:")
        )
        self.sharpening_checkbox.setText(t.get("sharpening", "Sharpening:"))
        self.sharpening_strength_label.setText(
            t.get("sharpening_strength", "Sharpening Strength:")
        )

        # 更新灰度转换参数
        self.grayscale_quantization_label.setText(
            t.get("grayscale_quantization", "Grayscale Quantization Levels:")
        )
        self.grayscale_quant_levels_label.setText(
            t.get("grayscale_quant_levels", "Quantization Levels:")
        )
        self.grayscale_scaling_label.setText(
            t.get("grayscale_scaling", "Grayscale Scaling:")
        )
        self.grayscale_scale_factor_label.setText(
            t.get("grayscale_scale_factor", "Scale Factor:")
        )
        self.grayscale_smoothing_method_label.setText(
            t.get("grayscale_smoothing_method", "Grayscale Smoothing Method:")
        )
        self.grayscale_smoothing_kernel_label.setText(
            t.get("grayscale_smoothing_kernel", "Smoothing Kernel Size:")
        )

    def init_ui(self):
        """初始化用户界面 - 使用标签页优化布局"""
        # 设置允许拖放
        self.setAcceptDrops(True)

        # 主布局
        main_layout = QVBoxLayout()

        # 顶部：拖放提示
        self.drag_drop_label = QLabel("Drag and drop a PDF file here")
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        main_layout.addWidget(self.drag_drop_label)

        # 文件选择部分
        input_layout = QHBoxLayout()
        self.input_label = QLabel()
        self.input_line = QLineEdit()
        self.input_browse = QPushButton()
        self.input_browse.setIcon(QIcon.fromTheme("document-open"))
        self.input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_browse)
        main_layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        self.output_label = QLabel()
        self.output_line = QLineEdit()
        self.output_browse = QPushButton()
        self.output_browse.setIcon(QIcon.fromTheme("document-save"))
        self.output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_browse)
        main_layout.addLayout(output_layout)

        # ===== 使用标签页组织设置 =====
        self.tabs = QTabWidget()  # 保存标签页引用以便后续更新

        # ===== 标签页 1: 基础设置 =====
        basic_widget = QWidget()
        basic_layout = QVBoxLayout()

        # 默认设置
        self.default_checkbox = QCheckBox()
        self.default_checkbox.setChecked(True)
        self.default_checkbox.stateChanged.connect(self.toggle_settings)
        basic_layout.addWidget(self.default_checkbox)

        # DPI 设置
        dpi_layout = QHBoxLayout()
        self.dpi_label = QLabel()
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setEnabled(False)
        dpi_layout.addWidget(self.dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        dpi_layout.addStretch()
        basic_layout.addLayout(dpi_layout)

        # 背景颜色
        bg_layout = QHBoxLayout()
        self.bg_label = QLabel()
        self.bg_combo = QComboBox()
        self.bg_combo.setEnabled(False)
        self.bg_combo.currentIndexChanged.connect(self.bg_selection_changed)
        self.bg_button = QPushButton()
        self.bg_button.setIcon(QIcon.fromTheme("color-picker"))
        self.bg_button.setEnabled(False)
        self.bg_button.clicked.connect(self.choose_color)
        bg_layout.addWidget(self.bg_label)
        bg_layout.addWidget(self.bg_combo)
        bg_layout.addWidget(self.bg_button)
        bg_layout.addStretch()
        basic_layout.addLayout(bg_layout)

        basic_layout.addStretch()
        basic_widget.setLayout(basic_layout)
        self.tabs.addTab(basic_widget, "Basic Settings")

        # ===== 标签页 2: 水印移除 =====
        watermark_widget = QWidget()
        watermark_layout = QVBoxLayout()

        self.remove_watermark_checkbox = QCheckBox()
        self.remove_watermark_checkbox.setChecked(True)
        self.remove_watermark_checkbox.stateChanged.connect(
            self.toggle_watermark_options
        )
        watermark_layout.addWidget(self.remove_watermark_checkbox)

        watermark_method_layout = QHBoxLayout()
        self.watermark_removal_method_label = QLabel()
        self.watermark_removal_method_combo = QComboBox()
        self.watermark_removal_method_combo.addItems(["Inpainting"])
        self.watermark_removal_method_combo.setEnabled(False)
        watermark_method_layout.addWidget(self.watermark_removal_method_label)
        watermark_method_layout.addWidget(self.watermark_removal_method_combo)
        watermark_method_layout.addStretch()
        watermark_layout.addLayout(watermark_method_layout)

        inpainting_layout = QHBoxLayout()
        self.inpainting_algorithm_label = QLabel()
        self.inpainting_algorithm_combo = QComboBox()
        self.inpainting_algorithm_combo.addItems(["Telea", "Navier-Stokes"])
        self.inpainting_algorithm_combo.setEnabled(False)
        inpainting_layout.addWidget(self.inpainting_algorithm_label)
        inpainting_layout.addWidget(self.inpainting_algorithm_combo)
        inpainting_layout.addStretch()
        watermark_layout.addLayout(inpainting_layout)

        threshold_layout = QHBoxLayout()
        self.watermark_mask_threshold_label = QLabel()
        self.watermark_mask_threshold_spin = QSpinBox()
        self.watermark_mask_threshold_spin.setRange(0, 255)
        self.watermark_mask_threshold_spin.setValue(127)
        self.watermark_mask_threshold_spin.setEnabled(False)
        threshold_layout.addWidget(self.watermark_mask_threshold_label)
        threshold_layout.addWidget(self.watermark_mask_threshold_spin)
        threshold_layout.addStretch()
        watermark_layout.addLayout(threshold_layout)

        watermark_layout.addStretch()
        watermark_widget.setLayout(watermark_layout)
        self.tabs.addTab(watermark_widget, "Watermark Removal")

        # ===== 标签页 3: 图像增强 =====
        enhance_widget = QWidget()
        enhance_layout = QVBoxLayout()

        self.enhance_image_checkbox = QCheckBox()
        self.enhance_image_checkbox.setChecked(True)
        self.enhance_image_checkbox.stateChanged.connect(self.toggle_enhance_options)
        enhance_layout.addWidget(self.enhance_image_checkbox)

        # 对比度增强
        self.contrast_enhancement_checkbox = QCheckBox()
        self.contrast_enhancement_checkbox.setChecked(True)
        self.contrast_enhancement_checkbox.stateChanged.connect(
            self.toggle_contrast_enhancement_options
        )
        enhance_layout.addWidget(self.contrast_enhancement_checkbox)

        contrast_layout = QHBoxLayout()
        self.contrast_level_label = QLabel()
        self.contrast_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_level_slider.setRange(1, 3)
        self.contrast_level_slider.setValue(2)
        self.contrast_level_slider.setEnabled(False)
        contrast_layout.addWidget(self.contrast_level_label)
        contrast_layout.addWidget(self.contrast_level_slider)
        enhance_layout.addLayout(contrast_layout)

        # 去噪
        denoising_layout = QHBoxLayout()
        self.denoising_method_label = QLabel()
        self.denoising_method_combo = QComboBox()
        self.denoising_method_combo.addItems(["Gaussian", "Median"])
        self.denoising_method_combo.setEnabled(False)
        denoising_layout.addWidget(self.denoising_method_label)
        denoising_layout.addWidget(self.denoising_method_combo)
        denoising_layout.addStretch()
        enhance_layout.addLayout(denoising_layout)

        kernel_layout = QHBoxLayout()
        self.denoising_kernel_label = QLabel()
        self.denoising_kernel_spin = QSpinBox()
        self.denoising_kernel_spin.setRange(1, 31)
        self.denoising_kernel_spin.setValue(3)
        self.denoising_kernel_spin.setEnabled(False)
        kernel_layout.addWidget(self.denoising_kernel_label)
        kernel_layout.addWidget(self.denoising_kernel_spin)
        kernel_layout.addStretch()
        enhance_layout.addLayout(kernel_layout)

        # 锐化
        self.sharpening_checkbox = QCheckBox()
        self.sharpening_checkbox.setChecked(False)
        self.sharpening_checkbox.stateChanged.connect(self.toggle_sharpening_options)
        enhance_layout.addWidget(self.sharpening_checkbox)

        sharp_layout = QHBoxLayout()
        self.sharpening_strength_label = QLabel()
        self.sharpening_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpening_strength_slider.setRange(1, 5)
        self.sharpening_strength_slider.setValue(3)
        self.sharpening_strength_slider.setEnabled(False)
        sharp_layout.addWidget(self.sharpening_strength_label)
        sharp_layout.addWidget(self.sharpening_strength_slider)
        enhance_layout.addLayout(sharp_layout)

        enhance_layout.addStretch()
        enhance_widget.setLayout(enhance_layout)
        self.tabs.addTab(enhance_widget, "Image Enhancement")

        # ===== 标签页 4: 灰度转换 =====
        grayscale_widget = QWidget()
        grayscale_layout = QVBoxLayout()

        self.convert_grayscale_checkbox = QCheckBox()
        self.convert_grayscale_checkbox.setChecked(False)
        self.convert_grayscale_checkbox.stateChanged.connect(
            self.toggle_grayscale_options
        )
        grayscale_layout.addWidget(self.convert_grayscale_checkbox)

        quant_layout = QHBoxLayout()
        self.grayscale_quantization_label = QLabel()
        self.grayscale_quant_levels_label = QLabel()
        self.grayscale_quant_levels_spin = QSpinBox()
        self.grayscale_quant_levels_spin.setRange(2, 256)
        self.grayscale_quant_levels_spin.setValue(64)
        self.grayscale_quant_levels_spin.setEnabled(False)
        quant_layout.addWidget(self.grayscale_quantization_label)
        quant_layout.addWidget(self.grayscale_quant_levels_label)
        quant_layout.addWidget(self.grayscale_quant_levels_spin)
        quant_layout.addStretch()
        grayscale_layout.addLayout(quant_layout)

        scale_layout = QHBoxLayout()
        self.grayscale_scaling_label = QLabel()
        self.grayscale_scale_factor_label = QLabel()
        self.grayscale_scale_factor_spin = QSpinBox()
        self.grayscale_scale_factor_spin.setRange(1, 5)
        self.grayscale_scale_factor_spin.setValue(1)
        self.grayscale_scale_factor_spin.setEnabled(False)
        scale_layout.addWidget(self.grayscale_scaling_label)
        scale_layout.addWidget(self.grayscale_scale_factor_label)
        scale_layout.addWidget(self.grayscale_scale_factor_spin)
        scale_layout.addStretch()
        grayscale_layout.addLayout(scale_layout)

        smooth_method_layout = QHBoxLayout()
        self.grayscale_smoothing_method_label = QLabel()
        self.grayscale_smoothing_method_combo = QComboBox()
        self.grayscale_smoothing_method_combo.addItems(["Gaussian", "Median"])
        self.grayscale_smoothing_method_combo.setEnabled(False)
        smooth_method_layout.addWidget(self.grayscale_smoothing_method_label)
        smooth_method_layout.addWidget(self.grayscale_smoothing_method_combo)
        smooth_method_layout.addStretch()
        grayscale_layout.addLayout(smooth_method_layout)

        smooth_kernel_layout = QHBoxLayout()
        self.grayscale_smoothing_kernel_label = QLabel()
        self.grayscale_smoothing_kernel_spin = QSpinBox()
        self.grayscale_smoothing_kernel_spin.setRange(1, 31)
        self.grayscale_smoothing_kernel_spin.setValue(3)
        self.grayscale_smoothing_kernel_spin.setEnabled(False)
        smooth_kernel_layout.addWidget(self.grayscale_smoothing_kernel_label)
        smooth_kernel_layout.addWidget(self.grayscale_smoothing_kernel_spin)
        smooth_kernel_layout.addStretch()
        grayscale_layout.addLayout(smooth_kernel_layout)

        grayscale_layout.addStretch()
        grayscale_widget.setLayout(grayscale_layout)
        self.tabs.addTab(grayscale_widget, "Grayscale Conversion")

        main_layout.addWidget(self.tabs)
        basic_layout.addLayout(dpi_layout)

        # 背景颜色
        bg_layout = QHBoxLayout()
        self.bg_label = QLabel()
        self.bg_combo = QComboBox()
        self.bg_combo.setEnabled(False)
        self.bg_combo.currentIndexChanged.connect(self.bg_selection_changed)
        self.bg_button = QPushButton()
        self.bg_button.setIcon(QIcon.fromTheme("color-picker"))
        self.bg_button.setEnabled(False)
        self.bg_button.clicked.connect(self.choose_color)
        bg_layout.addWidget(self.bg_label)
        bg_layout.addWidget(self.bg_combo)
        bg_layout.addWidget(self.bg_button)
        bg_layout.addStretch()
        basic_layout.addLayout(bg_layout)

        basic_layout.addStretch()
        basic_widget.setLayout(basic_layout)
        self.tabs.addTab(basic_widget, "Basic Settings")

        # ===== 标签页 2: 水印移除 =====
        watermark_widget = QWidget()
        watermark_layout = QVBoxLayout()

        self.remove_watermark_checkbox = QCheckBox()
        self.remove_watermark_checkbox.setChecked(True)
        self.remove_watermark_checkbox.stateChanged.connect(
            self.toggle_watermark_options
        )
        watermark_layout.addWidget(self.remove_watermark_checkbox)

        watermark_method_layout = QHBoxLayout()
        self.watermark_removal_method_label = QLabel()
        self.watermark_removal_method_combo = QComboBox()
        self.watermark_removal_method_combo.addItems(["Inpainting"])
        self.watermark_removal_method_combo.setEnabled(False)
        watermark_method_layout.addWidget(self.watermark_removal_method_label)
        watermark_method_layout.addWidget(self.watermark_removal_method_combo)
        watermark_method_layout.addStretch()
        watermark_layout.addLayout(watermark_method_layout)

        inpainting_layout = QHBoxLayout()
        self.inpainting_algorithm_label = QLabel()
        self.inpainting_algorithm_combo = QComboBox()
        self.inpainting_algorithm_combo.addItems(["Telea", "Navier-Stokes"])
        self.inpainting_algorithm_combo.setEnabled(False)
        inpainting_layout.addWidget(self.inpainting_algorithm_label)
        inpainting_layout.addWidget(self.inpainting_algorithm_combo)
        inpainting_layout.addStretch()
        watermark_layout.addLayout(inpainting_layout)

        threshold_layout = QHBoxLayout()
        self.watermark_mask_threshold_label = QLabel()
        self.watermark_mask_threshold_spin = QSpinBox()
        self.watermark_mask_threshold_spin.setRange(0, 255)
        self.watermark_mask_threshold_spin.setValue(127)
        self.watermark_mask_threshold_spin.setEnabled(False)
        threshold_layout.addWidget(self.watermark_mask_threshold_label)
        threshold_layout.addWidget(self.watermark_mask_threshold_spin)
        threshold_layout.addStretch()
        watermark_layout.addLayout(threshold_layout)

        watermark_layout.addStretch()
        watermark_widget.setLayout(watermark_layout)
        self.tabs.addTab(watermark_widget, "Watermark Removal")

        # ===== 标签页 3: 图像增强 =====
        enhance_widget = QWidget()
        enhance_layout = QVBoxLayout()

        self.enhance_image_checkbox = QCheckBox()
        self.enhance_image_checkbox.setChecked(True)
        self.enhance_image_checkbox.stateChanged.connect(self.toggle_enhance_options)
        enhance_layout.addWidget(self.enhance_image_checkbox)

        # 对比度增强
        self.contrast_enhancement_checkbox = QCheckBox()
        self.contrast_enhancement_checkbox.setChecked(True)
        self.contrast_enhancement_checkbox.stateChanged.connect(
            self.toggle_contrast_enhancement_options
        )
        enhance_layout.addWidget(self.contrast_enhancement_checkbox)

        contrast_layout = QHBoxLayout()
        self.contrast_level_label = QLabel()
        self.contrast_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_level_slider.setRange(1, 3)
        self.contrast_level_slider.setValue(2)
        self.contrast_level_slider.setEnabled(False)
        contrast_layout.addWidget(self.contrast_level_label)
        contrast_layout.addWidget(self.contrast_level_slider)
        enhance_layout.addLayout(contrast_layout)

        # 去噪
        denoising_layout = QHBoxLayout()
        self.denoising_method_label = QLabel()
        self.denoising_method_combo = QComboBox()
        self.denoising_method_combo.addItems(["Gaussian", "Median"])
        self.denoising_method_combo.setEnabled(False)
        denoising_layout.addWidget(self.denoising_method_label)
        denoising_layout.addWidget(self.denoising_method_combo)
        denoising_layout.addStretch()
        enhance_layout.addLayout(denoising_layout)

        kernel_layout = QHBoxLayout()
        self.denoising_kernel_label = QLabel()
        self.denoising_kernel_spin = QSpinBox()
        self.denoising_kernel_spin.setRange(1, 31)
        self.denoising_kernel_spin.setValue(3)
        self.denoising_kernel_spin.setEnabled(False)
        kernel_layout.addWidget(self.denoising_kernel_label)
        kernel_layout.addWidget(self.denoising_kernel_spin)
        kernel_layout.addStretch()
        enhance_layout.addLayout(kernel_layout)

        # 锐化
        self.sharpening_checkbox = QCheckBox()
        self.sharpening_checkbox.setChecked(False)
        self.sharpening_checkbox.stateChanged.connect(self.toggle_sharpening_options)
        enhance_layout.addWidget(self.sharpening_checkbox)

        sharp_layout = QHBoxLayout()
        self.sharpening_strength_label = QLabel()
        self.sharpening_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpening_strength_slider.setRange(1, 5)
        self.sharpening_strength_slider.setValue(3)
        self.sharpening_strength_slider.setEnabled(False)
        sharp_layout.addWidget(self.sharpening_strength_label)
        sharp_layout.addWidget(self.sharpening_strength_slider)
        enhance_layout.addLayout(sharp_layout)

        enhance_layout.addStretch()
        enhance_widget.setLayout(enhance_layout)
        self.tabs.addTab(enhance_widget, "Image Enhancement")

        # ===== 标签页 4: 灰度转换 =====
        grayscale_widget = QWidget()
        grayscale_layout = QVBoxLayout()

        self.convert_grayscale_checkbox = QCheckBox()
        self.convert_grayscale_checkbox.setChecked(False)
        self.convert_grayscale_checkbox.stateChanged.connect(
            self.toggle_grayscale_options
        )
        grayscale_layout.addWidget(self.convert_grayscale_checkbox)

        quant_layout = QHBoxLayout()
        self.grayscale_quantization_label = QLabel()
        self.grayscale_quant_levels_label = QLabel()
        self.grayscale_quant_levels_spin = QSpinBox()
        self.grayscale_quant_levels_spin.setRange(2, 256)
        self.grayscale_quant_levels_spin.setValue(64)
        self.grayscale_quant_levels_spin.setEnabled(False)
        quant_layout.addWidget(self.grayscale_quantization_label)
        quant_layout.addWidget(self.grayscale_quant_levels_label)
        quant_layout.addWidget(self.grayscale_quant_levels_spin)
        quant_layout.addStretch()
        grayscale_layout.addLayout(quant_layout)

        scale_layout = QHBoxLayout()
        self.grayscale_scaling_label = QLabel()
        self.grayscale_scale_factor_label = QLabel()
        self.grayscale_scale_factor_spin = QSpinBox()
        self.grayscale_scale_factor_spin.setRange(1, 5)
        self.grayscale_scale_factor_spin.setValue(1)
        self.grayscale_scale_factor_spin.setEnabled(False)
        scale_layout.addWidget(self.grayscale_scaling_label)
        scale_layout.addWidget(self.grayscale_scale_factor_label)
        scale_layout.addWidget(self.grayscale_scale_factor_spin)
        scale_layout.addStretch()
        grayscale_layout.addLayout(scale_layout)

        smooth_method_layout = QHBoxLayout()
        self.grayscale_smoothing_method_label = QLabel()
        self.grayscale_smoothing_method_combo = QComboBox()
        self.grayscale_smoothing_method_combo.addItems(["Gaussian", "Median"])
        self.grayscale_smoothing_method_combo.setEnabled(False)
        smooth_method_layout.addWidget(self.grayscale_smoothing_method_label)
        smooth_method_layout.addWidget(self.grayscale_smoothing_method_combo)
        smooth_method_layout.addStretch()
        grayscale_layout.addLayout(smooth_method_layout)

        smooth_kernel_layout = QHBoxLayout()
        self.grayscale_smoothing_kernel_label = QLabel()
        self.grayscale_smoothing_kernel_spin = QSpinBox()
        self.grayscale_smoothing_kernel_spin.setRange(1, 31)
        self.grayscale_smoothing_kernel_spin.setValue(3)
        self.grayscale_smoothing_kernel_spin.setEnabled(False)
        smooth_kernel_layout.addWidget(self.grayscale_smoothing_kernel_label)
        smooth_kernel_layout.addWidget(self.grayscale_smoothing_kernel_spin)
        smooth_kernel_layout.addStretch()
        grayscale_layout.addLayout(smooth_kernel_layout)

        grayscale_layout.addStretch()
        grayscale_widget.setLayout(grayscale_layout)
        self.tabs.addTab(grayscale_widget, "Grayscale Conversion")

        main_layout.addWidget(self.tabs)

        # ===== 底部：语言、主题、按钮 =====
        settings_layout = QHBoxLayout()

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        settings_layout.addWidget(self.language_label)
        settings_layout.addWidget(self.language_combo)

        settings_layout.addSpacing(20)

        self.theme_label = QLabel()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        settings_layout.addWidget(self.theme_label)
        settings_layout.addWidget(self.theme_combo)

        settings_layout.addStretch()

        self.help_button = QPushButton()
        self.help_button.setIcon(QIcon.fromTheme("help-browser"))
        self.help_button.clicked.connect(self.show_help)
        self.exit_button = QPushButton()
        self.exit_button.setIcon(QIcon.fromTheme("application-exit"))
        self.exit_button.clicked.connect(self.close)
        settings_layout.addWidget(self.help_button)
        settings_layout.addWidget(self.exit_button)

        main_layout.addLayout(settings_layout)

        # 运行和取消按钮
        button_layout = QHBoxLayout()
        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.run_button.clicked.connect(self.start_processing)
        self.run_button.setMinimumHeight(40)
        button_layout.addWidget(self.run_button)

        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(QIcon.fromTheme("process-stop"))
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setMinimumHeight(40)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_label = QLabel("0%")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        main_layout.addLayout(progress_layout)

        # 状态信息
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.status_text = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_text)
        main_layout.addLayout(status_layout)

        # 页数信息
        pages_layout = QHBoxLayout()
        self.total_pages_label = QLabel()
        self.total_pages_value = QLabel("0")
        self.current_page_label = QLabel()
        self.current_page_value = QLabel("0")
        pages_layout.addWidget(self.total_pages_label)
        pages_layout.addWidget(self.total_pages_value)
        pages_layout.addStretch()
        pages_layout.addWidget(self.current_page_label)
        pages_layout.addWidget(self.current_page_value)
        main_layout.addLayout(pages_layout)

        # 日志窗口
        self.log_label = QLabel()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f0f0f0;")
        self.log_text.setMaximumHeight(100)
        main_layout.addWidget(self.log_label)
        main_layout.addWidget(self.log_text)

        # 处理前后对比
        images_layout = QHBoxLayout()
        self.before_label = QLabel("Before")
        self.before_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.before_label.setStyleSheet("border: 1px solid black;")
        self.before_label.setMaximumHeight(150)
        self.after_label = QLabel("After")
        self.after_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.after_label.setStyleSheet("border: 1px solid black;")
        self.after_label.setMaximumHeight(150)
        images_layout.addWidget(self.before_label)
        images_layout.addWidget(self.after_label)
        main_layout.addLayout(images_layout)

        # 设置窗口
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 设置窗口大小
        self.resize(900, 700)

        # 初始化文本
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
        themes = ["light_blue.xml", "dark_teal.xml", "blue.xml"]
        selected_theme = themes[index] if index < len(themes) else "light_blue.xml"
        apply_stylesheet(QApplication.instance(), theme=selected_theme)

    def browse_input(self):
        """浏览选择输入PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getOpenFileName(
            self, t["input_pdf"], "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_line.setText(file_path)
            # 自动设置默认输出路径
            input_dir = os.path.dirname(file_path)
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            if self.current_language == Language.ENGLISH:
                default_output = os.path.join(
                    input_dir, f"{input_basename}_deskewed.pdf"
                )
            else:
                default_output = os.path.join(input_dir, f"{input_basename}_校准.pdf")
            self.output_line.setText(default_output)

    def browse_output(self):
        """浏览选择输出PDF文件"""
        t = self.get_translation()
        file_path, _ = QFileDialog.getSaveFileName(
            self, t["output_pdf"], "", "PDF Files (*.pdf)"
        )
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
            # Disable image processing options when using defaults
            self.remove_watermark_checkbox.setEnabled(False)
            self.enhance_image_checkbox.setEnabled(False)
            self.convert_grayscale_checkbox.setEnabled(False)
            self.contrast_enhancement_checkbox.setEnabled(False)
            # Disable watermark removal parameters
            self.watermark_removal_method_combo.setEnabled(False)
            self.inpainting_algorithm_combo.setEnabled(False)
            self.watermark_mask_threshold_spin.setEnabled(False)
            # Disable image enhancement parameters
            self.contrast_level_slider.setEnabled(False)
            self.denoising_method_combo.setEnabled(False)
            self.denoising_kernel_spin.setEnabled(False)
            self.sharpening_checkbox.setEnabled(False)
            self.sharpening_strength_slider.setEnabled(False)
            # Disable grayscale parameters
            self.grayscale_quant_levels_spin.setEnabled(False)
            self.grayscale_scale_factor_spin.setEnabled(False)
            self.grayscale_smoothing_method_combo.setEnabled(False)
            self.grayscale_smoothing_kernel_spin.setEnabled(False)
        else:
            self.dpi_spin.setEnabled(True)
            self.bg_combo.setEnabled(True)
            if self.bg_combo.currentText() == t["custom"]:
                self.bg_button.setEnabled(True)
            else:
                self.bg_button.setEnabled(False)
            # Enable image processing options
            self.remove_watermark_checkbox.setEnabled(True)
            self.enhance_image_checkbox.setEnabled(True)
            self.convert_grayscale_checkbox.setEnabled(True)
            self.contrast_enhancement_checkbox.setEnabled(True)
            # Enable watermark removal parameters if watermark removal is checked
            self.watermark_removal_method_combo.setEnabled(
                self.remove_watermark_checkbox.isChecked()
            )
            self.inpainting_algorithm_combo.setEnabled(
                self.remove_watermark_checkbox.isChecked()
            )
            self.watermark_mask_threshold_spin.setEnabled(
                self.remove_watermark_checkbox.isChecked()
            )
            # Enable image enhancement parameters if enhancement is checked
            self.contrast_level_slider.setEnabled(
                self.enhance_image_checkbox.isChecked()
                and self.contrast_enhancement_checkbox.isChecked()
            )
            self.denoising_method_combo.setEnabled(
                self.enhance_image_checkbox.isChecked()
                and self.contrast_enhancement_checkbox.isChecked()
            )
            self.denoising_kernel_spin.setEnabled(
                self.enhance_image_checkbox.isChecked()
                and self.contrast_enhancement_checkbox.isChecked()
            )
            self.sharpening_checkbox.setEnabled(self.enhance_image_checkbox.isChecked())
            self.sharpening_strength_slider.setEnabled(
                self.enhance_image_checkbox.isChecked()
                and self.sharpening_checkbox.isChecked()
            )
            # Enable grayscale parameters if grayscale conversion is checked
            self.grayscale_quant_levels_spin.setEnabled(
                self.convert_grayscale_checkbox.isChecked()
            )
            self.grayscale_scale_factor_spin.setEnabled(
                self.convert_grayscale_checkbox.isChecked()
            )
            self.grayscale_smoothing_method_combo.setEnabled(
                self.convert_grayscale_checkbox.isChecked()
            )
            self.grayscale_smoothing_kernel_spin.setEnabled(
                self.convert_grayscale_checkbox.isChecked()
            )

    def toggle_watermark_options(self, state):
        """切换水印移除参数选项"""
        enabled = (
            self.remove_watermark_checkbox.isChecked()
            and not self.default_checkbox.isChecked()
        )
        self.watermark_removal_method_combo.setEnabled(enabled)
        self.inpainting_algorithm_combo.setEnabled(enabled)
        self.watermark_mask_threshold_spin.setEnabled(enabled)

    def toggle_enhance_options(self, state):
        """切换图像增强参数选项"""
        enabled = (
            self.enhance_image_checkbox.isChecked()
            and not self.default_checkbox.isChecked()
        )
        self.contrast_enhancement_checkbox.setEnabled(enabled)
        self.contrast_level_slider.setEnabled(
            enabled and self.contrast_enhancement_checkbox.isChecked()
        )
        self.denoising_method_combo.setEnabled(
            enabled and self.contrast_enhancement_checkbox.isChecked()
        )
        self.denoising_kernel_spin.setEnabled(
            enabled and self.contrast_enhancement_checkbox.isChecked()
        )
        self.sharpening_checkbox.setEnabled(enabled)
        self.sharpening_strength_slider.setEnabled(
            enabled and self.sharpening_checkbox.isChecked()
        )

    def toggle_contrast_enhancement_options(self, state):
        """切换对比度增强选项"""
        enabled = (
            self.contrast_enhancement_checkbox.isChecked()
            and not self.default_checkbox.isChecked()
        )
        self.contrast_level_slider.setEnabled(enabled)
        self.denoising_method_combo.setEnabled(enabled)
        self.denoising_kernel_spin.setEnabled(enabled)

    def toggle_sharpening_options(self, state):
        """切换锐化参数选项"""
        enabled = (
            self.sharpening_checkbox.isChecked()
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
        )
        self.sharpening_strength_slider.setEnabled(enabled)

    def toggle_grayscale_options(self, state):
        """切换灰度转换参数选项"""
        enabled = (
            self.convert_grayscale_checkbox.isChecked()
            and not self.default_checkbox.isChecked()
        )
        self.grayscale_quant_levels_spin.setEnabled(enabled)
        self.grayscale_scale_factor_spin.setEnabled(enabled)
        self.grayscale_smoothing_method_combo.setEnabled(enabled)
        self.grayscale_smoothing_kernel_spin.setEnabled(enabled)

    def bg_selection_changed(self, index):
        """背景颜色选择变化"""
        t = self.get_translation()
        if self.bg_combo.currentText() == t["custom"]:
            self.bg_button.setEnabled(True)
            self.selected_color = self.background_colors["Custom"].rgb
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
                QMessageBox.warning(
                    self, t["output_error_title"], t["output_error_text"]
                )
                return

            use_defaults = self.default_checkbox.isChecked()
            if use_defaults:
                dpi = 300
                background_color = self.background_colors["White"].rgb
                # 使用默认图像处理选项
                remove_watermark = True
                enhance_image = True
                convert_grayscale = False
                # 默认参数
                watermark_method = "Inpainting"
                inpainting_algo = "Telea"
                watermark_threshold = 127
                contrast_enhancement = True
                contrast_level = 2
                denoising_method = "Gaussian"
                denoising_kernel = 3
                sharpening = False
                sharpening_strength = 3
                grayscale_quant_levels = 64
                grayscale_scale_factor = 1
                grayscale_smoothing_method = "Gaussian"
                grayscale_smoothing_kernel = 3
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

                # 获取用户选择的图像处理选项
                remove_watermark = self.remove_watermark_checkbox.isChecked()
                enhance_image = self.enhance_image_checkbox.isChecked()
                convert_grayscale = self.convert_grayscale_checkbox.isChecked()

                # 获取水印移除参数
                watermark_method = self.watermark_removal_method_combo.currentText()
                inpainting_algo = self.inpainting_algorithm_combo.currentText()
                watermark_threshold = self.watermark_mask_threshold_spin.value()

                # 获取图像增强参数
                contrast_enhancement = self.contrast_enhancement_checkbox.isChecked()
                contrast_level = self.contrast_level_slider.value()
                denoising_method = self.denoising_method_combo.currentText()
                denoising_kernel = self.denoising_kernel_spin.value()
                sharpening = self.sharpening_checkbox.isChecked()
                sharpening_strength = self.sharpening_strength_slider.value()

                # 获取灰度转换参数
                grayscale_quant_levels = self.grayscale_quant_levels_spin.value()
                grayscale_scale_factor = self.grayscale_scale_factor_spin.value()
                grayscale_smoothing_method = (
                    self.grayscale_smoothing_method_combo.currentText()
                )
                grayscale_smoothing_kernel = (
                    self.grayscale_smoothing_kernel_spin.value()
                )

            # 确认设置
            confirm_text = (
                f"<h2>{t['confirm_settings_title']}</h2>"
                f"<p><b>{t['input_path']}</b> {input_pdf}</p>"
                f"<p><b>{t['output_path']}</b> {output_pdf}</p>"
                f"<p><b>{t['dpi']}</b> {dpi}</p>"
                f"<p><b>{t['bg_color']}</b> {background_color}</p>"
                f"<p><b>{t['remove_watermark']}</b> "
                f"{'Yes' if remove_watermark else 'No'}</p>"
                f"<p><b>{t['enhance_image']}</b> "
                f"{'Yes' if enhance_image else 'No'}</p>"
                f"<p><b>{t['convert_grayscale']}</b> "
                f"{'Yes' if convert_grayscale else 'No'}</p>"
            )

            if not use_defaults:
                # 添加详细参数到确认文本
                confirm_text += "<h3>Watermark Removal Parameters:</h3>"
                confirm_text += (
                    f"<p><b>{t['watermark_removal_method']}</b> {watermark_method}</p>"
                )
                confirm_text += (
                    f"<p><b>{t['inpainting_algorithm']}</b> {inpainting_algo}</p>"
                )
                confirm_text += (
                    f"<p><b>{t['watermark_mask_threshold']}</b> "
                    f"{watermark_threshold}</p>"
                )

                confirm_text += "<h3>Image Enhancement Parameters:</h3>"
                confirm_text += (
                    f"<p><b>{t['contrast_enhancement']}</b> "
                    f"{'Yes' if contrast_enhancement else 'No'}</p>"
                )
                if contrast_enhancement:
                    confirm_text += (
                        f"<p><b>{t['contrast_level']}</b> {contrast_level}</p>"
                    )
                confirm_text += (
                    f"<p><b>{t['denoising_method']}</b> {denoising_method}</p>"
                )
                confirm_text += (
                    f"<p><b>{t['denoising_kernel_size']}</b> {denoising_kernel}</p>"
                )
                confirm_text += (
                    f"<p><b>{t['sharpening']}</b> {'Yes' if sharpening else 'No'}</p>"
                )
                if sharpening:
                    confirm_text += (
                        f"<p><b>{t['sharpening_strength']}</b> "
                        f"{sharpening_strength}</p>"
                    )

                confirm_text += "<h3>Grayscale Conversion Parameters:</h3>"
                confirm_text += (
                    f"<p><b>{t['grayscale_quantization']}</b> "
                    f"{grayscale_quant_levels} levels</p>"
                )
                confirm_text += (
                    f"<p><b>{t['grayscale_scaling']}</b> {grayscale_scale_factor}x</p>"
                )
                confirm_text += (
                    f"<p><b>{t['grayscale_smoothing_method']}</b> "
                    f"{grayscale_smoothing_method}</p>"
                )
                confirm_text += (
                    f"<p><b>{t['grayscale_smoothing_kernel']}</b> "
                    f"{grayscale_smoothing_kernel}</p>"
                )

                confirm_text += f"<p>{t['confirm_settings_text']}</p>"

            reply = QMessageBox.question(
                self,
                t["confirm_settings_title"],
                confirm_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            # 禁用界面元素
            self.set_ui_enabled(False)

            # 重置进度条和页数显示
            self.progress_bar.setValue(0)
            self.progress_label.setText("0%")
            self.status_text.setText("")  # 清空状态文本
            self.total_pages_value.setText("0")
            self.current_page_value.setText("0")
            self.log_text.clear()  # 清空日志窗口

            # 启动工作线程
            selected_features = {
                "remove_watermark": remove_watermark,
                "enhance_image": enhance_image,
                "convert_grayscale": convert_grayscale,
                "watermark_method": watermark_method,
                "inpainting_algorithm": inpainting_algo,
                "watermark_threshold": watermark_threshold,
                "contrast_enhancement": contrast_enhancement,
                "contrast_level": contrast_level,
                "denoising_method": denoising_method,
                "denoising_kernel": denoising_kernel,
                "sharpening": sharpening,
                "sharpening_strength": sharpening_strength,
                "grayscale_quant_levels": grayscale_quant_levels,
                "grayscale_scale_factor": grayscale_scale_factor,
                "grayscale_smoothing_method": grayscale_smoothing_method,
                "grayscale_smoothing_kernel": grayscale_smoothing_kernel,
            }
            self.worker = WorkerThread(
                input_pdf, output_pdf, dpi, background_color, selected_features
            )
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.processing_finished)
            self.worker.error.connect(self.processing_error)
            self.worker.before_after.connect(self.display_before_after)  # 连接新的信号
            self.worker.status.connect(self.update_status)  # 连接状态更新信号
            self.worker.total_pages.connect(self.update_total_pages)  # 连接总页数信号
            self.worker.current_page.connect(
                self.update_current_page
            )  # 连接当前页数信号
            self.worker.start()
            self.cancel_button.setEnabled(True)  # 启用取消按钮

        except Exception as e:
            QMessageBox.critical(
                self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}"
            )
            logging.exception("An unexpected error occurred in start_processing")
            self.set_ui_enabled(True)

    def get_translation(self) -> dict[str, str]:
        """获取当前语言的翻译字典"""
        lang = self.current_language.value
        translations = self.translations.get(
            lang, self.translations[Language.CHINESE.value]
        )
        return translations  # type: ignore

    # 文件拖放事件
    def dragEnterEvent(self, event: QDragEnterEvent | None):
        """处理拖入事件"""
        if event:
            mime_data = event.mimeData()
            if mime_data and mime_data.hasUrls():
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None):
        """处理拖放事件"""
        if event:
            mime_data = event.mimeData()
            if mime_data:
                for url in mime_data.urls():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(".pdf"):
                        self.input_line.setText(file_path)
                        # 自动设置默认输出路径
                        input_dir = os.path.dirname(file_path)
                        input_basename = os.path.splitext(os.path.basename(file_path))[
                            0
                        ]
                        if self.current_language == Language.ENGLISH:
                            default_output = os.path.join(
                                input_dir, f"{input_basename}_deskewed.pdf"
                            )
                        else:
                            default_output = os.path.join(
                                input_dir, f"{input_basename}_校准.pdf"
                            )
                        self.output_line.setText(default_output)
                        break  # 仅处理第一个PDF文件

    def cancel_processing(self):
        """取消当前的处理"""
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.cancel_button.setEnabled(False)
            self.set_ui_enabled(True)
            self.status_text.setText(
                "Processing cancelled."
                if self.current_language == Language.ENGLISH
                else "处理已取消。"
            )
            self.log_text.append(
                "Processing cancelled by user."
                if self.current_language == Language.ENGLISH
                else "用户取消了处理。"
            )
            logging.info("Processing cancelled by user.")

    def update_progress(self, value):
        """更新进度条和标签"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")

    def update_status(self, message):
        """更新状态信息"""
        self.status_text.setText(message)
        self.log_text.append(message)  # 将状态信息追加到日志窗口
        logging.info(f"Status Update: {message}")

    def update_total_pages(self, total):
        """更新总页数显示"""
        self.total_pages_value.setText(str(total))

    def update_current_page(self, current):
        """更新当前页数显示"""
        self.current_page_value.setText(str(current))

    def processing_finished(self, output_pdf):
        """处理完成"""
        t = self.get_translation()
        self.progress_bar.setValue(100)
        self.progress_label.setText("100%")
        self.status_text.setText(t["processing_complete_text"])
        self.log_text.append(t["processing_complete_text"])
        QMessageBox.information(
            self,
            t["processing_complete_title"],
            f"{t['processing_complete_text']}\n{output_pdf}",
        )

        # 重新启用界面元素
        self.set_ui_enabled(True)
        self.cancel_button.setEnabled(False)

    def processing_error(self, error_message):
        """处理错误"""
        t = self.get_translation()
        QMessageBox.critical(
            self,
            t["processing_error_title"],
            f"{t['processing_error_text']}\n{error_message}",
        )
        self.log_text.append(f"{t['processing_error_text']}\n{error_message}")

        # 重新启用界面元素
        self.set_ui_enabled(True)
        self.cancel_button.setEnabled(False)

    def display_before_after(self, before_image_path, after_image_path):
        """显示处理前后的图像"""
        before_pix = QPixmap(before_image_path)
        after_pix = QPixmap(after_image_path)

        # 缩放图像以适应标签
        before_pix = before_pix.scaled(
            self.before_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        after_pix = after_pix.scaled(
            self.after_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.before_label.setPixmap(before_pix)
        self.after_label.setPixmap(after_pix)

        # 清理临时图像文件
        try:
            os.remove(before_image_path)
            os.remove(after_image_path)
        except Exception as e:
            logging.warning(f"Unable to remove temporary images: {e}")

    def set_ui_enabled(self, enabled: bool):
        """启用或禁用所有UI元素"""
        self.run_button.setEnabled(enabled)
        self.input_browse.setEnabled(enabled)
        self.output_browse.setEnabled(enabled)
        self.default_checkbox.setEnabled(enabled)
        self.dpi_spin.setEnabled(enabled and not self.default_checkbox.isChecked())
        self.bg_combo.setEnabled(enabled and not self.default_checkbox.isChecked())
        self.bg_button.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.bg_combo.currentText()
            == self.get_translation().get("custom", "Custom")
        )
        self.help_button.setEnabled(enabled)
        self.exit_button.setEnabled(enabled)
        self.language_combo.setEnabled(enabled)
        self.theme_combo.setEnabled(enabled)
        # 控制图像处理复选框的启用状态
        self.remove_watermark_checkbox.setEnabled(
            enabled and not self.default_checkbox.isChecked()
        )
        self.enhance_image_checkbox.setEnabled(
            enabled and not self.default_checkbox.isChecked()
        )
        self.convert_grayscale_checkbox.setEnabled(
            enabled and not self.default_checkbox.isChecked()
        )
        self.contrast_enhancement_checkbox.setEnabled(
            enabled and not self.default_checkbox.isChecked()
        )
        # 控制水印移除参数的启用状态
        self.watermark_removal_method_combo.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.remove_watermark_checkbox.isChecked()
        )
        self.inpainting_algorithm_combo.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.remove_watermark_checkbox.isChecked()
        )
        self.watermark_mask_threshold_spin.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.remove_watermark_checkbox.isChecked()
        )
        # 控制图像增强参数的启用状态
        self.contrast_level_slider.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
            and self.contrast_enhancement_checkbox.isChecked()
        )
        self.denoising_method_combo.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
            and self.contrast_enhancement_checkbox.isChecked()
        )
        self.denoising_kernel_spin.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
            and self.contrast_enhancement_checkbox.isChecked()
        )
        self.sharpening_checkbox.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
        )
        self.sharpening_strength_slider.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.enhance_image_checkbox.isChecked()
            and self.sharpening_checkbox.isChecked()
        )
        # 控制灰度转换参数的启用状态
        self.grayscale_quant_levels_spin.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.convert_grayscale_checkbox.isChecked()
        )
        self.grayscale_scale_factor_spin.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.convert_grayscale_checkbox.isChecked()
        )
        self.grayscale_smoothing_method_combo.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.convert_grayscale_checkbox.isChecked()
        )
        self.grayscale_smoothing_kernel_spin.setEnabled(
            enabled
            and not self.default_checkbox.isChecked()
            and self.convert_grayscale_checkbox.isChecked()
        )
