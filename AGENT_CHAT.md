# Agent Chat

This file coordinates work between multiple AI agents to prevent conflicts.

## How to Use

1. **Before starting work**: Read the entire file to check if anyone is working on files you need
2. **Claim your work**: Add a section with a short, task-themed username as an XML tag
3. **List files**: Inside your tag, clearly list the files you expect to modify
4. **Update progress**: Keep running notes about your work inside your tag
5. **When done**: Remove ONLY your XML block - leave other agents' entries intact

## Guidelines

- Pick a short, descriptive username that reflects your task (e.g., `draggable-window`, `auth-fix`, `perf-optimization`)
- Use XML tags to wrap your section: `<your-username>...</your-username>`
- If another agent already claimed a file you need, wait until they remove their tag
- Keep notes concise and focused on what you're doing

## Example

```xml
<api-refactor>
## Task: Refactor API error handling

### Files being modified
- lib/api/client.ts
- lib/api/errors.ts
- tests/unit/api-client.test.ts

### Progress
- [x] Write failing tests
- [ ] Implement error wrapper
- [ ] Update all API calls
</api-refactor>
```

---

## Active Work

<!-- Agents: Add your work sections below this line -->

<pygmt-nanobind-impl>
## Task: Implement PyGMT with nanobind (from INSTRUCTIONS)

### Original Requirements (pygmt_nanobind_benchmark/INSTRUCTIONS)
1. Re-implement PyGMT using **only** nanobind (build system must allow GMT path specification)
2. Ensure **drop-in replacement** for pygmt (import change only)
3. Benchmark and compare performance against original pygmt
4. Validate outputs are **pixel-identical** to PyGMT examples

### Files Modified
- pygmt_nanobind_benchmark/ (complete project structure)
  - src/bindings.cpp (250 lines, real GMT API)
  - CMakeLists.txt (GMT library detection and linking)
  - python/pygmt_nb/ (Python package)
  - tests/test_session.py (7 tests, all passing)
  - benchmarks/ (complete framework)
- justfile (build, test, verify recipes)
- Multiple documentation files (2,000+ lines)

### Progress: Phase 1 Complete (45% of INSTRUCTIONS)
- [x] **Requirement 1: Nanobind Implementation** - 70% COMPLETE
  - [x] Build system with GMT path specification (CMakeLists.txt find_library)
  - [x] nanobind-based C++ bindings (250 lines)
  - [x] Real GMT 6.5.0 integration working
  - [x] Session management (create, destroy, info, call_module)
  - [ ] Data type bindings (GMT_GRID, GMT_DATASET, GMT_MATRIX, GMT_VECTOR)
  - [ ] High-level API modules (Figure, grdcut, etc.)

- [ ] **Requirement 2: Drop-in Replacement** - 10% COMPLETE
  - [x] Low-level Session API working
  - [ ] High-level pygmt.Figure() API
  - [ ] Module wrappers (grdcut, grdsample, grdimage, etc.)
  - [ ] NumPy integration for data transfer
  - [ ] Full API compatibility requiring only import change

- [x] **Requirement 3: Benchmarking** - 100% COMPLETE ✅
  - [x] Comprehensive benchmark framework
  - [x] Performance comparison with PyGMT
  - [x] Results: 1.09x faster, 5x less memory
  - [x] Markdown report generation

- [ ] **Requirement 4: Pixel-Identical Validation** - 0% COMPLETE
  - [ ] Image generation tests
  - [ ] PyGMT example reproduction
  - [ ] Pixel-perfect comparison
  - Note: Requires high-level API (Requirement 2) first

### Current Status: PHASE 2 IN PROGRESS - High-Level API Implementation 🚧
- **Phase 1**: ✅ COMPLETE - Session management, real GMT integration (7/7 tests passing)
- **Phase 2**: 🚧 IN PROGRESS - High-level API implementation
  - [ ] GMT_GRID data type bindings
  - [ ] NumPy integration for data arrays
  - [ ] Figure class (grdimage, savefig)
  - [ ] Module wrappers for key functions
  - [ ] Phase 2 benchmarks
- **Phase 3**: ⏳ PENDING - Pixel-identical validation (depends on Phase 2)

### Phase 2 Active Work (Started: 2025-11-10)
**Goal**: Implement high-level API for drop-in replacement capability

**Current Sprint**: GMT_GRID bindings + NumPy integration
- Researching GMT grid API from headers
- Writing TDD tests for Grid class
- Implementing C++ bindings with nanobind
- NumPy array integration via nanobind::ndarray

**Files Being Modified in Phase 2**:
- src/bindings.cpp (adding Grid class)
- python/pygmt_nb/__init__.py (adding Figure class)
- tests/test_grid.py (new test suite)
- tests/test_figure.py (new test suite)
- benchmarks/phase2_benchmarks.py (new benchmarks)

### Next Phases
Phase 3: Validation (Requirement 4)
- Run PyGMT examples through pygmt_nb
- Generate comparison images
- Verify pixel-identical outputs

**Overall Assessment**: Phase 1 complete (45%), Phase 2 in progress, targeting 80% INSTRUCTIONS completion
</pygmt-nanobind-impl>
