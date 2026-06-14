# PDF Deskew Tool

[![PyPI version](https://badge.fury.io/py/pdf-deskew.svg)](https://badge.fury.io/py/pdf-deskew)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Tinnci/pdf_deskew/actions/workflows/ci.yml/badge.svg)](https://github.com/Tinnci/pdf_deskew/actions/workflows/ci.yml)

PDF Deskew Tool is a desktop and command-line utility for correcting skewed scanned PDF pages. It renders pages with PyMuPDF, detects skew with OpenCV and `deskew`, then writes a corrected PDF with optional cleanup steps.

PDF Deskew Tool 是一个用于扫描 PDF 页面纠偏的桌面和命令行工具。它使用 PyMuPDF 渲染页面，通过 OpenCV 和 `deskew` 检测倾斜角度，并可在输出前执行可选的图像清理。

## Features / 功能

- Automatic page deskewing / 自动页面纠偏
- Parallel page processing for a single PDF / 单个 PDF 内的页面并行处理
- Optional watermark removal with inpainting / 可选的水印修复去除
- Optional contrast, denoising, sharpening, and grayscale conversion / 可选的对比度、降噪、锐化和灰度转换
- PyQt6 GUI with drag and drop, before/after preview, progress, cancel, themes, and Chinese/English UI / PyQt6 图形界面，支持拖放、前后预览、进度、取消、主题和中英文切换
- CLI entry point for automation / 面向自动化流程的命令行入口

## Requirements / 环境要求

- Python 3.12 or higher
- Windows, macOS, or Linux
- Runtime dependencies are installed by the package: PyQt6, PyMuPDF, OpenCV, Pillow, NumPy, `deskew`, `qt-material`, and `tqdm`

## Installation / 安装

Using `uv`:

```bash
uv tool install pdf-deskew
```

Using `pip`:

```bash
pip install pdf-deskew
```

## Usage / 使用

Start the GUI / 启动图形界面:

```bash
pdf-deskew
```

Run the CLI / 使用命令行:

```bash
# Output defaults to input_deskewed.pdf
pdf-deskew-cli input.pdf

# Custom output path and render DPI
pdf-deskew-cli input.pdf -o output.pdf -d 600

# Enable cleanup options
pdf-deskew-cli input.pdf --enhance --remove-watermark --grayscale --sharpen

# Show all CLI options
pdf-deskew-cli --help
```

## Development / 开发

Development setup, quality checks, release notes, and contribution guidance are maintained in [DEVELOPMENT.md](DEVELOPMENT.md).

开发环境、质量检查、发布说明和贡献流程请见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## Support / 支持

- Issues: [GitHub Issues](https://github.com/Tinnci/pdf_deskew/issues)
- Email: luoyido@outlook.com

## License / 许可证

This project is licensed under the [MIT License](LICENSE).

本项目使用 [MIT License](LICENSE)。
