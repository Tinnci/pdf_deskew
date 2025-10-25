# PDF 倾斜校正工具

[English](./README.md)

## 概述

PDF 倾斜校正工具是一款专为纠正扫描 PDF 文档中歪斜页面而设计的图形用户界面 (GUI) 应用程序。它利用 PyMuPDF、OpenCV 和其他强大的库来处理 PDF 的每一页，并生成更正后的版本，具有更好的可读性和视觉平衡。该工具支持多语言界面、主题切换、文件拖放和详细的进度反馈，旨在提供简单高效的用户体验。

## 功能特性

- **多语言支持**：支持中英文界面，可轻松切换语言。
- **拖放文件选择**：简单地拖放 PDF 文件即可选择。
- **批处理**：同时处理多个 PDF 文件，提高工作效率。
- **实时进度反馈**：显示进度条和百分比，跟踪处理状态。
- **主题切换**：提供多种界面主题供选择。
- **自定义设置**：
  - **DPI 配置**：自定义渲染 DPI 以满足不同的质量要求。
  - **背景颜色选择**：选择或自定义背景颜色，优化校正效果。
- **日志记录**：记录处理过程中的重要信息和错误，便于调试和反馈。
- **直观界面**：用户友好的设计，包含图标和工具提示，增强易用性。

## 安装

### 方法 1：使用 pip（推荐）

```bash
pip install pdf-deskew
```

### 方法 2：使用 uv（快速安装）

```bash
uv tool install pdf-deskew
```

### 方法 3：从源代码安装（开发）

```bash
git clone https://github.com/tinnci/pdf_deskew.git
cd pdf_deskew

# 创建虚拟环境
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 开发模式安装
uv pip install -e .
```

## 依赖项

工具会自动安装以下依赖项：

- **PyQt6** (>=6.7.1)：图形用户界面框架
- **PyMuPDF** (>=1.24.13)：PDF 处理库
- **OpenCV** (>=4.10.0.84)：图像处理库
- **Pillow** (>=11.0.0)：图像操作库
- **numpy** (>=2.1.2)：数值计算库
- **deskew** (>=1.5.1)：倾斜检测库
- **qt-material** (>=2.14)：主题支持库
- **tqdm** (>=4.66.6)：进度条库

## 使用方法

### GUI 应用程序

启动应用程序：

```bash
pdf-deskew
```

**界面指南**：

1. **文件选择**：
   - **输入 PDF**：点击"浏览"按钮或拖放 PDF 文件
   - **输出 PDF**：指定保存位置（默认：`输入文件名_deskewed.pdf`）

2. **处理选项**：
   - **使用推荐设置**：DPI=300，白色背景
   - **自定义设置**：调整 DPI、背景颜色、去水印、图像增强
   - **图像处理**：
     - 去除水印（图像修复）
     - 增强图像（对比度、降噪、锐化）
     - 转换为灰度图

3. **语言与主题**：
   - 在中英文之间切换
   - 选择多种界面主题

### 命令行工具

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

# 启用增强功能
pdf-deskew-cli input.pdf --enhance --remove-watermark

# 更改背景颜色
pdf-deskew-cli input.pdf --bg-color black
```

**命令行参数**：
- `input`：输入 PDF 文件路径（必需）
- `-o, --output`：输出文件路径（默认：`input_deskewed.pdf`）
- `-d, --dpi`：渲染 DPI，范围 72-1200（默认：300）
- `--bg-color`：背景颜色，white 或 black（默认：white）
- `--enhance`：启用图像增强
- `--remove-watermark`：启用去水印功能
- `-v, --version`：显示版本号

## 系统要求

- **操作系统**：Windows、macOS 或 Linux
- **Python**：3.12 及更高版本
- **可选**：[uv 包管理器](https://docs.astral.sh/uv/)（推荐）

## 注意事项

- **路径中的特殊字符**：如果文件路径中包含空格或特殊字符，请使用引号以避免错误。
- **临时文件**：应用程序为中间图像创建临时文件夹，处理完成后会自动清理。
- **日志记录**：处理日志记录在 `pdf_deskew.log` 中，用于调试。
- **主题切换**：主题更改立即生效，无需重启应用程序。

## 开发

贡献代码：

1. **克隆仓库**：
   ```bash
   git clone https://github.com/tinnci/pdf_deskew.git
   cd pdf_deskew
   ```

2. **设置开发环境**：
   ```bash
   uv venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **运行测试**：
   ```bash
   pytest
   ```

4. **提交更改**：
   ```bash
   git add .
   git commit -m "更改描述"
   git push origin your-branch
   ```

## 许可证

本项目采用 MIT 许可证。您可以自由使用和修改。

## 支持

如有问题或建议：
- GitHub Issues：https://github.com/tinnci/pdf_deskew/issues
- 邮箱：luoyido@outlook.com

## 日志记录

应用程序生成 `pdf_deskew.log` 文件，其中包含重要事件和错误消息，有助于调试和故障排除。

---

感谢使用 PDF 倾斜校正工具！如果对您有帮助，请在 GitHub 上给我们一个 ⭐ 并分享给其他可能受益的人。
