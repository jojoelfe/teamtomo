# Requirements: Modified Fourier Shell Correlation (mFSC)

**Defined:** 2026-03-13
**Core Value:** Provide correct, mask-artifact-free FSC computation integrated with the existing torch-fourier-shell-correlation API

## v1 Requirements

### Core Algorithm

- [x] **MFSC-01**: User can compute modified Fourier ring correlation (2D) given two images and a real-space mask
- [x] **MFSC-02**: User can compute modified Fourier shell correlation (3D) given two volumes and a real-space mask
- [x] **MFSC-03**: Gaussian bandpass window sigma is configurable (default: 1 Fourier pixel)
- [x] **MFSC-04**: mFSC returns correlation values per shell, same shape as existing FSC functions

### API Consistency

- [x] **API-01**: Functions follow existing naming pattern (`modified_fourier_ring_correlation`, `modified_fourier_shell_correlation`)
- [x] **API-02**: Batch dimension support matching existing `(..., h, w)` / `(..., d, h, w)` pattern
- [x] **API-03**: Functions exported from package `__init__.py` and added to `__all__`

### Testing

- [ ] **TEST-01**: mFSC without mask (all-ones) produces similar results to standard FSC (with Gaussian vs binary shells)
- [ ] **TEST-02**: mFSC with mask on uncorrelated data returns values near zero
- [ ] **TEST-03**: mFSC with mask on identical data returns values near one
- [ ] **TEST-04**: 2D and 3D variants produce correct output shapes

## v2 Requirements

### Statistical Analysis

- **NDF-01**: User can compute number of degrees of freedom for mFSC (Eq 12-13)
- **CI-01**: User can compute one-sided confidence interval via Fisher z-transform (Eq 14-17)

### Local Resolution

- **LOCAL-01**: User can compute per-voxel local resolution map using sliding box mFSC (Eq 7)
- **LOCAL-02**: User can compute per-segment resolution using arbitrary segmentation masks

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mask generation utilities | Not part of FSC package — users bring their own masks |
| Phase randomization correction | mFSC eliminates the need for this workaround |
| Prewhitening | Implied by the FSC/mFSC normalization (Eq 10 in paper) |
| GPU-optimized batched shells | Memory cost too high for large volumes; defer to v2 if needed |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MFSC-01 | Phase 1 | Complete |
| MFSC-02 | Phase 1 | Complete |
| MFSC-03 | Phase 1 | Complete |
| MFSC-04 | Phase 1 | Complete |
| API-01 | Phase 1 | Complete |
| API-02 | Phase 1 | Complete |
| API-03 | Phase 1 | Complete |
| TEST-01 | Phase 2 | Pending |
| TEST-02 | Phase 2 | Pending |
| TEST-03 | Phase 2 | Pending |
| TEST-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 after initial definition*
