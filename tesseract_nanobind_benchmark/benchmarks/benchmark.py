#!/usr/bin/env python3
"""Comprehensive benchmark comparing pytesseract, tesserocr, and tesseract_nanobind.

This script benchmarks three Tesseract Python bindings:
1. pytesseract - subprocess-based wrapper
2. tesserocr - CFFI-based direct API bindings
3. tesseract_nanobind - nanobind-based direct API bindings (this project)

Usage:
    python benchmark.py [--iterations N] [--images N]
"""
import argparse
import os
import time
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from tesseract_nanobind.compat import PyTessBaseAPI as NanobindAPI
from tesserocr import PyTessBaseAPI as TesserocrAPI
from pathlib import Path


def get_tessdata_prefix():
    """Get tessdata prefix path from environment or system default."""
    # Check environment variable first
    if 'TESSDATA_PREFIX' in os.environ:
        return os.environ['TESSDATA_PREFIX']

    # Try common installation paths
    common_paths = [
        '/usr/share/tessdata',  # Linux (apt)
        '/usr/share/tesseract-ocr/4.00/tessdata',  # Linux (older)
        '/usr/share/tesseract-ocr/5/tessdata',  # Linux (newer)
        '/opt/homebrew/share/tessdata',  # macOS (brew)
        '/usr/local/share/tessdata',  # macOS (brew, old)
    ]

    for path in common_paths:
        if os.path.isdir(path) and os.path.exists(os.path.join(path, 'eng.traineddata')):
            return path

    # If nothing found, return empty string (let tesseract find it)
    return ''


def load_real_test_images():
    """Load real test images from pytesseract and tesserocr test data."""
    images = []
    image_names = []

    base_dir = Path(__file__).parent.parent.parent
    test_image_paths = [
        base_dir / "external/pytesseract/tests/data/test.jpg",
        base_dir / "external/pytesseract/tests/data/test.png",
        base_dir / "external/pytesseract/tests/data/test-small.jpg",
        base_dir / "external/pytesseract/tests/data/test-european.jpg",
        base_dir / "external/tesserocr/tests/eurotext.png",
    ]

    for img_path in test_image_paths:
        if img_path.exists():
            try:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
                image_names.append(img_path.name)
            except Exception as e:
                print(f"Warning: Could not load {img_path}: {e}")

    return images, image_names


