# Technology Stack

**Analysis Date:** 2026-03-13

## Languages

**Primary:**
- Python 3.12 - Main language for all packages
  - Minimum: 3.11, Maximum tested: 3.13
  - Enforced via `.python-version` file at `/.python-version`

## Runtime

**Environment:**
- CPython 3.12 (with support for 3.11, 3.13)
- Linux, macOS (x86_64, arm64), Windows via GitHub Actions

**Package Manager:**
- uv 0.x - Fast Python package and project manager
  - Lockfile: `uv.lock` - Deterministic dependency resolution
  - Configuration: `pyproject.toml` root and per-package

## Frameworks

**Core Scientific Computing:**
- PyTorch 2.9.1 - Deep learning and tensor computations
  - Used across all torch-* subpackages for GPU-accelerated operations
  - Critical for cryo-EM/cryo-ET image processing

**Data Processing:**
- NumPy 2.4.0 - Numerical computing foundation
- SciPy 1.16.3 - Scientific and technical computing (used in test dependencies)
- Pandas - Data manipulation (used in alnfile dependency)
- einops 0.8.1 - Tensor reshaping operations for readable code

**Testing:**
- pytest 9.0.2 - Test runner
  - Config: per-package `pyproject.toml` with `[tool.pytest.ini_options]`
- pytest-cov - Code coverage measurement

**Code Quality & Development:**
- ruff 0.15.1 - Fast Python linter and formatter
  - Config: `[tool.ruff]` in each `pyproject.toml`
  - Linting rules: E, W, F, D, I, UP, C4, B, A001, RUF, TCH, TID
  - Format configuration with docstring-code formatting enabled
- mypy 1.19.1 - Static type checker
  - Config: `[tool.mypy]` in each `pyproject.toml`
  - Strict mode enabled
- pre-commit 2.x - Git hook framework
  - Config: `.pre-commit-config.yaml` at root

**Build & Versioning:**
- hatchling - Build backend for packaging
- hatch-vcs - Version control system integration for semantic versioning
  - Uses git tags matching pattern `{package}@v{semver}`
  - Example: `teamtomo@v0.5.0`, `torch-fourier-slice@v0.5.0`

**Documentation & Visualization:**
- matplotlib 3.10.8 - Plotting library (test dependency)
- beautifulsoup4 - HTML parsing (dev environment only)

## Key Dependencies

**Critical (Direct):**
- torch 2.9.1 - Tensor operations, GPU support
- numpy 2.4.0 - Array operations, numerical computing
- einops 0.8.1 - Tensor manipulation utilities

**Torch Ecosystem (Internal Packages):**
All packages built in-house and available at `packages/primitives/`:
- torch-grid-utils - Grid operations
- torch-affine-utils - Affine transformations
- torch-image-interpolation - Image resampling
- torch-transform-image - Image transformations
- torch-so3 - Special orthogonal group operations
- torch-fourier-shift - Fourier-domain shifting
- torch-fourier-rescale - Fourier-domain rescaling
- torch-subpixel-crop - Subpixel-accurate cropping
- torch-fourier-slice - Fourier slice extraction/insertion
- torch-ctf - Contrast transfer function utilities
- torch-fourier-filter - Fourier-domain filtering
- torch-fourier-shell-correlation - Fourier shell correlation
- torch-cubic-spline-grids - B-spline grid interpolation
- torch-find-peaks - Peak detection
- torch-tilt-series - Tilt series utilities

**Scientific Data:**
- astropy 7.2.0 - Astronomy/scientific data handling
- pydantic 2.12.5 - Data validation
- alnfile 0.1.1 - ALN file format support

## Configuration

**Environment:**
- No environment variables required for development
- GitHub Actions CI uses uv for deterministic builds from `uv.lock`
- GitHub token (`GITHUB_TOKEN`) optional for scripts in `scripts/` (citation update)

**Build:**
- Root: `/pyproject.toml` - Workspace and shared configuration
- Per-package: `packages/primitives/{name}/pyproject.toml` and `packages/wip/{name}/pyproject.toml`

**Dependencies Grouping (PEP 735):**
- `test` - pytest, pytest-cov, scipy, matplotlib, ttsim3d, urllib3
- `dev` - includes test group, adds ipython, mypy, pdbpp, pre-commit-uv, rich, ruff

## Platform Requirements

**Development:**
- Python 3.11+
- uv for package management
- Git for version control (hatch-vcs dependency)

**Production:**
- PyPI distribution for all packages under namespace `torch-*`
- Deployment: PyPI via GitHub Actions on tag push
- Automated releases with GitHub Release creation and assets

## Version Management

**Semantic Versioning:**
- Pattern: `{package}@v{major}.{minor}.{patch}`
- Fallback version: 0.5.0
- Git describe constraints to filter workspace-specific tags

**Package Distribution:**
- Published to PyPI as individual packages
- Published by: `pypa/gh-action-pypi-publish` action with trusted publishing (OIDC)

---

*Stack analysis: 2026-03-13*
