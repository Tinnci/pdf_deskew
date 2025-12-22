# PDF Deskew Tool

[![PyPI version](https://badge.fury.io/py/pdf-deskew.svg)](https://badge.fury.io/py/pdf-deskew)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/tinnci/pdf_deskew/actions/workflows/ci.yml/badge.svg)](https://github.com/tinnci/pdf_deskew/actions/workflows/ci.yml)

[English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>

## English

### Overview

**PDF Deskew Tool** is a powerful GUI and CLI application designed to automatically detect and correct skewed pages in scanned PDF documents. By leveraging PyMuPDF and OpenCV, it provides high-quality image processing to ensure your documents are perfectly aligned and highly readable.

### Key Features

- **Smart Deskewing**: Automatically detects and corrects rotation angles.
- **Batch Processing**: Handle multiple PDF files simultaneously.
- **Image Enhancement**:
  - **Watermark Removal**: Advanced inpainting to clean up documents.
  - **Quality Boost**: Contrast enhancement, denoising, and sharpening.
  - **Grayscale Conversion**: Reduce file size and improve clarity.
- **User Friendly**:
  - **Modern GUI**: Built with PyQt6 and Material Design themes.
  - **Drag & Drop**: Easy file selection.
  - **Bilingual**: Full support for English and Chinese.
- **Flexible CLI**: Robust command-line interface for automation and power users.

### Installation

#### Recommended: Using [uv](https://docs.astral.sh/uv/)

```bash
uv tool install pdf-deskew
```

#### Using pip

```bash
pip install pdf-deskew
```

### Usage

#### GUI Application
Simply run the command to open the interface:
```bash
pdf-deskew
```

#### Command Line Interface (CLI)
```bash
# Basic usage (output saved as input_deskewed.pdf)
pdf-deskew-cli input.pdf

# Custom output and DPI
pdf-deskew-cli input.pdf -o output.pdf -d 600

# Enable all enhancements
pdf-deskew-cli input.pdf --enhance --remove-watermark
```

---

<a name="简体中文"></a>

## 简体中文

### 概述

**PDF 倾斜校正工具 (PDF Deskew Tool)** 是一款功能强大的图形界面 (GUI) 和命令行 (CLI) 应用程序，专门用于自动检测并纠正扫描 PDF 文档中的页面倾斜。通过结合 PyMuPDF 和 OpenCV 的强大功能，它能提供高质量的图像处理，确保您的文档排列整齐、清晰易读。

### 核心功能

- **智能纠偏**：自动检测并修正页面旋转角度。
- **批量处理**：支持同时处理多个 PDF 文件，提高效率。
- **图像增强**：
  - **去除水印**：使用先进的修复算法清理文档背景。
  - **画质提升**：对比度增强、降噪及锐化处理。
  - **灰度转换**：减小文件体积并提升文字清晰度。
- **用户友好**：
  - **现代界面**：基于 PyQt6 和 Material Design 主题构建。
  - **拖放支持**：支持直接拖入文件进行处理。
  - **双语支持**：完整的中英文界面切换。
- **灵活的命令行**：为高级用户和自动化脚本提供强大的 CLI 支持。

### 安装方法

#### 推荐方式：使用 [uv](https://docs.astral.sh/uv/)

```bash
uv tool install pdf-deskew
```

#### 使用 pip

```bash
pip install pdf-deskew
```

### 使用说明

#### 图形界面 (GUI)
直接运行以下命令启动程序：
```bash
pdf-deskew
```

#### 命令行界面 (CLI)
```bash
# 基本用法（输出默认为 input_deskewed.pdf）
pdf-deskew-cli input.pdf

# 指定输出路径和 DPI
pdf-deskew-cli input.pdf -o output.pdf -d 600

# 开启所有增强功能
pdf-deskew-cli input.pdf --enhance --remove-watermark
```

---

## System Requirements / 系统要求

- **OS**: Windows, macOS, or Linux
- **Python**: 3.12 or higher
- **Dependencies**: PyQt6, PyMuPDF, OpenCV, Pillow, numpy, deskew, qt-material, tqdm

## Development / 开发

```bash
git clone https://github.com/tinnci/pdf_deskew.git
cd pdf_deskew
uv venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
uv pip install -e .
pytest
```

## License / 许可证

This project is licensed under the **MIT License**.

## Support / 支持

- **Issues**: [GitHub Issues](https://github.com/tinnci/pdf_deskew/issues)
- **Email**: luoyido@outlook.com
