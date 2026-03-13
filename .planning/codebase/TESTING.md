# Testing Patterns

**Analysis Date:** 2026-03-13

## Test Framework

**Runner:**
- `pytest` (framework and runner)
- Version: Specified in `dependency-groups` as `pytest`
- Config: `pyproject.toml` file at each package root

**Assertion Library:**
- `torch.allclose()` for tensor comparisons (primary assertion method)
- Standard Python `assert` statements
- No specialized assertion library; pure pytest

**Run Commands:**
```bash
pytest tests/                  # Run all tests in tests directory
pytest tests/ --cov            # Run with coverage reporting
pytest -v                      # Verbose output
```

**Coverage:**
- Tool: `pytest-cov`
- Tracked via `[tool.coverage.run]` in `pyproject.toml`
- Source pattern: `source = ["torch_affine_utils"]` (module-specific per package)

## Test File Organization

**Location:**
- Co-located pattern: Tests live in `tests/` subdirectory at package root, parallel to `src/`
- Example structure:
  - `packages/primitives/torch-affine-utils/src/torch_affine_utils/` (source)
  - `packages/primitives/torch-affine-utils/tests/` (tests)

**Naming:**
- Test files: `test_*.py` pattern strictly followed
- Examples: `test_transforms_2d.py`, `test_torch_ctf.py`, `test_grids.py`
- Test functions: `test_*` naming convention

**Structure:**
```
packages/primitives/[package-name]/
├── src/
│   └── [package_name]/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── __init__.py            # Empty init file for test discovery
│   ├── conftest.py            # Optional pytest fixtures
│   ├── _utils.py              # Helper utilities (not test_*.py)
│   ├── test_module1.py
│   └── test_module2.py
└── pyproject.toml
```

## Test Structure

**Suite Organization:**
```python
# tests/test_transforms_2d.py
import torch

from torch_affine_utils.transforms_2d import R, T, S

TRANSFORMS = [R, T, S]  # Test data constants at module level

def test_rotation():
    """Rotating x-axis by 90 degrees should become y-axis."""
    # Standard coordinate system (xyw)
    rotation = R(90)
    v = torch.tensor([1, 0, 1]).view((3, 1)).float()
    expected = torch.tensor([0, 1, 1]).view((3, 1)).float()
    assert torch.allclose(rotation @ v, expected, atol=1e-6)
```

**Patterns:**

1. **Setup pattern:** Inline within test functions; no `setup()` or `setUp()` methods
   - Constants defined at module level (e.g., `TRANSFORMS = [R, T, S]`)
   - Fixture objects created directly in test: `rotation = R(90)`
   - Global random seed set once at module level: `torch.manual_seed(42)`

2. **Teardown pattern:** Implicit; PyTorch tensors garbage collected naturally
   - No explicit teardown in tests found
   - Fixtures handle cleanup via pytest's fixture system if needed

3. **Assertion pattern:** Direct assertions with `torch.allclose()` for floating-point tensors
   ```python
   assert torch.allclose(result, expected, atol=1e-6)
   assert tensor.shape == expected_shape
   assert hasattr(object, "attribute")
   ```

## Mocking

**Framework:** No mocking library detected (no unittest.mock, pytest-mock, or similar imports)

**Patterns:** No mocking in existing tests; all tests use real objects:
- Real torch tensors in assertions
- Real module instances tested directly
- No patching or stubbing observed

**What to Mock:**
- Not applicable in current codebase; testing approach uses real dependencies

**What NOT to Mock:**
- All PyTorch operations tested with actual tensors (no mocking)
- Real mathematical functions executed in tests

## Fixtures and Factories

**Test Data:**
- Inline data generation typical:
```python
def test_rotation():
    rotation = R(90)
    v = torch.tensor([1, 0, 1]).view((3, 1)).float()
    expected = torch.tensor([0, 1, 1]).view((3, 1)).float()
```

- Pytest fixtures for repeated setup (when needed):
```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def set_default_device():
    torch.set_default_device("cpu")
```

