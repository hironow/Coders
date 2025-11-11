# Tesseract Nanobind Benchmark

High-performance Python bindings for Tesseract OCR using nanobind.

## Objective

Create a high-speed Tesseract OCR binding using `nanobind` to provide:
- Direct memory access for image data (NumPy arrays)
- High-speed text extraction with coordinates and confidence
- Better performance than pytesseract (subprocess) and tesserocr (CFFI)

## Requirements

### System Dependencies
- Tesseract OCR library (`libtesseract`)
- Leptonica library (`libleptonica`)
- CMake >= 3.15
- C++17 compatible compiler

### Python Dependencies
- Python >= 3.8
- NumPy >= 1.20

## Installation

### Development Installation

```bash
# Install with test dependencies
uv pip install -e ".[test]"
```

### Build with Custom Library Paths

If you have Tesseract and Leptonica installed in custom locations:

```bash
pip install -e . \
  -C cmake.define.TESSERACT_INCLUDE_DIR=/path/to/tesseract/include \
  -C cmake.define.TESSERACT_LIB_DIR=/path/to/tesseract/lib \
  -C cmake.define.LEPTONICA_INCLUDE_DIR=/path/to/leptonica/include \
  -C cmake.define.LEPTONICA_LIB_DIR=/path/to/leptonica/lib
```

## Usage

```python
import numpy as np
from tesseract_nanobind import TesseractAPI

# Initialize API
api = TesseractAPI()
api.init("", "eng")  # Empty datapath uses system tessdata

# Load image as NumPy array (height, width, 3)
image = np.array(...)  # Your image data

# Perform OCR
api.set_image(image)
text = api.get_utf8_text()
print(text)
```

## Testing

```bash
# Run tests
uv run pytest tests/
```

## Benchmarking

```bash
# Install benchmark dependencies
uv pip install -e ".[benchmark]"

# Run benchmarks
uv run python benchmarks/run_benchmarks.py
```

## Project Structure

- `src/tesseract_nanobind_ext.cpp` - C++ nanobind wrapper
- `src/tesseract_nanobind/` - Python package
- `tests/` - Unit tests
- `benchmarks/` - Performance benchmarks
- `CMakeLists.txt` - Build configuration
- `pyproject.toml` - Project metadata and dependencies
