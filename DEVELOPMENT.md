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
uv sync --all-extras --dev
uv run pre-commit install
```

Use `--frozen` when you need to verify the lockfile exactly:

```bash
uv run --frozen pytest
```

## Daily Workflow

Keep changes small enough to review and commit by topic:

- User documentation: `README.md`
- Contributor documentation and release process: `DEVELOPMENT.md`
- Tooling and gates: `pyproject.toml`, `.pre-commit-config.yaml`, `.jscpd.json`, and workflow files
- Runtime behavior: files under `src/`
- Test coverage: files under `tests/`

Before editing, check the current working tree:

```bash
git status --short --branch
```

Do not mix unrelated source changes into documentation-only commits.

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

Fast local loop:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run pytest
```

Commit-time checks are managed by `pre-commit`:

```bash
uv run pre-commit run --all-files
```

Run the full quality gate before opening a pull request, tagging a release, or pushing broad maintenance changes:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run lint-imports
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80
uv run bandit -c pyproject.toml -r src -ll
uv run pip-audit
uv run radon cc src -s -a
uv run radon mi src -s
uv run radon raw src
npx --yes jscpd@4.0.5 --config .jscpd.json src tests
```

Focused test runs are useful while iterating:

```bash
uv run pytest tests/test_deskew.py -q
uv run pytest tests/test_ui.py -q
```

## Security and Audit Tools

The repository uses two different security checks:

- `bandit` scans project source code for Python security issues.
- `pip-audit` checks installed Python dependencies against advisory databases.

`pip-audit` depends on vulnerability and SBOM libraries such as `cyclonedx-python-lib`. Some endpoint security products may classify these scanners or their generated Python bytecode caches as hacktool or vulnerability-scanner heuristics. If that happens:

- Prefer running `pip-audit` in CI or an isolated disposable virtual environment.
- If an allowlist is required, scope it narrowly to the project virtual environment or the exact scanner path.
- Do not allowlist the whole user profile or the whole repository.
- Re-check package integrity before treating an alert as a false positive. Compare installed files with PyPI metadata or reinstall into a clean environment.

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
- Keep English and Chinese content aligned in `README.md`. If a feature is documented in one language, document the same behavior in the other.
- Prefer concise examples over repeating the full option list in multiple places. `README.md` can list common options; `pdf-deskew-cli --help` remains the source of truth for every CLI flag.

## CI and Release

GitHub Actions runs on pushes and pull requests to `main`:

- `ruff check .`
- `ruff format --check .`
- `mypy src`
- `lint-imports`
- `pytest` with coverage threshold
- `bandit` for medium/high severity Python security issues
- `pip-audit` for dependency vulnerabilities
- `radon` for complexity, maintainability, and raw code metrics
- `jscpd` for duplicate code detection

Quality gates are intentionally split by purpose:

- Must pass: formatting, linting, type checking, tests, coverage, architecture contract, and security scans.
- Threshold-based: coverage stays at 80%; jscpd currently allows up to 5% duplication.
- Report/trend: Radon complexity, maintainability index, raw size, and comment metrics.

Release publishing is handled by `.github/workflows/release.yml` when a tag matching `v*` is pushed. The workflow uses PyPI Trusted Publishing through OIDC, so no PyPI API token should be stored in GitHub Secrets.

Before release:

```bash
uv sync --all-extras --dev --frozen
uv run pytest
uv build
```

## Versioning

The package version is defined in `src/deskew_tool/__init__.py`.

To release:

```bash
# 1. Update __version__ in src/deskew_tool/__init__.py
# 2. Commit the version change
git tag v0.1.x
git push origin main --tags
```