- Factory functions for complex test data:
```python
# tests/_utils.py
def create_test_image(size: int = 100, peaks: torch.tensor = torch.tensor([]), noise_level=0.1):
    """Create a test image with known Gaussian peaks."""
    image = torch.randn((size, size)) * noise_level
    gaussian_model = Gaussian2D(
        amplitude=peaks[:, 0],
        center_y=peaks[:, 1],
        center_x=peaks[:, 2],
        sigma_y=peaks[:, 3],
        sigma_x=peaks[:, 4],
    )
    grid = coordinate_grid((size, size))
    image += gaussian_model(grid).sum(dim=0)
    return image

def create_test_volume(size: int = 100, peaks: torch.tensor = torch.tensor([]), noise_level=0.1):
    """Create a test volume with known Gaussian peaks."""
    # Similar pattern for 3D data
```

**Location:**
- Fixtures in `tests/conftest.py` (auto-discovered by pytest)
- Factory functions in `tests/_utils.py` (imported as needed)
- Module-level test constants in test files themselves

## Coverage

**Requirements:** No explicit coverage target enforced via CI (not found in config)

**View Coverage:**
```bash
pytest --cov=torch_affine_utils --cov-report=html
```

**Exclusions:**
```toml
# pyproject.toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "@overload",
    "except ImportError",
    "\\.\\.\\.",
    "raise NotImplementedError()",
    "pass",
]
```

## Test Types

**Unit Tests:**
- Primary test type in codebase
- Scope: Individual functions and mathematical operations
- Approach: Direct function calls with tensor inputs/outputs
- Example: `test_rotation()` in `torch_affine_utils` tests rotation matrix generation in isolation

**Integration Tests:**
- Existing integration tests verify module imports across workspaces:
  - `tests/test_teamtomo_imports.py`: Tests that all primitive packages importable under `teamtomo` namespace
  - Verify namespace consistency across workspace packages

- Some tests verify component interactions:
  - `test_grids.py`: Tests grid instantiation, data operations, and interpolation together
  - `test_grid_optimisation.py`: Tests grid optimization end-to-end with PyTorch optimizer

**E2E Tests:**
- Not present in codebase; workspace is library packages
- Import verification serves as basic end-to-end test

## Common Patterns

**Async Testing:**
- Not applicable; no async code in codebase

**Error Testing:**
- Error cases tested via exception assertion:
```python
def test_batching():
    # 1D tensors with length greater than 2 should raise an error for T and S
    for O in [T, S]:
        try:
            O(torch.tensor([0, 90, 180]))
        except ValueError:
            pass
        else:
            raise AssertionError(f"{O.__name__} should raise an error...")
```

- Or using pytest exception context (not seen but preferred pattern):
```python
with pytest.raises(ValueError):
    O(torch.tensor([0, 90, 180]))
```

**Parametrized Testing:**
```python
@pytest.mark.parametrize(
    'grid_cls', [CubicBSplineGrid1d, CubicCatmullRomGrid1d]
)
def test_1d_grid_direct_instantiation(grid_cls):
    """Test grid instantiation with different types for resolution argument."""
    grid = grid_cls()
    assert isinstance(grid, grid_cls)
```

**Device Testing:**
```python
def test_devices():
    """Test that matrices are created on the correct device."""
    for O in TRANSFORMS:
        assert O(torch.tensor(0)).device.type == 'cpu'
        assert O(torch.tensor(0, device="meta")).device.type == 'meta'
        assert O(torch.tensor(0), device="meta").device.type == 'meta'
```

**Gradient/Backprop Testing:**
```python
def test_backpropagation_gradients():
    """Test that gradients can be backpropagated from output to input."""
    for O in TRANSFORMS:
        x = torch.tensor([90.0, 45.0], requires_grad=True)
        y = O(x)
        assert y.requires_grad
        y.sum().backward()
        assert x.grad is not None
```

**Numerical Tolerance:**
- `torch.allclose()` with explicit tolerance for floating-point comparisons:
```python
assert torch.allclose(result, expected, atol=1e-6)  # Absolute tolerance
```

---

*Testing analysis: 2026-03-13*
