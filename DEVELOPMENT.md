# Development Guide

This document provides instructions for setting up the development environment and contributing to the PDF Deskew Tool.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Recommended)
- Python 3.12 or higher
- System dependencies (for OpenCV and Qt):
  - **Ubuntu/Debian**: `sudo apt-get install libgl1 libglib2.0-0`
  - **Windows/macOS**: Usually handled by the installers.

## Setup Development Environment

We use `uv` for dependency management. To set up the project:

```bash
# Clone the repository
git clone https://github.com/Tinnci/pdf_deskew.git
cd pdf_deskew

# Create virtual environment and install dependencies
uv sync --all-extras --dev
```

## Running the Application

### GUI Mode
```bash
uv run pdf-deskew
```

### CLI Mode
```bash
uv run pdf-deskew-cli --help
```

## Code Quality

We use `ruff` for linting and formatting, and `mypy` for type checking.

```bash
# Run linting
uv run ruff check .

# Run formatting check
uv run ruff format --check .

# Run type checking
uv run mypy src
```

## Testing

We use `pytest` for testing.

```bash
uv run pytest
```

## CI/CD and Publishing

### GitHub Actions
- **CI**: Triggered on every push and pull request to `main`. Runs linting, type checking, and tests.
- **Release**: Triggered when a new tag starting with `v*` is pushed. Builds the package and publishes it to PyPI.

### Trusted Publishing
This project uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/). No API tokens are stored in GitHub Secrets. The `release.yml` workflow uses OIDC to authenticate with PyPI.

To configure a new publisher:
1. Go to your project on PyPI.
2. Navigate to **Settings** > **Publishing**.
3. Add a new GitHub publisher with:
   - Owner: `Tinnci`
   - Repository: `pdf_deskew`
   - Workflow: `release.yml`

## Versioning

We use dynamic versioning. The version is defined in `src/deskew_tool/__init__.py`.

To release a new version:
1. Update `__version__` in `src/deskew_tool/__init__.py`.
2. Commit the change.
3. Create and push a tag:
   ```bash
   git tag v0.1.x
   git push origin main --tags
   ```
