# src/deskew_tool/deskew_pdf.py

import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from deskew import determine_skew
import os
import shutil
import logging

def rotate_image(image: np.ndarray, angle: float, background: tuple = (255, 255, 255)) -> np.ndarray:
    """
    旋转图像以校正倾斜。
    """
    old_height, old_width = image.shape[:2]
    angle_radian = np.radians(angle)
    new_width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    new_height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (new_height - old_height) / 2
    rot_mat[0, 2] += (new_width - old_width) / 2

    return cv2.warpAffine(image, rot_mat, (int(round(new_width)), int(round(new_height))), borderValue=background)

def deskew_pdf(input_pdf_path, output_pdf_path, dpi=300, background_color=(255, 255, 255), progress_callback=None):
    """
    校正 PDF 文件中的图像倾斜。
    """
    # 打开 PDF 文件，添加错误处理
    try:
        pdf_document = fitz.open(input_pdf_path)
    except Exception as e:
        logging.error(f"无法打开 PDF 文件: {e}")
        raise IOError(f"无法打开 PDF 文件: {e}")

    output_images = []
    temp_folder = "temp_images"

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    try:
        total_pages = len(pdf_document)
        for page_num in range(total_pages):
            if progress_callback:
                progress_percentage = int((page_num / total_pages) * 100)
                progress_callback.emit(progress_percentage)
            # 将页面渲染为图像
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)  # 使用自定义 DPI
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

            # 如果图像是灰度，则转换为 RGB
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            # 将图像转换为灰度图像并确定倾斜角度
            grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            angle = determine_skew(grayscale)

            # 如果检测到角度则进行校正
            if angle is not None:
                logging.info(f"Detected skew angle {angle} degrees on page {page_num + 1}")
                # 旋转图像校正倾斜，使用自定义背景颜色
                corrected_img = rotate_image(img, angle, background=background_color)
            else:
                logging.info(f"No skew detected on page {page_num + 1}")
                corrected_img = img

            # 保存校正后的图像到临时文件夹
            corrected_img_path = os.path.join(temp_folder, f"page_{page_num}.png")
            cv2.imwrite(corrected_img_path, corrected_img)
            output_images.append(corrected_img_path)

        if progress_callback:
            progress_callback.emit(90)

        # 使用 PIL 将所有校正后的图像重新保存为 PDF
        image_list = [Image.open(img_path).convert("RGB") for img_path in output_images]
        if image_list:
            image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])

        if progress_callback:
            progress_callback.emit(100)

    except Exception as e:
        logging.error(f"Error during deskewing PDF: {e}")
        raise e

    finally:
        # 清理临时文件夹
        for img_path in output_images:
            os.remove(img_path)
        shutil.rmtree(temp_folder)
