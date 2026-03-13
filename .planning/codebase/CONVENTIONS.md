# Coding Conventions

**Analysis Date:** 2026-03-13

## Naming Patterns

**Files:**
- Module files use snake_case: `transforms_2d.py`, `ctf_1d.py`, `ctf_utils.py`
- Private/internal modules prefixed with underscore: `_base_cubic_grid.py`, `_constants.py`, `_utils.py`
- Test files follow `test_*.py` pattern: `test_transforms_2d.py`, `test_torch_ctf.py`

**Functions:**
- Public functions use snake_case: `calculate_ctf_1d()`, `find_peaks_2d()`, `homogenise_coordinates()`
- Private functions (internal helpers) prefixed with underscore: `_setup_ctf_1d()`, `_setup_ctf_2d()`
- Single-letter function names for mathematical operations: `R()` (rotation), `T()` (translation), `S()` (scaling) in `torch_affine_utils`

**Variables:**
- snake_case for all variables: `defocus`, `voltage_kv`, `amplitude_contrast_fraction`
- Abbreviations preserved in parameter names that match scientific domains: `kV` for kilovolts, `mm` for millimeters, `Å` for Angströms
- Matrix variables end with 's': `matrices`, `angles`, `shifts`

**Types:**
- PascalCase for class names: `CubicBSplineGrid1d`, `CubicCatmullRomGrid2d`, `Gaussian2D`, `Gaussian3D`
- Type hints use modern Python syntax: `torch.Tensor | list | tuple | float` (union operator, not `Union`)
- Optional types: `Optional[T]` or `T | None`

## Code Style

**Formatting:**
- Tool: `ruff-format` (enforced via pre-commit)
- Line length: Default ruff settings (typically 88 characters)
- Indentation: 4 spaces

**Linting:**
- Tool: `ruff` with `--fix` auto-fix enabled in pre-commit
- Enforced rules configured via ruff (specific rules not explicitly listed in config files found)
- Type checking: `mypy` runs on files matching pattern `^(src/|packages/.*/src/).*\.py$`

**Pre-commit hooks:**
- `validate-pyproject`: Validates all `pyproject.toml` files
- `typos`: Checks for typos (enforces consistent spelling)
- `ruff`: Linting with auto-fix
- `ruff-format`: Code formatting
- `mypy`: Type checking

## Import Organization

**Order:**
1. Standard library imports: `import torch`, `import einops`, `from typing import ...`
2. Third-party packages: `from scipy import constants as C`, `import numpy as np`
3. Relative package imports: `from torch_ctf.ctf_utils import ...`, `from torch_cubic_spline_grids import ...`
4. Local relative imports: `from ._base_cubic_grid import ...`

**Example from `ctf_2d.py`:**
```python
import einops
import torch

from torch_grid_utils.fftfreq_grid import fftfreq_grid, transform_fftfreq_grid
from torch_grid_utils.polar_grid import fftfreq_grid_polar
from torch_ctf.ctf_aberrations import apply_even_zernikes, apply_odd_zernikes
from torch_ctf.ctf_utils import calculate_total_phase_shift
```

**Path Aliases:**
- No explicit path aliases detected; imports use full module paths

## Error Handling

**Patterns:**
- Explicit validation with `ValueError` for invalid inputs: `raise ValueError("Shifts must have the last dimension of size 2 for 2D transformations.")`
- Input shape validation at function entry: Check last dimension size before processing
- Type coercion before processing: `torch.as_tensor(angles, dtype=torch.float32)` for flexible input handling
- Exception handling in init files: `try/except PackageNotFoundError` for version detection

**Example from `transforms_2d.py`:**
```python
if shifts.ndim > 0 and shifts.shape[-1] != 2:
    raise ValueError("Shifts must have the last dimension of size 2 for 2D transformations.")
```

## Logging

**Framework:** No dedicated logging framework; no logger imports found in codebase
- Minimal logging; code is silent by design
- Debug output only via `print()` statements in development/test code (found in utilities, not production code)
- Tests may use `print()` for debugging but not for structured logging

## Comments

**When to Comment:**
- Module-level docstrings required for all public modules
- Mathematical derivations and matrix structures documented in docstrings
- Complex algorithms documented inline (e.g., CTF calculations, spline interpolation)
- Limitations and special cases noted in comments

**JSDoc/TSDoc:**
- NumPy-style docstrings for all public functions
- Parameters documented with type and description
- Returns documented with type and shape information
- Example docstring pattern:

```python
def calculate_ctf_1d(
    defocus: float | torch.Tensor,
    voltage: float | torch.Tensor,
    ...
) -> torch.Tensor:
    """Calculate the Contrast Transfer Function (CTF) for a 1D signal.

    Parameters
    ----------
    defocus : float | torch.Tensor
        Defocus in micrometers, positive is underfocused.
    voltage : float | torch.Tensor
        Acceleration voltage in kilovolts (kV).
    ...

    Returns
    -------
    ctf : torch.Tensor
        The Contrast Transfer Function for the given parameters.
    """
```

## Function Design

**Size:** Functions typically stay under 50 lines for public APIs; complex operations delegated to private `_setup_*()` functions
- Example: `calculate_ctf_1d()` delegates to `_setup_ctf_1d()` which handles parameter validation and initialization

**Parameters:**
- Explicit parameters; no `*args` or `**kwargs` in mathematical functions
- Type hints on all parameters (required)
- Union types for flexible input: `float | torch.Tensor | list | tuple`
- Optional parameters have sensible defaults: `yx: bool = False`, `device: torch.device | None = None`

**Return Values:**
- Single return value (torch.Tensor) typical for most functions
- Multiple returns via tuple unpacking in setup functions: `return (param1, param2, param3, ...)`
- Consistent return shapes documented in docstring

## Module Design

**Exports:**
- Explicit `__all__` list in init files: `__all__ = ["homogenise_coordinates"]`
- Version accessible via `__version__` in init files (via importlib.metadata)
- Author and email metadata in init files

**Example from `torch_affine_utils/__init__.py`:**
```python
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("torch-affine-utils")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Alister Burt"
__email__ = "alisterburt@gmail.com"

from torch_affine_utils.utils import homogenise_coordinates

__all__ = [
    "homogenise_coordinates",
]
```

**Barrel Files:** Used in test package init files (empty `__init__.py` in `tests/` directories); not used for re-exporting in main packages

---

*Convention analysis: 2026-03-13*
