# tesseract_nanobind

[![CI Status](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yaml/badge.svg)](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yaml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**High-performance Tesseract OCR Python bindings with full tesserocr API compatibility.**

A drop-in replacement for tesserocr that's **1.56x faster** than pytesseract with zero-copy NumPy integration.

## Why Use This?

✅ **tesserocr-compatible API** - Change one import line and you're done
✅ **1.56x faster than pytesseract** - Direct C++ API, no subprocess overhead
✅ **Near-tesserocr performance** - Only 8% slower, often negligible
✅ **Zero-copy NumPy** - Efficient array handling without conversions
✅ **163 passing tests** - Comprehensive test coverage
✅ **Python 3.10-3.14** - Modern Python support

## Quick Start

### Installation

```bash
# Install from source
pip install git+https://github.com/hironow/Coders.git#subdirectory=tesseract_nanobind_benchmark

# Or for development
git clone https://github.com/hironow/Coders.git
cd Coders/tesseract_nanobind_benchmark
pip install -e ".[test]"
```

**Requirements:** Tesseract OCR library must be installed on your system.

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr libtesseract-dev libleptonica-dev

# macOS (Homebrew)
brew install tesseract leptonica
```

### Basic Usage

```python
from tesseract_nanobind.compat import PyTessBaseAPI
from PIL import Image

# Same API as tesserocr - just change the import!
with PyTessBaseAPI(lang='eng') as api:
    api.SetImage(Image.open('document.png'))
    text = api.GetUTF8Text()
    confidence = api.MeanTextConf()
    print(f"Text: {text}")
    print(f"Confidence: {confidence}%")
```

### Migrating from tesserocr

**Before:**
```python
from tesserocr import PyTessBaseAPI
```

**After:**
```python
from tesseract_nanobind.compat import PyTessBaseAPI
```

That's it! Your code works without any other changes.

### Key Features

```python
from tesseract_nanobind.compat import PyTessBaseAPI, PSM
import numpy as np

with PyTessBaseAPI(lang='eng') as api:
    # Set page segmentation mode
    api.SetPageSegMode(PSM.SINGLE_LINE)

    # Works with PIL Images or NumPy arrays (zero-copy)
    image_array = np.array(pil_image)
    api.SetImage(image_array)

    # Get text and confidence
    text = api.GetUTF8Text()

    # Get word-level details
    words_with_conf = api.MapWordConfidences()
    for word, conf in words_with_conf:
        print(f"{word}: {conf}%")

    # Alternative output formats
    hocr = api.GetHOCRText(0)  # hOCR format
    tsv = api.GetTSVText(0)    # TSV format
```

## Performance Benchmarks

Latest results (5 real test images, 5 iterations, macOS M-series):

| Implementation | Time per Image | vs pytesseract | vs tesserocr |
|---------------|----------------|----------------|--------------|
| **pytesseract** | 244.4 ms | 1.0x (baseline) | 0.59x |
| **tesserocr** | 144.3 ms | **1.69x faster** | 1.0x (baseline) |
| **tesseract_nanobind** | 156.2 ms | **1.56x faster** | 0.92x (8% slower) |

**Key Findings:**
- ✅ **1.56x faster** than pytesseract (56% improvement)
- ✅ **Only 8% slower** than tesserocr (negligible in most use cases)
- ✅ **100% identical results** across all three implementations
- ✅ **Zero-copy** NumPy array handling for maximum efficiency
- ✅ **No subprocess** overhead - direct C++ API access

**Why the slight difference vs tesserocr?**
We use nanobind instead of CFFI, trading ~8% performance for easier builds, better NumPy integration, and maintainability. For most applications, this difference is negligible compared to the actual OCR processing time.

## Documentation

- **[API Compatibility Guide](docs/COMPATIBILITY.md)** - Full tesserocr compatibility details
- **[Version Management](VERSION_MANAGEMENT.md)** - Release workflow and versioning
- **[Development History](docs/development-history/)** - Implementation timeline

### Supported Features

**Core OCR (100% compatible):**
- ✅ Text extraction (`GetUTF8Text`)
- ✅ Confidence scores (`MeanTextConf`, `AllWordConfidences`)
- ✅ Word/line extraction (`GetWords`, `GetTextlines`)
- ✅ Bounding boxes with coordinates
- ✅ Multiple languages

**Configuration (100% compatible):**
- ✅ Page segmentation modes (PSM)
- ✅ Tesseract variables (`SetVariable`, `GetVariable`)
- ✅ Region of interest (`SetRectangle`)
- ✅ Orientation detection (`DetectOrientationScript`)

**Output Formats (100% compatible):**
- ✅ Plain text (UTF-8)
- ✅ hOCR format
- ✅ TSV format
- ✅ Box file format
- ✅ UNLV format

**Advanced Features:**
- ✅ Component images (`GetComponentImages`)
- ✅ Image thresholding (`GetThresholdedImage`)
- ✅ Layout analysis at multiple levels (block, paragraph, line, word)

See [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) for detailed API coverage (98%+ for typical use cases).

## Development

### Setup

```bash
# Clone and install with all dependencies
git clone https://github.com/hironow/Coders.git
cd Coders/tesseract_nanobind_benchmark

# Install with uv (recommended)
uv sync --all-extras

# Or with pip
pip install -e ".[test,benchmark]"
```

### Testing

```bash
# Run all tests (163 tests)
just tesseract-test

# Run code quality checks
just tesseract-check

# Run benchmarks
just tesseract-benchmark
```

### Building

```bash
# Clean build
just tesseract-clean
just tesseract-build

# Run all validation
just tesseract-test
```

See `just --list` for all available commands.

## System Requirements

- **Python:** 3.10, 3.11, 3.12, 3.13, or 3.14
- **Tesseract:** 5.0+ (system installation required)
- **NumPy:** 2.0+
- **Pillow:** 12.0+ (for image loading)
- **CMake:** 3.15+ (for building)

## License

This project is part of the [Coders repository](https://github.com/hironow/Coders).

## Contributing

Contributions are welcome! Please see the main repository for contribution guidelines.

---

**Built with:**
- [nanobind](https://github.com/wjakob/nanobind) - Modern C++/Python bindings
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Industry-standard OCR engine
- [NumPy](https://numpy.org/) - Efficient numerical computing
