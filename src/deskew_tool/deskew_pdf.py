# src/deskew_tool/deskew_pdf.py

import concurrent.futures
import logging
import os
import shutil
import tempfile
import warnings
from collections.abc import Callable
from dataclasses import dataclass

import cv2
import fitz  # PyMuPDF
import numpy as np
from deskew import determine_skew
from PIL import Image

from .config import DeskewConfig

# Suppress SwigPyPacked deprecation warnings from PyMuPDF/SWIG
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message="builtin type .* has no __module__"
)


class ProcessingCancelledError(RuntimeError):
    """Raised when PDF processing is cancelled by the caller."""


ProcessingCancelled = ProcessingCancelledError


@dataclass(frozen=True)
class ProcessingCallbacks:
    progress: Callable[[int], None] | None = None
    current_page: Callable[[int], None] | None = None
    status: Callable[[str], None] | None = None
    is_running: Callable[[], bool] | None = None


def _emit(callback: Callable[..., None] | None, *args: object) -> None:
    if callback:
        callback(*args)


def get_pdf_page_count(
    input_pdf_path: str | os.PathLike[str],
    status_callback: Callable[[str], None] | None = None,
) -> int:
    try:
        with fitz.open(os.fspath(input_pdf_path)) as doc:
            return len(doc)
    except Exception as exc:
        message = f"无法打开 PDF 文件: {exc}"
        logging.exception(message)
        _emit(status_callback, message)
        raise OSError(message) from exc


def _pixmap_to_bgr(pix: fitz.Pixmap) -> np.ndarray:
    image: np.ndarray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )

    if image.ndim == 2 or pix.n == 1:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if pix.n == 3:
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if pix.n == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

    raise ValueError(f"Unsupported pixmap channel count: {pix.n}")


def _odd_kernel_size(value: int, default: int = 3) -> int:
    try:
        kernel = int(value)
    except (TypeError, ValueError):
        logging.warning("Invalid kernel size %r, defaulting to %s", value, default)
        return default

    if kernel < 1:
        logging.warning("Kernel size %s is too small, defaulting to %s", value, default)
        return default
    if kernel % 2 == 0:
        kernel += 1
    return kernel


