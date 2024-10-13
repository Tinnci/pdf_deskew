import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from deskew import determine_skew
import os
import sys
from tqdm import tqdm
import shutil
import shlex
import os.path

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

def deskew_pdf(input_pdf_path, output_pdf_path, dpi=300, background_color=(255, 255, 255)):
    # 打开 PDF 文件，添加错误处理
    try:
        pdf_document = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"无法打开 PDF 文件: {e}")
        sys.exit(1)
    
    output_images = []
    temp_folder = "temp_images"

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    try:
        # 逐页处理 PDF
        for page_num in tqdm(range(len(pdf_document)), desc="处理进度"):
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
                # 旋转图像校正倾斜，使用自定义背景颜色
                corrected_img = rotate_image(img, angle, background=background_color)
            else:
                corrected_img = img

            # 保存校正后的图像到临时文件夹
            corrected_img_path = os.path.join(temp_folder, f"page_{page_num}.png")
            cv2.imwrite(corrected_img_path, corrected_img)
            output_images.append(corrected_img_path)

        # 使用 PIL 将所有校正后的图像重新保存为 PDF
        image_list = [Image.open(img_path).convert("RGB") for img_path in output_images]
        if image_list:
            image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])

    finally:
        # 清理临时文件夹
        for img_path in output_images:
            os.remove(img_path)
        shutil.rmtree(temp_folder)

    print(f"校准后的 PDF 已保存到: {output_pdf_path}")

if __name__ == "__main__":
    # 交互式输入
    print("欢迎使用 PDF 校准工具！\n输入 'h' 查看帮助信息，输入 'q' 退出程序。")
    while True:
        initial_input = input("请输入您的选择 (按回车继续选择待处理的输入文件): ").strip().lower()
        if initial_input == 'h':
            print("""帮助信息：
此工具用于校准 PDF 文件中的扫描图像。
您可以选择文件、设置 DPI 以及背景颜色。
以下是使用示例：
1. 按提示选择输入和输出 PDF 文件。
2. 选择是否使用默认的 DPI 和背景颜色。
3. 若不使用默认设置，可以手动输入 DPI 和背景颜色（例如：'255,255,255' 表示白色背景）。
4. 输入 'h' 查看帮助，输入 'q' 退出程序。
""")
        elif initial_input == 'q':
            print("程序已退出。")
            sys.exit(0)
        else:
            break

    # 用户输入输入 PDF 文件路径
    input_pdf_path = input("请输入输入 PDF 文件的路径 (或按回车选择默认文件): ").strip()
    input_pdf_path = shlex.split(input_pdf_path)[0] if input_pdf_path else input_pdf_path
    while not os.path.isfile(input_pdf_path):
        print("文件无效，请重新输入有效的 PDF 文件路径。")
        input_pdf_path = input("请输入输入 PDF 文件的路径: ").strip()
        input_pdf_path = shlex.split(input_pdf_path)[0] if input_pdf_path else input_pdf_path

    # 用户输入输出 PDF 文件路径，默认使用 输入文件名_矫正.pdf，保存到与输入文件相同的目录
    input_dir = os.path.dirname(input_pdf_path)
    default_output_pdf_path = os.path.join(input_dir, os.path.splitext(os.path.basename(input_pdf_path))[0] + "_矫正.pdf")
    output_pdf_path = input(f"请输入输出 PDF 文件的路径 (按回车使用默认值 '{default_output_pdf_path}'): ").strip() or default_output_pdf_path
    
    # 用户选择使用推荐设置或自定义设置
    use_defaults = input("是否使用推荐设置？(Y/n): ").strip().lower() != 'n'
    
    # 使用推荐设置
    if use_defaults:
        dpi = 300
        background_color = (255, 255, 255)
    else:
        # 自定义 DPI
        try:
            dpi = int(input("请输入渲染 PDF 页面的 DPI (按回车使用默认值 300): ").strip() or 300)
        except ValueError:
            print("无效的 DPI 值，使用默认值 300。")
            dpi = 300
        
        # 自定义背景颜色
        background_input = input("请输入校正区域的背景颜色 ('white', 'black' 或逗号分隔的 RGB 值，如 '255,255,255') (按回车使用默认值 'white'): ").strip().lower()
        if background_input == "black":
            background_color = (0, 0, 0)
        elif background_input == "white" or not background_input:
            background_color = (255, 255, 255)
        else:
            try:
                background_color = tuple(map(int, background_input.split(",")))
                if len(background_color) != 3:
                    raise ValueError
            except ValueError:
                print("无效的背景颜色，使用默认值 'white'。")
                background_color = (255, 255, 255)

    # 预览设置并确认
    print("\n您已输入以下设置：")
    print(f"输入 PDF 文件路径: {input_pdf_path}")
    print(f"输出 PDF 文件路径: {output_pdf_path}")
    print(f"渲染 DPI: {dpi}")
    print(f"背景颜色: {background_color}")
    confirm = input("请确认这些设置是否正确 (Y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消。请重新运行程序并输入正确的设置。")
        sys.exit(0)

    # 执行校准
    deskew_pdf(input_pdf_path, output_pdf_path, dpi=dpi, background_color=background_color)