# Codebase Concerns

**Analysis Date:** 2026-03-13

## Tech Debt

**Missing Input Validation in SO(3) Sampling:**
- Issue: `get_uniform_euler_angles()` lacks validation for input parameters; angles are not wrapped between 0 and 2π
- Files: `packages/primitives/torch-so3/src/torch_so3/uniform_so3_sampling.py` (line 61)
- Impact: Invalid angle values could be generated without user awareness. Wrapping inconsistencies may cause silent computation errors
- Fix approach: Add input validation for min/max bounds, angle normalization, and parameter consistency checks

**Periodic Interpolation Not Implemented:**
- Issue: `torch_interp()` function explicitly does not support periodic boundary conditions despite having a `period` parameter
- Files: `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/utils.py` (line 114, raises NotImplementedError for period != None)
- Impact: Users cannot use periodic interpolation needed for some Fourier-domain operations; workaround required
- Fix approach: Implement periodic wrapping logic for interpolation or remove the parameter entirely

**Dimension Limitations in Grid Utilities:**
- Issue: Multiple modules only support 2D and 3D patches/grids but not 1D or 4D+
- Files:
  - `packages/primitives/torch-grid-utils/src/torch_grid_utils/patch_grid/patch_grid.py` (raises NotImplementedError for ndim != 2, 3)
  - `packages/primitives/torch-grid-utils/src/torch_grid_utils/patch_grid/_patch_grid_centers.py`
  - `packages/primitives/torch-grid-utils/src/torch_grid_utils/patch_grid/_patch_grid_indices.py`
  - `packages/primitives/torch-grid-utils/src/torch_grid_utils/fftfreq_grid.py` (only 2D/3D supported)
- Impact: Code is inflexible; future support for other dimensionalities requires refactoring
- Fix approach: Generalize grid generation to arbitrary dimensions or document limitation clearly in API

**Mixed Tensor/Slice Indexing Not Supported:**
- Issue: `patch_grid.py` explicitly does not support mixed tensor/slice indexing patterns
- Files: `packages/primitives/torch-grid-utils/src/torch_grid_utils/patch_grid/patch_grid.py` (raises NotImplementedError)
- Impact: Certain advanced indexing patterns for patch extraction fail silently with unclear error
- Fix approach: Either implement mixed indexing or provide clear documentation with examples of supported patterns

**Duplicate Package Override in Configuration:**
- Issue: `torch-fourier-filter` is listed in `override-dependencies` but also in `uv.sources` workspace specification
- Files: `/pyproject.toml` (lines 32, 44-45)
- Impact: Unclear configuration intent; could cause version resolution issues if not carefully maintained
- Fix approach: Clarify why this package needs override and document the reason in comments

**Package Renaming Incomplete:**
- Issue: `torch-tilt-series` was renamed from `torch-tomogram` but README still references old name
- Files: `packages/wip/torch-tilt-series/README.md` (line 1 says "torch-tomogram")
- Impact: Documentation inconsistency; users find old references in search results
- Fix approach: Update all references to use `torch-tilt-series` consistently across all documentation

## Known Bugs / Test Gaps

**Dose Weight Tests Lack Ground Truth Validation:**
- Symptoms: Tests only validate output range (0 to 1) rather than correctness of values
- Files: `packages/primitives/torch-fourier-filter/tests/test_dose_weight.py` (lines 197, 203)
- Trigger: All cumulative dose filter tests fail to validate against known reference values
- Workaround: None; tests should be enhanced
- Impact: Dose weighting calculations could be mathematically incorrect without detection

**Angular Search Tests Incomplete:**
- Symptoms: Tests do not validate actual tensor values returned by angle generators
- Files: `packages/primitives/torch-so3/tests/test_torch_angular_search.py` (line 14)
- Trigger: All tests only check output shape, not correctness of angle calculations
- Workaround: None; requires implementing reference comparisons
- Impact: Subtle bugs in angle generation, rotation matrices, or Hopf fibration sampling would not be caught

**Missing Test Assertions:**
- Symptoms: Placeholder `pass` statements in error exception tests
- Files:
  - `packages/primitives/torch-affine-utils/tests/test_transforms_2d.py`
  - `packages/primitives/torch-fourier-filter/tests/test_torch_fourier_filter.py`
