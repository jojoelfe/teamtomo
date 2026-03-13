# Architecture

**Analysis Date:** 2026-03-13

## Pattern Overview

**Overall:** Modular monorepo with unified workspace architecture

**Key Characteristics:**
- Monorepo containing 15+ specialized PyTorch-based packages for cryo-EM/cryo-ET processing
- Workspace-based structure using `uv` package manager with centralized dependency management
- Namespace aggregation pattern where sub-packages are exposed through parent modules
- Each primitive package is a self-contained, publishable Python package with its own build configuration
- Strict separation between primitive packages (stable), WIP packages (experimental), and root metapackage

## Layers

**Root Metapackage (`teamtomo`):**
- Purpose: Unified entry point that aggregates all workspace packages
- Location: `src/teamtomo/`
- Contains: Namespace aggregation modules that import and expose child packages
- Depends on: All primitive and WIP packages as direct dependencies
- Used by: End users who want the full TeamTomo suite; other packages that need cross-package functionality

**Namespace Modules (`primitives`, `wip`):**
- Purpose: Organize packages into logical groups; graceful degradation of missing optional dependencies
- Location: `src/teamtomo/primitives/__init__.py`, `src/teamtomo/wip/__init__.py`
- Contains: Try-except wrapped imports of all sub-packages (optional import pattern)
- Depends on: Individual primitive and WIP packages
- Used by: Users accessing `teamtomo.primitives.*` or `teamtomo.wip.*`

**Primitive Packages:**
- Purpose: Provide core PyTorch-based utilities for cryo-EM/cryo-ET operations
- Location: `packages/primitives/[package-name]/src/[module-name]/`
- Contains: Domain-specific computation functions (CTF, affine transforms, interpolation, etc.)
- Depends on: PyTorch, NumPy, einops, and other scientific libraries (no cross-package dependencies)
- Used by: Root metapackage, WIP packages, external applications

**WIP Packages:**
- Purpose: Experimental/under-development functionality not yet stable for general use
- Location: `packages/wip/[package-name]/src/[module-name]/`
- Contains: Early-stage features (e.g., TiltSeries reconstruction)
- Depends on: Primitive packages and PyTorch ecosystem
- Used by: Researchers exploring new functionality; special-purpose workflows

**Test Layer:**
- Purpose: Validate package functionality and integration
- Location: `tests/` (root) and `[package]/tests/` (package-specific)
- Contains: Unit tests for individual packages and integration tests for namespace imports
- Depends on: pytest, pytest-cov, individual packages under test
- Used by: CI/CD pipeline, developers during development

## Data Flow

**Package Publication Flow:**

1. Developer writes code in isolated package (`packages/primitives/torch-xyz/src/torch_xyz/`)
2. Package exposes public API via `__init__.py` with `__all__` declaration
3. Root metapackage imports package in `src/teamtomo/primitives/__init__.py` with try-except
4. Users import via `from teamtomo.primitives import torch_xyz` or `import teamtomo`
5. Each package maintains independent version via git tags (`[package-name]@v[semver]`)

**Initialization Flow:**

1. `src/teamtomo/__init__.py` imports namespaces (primitives, wip)
2. `src/teamtomo/primitives/__init__.py` attempts import of each primitive package
3. Failed imports are silently caught (None assigned) to allow partial installation
4. Users can access via `from teamtomo import primitives` → `primitives.torch_affine_utils`

**State Management:**
- No global state in application layer; packages are stateless utility libraries
- PyTorch modules (e.g., `CubicSplineGrid` in `torch_cubic_spline_grids`) inherit from `torch.nn.Module` for parameter management
- Version information captured at import time from package metadata (hatch-vcs)

## Key Abstractions

**PyTorch Module Abstraction:**
- Purpose: Enable parameterized computation with gradient tracking
- Examples: `torch_cubic_spline_grids.CubicSplineGrid`, `torch_cubic_spline_grids.CubicBSplineGrid1d`
- Pattern: Classes inherit from `torch.nn.Module`, use `register_buffer()` for non-parameter tensors, implement `forward()` for computation

