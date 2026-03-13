# Codebase Structure

**Analysis Date:** 2026-03-13

## Directory Layout

```
teamtomo/
├── .github/               # GitHub configuration
│   ├── scripts/           # Automation scripts for CI
│   └── workflows/         # GitHub Actions workflows
├── .planning/             # GSD planning documents
│   └── codebase/          # Codebase analysis (this directory)
├── notes/                 # Project documentation and migration notes
├── packages/              # Workspace packages (the core)
│   ├── primitives/        # Stable, production-ready packages
│   │   ├── torch-affine-utils/
│   │   ├── torch-ctf/
│   │   ├── torch-cubic-spline-grids/
│   │   ├── torch-find-peaks/
│   │   ├── torch-fourier-filter/
│   │   ├── torch-fourier-rescale/
│   │   ├── torch-fourier-shell-correlation/
│   │   ├── torch-fourier-shift/
│   │   ├── torch-fourier-slice/
│   │   ├── torch-grid-utils/
│   │   ├── torch-image-interpolation/
│   │   ├── torch-so3/
│   │   ├── torch-subpixel-crop/
│   │   └── torch-transform-image/
│   └── wip/               # Work-in-progress/experimental packages
│       └── torch-tilt-series/
├── scripts/               # Utility scripts (not part of package)
│   ├── check_teamtomo_dependencies.py
│   └── update_citation_authors.py
├── src/teamtomo/          # Root metapackage source
│   ├── __init__.py        # Main entry point
│   ├── primitives/        # Namespace for primitive packages
│   └── wip/               # Namespace for WIP packages
├── tests/                 # Root-level integration tests
│   └── test_teamtomo_imports.py
├── pyproject.toml         # Root workspace configuration
├── uv.lock                # Dependency lock file
├── README.md              # Project overview
├── LICENSE                # BSD-3-Clause license
├── CITATION.cff           # Citation metadata
└── .pre-commit-config.yaml # Pre-commit hooks

```

## Directory Purposes

**packages/primitives/:**
- Purpose: Contains stable, production-ready PyTorch utility packages for cryo-EM/cryo-ET
- Contains: 14 independent packages, each with its own `src/`, `tests/`, and `pyproject.toml`
- Key files: Each package has `src/[module]/__init__.py` as the module entry point

**packages/wip/:**
- Purpose: Contains experimental/work-in-progress packages not yet stable
- Contains: 1 package (torch-tilt-series) for tomogram reconstruction
- Key files: `src/torch_tilt_series/__init__.py`, examples directory for usage patterns

**src/teamtomo/:**
- Purpose: Root metapackage namespace for unified API
- Contains: Aggregation modules that import child packages
- Key files:
  - `src/teamtomo/__init__.py`: Root entry point with version and namespace imports
  - `src/teamtomo/primitives/__init__.py`: Try-except wrapped imports of all 14 primitive packages
  - `src/teamtomo/wip/__init__.py`: Import of WIP packages

**tests/:**
- Purpose: Integration tests for the root metapackage
- Contains: Tests that verify namespaces are correctly exposed
- Key files: `tests/test_teamtomo_imports.py` - validates all packages are importable and in `__all__`

**scripts/:**
- Purpose: Utility scripts for development and CI automation
- Contains: Dependency validation and citation updating scripts
- Key files:
  - `scripts/check_teamtomo_dependencies.py`: Validates root package depends on all sub-packages
  - `scripts/update_citation_authors.py`: Updates CITATION.cff from GitHub repo metadata

**notes/:**
- Purpose: Project documentation and migration history
- Contains: Guides for monorepo migration, versioning policies, progress tracking
- Key files: Migration notes and dependency management documentation

**.github/:**
- Purpose: GitHub-specific configuration and CI/CD
- Contains: Actions workflows and scripts for automated testing and deployment

## Key File Locations

**Entry Points:**
- `src/teamtomo/__init__.py`: Main entry point for `import teamtomo`
- `packages/primitives/torch-affine-utils/src/torch_affine_utils/__init__.py`: Example primitive package entry
- `packages/wip/torch-tilt-series/src/torch_tilt_series/__init__.py`: WIP package entry
- `tests/test_teamtomo_imports.py`: Integration test entry point

**Configuration:**
- `pyproject.toml`: Root workspace configuration with all dependencies and dependency groups
- `uv.lock`: Locked dependency versions
- `packages/primitives/torch-affine-utils/pyproject.toml`: Example package configuration
- `.pre-commit-config.yaml`: Pre-commit hooks for code quality

