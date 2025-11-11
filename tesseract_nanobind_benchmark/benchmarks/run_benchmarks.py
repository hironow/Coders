#!/usr/bin/env python3
"""Benchmark tesseract_nanobind against pytesseract."""
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from tesseract_nanobind import TesseractAPI
import os
from pathlib import Path


def load_real_test_images():
    """Load real test images from pytesseract and tesserocr test data."""
    images = []
    image_names = []
    
    # Find test images from external repos
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
                images.append(np.array(img))
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
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 50), text, fill='black', font=font)
        images.append(np.array(img))
    
    return images


def create_test_images(count=10):
    """Create a mix of real and synthetic test images."""
    images = []
    
    # Try to load real test images first
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
            pil_img = Image.fromarray(img)
            text = pytesseract.image_to_string(pil_img)
    
    elapsed = time.time() - start
    return elapsed


def benchmark_tesseract_nanobind(images, iterations=1):
    """Benchmark tesseract_nanobind."""
    api = TesseractAPI()
    api.init("", "eng")
    
    start = time.time()
    
    for _ in range(iterations):
        for img in images:
            api.set_image(img)
            text = api.get_utf8_text()
    
    elapsed = time.time() - start
    return elapsed


def benchmark_tesseract_nanobind_with_boxes(images, iterations=1):
    """Benchmark tesseract_nanobind with bounding boxes."""
    api = TesseractAPI()
    api.init("", "eng")
    
    start = time.time()
    
    for _ in range(iterations):
        for img in images:
            api.set_image(img)
            api.recognize()
            boxes = api.get_bounding_boxes()
    
    elapsed = time.time() - start
    return elapsed


def validate_results(images):
    """Validate that both methods produce similar results."""
    print("\n=== Validation ===")
    
    # Test with first image
    img = images[0]
    
    # pytesseract result
    pil_img = Image.fromarray(img)
    pytess_text = pytesseract.image_to_string(pil_img).strip()
    
    # tesseract_nanobind result
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(img)
    nanobind_text = api.get_utf8_text().strip()
    
    print(f"pytesseract result: {repr(pytess_text[:50])}")
    print(f"nanobind result:    {repr(nanobind_text[:50])}")
    
    # Check if they are similar (may have minor differences in whitespace)
    pytess_words = set(pytess_text.lower().split())
    nanobind_words = set(nanobind_text.lower().split())
    
    if pytess_words and nanobind_words:
        overlap = len(pytess_words & nanobind_words) / max(len(pytess_words), len(nanobind_words))
        print(f"Word overlap: {overlap*100:.1f}%")
        
        if overlap > 0.8:
            print("✓ Results are consistent")
        else:
            print("⚠ Results may differ")
    else:
        print("Note: One or both results are empty")


def main():
    """Run all benchmarks."""
    print("Creating test images...")
    images = create_test_images(10)
    
    print(f"Number of test images: {len(images)}")
    print(f"Image size: {images[0].shape}")
    
    # Validate results first
    validate_results(images)
    
    # Warm up
    print("\n=== Warming up ===")
    benchmark_pytesseract(images[:2], 1)
    benchmark_tesseract_nanobind(images[:2], 1)
    
    # Run benchmarks
    iterations = 5
    print(f"\n=== Benchmarking ({iterations} iterations) ===")
    
    print("\n1. pytesseract (subprocess):")
    pytess_time = benchmark_pytesseract(images, iterations)
    print(f"   Total time: {pytess_time:.3f}s")
    print(f"   Per image: {pytess_time / (len(images) * iterations) * 1000:.1f}ms")
    
    print("\n2. tesseract_nanobind (direct API):")
    nanobind_time = benchmark_tesseract_nanobind(images, iterations)
    print(f"   Total time: {nanobind_time:.3f}s")
    print(f"   Per image: {nanobind_time / (len(images) * iterations) * 1000:.1f}ms")
    
    print("\n3. tesseract_nanobind with bounding boxes:")
    nanobind_boxes_time = benchmark_tesseract_nanobind_with_boxes(images, iterations)
    print(f"   Total time: {nanobind_boxes_time:.3f}s")
    print(f"   Per image: {nanobind_boxes_time / (len(images) * iterations) * 1000:.1f}ms")
    
    # Calculate speedup
    print("\n=== Performance Comparison ===")
    speedup = pytess_time / nanobind_time
    print(f"tesseract_nanobind is {speedup:.2f}x faster than pytesseract")
    
    if nanobind_time < pytess_time:
        improvement = (1 - nanobind_time / pytess_time) * 100
        print(f"Performance improvement: {improvement:.1f}%")
    
    print("\n=== Summary ===")
    print(f"✓ All benchmarks completed successfully")
    print(f"✓ tesseract_nanobind demonstrates {'better' if speedup > 1 else 'comparable'} performance")


if __name__ == "__main__":
    main()
