# src/pdf_deskew_ui/worker.py

import logging
import os

import cv2
import fitz  # PyMuPDF
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from deskew_tool.deskew_pdf import deskew_pdf


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    before_after = pyqtSignal(str, str)  # 新增信号
    status = pyqtSignal(str)  # 新增信号，用于发送状态更新
    total_pages = pyqtSignal(int)  # 新增信号，用于发送总页数
    current_page = pyqtSignal(int)  # 新增信号，用于发送当前页数

    def __init__(self, input_pdf, output_pdf, dpi, background_color, selected_features):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.dpi = dpi
        self.background_color = background_color
        self.selected_features = selected_features  # 用户选择的图像处理功能
        self._is_running = True  # 标志位

    def run(self):
        try:
            logging.info(f"Processing started for {self.input_pdf}")
            self.status.emit("Opening input PDF file...")
            # 在处理前保存一张原始页面的图像用于展示
            temp_before = "temp_before.png"
            pdf_document = fitz.open(self.input_pdf)
            total_pages = len(pdf_document)
            self.total_pages.emit(total_pages)  # 发送总页数

            if total_pages > 0:
                page = pdf_document.load_page(0)
                pix = page.get_pixmap(dpi=self.dpi)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, pix.n
                )
                if img.ndim == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                cv2.imwrite(temp_before, img)
                self.status.emit("Saving 'Before' image...")

            # 启动PDF校准
            deskew_pdf(
                self.input_pdf,
                self.output_pdf,
                dpi=self.dpi,
                background_color=self.background_color,
                progress_callback=self.update_progress_with_status,
                current_page_callback=self.update_current_page_status,
                status_callback=self.update_status,  # 传递status_callback
                is_running_callback=self.is_running,  # 传递is_running_callback
                selected_features=self.selected_features,
            )

            # 在处理后保存一张处理后的页面图像用于展示
            temp_after = "temp_after.png"
            self.status.emit("Opening output PDF file...")
            pdf_document = fitz.open(self.output_pdf)
            if len(pdf_document) > 0:
                page = pdf_document.load_page(0)
                pix = page.get_pixmap(dpi=self.dpi)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, pix.n
                )
                if img.ndim == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                cv2.imwrite(temp_after, img)
                self.status.emit("Saving 'After' image...")
            logging.info(f"Processing completed successfully for {self.output_pdf}")
            self.before_after.emit(temp_before, temp_after)  # 发送信号
            self.finished.emit(self.output_pdf)
        except Exception as e:
            logging.error(f"Processing error: {e}")
            self.error.emit(str(e))
        finally:
            # 清理临时文件
            if os.path.exists(temp_before):
                try:
                    os.remove(temp_before)
                except Exception as e:
                    logging.warning(
                        f"Unable to remove temporary file {temp_before}: {e}"
                    )
            if os.path.exists(temp_after):
                try:
                    os.remove(temp_after)
                except Exception as e:
                    logging.warning(
                        f"Unable to remove temporary file {temp_after}: {e}"
                    )

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

    def is_running(self):
        """返回当前线程是否在运行"""
        return self._is_running

    def stop(self):
        """停止线程"""
        self._is_running = False
