# src/deskew_tool/deskew_pdf.py

import logging
import os
import shutil
import tempfile
import warnings

import cv2
import fitz  # PyMuPDF
import numpy as np
from deskew import determine_skew
from PIL import Image

# Suppress SwigPyPacked deprecation warnings from PyMuPDF/SWIG
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message="builtin type .* has no __module__"
)


def rotate_image(
    image: np.ndarray, angle: float, background: tuple = (255, 255, 255)
) -> np.ndarray:
    """
    旋转图像以校正倾斜。
    """
    old_height, old_width = image.shape[:2]
    angle_radian = np.radians(angle)
    new_width = abs(np.sin(angle_radian) * old_height) + abs(
        np.cos(angle_radian) * old_width
    )
    new_height = abs(np.sin(angle_radian) * old_width) + abs(
        np.cos(angle_radian) * old_height
    )

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (new_height - old_height) / 2
    rot_mat[0, 2] += (new_width - old_width) / 2

    return cv2.warpAffine(
        image,
        rot_mat,
        (int(round(new_width)), int(round(new_height))),
        borderValue=background,
    )


def remove_watermark(
    image: np.ndarray,
    method: str = "Inpainting",
    algorithm: str = "Telea",
    threshold: int = 127,
) -> np.ndarray:
    """
    使用Inpainting方法移除水印。
    :param image: 输入图像
    :param method: 移除方法，目前仅支持"Inpainting"
    :param algorithm: 修复算法，"Telea"或"Navier-Stokes"
    :param threshold: 掩码阈值，用于生成水印掩码
    :return: 移除水印后的图像
    """
    if method != "Inpainting":
        logging.warning(f"Unsupported watermark removal method: {method}")
        return image

    # 生成水印掩码
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # 选择修复算法
    if algorithm == "Telea":
        flags = cv2.INPAINT_TELEA
    elif algorithm == "Navier-Stokes":
        flags = cv2.INPAINT_NS
    else:
        logging.warning(
            f"Unsupported inpainting algorithm: {algorithm}, defaulting to Telea"
        )
        flags = cv2.INPAINT_TELEA

    # 应用Inpainting
    inpainted = cv2.inpaint(image, mask, 3, flags)

    return inpainted


def enhance_image(
    image: np.ndarray,
    contrast_level: int = 2,
    denoising_method: str = "Gaussian",
    denoising_kernel: int = 3,
    sharpening: bool = False,
    sharpening_strength: int = 3,
) -> np.ndarray:
    """
    优化图像的可读性。
    :param image: 输入图像
    :param contrast_level: 对比度等级，1: 低, 2: 中, 3: 高
    :param denoising_method: 去噪方法，"Gaussian"或"Median"
    :param denoising_kernel: 去噪内核大小（奇数）
    :param sharpening: 是否进行锐化
    :param sharpening_strength: 锐化强度，1-5
    :return: 增强后的图像
    """
    # 对比度调整
    if contrast_level == 1:
        # 低对比度
        alpha = 1.2  # 对比度控制（1.0-3.0）
        beta = 20  # 亮度控制（0-100）
    elif contrast_level == 2:
        # 中等对比度
        alpha = 1.5
        beta = 30
    elif contrast_level == 3:
        # 高对比度
        alpha = 1.8
        beta = 40
    else:
        alpha = 1.5
        beta = 30

    contrasted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    # 去噪
    if denoising_method == "Gaussian":
        denoised = cv2.GaussianBlur(contrasted, (denoising_kernel, denoising_kernel), 0)
    elif denoising_method == "Median":
        denoised = cv2.medianBlur(contrasted, denoising_kernel)
    else:
        logging.warning(
            f"Unsupported denoising method: {denoising_method}, skipping denoising"
        )
        denoised = contrasted

    # 锐化
    if sharpening:
        # 使用拉普拉斯算子进行锐化
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        sharpened = cv2.filter2D(denoised, -1, kernel * sharpening_strength)
    else:
        sharpened = denoised

    return sharpened