def _quantization_step(quant_levels: int) -> int:
    try:
        levels = int(quant_levels)
    except (TypeError, ValueError):
        logging.warning("Invalid quantization level %r, defaulting to 64", quant_levels)
        levels = 64

    if levels < 2:
        logging.warning("Quantization level %s is too low, using 2", levels)
        levels = 2
    elif levels > 256:
        logging.warning("Quantization level %s is too high, using 256", levels)
        levels = 256

    return max(1, 256 // levels)


def _positive_scale_factor(scale_factor: int) -> int:
    try:
        factor = int(scale_factor)
    except (TypeError, ValueError):
        logging.warning("Invalid scale factor %r, defaulting to 1", scale_factor)
        return 1

    if factor < 1:
        logging.warning("Scale factor %s is too small, defaulting to 1", scale_factor)
        return 1
    return factor


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
    contrast_settings = {
        1: (1.2, 20),
        2: (1.5, 30),
        3: (1.8, 40),
    }
    alpha, beta = contrast_settings.get(contrast_level, contrast_settings[2])

    contrasted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    denoising_kernel = _odd_kernel_size(denoising_kernel)
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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    quant_step = _quantization_step(quant_levels)
    gray_quant = np.floor_divide(gray, quant_step) * quant_step
    gray_quant = gray_quant.astype(np.uint8)

    scale_factor = _positive_scale_factor(scale_factor)
    if scale_factor != 1:
        width = int(gray_quant.shape[1] * scale_factor)
        height = int(gray_quant.shape[0] * scale_factor)
        gray_quant = cv2.resize(
            gray_quant, (width, height), interpolation=cv2.INTER_LINEAR
        )

    smoothing_kernel = _odd_kernel_size(smoothing_kernel)
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


def _apply_configured_processing(image: np.ndarray, config: DeskewConfig) -> np.ndarray:
    if config.remove_watermark:
        image = remove_watermark(
            image,
            method=config.watermark_method,
            algorithm=config.inpainting_algorithm,
            threshold=config.watermark_threshold,
        )

    if config.enhance_image:
        image = enhance_image(
            image,
            contrast_level=config.contrast_level,
            denoising_method=config.denoising_method,
            denoising_kernel=config.denoising_kernel,
            sharpening=config.sharpening,
            sharpening_strength=config.sharpening_strength,
        )

    if config.convert_grayscale:
        image = convert_grayscale(
            image,
            quant_levels=config.grayscale_quant_levels,
            scale_factor=config.grayscale_scale_factor,
            smoothing_method=config.grayscale_smoothing_method,
            smoothing_kernel=config.grayscale_smoothing_kernel,
        )

    return image


def _deskew_image(
    image: np.ndarray, background_color: tuple[int, int, int]
) -> np.ndarray:
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    if angle is None:
        return image
    return rotate_image(image, angle, background=background_color)


def render_page_image(
    input_pdf_path: str | os.PathLike[str], page_num: int, dpi: int
) -> np.ndarray:
    """Render a PDF page to a BGR image suitable for OpenCV operations."""
    with fitz.open(os.fspath(input_pdf_path)) as doc:
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        return _pixmap_to_bgr(pix)


def process_single_page(
    page_num: int,
    input_pdf_path: str | os.PathLike[str],
    config: DeskewConfig,
    temp_folder: str | os.PathLike[str],
) -> tuple[int, str | None]:
    """
    处理单个页面的辅助函数，供多进程调用。
    """
    try:
        img = render_page_image(input_pdf_path, page_num, config.dpi)
        img = _apply_configured_processing(img, config)
        corrected_img = _deskew_image(img, config.background_color)

        img_path = os.path.join(os.fspath(temp_folder), f"page_{page_num}.png")
        if not cv2.imwrite(img_path, corrected_img):
            raise OSError(f"Unable to write temporary image: {img_path}")

        return page_num, img_path
    except Exception:
        logging.exception("Error processing page %s", page_num)
        return page_num, None


def _update_page_progress(
    callbacks: ProcessingCallbacks, completed_count: int, total_pages: int
) -> None:
    _emit(callbacks.progress, int((completed_count / total_pages) * 100))
    _emit(callbacks.current_page, completed_count)
    _emit(callbacks.status, f"Processed page {completed_count}/{total_pages}")


def _collect_page_images(
    input_pdf_path: str | os.PathLike[str],
    config: DeskewConfig,
    temp_folder: str,
    total_pages: int,
    callbacks: ProcessingCallbacks,
) -> list[str]:
    results: list[str | None] = [None] * total_pages
    completed_count = 0
    max_workers = min(os.cpu_count() or 4, total_pages)
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
    cancelled = False

    try:
        future_to_page = {
            executor.submit(
                process_single_page, i, input_pdf_path, config, temp_folder
            ): i
            for i in range(total_pages)
        }

        for future in concurrent.futures.as_completed(future_to_page):
            if callbacks.is_running and not callbacks.is_running():
                cancelled = True
                executor.shutdown(wait=True, cancel_futures=True)
                _emit(callbacks.status, "Processing cancelled.")
                logging.info("Processing cancelled by user.")
                raise ProcessingCancelledError("Processing cancelled.")

            try:
                page_num, img_path = future.result()
            except Exception:
                logging.exception("Page processing generated an exception")
            else:
                if img_path:
                    results[page_num] = img_path

            completed_count += 1
            _update_page_progress(callbacks, completed_count, total_pages)

    finally:
        if not cancelled:
            executor.shutdown()

    output_images = [path for path in results if path is not None]
    if not output_images:
        raise RuntimeError("No pages were successfully processed.")
    return output_images


def _save_images_as_pdf(
    image_paths: list[str], output_pdf_path: str | os.PathLike[str]
) -> None:
    images: list[Image.Image] = []
    try:
        for image_path in image_paths:
            with Image.open(image_path) as image:
                images.append(image.convert("RGB"))

        images[0].save(
            os.fspath(output_pdf_path),
            save_all=True,
            append_images=images[1:],
        )
    finally:
        for image in images:
            image.close()


def _cleanup_processing_files(temp_folder: str | None) -> None:
    if temp_folder:
        try:
            shutil.rmtree(temp_folder)
        except FileNotFoundError:
            pass
        except Exception as exc:
            logging.warning(
                "Unable to remove temporary folder %s: %s", temp_folder, exc
            )


def deskew_pdf(
    input_pdf_path: str | os.PathLike[str],
    output_pdf_path: str | os.PathLike[str],
    config: DeskewConfig | None = None,
    progress_callback: Callable[[int], None] | None = None,
    current_page_callback: Callable[[int], None] | None = None,
    status_callback: Callable[[str], None] | None = None,
    is_running_callback: Callable[[], bool] | None = None,
) -> None:
    """
    校正 PDF 文件中的图像倾斜，并根据用户选择应用图像处理功能。
    """
    config = config or DeskewConfig()
    callbacks = ProcessingCallbacks(
        progress=progress_callback,
        current_page=current_page_callback,
        status=status_callback,
        is_running=is_running_callback,
    )

    temp_folder: str | None = None
    output_images: list[str] = []

    try:
        total_pages = get_pdf_page_count(input_pdf_path, status_callback)
        if total_pages <= 0:
            raise RuntimeError("Input PDF contains no pages.")

        temp_folder = tempfile.mkdtemp(prefix="pdf_deskew_")
        output_images = _collect_page_images(
            input_pdf_path, config, temp_folder, total_pages, callbacks
        )

        _emit(status_callback, "Generating output PDF...")
        _save_images_as_pdf(output_images, output_pdf_path)
        _emit(status_callback, "Processing completed successfully.")
        logging.info("Processing completed successfully for %s", output_pdf_path)

    except ProcessingCancelledError:
        raise
    except OSError:
        raise
    except Exception as exc:
        logging.exception("Error during deskewing PDF")
        _emit(status_callback, f"Error during processing: {exc}")
        raise

    finally:
        _cleanup_processing_files(temp_folder)
