---
phase: 02-validation
plan: 01
subsystem: testing
tags: [mfsc, fsc, validation, pytest, torch]

# Dependency graph
requires:
  - phase: 01-core-implementation
    provides: mFSC implementation (modified_fourier_ring_correlation, modified_fourier_shell_correlation)
provides:
  - 7 rigorous validation tests covering mFSC correctness
  - Comparison tests between mFSC and standard FSC
  - Non-trivial mask tests (circular/spherical)
  - Extended shape validation for batched and non-square inputs
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pearson correlation for comparing FSC curves with different shell windowing"
    - "Helper functions (_circular_mask, _spherical_mask) for generating non-trivial test masks"

key-files:
  created: []
  modified:
    - packages/primitives/torch-fourier-shell-correlation/tests/test_torch_fourier_shell_correlation.py

key-decisions:
  - "Used Pearson correlation > 0.8 to compare mFSC vs standard FSC trends rather than absolute value comparison, since Gaussian vs binary shells produce legitimately different values"
  - "Used mean(abs(non-DC shells)) < 0.15 for uncorrelated noise assertion to account for statistical variation at small sizes"

patterns-established:
  - "Phase 2 validation tests appended after Phase 1 tests with separator comment"
  - "Non-trivial mask generation helpers for reuse in future tests"

requirements-completed: [TEST-01, TEST-02, TEST-03, TEST-04]

# Metrics
duration: 2min
completed: 2026-03-13
---

# Phase 2 Plan 01: Validation Summary

**7 validation tests verifying mFSC correctness: FSC curve comparison via Pearson correlation, uncorrelated noise with circular/spherical masks, identical data correlation, and extended shape coverage for non-square/batched inputs**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-13T16:07:50Z
- **Completed:** 2026-03-13T16:09:32Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Validated mFSC produces correlation trends consistent with standard FSC (Pearson > 0.8) for both 2D and 3D
- Confirmed uncorrelated noise with non-trivial masks yields near-zero correlations (mean |r| < 0.15)
- Confirmed identical data with non-trivial masks yields near-one correlations (atol=0.05)
- Verified output shapes for non-square 2D, non-cubic 3D, batched, and multi-batch dimension inputs
- All 28 tests pass (21 existing + 7 new) with zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Add mFSC-vs-standard-FSC comparison test and non-trivial mask tests** - `0d74610` (test)

## Files Created/Modified
- `packages/primitives/torch-fourier-shell-correlation/tests/test_torch_fourier_shell_correlation.py` - Added 7 new validation test functions + 2 helper functions for mask generation

## Decisions Made
- Used Pearson correlation > 0.8 to compare mFSC vs standard FSC trends, since Gaussian bandpass vs binary shell windowing produces legitimately different absolute values but the correlation trends should agree
- Used mean(abs(non-DC shells)) < 0.15 threshold for uncorrelated noise tests to balance statistical robustness at small tensor sizes (32x32, 16^3) with meaningful validation
- Used atol=0.05 for identical data tests to verify near-perfect correlation with non-trivial masks

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 is the final phase; all validation tests pass
- mFSC implementation fully validated and ready for production use

## Self-Check: PASSED

- FOUND: packages/primitives/torch-fourier-shell-correlation/tests/test_torch_fourier_shell_correlation.py
- FOUND: commit 0d74610 (test(02-01): add Phase 2 mFSC validation tests)
- VERIFIED: 28 tests collected, all passing

---
*Phase: 02-validation*
*Completed: 2026-03-13*