def convert_grayscale(
    image: np.ndarray,
    quant_levels: int = 64,
    scale_factor: int = 1,
    smoothing_method: str = "Gaussian",
    smoothing_kernel: int = 3,
) -> np.ndarray:
    """
    将图像转换为灰度图像，并应用量化、缩放和平滑。
    :param image: 输入图像
    :param quant_levels: 灰度量化等级
    :param scale_factor: 缩放比例（1-5）
    :param smoothing_method: 平滑方法，"Gaussian"或"Median"
    :param smoothing_kernel: 平滑内核大小（奇数）
    :return: 转换后的灰度图像
    """
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 灰度量化
    gray_quant = np.floor_divide(gray, 256 // quant_levels) * (256 // quant_levels)
    gray_quant = gray_quant.astype(np.uint8)

    # 缩放
    if scale_factor != 1:
        width = int(gray_quant.shape[1] * scale_factor)
        height = int(gray_quant.shape[0] * scale_factor)
        gray_quant = cv2.resize(
            gray_quant, (width, height), interpolation=cv2.INTER_LINEAR
        )

    # 平滑
    if smoothing_method == "Gaussian":
        smoothed = cv2.GaussianBlur(gray_quant, (smoothing_kernel, smoothing_kernel), 0)
    elif smoothing_method == "Median":
        smoothed = cv2.medianBlur(gray_quant, smoothing_kernel)
    else:
        logging.warning(
            f"Unsupported smoothing method: {smoothing_method}, skipping smoothing"
        )
        smoothed = gray_quant

    # 转换回BGR以保持一致性
    gray_final = cv2.cvtColor(smoothed, cv2.COLOR_GRAY2BGR)

    return gray_final


def deskew_pdf(
    input_pdf_path,
    output_pdf_path,
    dpi=300,
    background_color=(255, 255, 255),
    progress_callback=None,
    current_page_callback=None,
    status_callback=None,
    is_running_callback=None,
    selected_features=None,
):
    """
    校正 PDF 文件中的图像倾斜，并根据用户选择应用图像处理功能。
    """
    if not selected_features:
        selected_features = {}

    # 打开 PDF 文件，添加错误处理
    try:
        pdf_document = fitz.open(input_pdf_path)
    except Exception as e:
        logging.error(f"无法打开 PDF 文件: {e}")
        if status_callback:
            status_callback(f"无法打开 PDF 文件: {e}")
        raise OSError(f"无法打开 PDF 文件: {e}") from e

    output_images = []
    temp_folder = tempfile.mkdtemp(prefix="pdf_deskew_")

    try:
        total_pages = len(pdf_document)
        for page_num in range(total_pages):
            # ... (rest of the loop)
            # 检查是否需要取消处理
            if is_running_callback and not is_running_callback():
                if status_callback:
                    status_callback("Processing cancelled.")
                logging.info("Processing cancelled by user.")
                return

            # 发送当前页数
            if current_page_callback:
                current_page_callback(page_num + 1)

            # 基本进度计算
            base_progress = int((page_num / total_pages) * 100)
            if progress_callback:
                progress_callback(base_progress)

            # 将页面渲染为图像
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )

            # 如果图像是灰度，则转换为 RGB
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            # 图像预处理
            # 1. 根据用户选择移除水印
            if selected_features.get("remove_watermark", False):
                method = selected_features.get("watermark_method", "Inpainting")
                algorithm = selected_features.get("inpainting_algorithm", "Telea")
                threshold = selected_features.get("watermark_threshold", 127)
                img = remove_watermark(
                    img, method=method, algorithm=algorithm, threshold=threshold
                )
                if progress_callback:
                    progress_callback(base_progress + 5)
                if status_callback:
                    status_callback("Removing watermarks...")

            # 2. 根据用户选择增强图像
            if selected_features.get("enhance_image", False):
                contrast_level = selected_features.get("contrast_level", 2)
                denoising_method = selected_features.get("denoising_method", "Gaussian")
                denoising_kernel = selected_features.get("denoising_kernel", 3)
                sharpening = selected_features.get("sharpening", False)
                sharpening_strength = selected_features.get("sharpening_strength", 3)
                img = enhance_image(
                    img,
                    contrast_level=contrast_level,
                    denoising_method=denoising_method,
                    denoising_kernel=denoising_kernel,
                    sharpening=sharpening,
                    sharpening_strength=sharpening_strength,
                )
                if progress_callback:
                    progress_callback(base_progress + 10)
                if status_callback:
                    status_callback("Enhancing image readability...")

            # 3. 根据用户选择转换为灰度图像
            if selected_features.get("convert_grayscale", False):
                quant_levels = selected_features.get("grayscale_quant_levels", 64)
                scale_factor = selected_features.get("grayscale_scale_factor", 1)
                smoothing_method = selected_features.get(
                    "grayscale_smoothing_method", "Gaussian"
                )
                smoothing_kernel = selected_features.get(
                    "grayscale_smoothing_kernel", 3
                )
                img = convert_grayscale(
                    img,
                    quant_levels=quant_levels,
                    scale_factor=scale_factor,
                    smoothing_method=smoothing_method,
                    smoothing_kernel=smoothing_kernel,
                )
                if progress_callback:
                    progress_callback(base_progress + 15)
                if status_callback:
                    status_callback("Converting to grayscale...")

            # 转换为灰度图像并确定倾斜角度
            grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            angle = determine_skew(grayscale)

            # 如果检测到角度则进行校正
            if angle is not None:
                logging.info(
                    f"Detected skew angle {angle} degrees on page {page_num + 1}"
                )
                if status_callback:
                    status_callback(
                        f"Detected skew angle {angle} degrees on page {page_num + 1}"
                    )
                # 旋转图像校正倾斜，使用自定义背景颜色
                corrected_img = rotate_image(img, angle, background=background_color)
            else:
                logging.info(f"No skew detected on page {page_num + 1}")
                if status_callback:
                    status_callback(f"No skew detected on page {page_num + 1}")
                corrected_img = img

            if progress_callback:
                progress_callback(base_progress + 20)
            if status_callback:
                status_callback("Detecting and correcting skew...")

            # 保存校正后的图像到临时文件夹
            corrected_img_path = os.path.join(temp_folder, f"page_{page_num}.png")
            cv2.imwrite(corrected_img_path, corrected_img)
            output_images.append(corrected_img_path)

            if progress_callback:
                progress_callback(base_progress + 25)
            if status_callback:
                status_callback("Saving corrected images...")

        if progress_callback:
            progress_callback(100)
        if status_callback:
            status_callback("Generating output PDF...")

        # 使用 PIL 将所有校正后的图像重新保存为 PDF
        image_list = [Image.open(img_path).convert("RGB") for img_path in output_images]
        if image_list:
            image_list[0].save(
                output_pdf_path, save_all=True, append_images=image_list[1:]
            )

        if status_callback:
            status_callback("Processing completed successfully.")
        logging.info(f"Processing completed successfully for {output_pdf_path}")

    except Exception as e:
        logging.error(f"Error during deskewing PDF: {e}")
        if status_callback:
            status_callback(f"Error during processing: {e}")
        raise e

    finally:
        if "pdf_document" in locals():
            pdf_document.close()
        # 清理临时文件夹
        for img_path in output_images:
            try:
                os.remove(img_path)
            except Exception as e:
                logging.warning(f"Unable to remove temporary image {img_path}: {e}")
        try:
            shutil.rmtree(temp_folder)
        except Exception as e:
            logging.warning(f"Unable to remove temporary folder {temp_folder}: {e}")
