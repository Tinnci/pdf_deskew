from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
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
from pdf_deskew_ui.styles import StyleManager


class StyledFrame(QFrame):
    """A styled frame for grouping widgets with a consistent look."""

    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.content_layout = QVBoxLayout(self)

        if title:
            self.add_title(title)

        self.update_style()

    def update_style(self):
        theme = StyleManager.get_theme()
        self.setStyleSheet(f"""
            StyledFrame {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: 8px;
            }}
        """)

        if hasattr(self, "title_label"):
            self.title_label.setStyleSheet(f"""
                font-weight: bold;
                font-size: 14px;
                color: {theme.primary};
            """)

        if hasattr(self, "separator"):
            self.separator.setStyleSheet(f"background-color: {theme.border};")

    def add_title(self, title):
        theme = StyleManager.get_theme()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {theme.primary};
        """)
        self.content_layout.addWidget(self.title_label)

        # Add a separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet(f"background-color: {theme.border};")
        self.content_layout.addWidget(self.separator)


class FileSelectionWidget(QWidget):
    file_selected = pyqtSignal(str, str)

    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = StyledFrame(self.t.get("input_pdf", "File Selection"))
        container_layout = self.container.content_layout

        # Drag and drop hint
        self.drag_drop_label = QLabel(
            self.t.get("drag_drop_hint", "Drag and drop a PDF file here")
        )
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.drag_drop_label)

        # Input file
        input_layout = QVBoxLayout()
        self.input_label = QLabel(self.t["input_pdf"])

        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Select input PDF...")
        self.input_browse = QPushButton(self.t["browse"])
        input_row.addWidget(self.input_line)
        input_row.addWidget(self.input_browse)

        input_layout.addWidget(self.input_label)
        input_layout.addLayout(input_row)
        container_layout.addLayout(input_layout)

        # Output file
        output_layout = QVBoxLayout()
        self.output_label = QLabel(self.t["output_pdf"])

        output_row = QHBoxLayout()
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText("Select output path...")
        self.output_browse = QPushButton(self.t["browse"])
        output_row.addWidget(self.output_line)
        output_row.addWidget(self.output_browse)

        output_layout.addWidget(self.output_label)
        output_layout.addLayout(output_row)
        container_layout.addLayout(output_layout)

        layout.addWidget(self.container)
        self.update_style()

    def update_translations(self, t):
        self.t = t
        self.container.title_label.setText(t.get("input_pdf", "File Selection"))
        self.input_label.setText(t["input_pdf"])
        self.input_browse.setText(t["browse"])
        self.output_label.setText(t["output_pdf"])
        self.output_browse.setText(t["browse"])
        self.drag_drop_label.setText(
            t.get("drag_drop_hint", "Drag and drop a PDF file here")
        )

    def update_style(self):
        theme = StyleManager.get_theme()
        self.drag_drop_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {theme.border};
                border-radius: 8px;
                padding: 20px;
                background-color: {theme.primary_light};
                color: {theme.text_secondary};
            }}
            QLabel:hover {{
                border-color: {theme.primary};
                background-color: {theme.primary_light};
            }}
        """)

        btn_style = StyleManager.get_secondary_button_style()
        self.input_browse.setStyleSheet(btn_style)
        self.output_browse.setStyleSheet(btn_style)

        if hasattr(self, "container"):
            self.container.update_style()


class ConfigWidget(QWidget):
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = StyledFrame(self.t.get("image_processing", "Configuration"))
        container_layout = self.container.content_layout

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
        basic_layout.addStretch()

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
        watermark_layout.addStretch()

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
        enhance_layout.addStretch()

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
        grayscale_layout.addStretch()

        self.tabs.addTab(self.grayscale_tab, self.t["tab_grayscale"])

        container_layout.addWidget(self.tabs)
        layout.addWidget(self.container)
        self.update_style()

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
        self.container.title_label.setText(t.get("image_processing", "Configuration"))
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

    def update_style(self):
        theme = StyleManager.get_theme()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme.border};
                top: -1px;
                background: {theme.surface};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: {theme.background};
                border: 1px solid {theme.border};
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: {theme.text_secondary};
            }}
            QTabBar::tab:selected {{
                background: {theme.surface};
                border-bottom-color: {theme.surface};
                font-weight: bold;
                color: {theme.primary};
            }}
        """)

        # Ensure tab contents have the correct background
        tab_style = f"background-color: {theme.surface}; color: {theme.text_primary};"
        for tab in [
            self.basic_tab,
            self.watermark_tab,
            self.enhance_tab,
            self.grayscale_tab,
        ]:
            tab.setStyleSheet(tab_style)

        if hasattr(self, "container"):
            self.container.update_style()


class StatusWidget(QWidget):
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = StyledFrame(self.t.get("status_label", "Status"))
        container_layout = self.container.content_layout

        # Progress
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("0%")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        container_layout.addLayout(progress_layout)

        # Status
        status_layout = QHBoxLayout()
        self.status_label = QLabel(self.t["status_label"])
        self.status_text = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_text)
        container_layout.addLayout(status_layout)

        # Log
        log_label = QLabel(self.t.get("log_label", "Log:"))
        container_layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        container_layout.addWidget(self.log_text)

        self.update_style()
        layout.addWidget(self.container)

    def update_translations(self, t):
        self.t = t
        self.container.title_label.setText(t.get("status_label", "Status"))
        self.status_label.setText(t["status_label"])

    def update_style(self):
        theme = StyleManager.get_theme()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme.border};
                border-radius: 5px;
                text-align: center;
                height: 20px;
                background-color: {theme.background};
            }}
            QProgressBar::chunk {{
                background-color: {theme.primary};
                width: 10px;
                margin: 0.5px;
            }}
        """)
        self.status_text.setStyleSheet(
            f"color: {theme.text_secondary}; font-style: italic;"
        )
        self.log_text.setStyleSheet(f"""
            background-color: {theme.background};
            border: 1px solid {theme.border};
            border-radius: 4px;
            font-family: Consolas, monospace;
            color: {theme.text_primary};
        """)
        if hasattr(self, "container"):
            self.container.update_style()
