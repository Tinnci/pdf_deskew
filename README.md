# PDF Deskew Tool

[![PyPI version](https://badge.fury.io/py/pdf-deskew.svg)](https://badge.fury.io/py/pdf-deskew)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Tinnci/pdf_deskew/actions/workflows/ci.yml/badge.svg)](https://github.com/Tinnci/pdf_deskew/actions/workflows/ci.yml)

PDF Deskew Tool is a desktop and command-line utility for correcting skewed scanned PDF pages. It renders pages with PyMuPDF, detects skew with OpenCV and `deskew`, then writes a corrected PDF with optional cleanup steps.

PDF Deskew Tool 是一个用于扫描 PDF 页面纠偏的桌面和命令行工具。它使用 PyMuPDF 渲染页面，通过 OpenCV 和 `deskew` 检测倾斜角度，并可在输出前执行可选的图像清理。

## When to Use / 适用场景

- Scanned PDFs with slightly rotated pages / 扫描后页面轻微倾斜的 PDF
- Batch-friendly local processing from a terminal / 适合在本地命令行自动化处理
- Visual review and one-file processing from a desktop UI / 适合在桌面界面预览并处理单个文件

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

Install as a command-line tool with `uv`:

```bash
uv tool install pdf-deskew
```

Or install with `pip`:

```bash
pip install pdf-deskew
```

For local development from a clone, use the development workflow in [DEVELOPMENT.md](DEVELOPMENT.md).

如需从源码仓库本地开发，请使用 [DEVELOPMENT.md](DEVELOPMENT.md) 中的开发流程。

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

Common CLI options / 常用命令行参数:

- `-o, --output`: output PDF path / 输出 PDF 路径
- `-d, --dpi`: render DPI, default `300` / 渲染 DPI，默认 `300`
- `--bg-color`: background fill color, `white` or `black` / 背景填充色，支持 `white` 或 `black`
- `--enhance`: enable image enhancement / 启用图像增强
- `--contrast-level`: enhancement strength, `1` to `3` / 对比度增强等级，`1` 到 `3`
- `--denoising`: `Gaussian` or `Median` / 降噪方式，`Gaussian` 或 `Median`
- `--sharpen`: enable sharpening / 启用锐化
- `--remove-watermark`: enable watermark inpainting / 启用水印修复去除
- `--watermark-threshold`: watermark mask threshold, `0` to `255` / 水印遮罩阈值，`0` 到 `255`
- `--grayscale`: convert output pages to grayscale / 输出灰度页面

## Notes / 注意事项

- The CLI currently accepts one input PDF per command. Use a shell loop or script for multiple files.
- Higher DPI can improve detection quality, but increases memory use and processing time.
- Watermark removal is an image inpainting pass. Review output before replacing original documents.

- 命令行当前每次处理一个输入 PDF；批量处理可使用 shell 循环或脚本。
- 较高 DPI 可能提升检测质量，但会增加内存占用和处理时间。
- 水印去除属于图像修复处理，替换原文件前请先检查输出结果。

## Development / 开发

Development setup, quality checks, release notes, and contribution guidance are maintained in [DEVELOPMENT.md](DEVELOPMENT.md).

开发环境、质量检查、发布说明和贡献流程请见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## Support / 支持

- Issues: [GitHub Issues](https://github.com/Tinnci/pdf_deskew/issues)
- Email: luoyido@outlook.com

## License / 许可证

This project is licensed under the [MIT License](LICENSE).

本项目使用 [MIT License](LICENSE)。