- Trigger: Error handling paths are not actually tested
- Impact: Exception handling could break without test detection

## Fragile Areas

**CTF Aberrations Module with Overlapping Features:**
- Files: `packages/primitives/torch-ctf/src/torch_ctf/ctf_aberrations.py`
- Why fragile: Uses warnings when both beam tilt and Zernike aberrations are specified; could mask user configuration errors
- Safe modification: Add explicit validation and early error raising instead of warnings
- Test coverage: Tests exist but only check warning emission, not underlying logic

**Deprecated Functions Still Active:**
- Files: `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/ctf.py` (multiple deprecated functions)
- Why fragile: Multiple CTF calculation functions marked deprecated with FutureWarning but still heavily used; breaking change not yet made
- Safe modification: Create deprecation timeline; provide migration guide before removing
- Test coverage: Deprecated functions still tested; no tests for migration paths

**Deprecated Fourier Shell Correlation Function:**
- Files: `packages/primitives/torch-fourier-shell-correlation/src/torch_fourier_shell_correlation/fsc.py` (line 161 - `fsc()` function)
- Why fragile: Old `fsc()` function dispatches to newer `fourier_ring_correlation()` or `fourier_shell_correlation()` but has no deprecation warning
- Safe modification: Add `warnings.warn()` with FutureWarning and set removal version
- Test coverage: Function is tested but deprecation is undocumented

**Large Complex Modules:**
- Files:
  - `packages/primitives/torch-ctf/tests/test_torch_ctf.py` (1,747 lines - test file, but indicates complex module)
  - `packages/primitives/torch-grid-utils/src/torch_grid_utils/patch_grid/patch_grid.py` (768 lines)
  - `packages/primitives/torch-ctf/src/torch_ctf/ctf_lpp.py` (634 lines)
  - `packages/primitives/torch-ctf/src/torch_ctf/ctf_ewald.py` (587 lines)
  - `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/dose_weight.py` (568 lines)
- Why fragile: Size indicates high cyclomatic complexity; difficult to test edge cases
- Safe modification: Extract helper functions; refactor into smaller logical units
- Test coverage: Core functionality covered but edge cases sparse

## Missing Test Coverage

**Batching and Device Handling:**
- What's not tested: Device-agnostic operation for all mathematical functions
- Files: Most modules under `packages/primitives/`
- Risk: GPU/CPU specific bugs, mixed device operations fail
- Priority: High - device handling is critical for production cryo-EM pipelines

**Numerical Edge Cases:**
- What's not tested: Handling of zero frequencies, NaN/Inf propagation, numerical stability
- Files:
  - `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/dose_weight.py`
  - `packages/primitives/torch-ctf/src/torch_ctf/ctf_lpp.py`
  - `packages/primitives/torch-ctf/src/torch_ctf/ctf_ewald.py`
- Risk: Silent numerical errors in scientific computations; invalid results that users assume are correct
- Priority: High - correctness is paramount in cryo-EM

**Large Image Handling:**
- What's not tested: Memory efficiency and performance with large 3D volumes
- Files: `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/dose_weight.py` mentions chunking but no tests
- Risk: Out-of-memory failures in production, performance regressions undetected
- Priority: Medium - important for ET data (gigapixel volumes)

**Coordinate System Correctness:**
- What's not tested: XYW vs YX coordinate system conversions in multiple places
- Files:
  - `packages/primitives/torch-affine-utils/src/torch_affine_utils/transforms_2d.py`
  - `packages/primitives/torch-affine-utils/tests/test_transforms_2d.py` (only basic tests exist)
- Risk: Silent coordinate system mismatches causing registration failures
- Priority: High - coordinate mismatch is a common source of subtle bugs in image processing

## Incomplete Features

**Algorithm Packages Not Migrated:**
- What's missing: 8 algorithm packages not yet in monorepo
- Files: `notes/migration-progress.md` lists as incomplete:
  - `torch-2dtm` (2D template matching)
  - `torch-tiltxcorr` (tilt series alignment)
  - `torch-refine-tilt-axis-angle` (tilt axis refinement)
  - `torch-cryoeraser` (region erasing)
  - `torch-segment-fiducials-2d` (fiducial detection)
  - `torch-segment-tomogram-boundaries` (boundary detection)
  - `torch-motion-correction` (motion correction)
  - `torch-ctf-estimation` (defocus estimation)
