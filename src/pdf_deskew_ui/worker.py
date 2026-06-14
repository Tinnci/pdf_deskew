# src/pdf_deskew_ui/worker.py

import logging
import os
import tempfile

import cv2
from PyQt6.QtCore import QThread, pyqtSignal

from deskew_tool.config import DeskewConfig
from deskew_tool.deskew_pdf import (
    ProcessingCancelledError,
    deskew_pdf,
    get_pdf_page_count,
    render_page_image,
)

logger = logging.getLogger(__name__)


def _new_temp_png(prefix: str) -> str:
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".png")
    os.close(fd)
    return path


def _save_page_preview(pdf_path: str, page_num: int, dpi: int, image_path: str) -> None:
    image = render_page_image(pdf_path, page_num, dpi)
    if not cv2.imwrite(image_path, image):
        raise OSError(f"Unable to write preview image: {image_path}")


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    before_after = pyqtSignal(str, str)  # 新增信号
    status = pyqtSignal(str)  # 新增信号，用于发送状态更新
    total_pages = pyqtSignal(int)  # 新增信号，用于发送总页数
    current_page = pyqtSignal(int)  # 新增信号，用于发送当前页数

    def __init__(self, input_pdf, output_pdf, config: DeskewConfig):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.config = config
        self._is_running = True  # 标志位

    def run(self):
        temp_before: str | None = None
        temp_after: str | None = None
        preview_emitted = False

        try:
            logger.info("Processing started for %s", self.input_pdf)
            self.status.emit("Opening input PDF file...")
            total_pages = get_pdf_page_count(self.input_pdf)
            self.total_pages.emit(total_pages)

            if total_pages <= 0:
                raise RuntimeError("Input PDF contains no pages.")

            temp_before = _new_temp_png("pdf_deskew_before_")
            _save_page_preview(self.input_pdf, 0, self.config.dpi, temp_before)
            self.status.emit("Saving 'Before' image...")

            deskew_pdf(
                self.input_pdf,
                self.output_pdf,
                config=self.config,
                progress_callback=self.update_progress_with_status,
                current_page_callback=self.update_current_page_status,
                status_callback=self.update_status,  # 传递status_callback
                is_running_callback=self.is_running,  # 传递is_running_callback
            )

            temp_after = _new_temp_png("pdf_deskew_after_")
            self.status.emit("Opening output PDF file...")
            _save_page_preview(self.output_pdf, 0, self.config.dpi, temp_after)
            self.status.emit("Saving 'After' image...")

            logger.info("Processing completed successfully for %s", self.output_pdf)
            preview_emitted = True
            self.before_after.emit(temp_before, temp_after)  # 发送信号
            self.finished.emit(self.output_pdf)
        except ProcessingCancelledError:
            logger.info("Processing cancelled for %s", self.input_pdf)
            self.status.emit("Processing cancelled.")
        except Exception as e:
            logger.exception("Processing error: %s", e)
            self.error.emit(str(e))
        finally:
            if not preview_emitted:
                for temp_path in [temp_before, temp_after]:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception as e:
                            logger.warning("Unable to remove temporary file %s: %s", temp_path, e)

    def update_progress_with_status(self, value):
        """更新进度并发送状态信息"""
        self.progress.emit(value)
        if value < 10:
            self.status.emit("Rendering page images...")
        elif 10 <= value < 30:
            self.status.emit("Removing watermarks...")
        elif 30 <= value < 50:
            self.status.emit("Enhancing image readability...")
        elif 50 <= value < 80:
            self.status.emit("Detecting and correcting skew...")
        elif 80 <= value < 90:
            self.status.emit("Saving corrected images...")
        elif 90 <= value < 100:
            self.status.emit("Generating output PDF...")
        else:
            self.status.emit("Processing completed.")

    def update_current_page_status(self, current_page):
        """发送当前处理的页数"""
        self.current_page.emit(current_page)

    def update_status(self, message):
        """发送状态信息"""
        self.status.emit(message)

    def is_running(self):
        """返回当前线程是否在运行"""
        return self._is_running

    def stop(self):
        """停止线程"""
        self._is_running = False
