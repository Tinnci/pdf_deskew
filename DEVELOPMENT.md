# Development Guide

This guide is for contributors who build, test, or release PDF Deskew Tool. User-facing installation and usage examples live in [README.md](README.md).

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) for dependency and environment management
- Platform packages needed by OpenCV and Qt:
  - Ubuntu/Debian: `sudo apt-get install libgl1 libglib2.0-0`
  - Windows/macOS: usually handled by the Python wheels and installers

## Setup

```bash
git clone https://github.com/Tinnci/pdf_deskew.git
cd pdf_deskew
uv sync --dev
```

Use `--frozen` when you need to verify the lockfile exactly:

```bash
uv run --frozen pytest
```

## Run Locally

GUI:

```bash
uv run pdf-deskew
```

CLI:

```bash
uv run pdf-deskew-cli --help
uv run pdf-deskew-cli input.pdf -o output.pdf
```

## Quality Checks

Run these before opening a pull request or pushing release changes:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

Focused test runs are useful while iterating:

```bash
uv run pytest tests/test_deskew.py -q
uv run pytest tests/test_ui.py -q
```

## Project Layout

- `src/deskew_tool/config.py`: shared configuration dataclass and language enum
- `src/deskew_tool/deskew_pdf.py`: core PDF rendering, image processing, deskewing, progress, cancellation, and PDF output
- `src/deskew_tool/__init__.py`: CLI entry point and package version
- `src/pdf_deskew_ui/`: PyQt6 GUI, widgets, styles, and worker thread
- `tests/`: unit and UI smoke tests

Keep core processing reusable from both the CLI and GUI. UI code should call shared helpers instead of duplicating PDF rendering or image conversion logic.

## Documentation Maintenance

- Keep `README.md` focused on users: what the tool does, install commands, basic GUI and CLI usage, support, and license.
- Keep this file focused on contributors: setup, local runs, checks, release flow, and architecture notes.
- When CLI flags, entry points, supported Python versions, or release workflows change, update both docs only where the information is relevant.
- Avoid claiming features that are not implemented. For example, the tool processes pages in parallel within one PDF; it does not currently accept multiple PDF inputs in one CLI command.

## CI and Release

GitHub Actions runs on pushes and pull requests to `main`:

- `ruff check .`
- `ruff format --check .`
- `mypy src`
- `pytest` with coverage

Release publishing is handled by `.github/workflows/release.yml` when a tag matching `v*` is pushed. The workflow uses PyPI Trusted Publishing through OIDC, so no PyPI API token should be stored in GitHub Secrets.

## Versioning

The package version is defined in `src/deskew_tool/__init__.py`.

To release:

```bash
# 1. Update __version__ in src/deskew_tool/__init__.py
# 2. Commit the version change
git tag v0.1.x
git push origin main --tags
```
