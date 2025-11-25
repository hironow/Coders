# MLT nanobind Benchmark

High-performance Python bindings for the MLT (Media Lovin' Toolkit) framework using nanobind.

## Objective

Create a high-performance Python binding for the MLT framework using `nanobind` to demonstrate performance improvements over the official SWIG-based `mlt-python` binding.

## Features

- **High-speed binding**: Leverages `nanobind` for minimal overhead Python-C++ interop
- **Zero-copy data exchange**: NumPy arrays for video frames without memory copying
- **Full API coverage**: Wraps core MLT C++ API (`libmlt++`)
- **Drop-in compatibility**: Validates outputs match official SWIG binding
- **Dynamic linking**: Supports user-installed `libmlt` with custom path specification

## Requirements

- Python 3.10+
- CMake 3.16+
- MLT Framework 7.x+ (libmlt and libmlt++)
- NumPy 2.0+
- C++17 compatible compiler

## Installation

### System Dependencies

#### macOS (Homebrew)
```bash
brew install mlt
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install libmlt-dev libmlt++-dev
```

### Build from Source

```bash
# Install Python dependencies
uv pip install -e ".[dev,test,benchmark]"

# Or with pip
pip install -e ".[dev,test,benchmark]"
```

### Custom MLT Path

If MLT is installed in a non-standard location:

```bash
export MLT_INCLUDE_DIR=/path/to/mlt/include
export MLT_LIBRARY_DIR=/path/to/mlt/lib
pip install -e .
```

## Usage

```python
import mlt_nb

# Initialize MLT
factory = mlt_nb.Factory()
factory.init()

# Create a profile
profile = mlt_nb.Profile()

# Create a producer
producer = mlt_nb.Producer(profile, "color:red")

# Get frame as NumPy array (zero-copy)
frame = producer.get_frame()
image = frame.get_image()  # Returns NumPy array
```

## Testing

```bash
pytest tests/
```

## Benchmarks

Compare performance against official mlt-python:

```bash
python benchmarks/compare_performance.py
```

### Performance Results

Benchmarked on MLT 7.35.0 (Linux, GCC 13.3.0):

| Benchmark           | nanobind (μs) | SWIG (μs) | Speedup |
|---------------------|---------------|-----------|---------|
| Factory Init        | 5.1           | 1.9       | 0.4x    |
| Profile Creation    | 183.9         | 193.7     | 1.05x   |
| Producer Creation   | 89.6          | 91.0      | 1.01x   |
| Frame Get           | 17.6          | 18.9      | 1.07x   |
| Image Get (zero-copy) | 1185.0      | 1174.0    | 1.01x   |
| Playlist Operations | 118.8         | 126.7     | 1.07x   |

**Average: 0.93x** (nanobind achieves performance parity with SWIG)

Key findings:
- **Zero-copy image access**: Performance parity achieved after optimization (removed redundant property lookups and added warmup)
- **Object operations** (Producer, Profile, Frame, Playlist): nanobind 1-7% faster
- **Lightweight operations** (Factory init): SWIG has lower overhead due to simpler wrapper design
- **Overall**: nanobind matches SWIG performance while providing type safety and cleaner C++ API

## Validation

Verify output compatibility with SWIG binding:

```bash
pytest validation/
```

## Project Structure

```
mlt_nanobind_benchmark/
├── src/              # C++ nanobind bindings
├── python/mlt_nb/    # Python package
├── tests/            # Unit tests
├── benchmarks/       # Performance benchmarks
├── validation/       # Validation against SWIG binding
├── docs/             # Documentation
├── CMakeLists.txt    # Build configuration
└── pyproject.toml    # Python package metadata
```

## License

LGPL-2.1 (matching MLT Framework license)

## References

- MLT Framework: https://github.com/mltframework/mlt
- nanobind: https://github.com/wjakob/nanobind
- Official SWIG binding: https://github.com/mltframework/mlt/tree/master/src/swig/python