**Transform Matrix Generation:**
- Purpose: Create homogenous coordinate transformation matrices (rotation, translation, scaling)
- Examples: `torch_affine_utils.transforms_2d.R()`, `torch_affine_utils.transforms_2d.T()`, `torch_affine_utils.transforms_3d.R()`
- Pattern: Functions accept flexible input types (float, list, tensor), use einops for shape manipulation, return batched matrices

**CTF Calculation Functions:**
- Purpose: Compute Contrast Transfer Functions for electron microscopy
- Examples: `torch_ctf.calculate_ctf_1d()`, `torch_ctf.calculate_ctf_2d()`, `torch_ctf.calculate_ctfp_and_ctfq_2d()`
- Pattern: Functions accept physical parameters (defocus, voltage, etc.), return CTF tensors; support batch dimensions

**Workspace Package Structure:**
- Purpose: Enable monorepo management with isolated, publishable packages
- Examples: Each `packages/primitives/[package]/` is a complete package with its own `pyproject.toml`, tests, and version
- Pattern: Local imports use package name (e.g., `from torch_affine_utils.transforms_2d import R`); each package is self-contained

## Entry Points

**Module Entry (`src/teamtomo/__init__.py`):**
- Location: `src/teamtomo/__init__.py`
- Triggers: `import teamtomo` or `from teamtomo import ...`
- Responsibilities: Establish version information, import namespace modules (primitives, wip), expose `__all__` for public API

**Namespace Entry (`src/teamtomo/primitives/__init__.py`):**
- Location: `src/teamtomo/primitives/__init__.py`
- Triggers: `from teamtomo import primitives` or `from teamtomo.primitives import torch_*`
- Responsibilities: Try to import each primitive package; gracefully handle missing packages; maintain `__all__` for introspection

**Namespace Entry (`src/teamtomo/wip/__init__.py`):**
- Location: `src/teamtomo/wip/__init__.py`
- Triggers: `from teamtomo import wip` or `from teamtomo.wip import torch_*`
- Responsibilities: Import WIP packages; handle missing packages; expose experimental features

**Package Entry Points:**
- Location: `packages/[category]/[package]/src/[module]/__init__.py`
- Triggers: Direct package import (e.g., `import torch_ctf`)
- Responsibilities: Import and expose public functions/classes; define `__version__`, `__author__`, `__email__`; declare `__all__`

**Test Entry (`tests/test_teamtomo_imports.py`):**
- Location: `tests/test_teamtomo_imports.py`
- Triggers: `pytest tests/` or CI pipeline
- Responsibilities: Verify namespace imports work; check all packages are accessible; validate `__all__` contents

## Error Handling

**Strategy:** Graceful degradation with optional imports

**Patterns:**
- Try-except wrapped imports in namespace modules allow partial installation (missing packages set to `None`)
- Package-level imports fail fast if dependencies (torch, numpy, einops) are missing
- Test modules use standard pytest assertions; missing optional packages are skipped in integration tests
- Individual package functions validate input shapes/types and raise `ValueError` with descriptive messages

**Example from `packages/primitives/torch-affine-utils/src/torch_affine_utils/transforms_2d.py`:**
```python
if shifts.ndim > 0 and shifts.shape[-1] != 2:
    raise ValueError("Shifts must have the last dimension of size 2 for 2D transformations.")
```

## Cross-Cutting Concerns

**Logging:** Not implemented; packages use standard print/warnings for diagnostics

**Validation:** Input shape and type validation at function entry points; einops for tensor shape manipulation ensures consistency

**Versioning:** Each package has independent version via git tags and hatch-vcs; root metapackage has separate versioning

**Documentation:** Docstrings follow NumPy format with Parameters/Returns sections; mathematical notation in CTF and transform functions

**Type Hints:** Python 3.10+ union syntax (`type | None`); generic types for flexible input handling

---

*Architecture analysis: 2026-03-13*
