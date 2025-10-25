# PyPI 发布指南

## 准备发布

### 1. 配置虚拟环境

项目已使用 uv 创建虚拟环境 `.venv`，包含以下工具：
- `build`：用于构建分发包
- `twine`：用于上传到 PyPI
- 所有项目依赖

### 2. 激活虚拟环境

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. PyPI 配置

要使用提供的 API token 进行发布，需要在 `$HOME/.pypirc` 文件中配置：

```ini
[pypi]
username = __token__
password = pypi-[YOUR-TOKEN]
```

**重要**：永远不要将此文件提交到版本控制！

## 构建包

### 构建源代码分发和 wheel

```bash
python -m build
```

这将在 `dist/` 目录中生成：
- `pdf-deskew-0.1.0.tar.gz`：源代码分发
- `pdf-deskew-0.1.0-py3-none-any.whl`：wheel 文件

### 检查构建产物

```bash
twine check dist/*
```

## 发布到 PyPI

### 测试发布（推荐）

首先发布到 TestPyPI：

```bash
twine upload --repository testpypi dist/*
```

然后测试安装：

```bash
pip install --index-url https://test.pypi.org/simple/ pdf-deskew
```

### 生产发布

```bash
twine upload dist/*
```

或使用 API token：

```bash
twine upload -u __token__ -p pypi-[YOUR-TOKEN] dist/*
```

## 版本更新

发布新版本时：

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `src/deskew_tool/__init__.py` 中的 `__version__`
3. 更新 `src/pdf_deskew_ui/__init__.py` 中的 `__version__`
4. 提交更改并创建 Git 标签：
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

## 发布清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG/README
- [ ] 运行 `python -m build`
- [ ] 运行 `twine check dist/*`
- [ ] 在 TestPyPI 上测试
- [ ] 运行 `twine upload dist/*`
- [ ] 创建 Git 标签

## 常见问题

### 忘记了 API token 怎么办？

生成新的 token，但旧的 token 需要从 PyPI 账户撤销。

### 如何查看已发布的包？

https://pypi.org/project/pdf-deskew/

### 如何修改已发布的版本？

不能直接修改。必须撤销上传（需要 PyPI 支持）并发布新版本。

## 相关链接

- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Twine 文档](https://twine.readthedocs.io/)
- [Build 工具](https://github.com/pypa/build)
