# PyGMT nanobind Implementation

A high-performance reimplementation of PyGMT using nanobind for C++ bindings.

## Objective

Create a drop-in replacement for PyGMT that uses nanobind instead of ctypes for improved performance while maintaining full API compatibility.

## Goals

1. **Implementation**: Reimplement PyGMT interface using nanobind for C++ bindings
2. **Compatibility**: Ensure drop-in replacement (only import change required)
3. **Benchmark**: Measure and compare performance against original PyGMT
4. **Validate**: Confirm pixel-identical output with PyGMT examples

## Architecture

```
User Code
    ↓
pygmt_nb.Figure / pygmt_nb.src.* (Python API - unchanged from PyGMT)
    ↓
pygmt_nb.clib.Session (nanobind-based replacement)
    ↓
libgmt.so (GMT C library)
```

### Key Differences from PyGMT

- **Binding Technology**: nanobind (C++) instead of ctypes (Python)
- **Performance**: Direct NumPy array access, no conversion overhead
- **Type Safety**: Compile-time type checking
- **Memory**: Better memory management with RAII

### Files to Replace

- `pygmt/clib/session.py` → nanobind C++ bindings
- `pygmt/clib/conversion.py` → eliminated (nanobind handles conversions)
- `pygmt/clib/loading.py` → simplified (linked at compile time)
- `pygmt/datatypes/*.py` → C++ struct bindings

### Files to Preserve

- All `pygmt/src/*.py` (60+ GMT module wrappers)
- `pygmt/figure.py` (Figure class)
- `pygmt/helpers.py`, `pygmt/exceptions.py`
- All high-level API code

## Project Structure

```
pygmt_nanobind_benchmark/
├── CMakeLists.txt              # Build configuration
├── pyproject.toml              # Python package metadata
├── README.md                   # This file
├── src/                        # C++ source code
│   ├── bindings.cpp           # nanobind bindings
│   ├── session.cpp            # Session class implementation
│   ├── session.hpp            # Session class header
│   ├── datatypes.hpp          # GMT data type wrappers
│   └── virtualfile.cpp        # Virtual file implementation
├── python/                     # Python package
│   └── pygmt_nb/
│       ├── __init__.py
│       └── clib/
│           └── __init__.py    # Exports Session from C++ module
├── tests/                      # Test suite
│   ├── test_session.py
│   ├── test_datatypes.py
│   ├── test_virtualfile.py
│   └── test_compatibility.py
├── benchmarks/                 # Performance benchmarks
│   ├── benchmark_session.py
│   ├── benchmark_dataio.py
│   └── compare_with_pygmt.py
└── validation/                 # Pixel-perfect validation
    └── validate_examples.py
```

## Build Requirements

- CMake ≥ 3.16
- C++17 compiler (GCC ≥ 7, Clang ≥ 5, MSVC ≥ 19.14)
- Python ≥ 3.11
- GMT ≥ 6.5.0
- Ghostscript (required for PNG/JPG/PDF output via GMT psconvert)
- nanobind
- NumPy ≥ 2.0
- Pandas ≥ 2.2
- xarray ≥ 2024.5

## Building

```bash
# Install system dependencies (Ghostscript for image conversion)
sudo apt-get install ghostscript  # Ubuntu/Debian
# or
brew install ghostscript           # macOS

# Install Python dependencies
uv pip install nanobind numpy pandas xarray

# Build the package
just build

# Install in development mode
just install

# Run tests
just test

# Run benchmarks
just benchmark
```

**Note**: Ghostscript is required for PNG/JPG/PDF output. Without it, only PostScript (.ps) and EPS (.eps) formats are available.

## Implementation Plan

### Phase 1: Core Session (TDD)
- [ ] GMT session lifecycle (create/destroy)
- [ ] Module execution (call_module)
- [ ] Error handling

### Phase 2: Data Types
- [ ] GMT_GRID bindings
- [ ] GMT_DATASET bindings
- [ ] GMT_MATRIX bindings
- [ ] GMT_VECTOR bindings

### Phase 3: Virtual Files
- [ ] Virtual file creation
- [ ] Vector → virtual file
- [ ] Matrix → virtual file
- [ ] Grid → virtual file

### Phase 4: Data I/O
- [ ] Create data containers
- [ ] Put vector/matrix data
- [ ] Read/write operations

### Phase 5: High-Level API
- [ ] Copy PyGMT high-level code
- [ ] Adapt imports to use pygmt_nb.clib
- [ ] Verify API compatibility

### Phase 6: Testing & Validation
- [ ] Unit tests
- [ ] Integration tests
- [ ] PyGMT example validation
- [ ] Pixel-perfect output comparison

### Phase 7: Benchmarking
- [ ] Session creation overhead
- [ ] Data transfer performance
- [ ] Module execution speed
- [ ] Memory usage comparison

## Development Guidelines

This project follows Kent Beck's TDD and Tidy First principles as outlined in `../AGENTS.md`.

- Write tests first (Red → Green → Refactor)
- Separate structural and behavioral changes
- Commit frequently with clear messages
- Use `just` for all commands
- Use `uv run` for Python execution

## References

- [PyGMT Architecture Analysis](../PyGMT_Architecture_Analysis.md)
- [GMT C API Documentation](https://docs.generic-mapping-tools.org/latest/api/)
- [nanobind Documentation](https://nanobind.readthedocs.io/)
