# Roadmap: Modified Fourier Shell Correlation (mFSC)

## Overview

This roadmap delivers a mask-artifact-free resolution estimation method integrated into the existing `torch-fourier-shell-correlation` package. Phase 1 implements the core mFSC algorithm for both 2D and 3D inputs with API consistency. Phase 2 validates correctness through comprehensive testing against expected behaviors.

## Phases

**Phase Numbering:**
- Integer phases (1, 2): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Core Implementation** - Implement modified FSC/mFSC functions with consistent API
- [ ] **Phase 2: Validation** - Verify correctness through behavioral tests

## Phase Details

### Phase 1: Core Implementation
**Goal**: Users can compute mask-artifact-free resolution estimates using modified FSC
**Depends on**: Nothing (first phase)
**Requirements**: MFSC-01, MFSC-02, MFSC-03, MFSC-04, API-01, API-02, API-03
**Success Criteria** (what must be TRUE):
  1. User can call `modified_fourier_ring_correlation()` with two 2D images and a mask to get per-shell correlation values
  2. User can call `modified_fourier_shell_correlation()` with two 3D volumes and a mask to get per-shell correlation values
  3. User can configure Gaussian bandpass sigma parameter (defaults to 1 Fourier pixel)
  4. Functions accept batched inputs with shape `(..., h, w)` for 2D and `(..., d, h, w)` for 3D
  5. Functions are importable from package root and listed in `__all__`
**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md -- Implement mFSC algorithm (2D+3D) with tests and package exports

### Phase 2: Validation
**Goal**: mFSC implementation correctness is verified through behavioral tests
**Depends on**: Phase 1
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04
**Success Criteria** (what must be TRUE):
  1. mFSC with all-ones mask produces similar correlation values to standard FSC (accounting for Gaussian vs binary shell differences)
  2. mFSC with mask on uncorrelated noise returns correlation values near zero across all shells
  3. mFSC with mask on identical inputs returns correlation values near one across all shells
  4. Both 2D and 3D variants produce output with correct shape (number of shells)
**Plans:** 1 plan

Plans:
- [ ] 02-01-PLAN.md -- Rigorous validation tests comparing mFSC to standard FSC, with non-trivial masks and extended shape coverage

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Implementation | 1/1 | Complete | 2026-03-13 |
| 2. Validation | 0/1 | Not started | - |
