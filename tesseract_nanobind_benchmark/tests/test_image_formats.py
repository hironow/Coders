"""Test different image formats and input types."""
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os


def create_test_image(text="Test", format="PNG"):
    """Create a test image in various formats."""
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 30), text, fill='black', font=font)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix=f'.{format.lower()}', delete=False) as f:
        img.save(f, format=format)
        return f.name


@pytest.mark.parametrize('image_format', ['PNG', 'JPEG', 'TIFF'])
def test_different_image_formats(image_format):
    """Test OCR with different image formats."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an image in specific format
    image_path = create_test_image("Hello", format=image_format)
    
    try:
        # Load as NumPy array
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_array = np.array(img)
        
        # when: performing OCR
        api = TesseractAPI()
        api.init("", "eng")
        api.set_image(image_array)
        text = api.get_utf8_text()
        
        # then: we should recognize the text
        assert "Hello" in text or "hello" in text.lower()
    finally:
        os.unlink(image_path)


def test_numpy_array_input():
    """Test OCR with NumPy array input."""
    from tesseract_nanobind import TesseractAPI
    
    # given: a NumPy array image
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    draw.text((10, 30), "Test", fill='black', font=font)
    
    image_array = np.array(img)
    
    # when: performing OCR
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image_array)
    text = api.get_utf8_text()
    
    # then: we should recognize the text
    assert "Test" in text or "test" in text.lower()


def test_image_array_shape_validation():
    """Test that incorrect image shapes are rejected."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an incorrect image shape (2D instead of 3D)
    image = np.ones((100, 100), dtype=np.uint8) * 255
    
    # when/then: setting image should fail
    api = TesseractAPI()
    api.init("", "eng")
    
    with pytest.raises((RuntimeError, ValueError, TypeError)):
        api.set_image(image)


def test_grayscale_image_conversion():
    """Test OCR with grayscale image converted to RGB."""
    from tesseract_nanobind import TesseractAPI
    
    # given: a grayscale image converted to RGB
    img = Image.new('L', (200, 100), color=255)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    draw.text((10, 30), "Gray", fill=0, font=font)
    
    # Convert to RGB
    img_rgb = img.convert('RGB')
    image_array = np.array(img_rgb)
    
    # when: performing OCR
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image_array)
    text = api.get_utf8_text()
    
    # then: we should recognize the text
    assert "Gray" in text or "gray" in text.lower()
