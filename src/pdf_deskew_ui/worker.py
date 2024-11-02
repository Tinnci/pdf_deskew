# src/pdf_deskew_ui/worker.py

from PyQt6.QtCore import QThread, pyqtSignal
from deskew_tool.deskew_pdf import deskew_pdf

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_pdf, output_pdf, dpi, background_color):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.dpi = dpi
        self.background_color = background_color

    def run(self):
        try:
            deskew_pdf(
                self.input_pdf,
                self.output_pdf,
                dpi=self.dpi,
                background_color=self.background_color,
                progress_callback=self.progress
            )
            self.finished.emit(self.output_pdf)
        except Exception as e:
            self.error.emit(str(e))
