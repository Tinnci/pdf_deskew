import pytest
from PyQt6.QtWidgets import QApplication

from pdf_deskew_ui.ui import MainWindow
from pdf_deskew_ui.widgets import ConfigWidget, FileSelectionWidget, StatusWidget


@pytest.fixture
def app(qtbot):
    """Fixture for the QApplication."""
    # qtbot handles the application lifecycle
    return QApplication.instance()


def test_mainwindow_init(qtbot):
    """Test that MainWindow can be initialized without errors."""
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() != ""
    assert window.file_widget is not None
    assert window.config_widget is not None
    assert window.status_widget is not None


def test_file_selection_widget_init(qtbot):
    """Test that FileSelectionWidget can be initialized without errors."""
    translations = {"input_pdf": "Input", "browse": "Browse", "output_pdf": "Output"}
    widget = FileSelectionWidget(translations)
    qtbot.addWidget(widget)
    assert widget.input_line is not None
    assert widget.input_browse is not None


def test_config_widget_init(qtbot):
    """Test that ConfigWidget can be initialized without errors."""
    translations = {
        "image_processing": "Config",
        "use_defaults": "Default",
        "render_dpi": "DPI",
        "remove_watermark": "Watermark",
        "watermark_removal_method": "Method",
        "watermark_mask_threshold": "Threshold",
        "enhance_image": "Enhance",
        "contrast_level": "Contrast",
        "convert_grayscale": "Grayscale",
        "tab_basic": "Basic",
        "tab_watermark": "Watermark",
        "tab_enhance": "Enhance",
        "tab_grayscale": "Grayscale",
    }
    widget = ConfigWidget(translations)
    qtbot.addWidget(widget)
    assert widget.tabs is not None


def test_status_widget_init(qtbot):
    """Test that StatusWidget can be initialized without errors."""
    translations = {"status_label": "Status", "log_label": "Log"}
    widget = StatusWidget(translations)
    qtbot.addWidget(widget)
    assert widget.progress_bar is not None
    assert widget.log_text is not None


def test_theme_switching(qtbot):
    """Test that switching themes doesn't crash."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Switch to Dark
    window.change_theme(1)
    # Switch to Blue
    window.change_theme(2)
    # Switch back to Light
    window.change_theme(0)
