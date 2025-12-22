from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
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

        # Basic Tab
        self.basic_tab = QWidget()
        basic_layout = QVBoxLayout(self.basic_tab)
        self.default_checkbox = QCheckBox(self.t["use_defaults"])
        self.default_checkbox.setChecked(True)
        basic_layout.addWidget(self.default_checkbox)

        dpi_layout = QHBoxLayout()
        self.dpi_label = QLabel(self.t["render_dpi"])
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(300)
        dpi_layout.addWidget(self.dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        basic_layout.addLayout(dpi_layout)

        self.tabs.addTab(self.basic_tab, self.t["tab_basic"])
        # ... other tabs would go here ...

        main_layout.addWidget(self.tabs)

    def get_config(self) -> DeskewConfig:
        # Simplified for now
        return DeskewConfig(
            dpi=self.dpi_spin.value(),
            # ... other fields ...
        )

    def update_translations(self, t):
        self.t = t
        self.default_checkbox.setText(t["use_defaults"])
        self.dpi_label.setText(t["render_dpi"])
        self.tabs.setTabText(0, t["tab_basic"])


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
