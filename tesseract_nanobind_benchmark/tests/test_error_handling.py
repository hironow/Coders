"""Test error handling and edge cases."""

import numpy as np
import pytest
from PIL import Image

from tests.utils.fonts import load_test_font


def test_init_before_use():
    """Test that init must be called before using the API."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()

    # Should be able to create API without init
    assert api is not None

    # But need to init before using
    result = api.init("", "eng")
    assert result == 0


def test_init_with_invalid_language():
    """Test initialization with non-existent language."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()

    # Try to init with invalid language
    result = api.init("", "nonexistent_language_xyz")

    # Should fail (return non-zero)
    assert result != 0


def test_set_image_without_init():
    """Test setting image without initialization."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()

    # Create a simple image
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255

    # Should work even without init (init is needed for recognition though)
    api.set_image(image)


def test_invalid_image_shape():
    """Test with invalid image shapes."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # 2D array (grayscale) - should fail
    image_2d = np.ones((100, 100), dtype=np.uint8) * 255

    with pytest.raises((RuntimeError, ValueError, TypeError)):
        api.set_image(image_2d)


def test_invalid_image_channels():
    """Test with wrong number of channels."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # 4 channels (RGBA) - should fail since we expect 3
    image_4ch = np.ones((100, 100, 4), dtype=np.uint8) * 255

    with pytest.raises((RuntimeError, ValueError)):
        api.set_image(image_4ch)


def test_invalid_image_dtype():
    """Test with wrong data type."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Float array instead of uint8
    image_float = np.ones((100, 100, 3), dtype=np.float32)

    # Should handle or reject gracefully
    api.set_image(image_float)
    assert isinstance(api.get_utf8_text(), str)


def test_very_small_image():
    """Test with very small image."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # 1x1 image
    image = np.ones((1, 1, 3), dtype=np.uint8) * 255

    # Should handle gracefully
    api.set_image(image)
    text = api.get_utf8_text()

    # Should return empty or very short text
    assert len(text) < 10


def test_very_large_text():
    """Test with image containing lots of text."""
    from PIL import ImageDraw

    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Create image with multiple lines of text
    img = Image.new("RGB", (600, 400), color="white")
    draw = ImageDraw.Draw(img)

    font = load_test_font(20)

    # Draw multiple lines
    for i in range(10):
        draw.text(
            (10, 10 + i * 35), f"Line {i} with some text", fill="black", font=font
        )

    image = np.array(img)
    api.set_image(image)
    text = api.get_utf8_text()

    # Should recognize multiple lines
    assert len(text) > 50


def test_get_text_without_set_image():
    """Test getting text without setting image."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Try to get text without setting image
    assert api.get_utf8_text() == ""


def test_recognize_without_set_image():
    """Test recognizing without setting image."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Try to recognize without setting image
    assert api.recognize() != 0


def test_zero_size_dimension():
    """Test with zero-size dimension."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Empty array
    image = np.zeros((0, 100, 3), dtype=np.uint8)
    api.set_image(image)


def test_non_contiguous_array():
    """Test with non-contiguous NumPy array."""
    from tesseract_nanobind import TesseractAPI

    api = TesseractAPI()
    api.init("", "eng")

    # Create non-contiguous array
    full_image = np.ones((100, 100, 3), dtype=np.uint8) * 255

    # Slice creates non-contiguous array
    sliced = full_image[::2, ::2, :]

    # Should handle or convert to contiguous
    api.set_image(sliced)
    assert isinstance(api.get_utf8_text(), str)