- Impact: Incomplete ecosystem; users must maintain separate external packages
- Priority: Medium - blocks full feature parity of TeamTomo

**WIP Package Status Undefined:**
- What's missing: `torch-tilt-series` lives in `packages/wip/` but is active in workspace
- Files: `packages/wip/torch-tilt-series/pyproject.toml` shows "Development Status :: 3 - Alpha"
- Impact: Unclear stability guarantees for users; potential breaking changes without notice
- Priority: Medium - document release status in README or move to `packages/primitives/`

**Validation of Inputs Not Implemented:**
- What's missing: Most functions accept tensors but don't validate shapes, dtypes, ranges
- Files: Throughout all primitives packages
- Impact: Invalid inputs silently produce garbage results instead of failing fast
- Priority: High - early error detection is crucial for scientific software

## Security Considerations

**No Input Sanitization:**
- Risk: Functions accept arbitrary tensor shapes/values without validation
- Files: All computation modules
- Current mitigation: PyTorch runtime will error on incompatible operations
- Recommendations: Add explicit shape/dtype/value validation with clear error messages

**Type Checking Enabled but Optional:**
- Risk: `mypy` configured with `strict = true` but not enforced in CI/CD
- Files: `.pre-commit-config.yaml` runs mypy, pyproject.toml has strict config
- Current mitigation: `mypy` warnings generated but not blocking
- Recommendations: Make mypy failures block CI pipeline; use `pre-commit` as hard requirement

## Performance Bottlenecks

**Naive Batch Loop Over Dimensions:**
- Problem: `torch_interp()` uses explicit for-loop for batch dimensions instead of vectorized operations
- Files: `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/utils.py` (line 112-113 in docstring: "naive for loop")
- Cause: Torch's searchsorted doesn't easily vectorize across batch dimensions
- Improvement path: Use einops or reshape tricks to vectorize; profile with large batches to validate speedup

**Memory Inefficiency in Dose Weighting:**
- Problem: `dose_weight_movie()` loads entire movie into memory; can consume ~5 * n_frames * h * w * 8 bytes
- Files: `packages/primitives/torch-fourier-filter/src/torch_fourier_filter/dose_weight.py` (lines 10-15 document the issue)
- Cause: Intermediate arrays for all frames retained simultaneously
- Improvement path: Enforce memory-efficient chunked processing by default; legacy API deprecated

**Repeated FFT Computations:**
- Problem: Grid generation and filtering often recompute FFT frequency grids multiple times
- Files: `packages/primitives/torch-grid-utils/src/torch_grid_utils/fftfreq_grid.py` (line 9 notes lru_cache disabled)
- Cause: lru_cache removed due to gradient interference, but no alternative caching strategy
- Improvement path: Implement gradient-safe caching or memoization pattern; benchmark impact

## Dependencies at Risk

**torch-fourier-filter Version Override:**
- Risk: Package is overridden in `uv` configuration suggesting version conflicts
- Impact: Hidden dependency resolution issues; future updates could break unexpectedly
- Migration plan: Document why override is necessary; add CI test to catch resolution failures

**Coupled Versioning Strategy:**
- Risk: All packages share major.minor versions; patch versions independent
- Impact: Major version bumps force updates across entire ecosystem even if one package breaks compatibility
- Migration plan: Document migration paths clearly; maintain compatibility layers when possible

**PyTorch Version Flexibility:**
- Risk: No explicit PyTorch version constraint; codebase uses `torch.Tensor` API that varies across versions
- Impact: Silent API breaks when new PyTorch is used; FFT functions vary significantly across versions
- Migration plan: Pin torch version ranges; test against multiple torch versions in CI

**External Format Libraries:**
- Risk: Weak pins on `etomofiles`, `alnfile`, `mrcfile` - cryo-EM file format libraries
- Files: `packages/wip/torch-tilt-series/pyproject.toml` (lines 56-58)
- Impact: Breaking changes in format libraries propagate without control
- Migration plan: Pin to specific versions; monitor for updates; test integration regularly

---

*Concerns audit: 2026-03-13*
