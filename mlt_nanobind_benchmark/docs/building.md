# Building from Source

This document describes how to build mlt-nb from source.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.10 or later
- **CMake**: 3.16 or later
- **C++ Compiler**: GCC 7+, Clang 7+, or MSVC 2019+
- **MLT Framework**: 7.x or later with development files

### Installing MLT

#### macOS (Homebrew)

```bash
brew install mlt
```

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install libmlt-dev libmlt++-dev
```

#### Fedora/RHEL

```bash
sudo dnf install mlt-devel
```

#### Arch Linux

```bash
sudo pacman -S mlt
```

#### Windows

Use conda:
```bash
conda install -c conda-forge mlt
```

Or build from source following [MLT documentation](https://www.mltframework.org/docs/install/).

## Building mlt-nb

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mlt_nanobind_benchmark
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Or using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Build Dependencies

```bash
pip install -e ".[dev,test,benchmark]"
```

This will:
1. Install build tools (scikit-build-core, nanobind)
2. Run CMake to configure the build
3. Compile the C++ extension module
4. Install the Python package in editable mode

### Step 4: Verify Installation

```bash
python -c "import mlt_nb; print('mlt-nb installed successfully')"
```

## Custom MLT Installation

If MLT is installed in a non-standard location, set environment variables before building:

```bash
export MLT_INCLUDE_DIR=/path/to/mlt/include
export MLT_LIBRARY_DIR=/path/to/mlt/lib
export MLTPP_INCLUDE_DIR=/path/to/mlt/include/mlt++

pip install -e .
```

On Windows:
```cmd
set MLT_INCLUDE_DIR=C:\path\to\mlt\include
set MLT_LIBRARY_DIR=C:\path\to\mlt\lib
pip install -e .
```

## Build Options

### Debug Build

For debugging with symbols:

```bash
CMAKE_BUILD_TYPE=Debug pip install -e . --no-build-isolation
```

### Verbose Build

To see detailed build output:

```bash
pip install -e . -v
```

### Rebuild

To force a complete rebuild:

```bash
pip install -e . --force-reinstall --no-deps --no-build-isolation
```

## Building MLT from Source

If you need to build MLT itself from source:

```bash
# Clone MLT
git clone https://github.com/mltframework/mlt.git
cd mlt

# Create build directory
mkdir build && cd build

# Configure (minimal build)
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DMOD_SDL2=OFF \
  -DMOD_QT6=OFF \
  -DSWIG_PYTHON=OFF

# Build and install
cmake --build . -j$(nproc)
sudo cmake --install .
```

Then build mlt-nb:

```bash
cd /path/to/mlt_nanobind_benchmark
export MLT_INCLUDE_DIR=/usr/local/include
export MLT_LIBRARY_DIR=/usr/local/lib
pip install -e .
```

## Troubleshooting

### CMake Cannot Find MLT

**Error**: `MLT library not found`

**Solution**: Specify MLT paths explicitly:

```bash
export MLT_INCLUDE_DIR=/usr/local/include
export MLT_LIBRARY_DIR=/usr/local/lib
pip install -e .
```

### Python.h Not Found

**Error**: `fatal error: Python.h: No such file or directory`

**Solution**: Install Python development headers:

- Ubuntu/Debian: `sudo apt-get install python3-dev`
- Fedora: `sudo dnf install python3-devel`
- macOS: Included with Homebrew Python

### Linker Cannot Find libmlt

**Error**: `cannot find -lmlt` or `library not found for -lmlt`

**Solution**: Ensure MLT libraries are in the library path:

```bash
# Linux
export LD_LIBRARY_PATH=/path/to/mlt/lib:$LD_LIBRARY_PATH

# macOS
export DYLD_LIBRARY_PATH=/path/to/mlt/lib:$DYLD_LIBRARY_PATH
```

Or install MLT system-wide.

### Runtime Import Error

**Error**: `ImportError: _mlt_nb_core.*.so: cannot open shared object file`

**Solution**: The MLT libraries need to be findable at runtime:

```bash
# Add to ~/.bashrc or ~/.zshrc
export LD_LIBRARY_PATH=/path/to/mlt/lib:$LD_LIBRARY_PATH
```

Or on macOS:
```bash
export DYLD_LIBRARY_PATH=/path/to/mlt/lib:$DYLD_LIBRARY_PATH
```

### nanobind Version Mismatch

**Error**: ABI compatibility errors

**Solution**: Update nanobind:

```bash
pip install --upgrade nanobind
pip install -e . --force-reinstall
```

## Development Build

For active development with hot reload:

```bash
pip install -e . --no-build-isolation
```

After making C++ changes:

```bash
rm -rf build  # Clean build artifacts
pip install -e . --force-reinstall --no-deps --no-build-isolation
```

## Testing the Build

### Run Unit Tests

```bash
pytest tests/
```

### Run Benchmarks

```bash
python benchmarks/compare_performance.py
```

### Run Validation Tests

```bash
pytest validation/
```

## Building Wheels

To create distributable wheels:

```bash
pip install build
python -m build
```

Wheels will be in `dist/`.

## Continuous Integration

See `.github/workflows/` (if available) for CI build configurations.

## Build System Architecture

The build uses:
- **scikit-build-core**: Modern Python build backend for CMake projects
- **CMake**: Cross-platform build system
- **nanobind**: Lightweight C++/Python binding library

Build process:
1. `pyproject.toml` specifies build requirements
2. scikit-build-core invokes CMake
3. CMake finds MLT libraries and nanobind
4. C++ extension is compiled
5. Extension is installed into Python package

## Platform-Specific Notes

### Linux

Standard build should work with system package manager MLT.

### macOS

Homebrew MLT is recommended. If using multiple Python versions, ensure you're using Homebrew Python or specify paths correctly.

### Windows

Building on Windows requires:
- Visual Studio 2019 or later
- CMake (via Visual Studio or standalone)
- MLT built with same compiler

Consider using conda-forge MLT for easier setup.

## Next Steps

After successful build:
- Read [Usage Guide](usage.md)
- Check [API Reference](api_reference.md)
- Try [Examples](examples.md)