**Core Logic:**
- `packages/primitives/torch-affine-utils/src/torch_affine_utils/transforms_2d.py`: 2D transformation matrices
- `packages/primitives/torch-affine-utils/src/torch_affine_utils/transforms_3d.py`: 3D transformation matrices
- `packages/primitives/torch-ctf/src/torch_ctf/ctf_1d.py`: 1D CTF calculation
- `packages/primitives/torch-ctf/src/torch_ctf/ctf_2d.py`: 2D CTF calculation
- `packages/primitives/torch-cubic-spline-grids/src/torch_cubic_spline_grids/_base_cubic_grid.py`: Base grid class
- `packages/wip/torch-tilt-series/src/torch_tilt_series/tilt_series.py`: TiltSeries class for reconstruction

**Testing:**
- `tests/test_teamtomo_imports.py`: Root metapackage import tests
- `packages/primitives/torch-affine-utils/tests/test_transforms_2d.py`: Package-specific unit tests (pattern)
- `packages/primitives/torch-ctf/tests/test_torch_ctf.py`: Example of package test structure

## Naming Conventions

**Files:**
- Python source files: `snake_case.py` (e.g., `transforms_2d.py`, `ctf_1d.py`)
- Package directories: `kebab-case` in filesystem (e.g., `torch-affine-utils`), converted to `snake_case` in module names
- Test files: `test_*.py` or `*_test.py` (e.g., `test_transforms_2d.py`)
- Config files: Uppercase or special names (e.g., `pyproject.toml`, `LICENSE`, `README.md`)

**Directories:**
- Package root directories: `kebab-case` (e.g., `torch-affine-utils`, `torch-cubic-spline-grids`)
- Source directories: `src/[module-name]/` where module name is `snake_case`
- Test directories: `tests/` at package level and root level
- Feature grouping: `primitives/` and `wip/` for logical organization

**Python Modules:**
- Package names: `snake_case` with hyphens converted to underscores (e.g., `torch_affine_utils`)
- Functions: `snake_case` (e.g., `calculate_ctf_1d()`, `homogenise_coordinates()`)
- Classes: `PascalCase` (e.g., `CubicSplineGrid`, `TiltSeries`, `CubicBSplineGrid1d`)
- Constants: `UPPER_CASE` (e.g., `CUBIC_B_SPLINE_MATRIX`)

## Where to Add New Code

**New Primitive Package:**
1. Create directory: `packages/primitives/torch-[new-feature]/`
2. Create structure:
   ```
   torch-[new-feature]/
   ├── src/torch_[new_feature]/
   │   ├── __init__.py
   │   ├── main_module.py
   │   └── utils.py
   ├── tests/
   │   ├── __init__.py
   │   └── test_main_module.py
   ├── pyproject.toml
   ├── README.md
   └── LICENSE
   ```
3. Model `pyproject.toml` after `packages/primitives/torch-affine-utils/pyproject.toml`
4. Add package name to root `pyproject.toml` dependencies and `[tool.uv.sources]`
5. Add import in `src/teamtomo/primitives/__init__.py` with try-except pattern
6. Update `src/teamtomo/primitives/__init__.py` `__all__` list

**New WIP Package:**
1. Create directory: `packages/wip/torch-[feature]/` (same structure as primitive)
2. Follow same setup as primitive packages but under `wip/`
3. Add import in `src/teamtomo/wip/__init__.py`

**New Module in Existing Package:**
1. Create file in `packages/primitives/[package]/src/[module]/[new_module].py`
2. Implement functions/classes with full docstrings
3. Add to package's `__init__.py` `__all__` if public API
4. Add unit tests in `packages/primitives/[package]/tests/test_[new_module].py`

**New Utility Function:**
- If cross-package utility: Create new package in `packages/primitives/torch-[util]/`
- If package-specific: Add to `packages/primitives/[package]/src/[module]/utils.py`
- Always include in `__all__` and docstrings

**New Test:**
- Package-level: `packages/primitives/[package]/tests/test_*.py`
- Integration: `tests/test_*.py` at root
- Follow pattern: `def test_[feature]():` with docstring and assertions

## Special Directories

**packages/primitives/torch-cubic-spline-grids/examples/:**
- Purpose: Example notebooks/scripts for grid interpolation usage
- Generated: No
- Committed: Yes (reference material)

**packages/wip/torch-tilt-series/examples/:**
- Purpose: Example code for tilt series reconstruction
- Generated: No
- Committed: Yes

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (by GSD mapping)
- Committed: Yes

**.venv/:**
- Purpose: Virtual environment (if created locally with `uv venv`)
- Generated: Yes (by uv)
- Committed: No (in .gitignore)

**__pycache__/, *.egg-info/:**
- Purpose: Python compilation and package metadata
- Generated: Yes
- Committed: No (in .gitignore)

---

*Structure analysis: 2026-03-13*
