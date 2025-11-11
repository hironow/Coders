# Tesseract Nanobind Benchmark

[![Tesseract Nanobind CI](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yml/badge.svg)](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yml)
[![Build Wheels](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-build-wheels.yml/badge.svg)](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-build-wheels.yml)

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

### Basic Text Extraction

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

### Getting Bounding Boxes and Confidence

```python
# Get word-level bounding boxes with confidence scores
api.set_image(image)
api.recognize()  # Must call recognize first

boxes = api.get_bounding_boxes()
for box in boxes:
    print(f"Text: {box['text']}")
    print(f"Position: ({box['left']}, {box['top']})")
    print(f"Size: {box['width']}x{box['height']}")
    print(f"Confidence: {box['confidence']:.1f}%")

# Get mean confidence for the entire image
confidence = api.get_mean_confidence()
print(f"Mean confidence: {confidence}%")
```

### Complete Example

See `examples/basic_usage.py` for a complete working example.

## Testing

```bash
# Run tests
uv run pytest tests/
```

## Benchmarking

```bash
# Install benchmark dependencies
pip install -e ".[benchmark]"

# Run benchmarks
python benchmarks/run_benchmarks.py
```

### Performance Results

Benchmarked on test images (10 images, 5 iterations each):

| Implementation | Time per Image | Relative Speed |
|---------------|----------------|----------------|
| pytesseract (subprocess) | 105.7 ms | 1.0x (baseline) |
| tesseract_nanobind | 12.8 ms | **8.25x faster** |

**Key Findings:**
- tesseract_nanobind is 8.25x faster than pytesseract
- 87.9% performance improvement
- OCR results are consistent between implementations
- Zero-copy data transfer with NumPy arrays
- Direct C++ API access eliminates subprocess overhead

## API Reference

### TesseractAPI Class

#### Methods

- `__init__()` - Create a new TesseractAPI instance
- `init(datapath: str, language: str) -> int` - Initialize Tesseract with language data
  - Returns 0 on success, -1 on failure
  - Use empty string for datapath to use system tessdata
- `set_image(image: np.ndarray)` - Set image for OCR (height, width, 3) uint8 array
- `get_utf8_text() -> str` - Get OCR result as UTF-8 text
- `recognize() -> int` - Perform recognition (required before getting boxes/confidence)
- `get_bounding_boxes() -> List[Dict]` - Get word-level bounding boxes with confidence
  - Each box contains: text, left, top, width, height, confidence
- `get_mean_confidence() -> int` - Get mean confidence score (0-100)
- `version() -> str` (static) - Get Tesseract version string

## Project Structure

- `src/tesseract_nanobind_ext.cpp` - C++ nanobind wrapper
- `src/tesseract_nanobind/` - Python package
- `tests/` - Unit tests (11 tests, all passing)
- `benchmarks/` - Performance benchmarks
- `examples/` - Usage examples
- `CMakeLists.txt` - Build configuration
- `pyproject.toml` - Project metadata and dependencies
