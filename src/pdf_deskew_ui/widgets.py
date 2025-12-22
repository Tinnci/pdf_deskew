from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from deskew_tool.config import DeskewConfig


class FileSelectionWidget(QWidget):
    file_selected = pyqtSignal(str, str)

    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drag and drop hint
        self.drag_drop_label = QLabel(
            self.t.get("drag_drop_hint", "Drag and drop a PDF file here")
        )
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        layout.addWidget(self.drag_drop_label)

        # Input file
        input_layout = QHBoxLayout()
        self.input_label = QLabel(self.t["input_pdf"])
        self.input_line = QLineEdit()
        self.input_browse = QPushButton(self.t["browse"])
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_browse)
        layout.addLayout(input_layout)

        # Output file
        output_layout = QHBoxLayout()
        self.output_label = QLabel(self.t["output_pdf"])
        self.output_line = QLineEdit()
        self.output_browse = QPushButton(self.t["browse"])
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_browse)
        layout.addLayout(output_layout)

    def update_translations(self, t):
        self.t = t
        self.input_label.setText(t["input_pdf"])
        self.input_browse.setText(t["browse"])
        self.output_label.setText(t["output_pdf"])
        self.output_browse.setText(t["browse"])


class ConfigWidget(QWidget):
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # 1. Basic Tab
        self.basic_tab = QWidget()
        basic_layout = QVBoxLayout(self.basic_tab)
        self.default_checkbox = QCheckBox(self.t["use_defaults"])
        self.default_checkbox.setChecked(True)
        self.default_checkbox.stateChanged.connect(self.toggle_settings)
        basic_layout.addWidget(self.default_checkbox)

        dpi_layout = QHBoxLayout()
        self.dpi_label = QLabel(self.t["render_dpi"])
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setEnabled(False)
        dpi_layout.addWidget(self.dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        basic_layout.addLayout(dpi_layout)

        self.tabs.addTab(self.basic_tab, self.t["tab_basic"])

        # 2. Watermark Tab
        self.watermark_tab = QWidget()
        watermark_layout = QVBoxLayout(self.watermark_tab)
        self.remove_watermark_checkbox = QCheckBox(self.t["remove_watermark"])
        self.remove_watermark_checkbox.setChecked(False)
        self.remove_watermark_checkbox.stateChanged.connect(
            self.toggle_watermark_options
        )
        watermark_layout.addWidget(self.remove_watermark_checkbox)

        method_layout = QHBoxLayout()
        self.watermark_method_label = QLabel(self.t["watermark_removal_method"])
        self.watermark_method_combo = QComboBox()
        self.watermark_method_combo.addItems(["Inpainting"])
        self.watermark_method_combo.setEnabled(False)
        method_layout.addWidget(self.watermark_method_label)
        method_layout.addWidget(self.watermark_method_combo)
        watermark_layout.addLayout(method_layout)

        threshold_layout = QHBoxLayout()
        self.watermark_threshold_label = QLabel(self.t["watermark_mask_threshold"])
        self.watermark_threshold_spin = QSpinBox()
        self.watermark_threshold_spin.setRange(0, 255)
        self.watermark_threshold_spin.setValue(127)
        self.watermark_threshold_spin.setEnabled(False)
        threshold_layout.addWidget(self.watermark_threshold_label)
        threshold_layout.addWidget(self.watermark_threshold_spin)
        watermark_layout.addLayout(threshold_layout)

        self.tabs.addTab(self.watermark_tab, self.t["tab_watermark"])

        # 3. Enhance Tab
        self.enhance_tab = QWidget()
        enhance_layout = QVBoxLayout(self.enhance_tab)
        self.enhance_image_checkbox = QCheckBox(self.t["enhance_image"])
        self.enhance_image_checkbox.setChecked(False)
        self.enhance_image_checkbox.stateChanged.connect(self.toggle_enhance_options)
        enhance_layout.addWidget(self.enhance_image_checkbox)

        contrast_layout = QHBoxLayout()
        self.contrast_level_label = QLabel(self.t["contrast_level"])
        self.contrast_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_level_slider.setRange(1, 3)
        self.contrast_level_slider.setValue(2)
        self.contrast_level_slider.setEnabled(False)
        contrast_layout.addWidget(self.contrast_level_label)
        contrast_layout.addWidget(self.contrast_level_slider)
        enhance_layout.addLayout(contrast_layout)

        self.tabs.addTab(self.enhance_tab, self.t["tab_enhance"])

        # 4. Grayscale Tab
        self.grayscale_tab = QWidget()
        grayscale_layout = QVBoxLayout(self.grayscale_tab)
        self.convert_grayscale_checkbox = QCheckBox(self.t["convert_grayscale"])
        self.convert_grayscale_checkbox.setChecked(False)
        self.convert_grayscale_checkbox.stateChanged.connect(
            self.toggle_grayscale_options
        )
        grayscale_layout.addWidget(self.convert_grayscale_checkbox)

        self.tabs.addTab(self.grayscale_tab, self.t["tab_grayscale"])

        main_layout.addWidget(self.tabs)

    def toggle_settings(self, state):
        enabled = state == Qt.CheckState.Unchecked.value
        self.dpi_spin.setEnabled(enabled)

    def toggle_watermark_options(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.watermark_method_combo.setEnabled(enabled)
        self.watermark_threshold_spin.setEnabled(enabled)

    def toggle_enhance_options(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.contrast_level_slider.setEnabled(enabled)

    def toggle_grayscale_options(self, state):
        pass

    def get_config(self) -> DeskewConfig:
        return DeskewConfig(
            dpi=self.dpi_spin.value(),
            remove_watermark=self.remove_watermark_checkbox.isChecked(),
            watermark_threshold=self.watermark_threshold_spin.value(),
            enhance_image=self.enhance_image_checkbox.isChecked(),
            contrast_level=self.contrast_level_slider.value(),
            convert_grayscale=self.convert_grayscale_checkbox.isChecked(),
        )

    def update_translations(self, t):
        self.t = t
        self.default_checkbox.setText(t["use_defaults"])
        self.dpi_label.setText(t["render_dpi"])
        self.remove_watermark_checkbox.setText(t["remove_watermark"])
        self.watermark_method_label.setText(t["watermark_removal_method"])
        self.watermark_threshold_label.setText(t["watermark_mask_threshold"])
        self.enhance_image_checkbox.setText(t["enhance_image"])
        self.contrast_level_label.setText(t["contrast_level"])
        self.convert_grayscale_checkbox.setText(t["convert_grayscale"])

        self.tabs.setTabText(0, t["tab_basic"])
        self.tabs.setTabText(1, t["tab_watermark"])
        self.tabs.setTabText(2, t["tab_enhance"])
        self.tabs.setTabText(3, t["tab_grayscale"])


class StatusWidget(QWidget):
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Progress
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("0%")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # Status
        status_layout = QHBoxLayout()
        self.status_label = QLabel(self.t["status_label"])
        self.status_text = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_text)
        layout.addLayout(status_layout)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        layout.addWidget(self.log_text)

    def update_translations(self, t):
        self.t = t
        self.status_label.setText(t["status_label"])