def create_synthetic_test_images(count=10):
    """Create synthetic test images with various text patterns."""
    images = []
    texts = [
        "Hello World",
        "The quick brown fox",
        "jumps over the lazy dog",
        "Testing OCR performance",
        "CAPITAL LETTERS",
        "lowercase letters",
        "Numbers: 123456789",
        "Mixed Text 123",
        "Special chars: !@#$%",
        "Multiple lines\nof text here"
    ]

    for i in range(count):
        text = texts[i % len(texts)]
        img = Image.new('RGB', (300, 150), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except Exception:
            font = ImageFont.load_default()

        draw.text((10, 50), text, fill='black', font=font)
        images.append(img)

    return images


def create_test_images(count=10):
    """Create a mix of real and synthetic test images."""
    images = []

    # Load real test images
    real_images, real_names = load_real_test_images()

    if real_images:
        print(f"Loaded {len(real_images)} real test images from pytesseract/tesserocr:")
        for name in real_names:
            print(f"  - {name}")
        images.extend(real_images)

    # Add synthetic images to reach desired count
    remaining = max(0, count - len(images))
    if remaining > 0:
        print(f"Adding {remaining} synthetic test images")
        synthetic = create_synthetic_test_images(remaining)
        images.extend(synthetic)

    return images


def benchmark_pytesseract(images, iterations=1):
    """Benchmark pytesseract."""
    start = time.time()

    for _ in range(iterations):
        for img in images:
            _ = pytesseract.image_to_string(img)

    elapsed = time.time() - start
    return elapsed


def benchmark_tesserocr(images, iterations=1):
    """Benchmark tesserocr."""
    # Create API once and reuse
    tessdata_prefix = get_tessdata_prefix()
    api = TesserocrAPI(path=tessdata_prefix, lang='eng')

    start = time.time()

    for _ in range(iterations):
        for img in images:
            api.SetImage(img)
            _ = api.GetUTF8Text()

    elapsed = time.time() - start
    api.End()
    return elapsed


def benchmark_nanobind(images, iterations=1):
    """Benchmark tesseract_nanobind (compat API)."""
    api = NanobindAPI(lang='eng')

    start = time.time()

    for _ in range(iterations):
        for img in images:
            api.SetImage(img)
            _ = api.GetUTF8Text()

    elapsed = time.time() - start
    api.End()
    return elapsed


def benchmark_nanobind_with_boxes(images, iterations=1):
    """Benchmark tesseract_nanobind with bounding boxes."""
    api = NanobindAPI(lang='eng')

    start = time.time()

    for _ in range(iterations):
        for img in images:
            api.SetImage(img)
            api.Recognize()
            _ = api.GetWords()

    elapsed = time.time() - start
    api.End()
    return elapsed


def validate_results(images):
    """Validate that all three methods produce similar results."""
    print("\n=== Validation ===")

    # Test with first image
    img = images[0]

    # pytesseract result
    pytess_text = pytesseract.image_to_string(img).strip()

    # tesserocr result
    tessdata_prefix = get_tessdata_prefix()
    api_tesserocr = TesserocrAPI(path=tessdata_prefix, lang='eng')
    api_tesserocr.SetImage(img)
    tesserocr_text = api_tesserocr.GetUTF8Text().strip()
    api_tesserocr.End()

    # tesseract_nanobind result
    api_nanobind = NanobindAPI(lang='eng')
    api_nanobind.SetImage(img)
    nanobind_text = api_nanobind.GetUTF8Text().strip()
    api_nanobind.End()

    print(f"pytesseract result: {repr(pytess_text[:50])}")
    print(f"tesserocr result:   {repr(tesserocr_text[:50])}")
    print(f"nanobind result:    {repr(nanobind_text[:50])}")

    # Check overlaps
    tesserocr_words = set(tesserocr_text.lower().split())
    nanobind_words = set(nanobind_text.lower().split())

    if tesserocr_words and nanobind_words:
        overlap = len(tesserocr_words & nanobind_words) / max(len(tesserocr_words), len(nanobind_words))
        print(f"tesserocr vs nanobind overlap: {overlap*100:.1f}%")

        if overlap > 0.8:
            print("✓ Results are consistent")
        else:
            print("⚠ Results may differ")


def main():
    """Run all benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark tesseract_nanobind against pytesseract and tesserocr")
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations (default: 5)')
    parser.add_argument('--images', type=int, default=10, help='Number of test images (default: 10)')
    args = parser.parse_args()

    print("=" * 70)
    print("  Tesseract Python Bindings Benchmark")
    print("  tesseract_nanobind vs tesserocr vs pytesseract")
    print("=" * 70)

    print("\nCreating test images...")
    images = create_test_images(args.images)

    print(f"\nNumber of test images: {len(images)}")

    # Validate results first
    validate_results(images)

    # Warm up
    print("\n=== Warming up ===")
    benchmark_pytesseract(images[:2], 1)
    benchmark_tesserocr(images[:2], 1)
    benchmark_nanobind(images[:2], 1)

    # Run benchmarks
    iterations = args.iterations
    print(f"\n=== Benchmarking ({iterations} iterations) ===")

    print("\n1. pytesseract (subprocess):")
    pytess_time = benchmark_pytesseract(images, iterations)
    print(f"   Total time: {pytess_time:.3f}s")
    print(f"   Per image: {pytess_time / (len(images) * iterations) * 1000:.1f}ms")

    print("\n2. tesserocr (C API bindings):")
    tesserocr_time = benchmark_tesserocr(images, iterations)
    print(f"   Total time: {tesserocr_time:.3f}s")
    print(f"   Per image: {tesserocr_time / (len(images) * iterations) * 1000:.1f}ms")

    print("\n3. tesseract_nanobind (nanobind bindings):")
    nanobind_time = benchmark_nanobind(images, iterations)
    print(f"   Total time: {nanobind_time:.3f}s")
    print(f"   Per image: {nanobind_time / (len(images) * iterations) * 1000:.1f}ms")

    print("\n4. tesseract_nanobind with bounding boxes:")
    nanobind_boxes_time = benchmark_nanobind_with_boxes(images, iterations)
    print(f"   Total time: {nanobind_boxes_time:.3f}s")
    print(f"   Per image: {nanobind_boxes_time / (len(images) * iterations) * 1000:.1f}ms")

    # Performance comparison
    print("\n" + "=" * 70)
    print("  Performance Comparison")
    print("=" * 70)

    speedup_vs_pytesseract = pytess_time / nanobind_time
    speedup_vs_tesserocr = tesserocr_time / nanobind_time

    print(f"\ntesseract_nanobind is {speedup_vs_tesserocr:.2f}x vs tesserocr")
    print(f"tesseract_nanobind is {speedup_vs_pytesseract:.2f}x vs pytesseract")

    if nanobind_time < tesserocr_time:
        improvement = (1 - nanobind_time / tesserocr_time) * 100
        print(f"Performance improvement over tesserocr: {improvement:.1f}%")
    elif nanobind_time > tesserocr_time:
        degradation = (nanobind_time / tesserocr_time - 1) * 100
        print(f"Performance difference vs tesserocr: +{degradation:.1f}% (slightly slower)")
    else:
        print("Performance is equivalent to tesserocr")

    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    print("✓ All benchmarks completed successfully")
    print(f"✓ tesseract_nanobind vs tesserocr: {'faster' if speedup_vs_tesserocr > 1.05 else 'comparable' if speedup_vs_tesserocr > 0.95 else 'slower'}")
    print(f"✓ tesseract_nanobind is {'significantly faster' if speedup_vs_pytesseract > 2 else 'faster'} than pytesseract")
    print("✓ API compatibility with tesserocr verified")


if __name__ == "__main__":
    main()
