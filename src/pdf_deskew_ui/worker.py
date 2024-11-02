# src/pdf_deskew_ui/worker.py

import logging
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
            logging.info(f"Processing started for {self.input_pdf}")
            deskew_pdf(
                self.input_pdf,
                self.output_pdf,
                dpi=self.dpi,
                background_color=self.background_color,
                progress_callback=self.progress
            )
            logging.info(f"Processing completed successfully for {self.output_pdf}")
            self.finished.emit(self.output_pdf)
        except Exception as e:
            logging.error(f"Processing error: {e}")
            self.error.emit(str(e))
