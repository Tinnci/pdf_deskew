# PDF Deskew Tool

[English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>

## English

### Overview

PDF Deskew Tool is a graphical user interface (GUI) application designed to correct skewed pages in scanned PDF documents. It leverages PyMuPDF, OpenCV, and other powerful libraries to process each page of a PDF and generate a corrected version with improved readability and visual balance. The tool supports multi-language interfaces, theme switching, file drag-and-drop, and detailed progress feedback, aiming to provide a simple and efficient user experience.

### Features

- **Multi-language Support**: Supports both Chinese and English interfaces with easy language switching.
- **Drag-and-Drop File Selection**: Simply drag and drop your PDF files for easy selection.
- **Batch Processing**: Process multiple PDF files simultaneously to improve work efficiency.
- **Real-time Progress Feedback**: Display progress bars and percentages to track processing status.
- **Theme Switching**: Offers multiple interface themes for personalized appearance.
- **Customizable Settings**:
  - **DPI Configuration**: Customize rendering DPI to meet different quality requirements.
  - **Background Color Selection**: Choose or customize background colors to optimize correction results.
  - **Image Enhancement**: Remove watermarks, enhance contrast, denoise, and sharpen images.
- **Logging**: Records important information and errors during processing for debugging and user feedback.
- **Intuitive Interface**: User-friendly design with icons and tooltips for enhanced usability.

### Installation

#### Recommended: Using uv

```bash
uv tool install pdf-deskew
```

This will automatically create two executable commands: `pdf-deskew` (GUI) and `pdf-deskew-cli` (CLI).

#### Alternative: Using pip

```bash
pip install pdf-deskew
```

#### From Source (Development)

```bash
git clone https://github.com/tinnci/pdf_deskew.git
cd pdf_deskew

# Create virtual environment
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

### Usage

#### GUI Application

Start the application:

```bash
pdf-deskew
```

#### Command Line Tool

View help information:

```bash
pdf-deskew-cli --help
```

Basic usage:

```bash
# Simple conversion
pdf-deskew-cli input.pdf

# Specify output file
pdf-deskew-cli input.pdf -o output.pdf

# Custom DPI
pdf-deskew-cli input.pdf -d 600
```

---

<a name="简体中文"></a>

## 简体中文

### 概述

PDF 倾斜校正工具是一款专为纠正扫描 PDF 文档中歪斜页面而设计的图形用户界面 (GUI) 应用程序。它利用 PyMuPDF、OpenCV 和其他强大的库来处理 PDF 的每一页，并生成更正后的版本，具有更好的可读性和视觉平衡。该工具支持多语言界面、主题切换、文件拖放和详细的进度反馈，旨在提供简单高效的用户体验。

### 功能特性

- **多语言支持**：支持中英文界面，可轻松切换语言。
- **拖放文件选择**：简单地拖放 PDF 文件即可选择。
- **批处理**：同时处理多个 PDF 文件，提高工作效率。
- **实时进度反馈**：显示进度条和百分比，跟踪处理状态。
- **主题切换**：提供多种界面主题供选择。
- **自定义设置**：
  - **DPI 配置**：自定义渲染 DPI 以满足不同的质量要求。
  - **背景颜色选择**：选择或自定义背景颜色，优化校正效果。
  - **图像增强**：去除水印、增强对比度、降噪和锐化图像。
- **日志记录**：记录处理过程中的重要信息和错误，便于调试和反馈。
- **直观界面**：用户友好的设计，包含图标和工具提示，增强易用性。

### 安装

#### 推荐：使用 uv

```bash
uv tool install pdf-deskew
```

这将自动创建两个可执行命令：`pdf-deskew` (GUI) 和 `pdf-deskew-cli` (CLI)。

#### 备选：使用 pip

```bash
pip install pdf-deskew
```

#### 从源代码安装（开发）

```bash
git clone https://github.com/tinnci/pdf_deskew.git
cd pdf_deskew

# 创建虚拟环境
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 开发模式安装
uv pip install -e .
```

### 使用方法

#### GUI 应用程序

启动应用程序：

```bash
pdf-deskew
```

#### 命令行工具

查看帮助信息：

```bash
pdf-deskew-cli --help
```

基本用法：

```bash
# 简单转换
pdf-deskew-cli input.pdf

# 指定输出文件
pdf-deskew-cli input.pdf -o output.pdf

# 自定义 DPI
pdf-deskew-cli input.pdf -d 600
```

---

## License

This project is licensed under the MIT License.

## Dependencies

The tool automatically installs the following dependencies:

- **PyQt6** (>=6.7.1): GUI framework
- **PyMuPDF** (>=1.24.13): PDF processing
- **OpenCV** (>=4.10.0.84): Image processing
- **Pillow** (>=11.0.0): Image manipulation
- **numpy** (>=2.1.2): Numerical computing
- **deskew** (>=1.5.1): Skew detection
- **qt-material** (>=2.14): Theme support
- **tqdm** (>=4.66.6): Progress bars

## Usage

### GUI Application

Start the application:

```bash
pdf-deskew
```

**Interface Guide**:

1. **File Selection**:
   - **Input PDF**: Click "Browse" button or drag-and-drop a PDF file
   - **Output PDF**: Specify save location (default: `input_filename_deskewed.pdf`)

2. **Processing Options**:
   - **Use Recommended Settings**: DPI=300, white background
   - **Custom Settings**: Adjust DPI, background color, watermark removal, image enhancement
   - **Image Processing**:
     - Remove watermarks (Inpainting)
     - Enhance images (contrast, denoising, sharpening)
     - Convert to grayscale

3. **Language & Theme**:
   - Switch between English and Chinese
   - Choose from multiple interface themes

### Command-Line Tool

View help:

```bash
pdf-deskew-cli --help
```

Basic usage:

```bash
# Simple conversion
pdf-deskew-cli input.pdf

# Specify output
pdf-deskew-cli input.pdf -o output.pdf

# Custom DPI
pdf-deskew-cli input.pdf -d 600

# With enhancements
pdf-deskew-cli input.pdf --enhance --remove-watermark

# Change background
pdf-deskew-cli input.pdf --bg-color black
```

**Command-line Arguments**:
- `input`: Input PDF file path (required)
- `-o, --output`: Output file path (default: `input_deskewed.pdf`)
- `-d, --dpi`: Rendering DPI, range 72-1200 (default: 300)
- `--bg-color`: Background color, white or black (default: white)
- `--enhance`: Enable image enhancement
- `--remove-watermark`: Enable watermark removal
- `-v, --version`: Show version number

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.12 or higher
- **Optional**: [uv package manager](https://docs.astral.sh/uv/) (recommended)

## Notes

- **Special Characters in Paths**: If your file paths contain spaces or special characters, use quotes to avoid errors.
- **Temporary Files**: The application creates a temporary folder for intermediate images, which is automatically cleaned up after processing.
- **Logging**: Processing logs are recorded in `pdf_deskew.log` for debugging purposes.
- **Theme Switching**: Theme changes take effect immediately without requiring application restart.

## Development

To contribute to this project:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tinnci/pdf_deskew.git
   cd pdf_deskew
   ```

2. **Set Up Environment**:
   ```bash
   uv venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Run Tests**:
   ```bash
   pytest
   ```

4. **Submit Changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin your-branch
   ```

## License

This project is licensed under the MIT License. You are free to use and modify it.

## Support

For issues or questions:
- GitHub Issues: https://github.com/tinnci/pdf_deskew/issues
- Email: luoyido@outlook.com

---

Thank you for using PDF Deskew Tool! If you find it useful, please give us a ⭐ on GitHub and share it with others who might benefit.
