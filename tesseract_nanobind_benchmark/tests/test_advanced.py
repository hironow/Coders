"""Advanced tests for tesseract_nanobind with real OCR operations."""
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont


def create_test_image_with_text(text="Hello", width=200, height=100):
    """Create a simple test image with text."""
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Use default font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text in black
    draw.text((10, 30), text, fill='black', font=font)
    
    # Convert to numpy array
    return np.array(image)


def test_ocr_with_real_text():
    """Test OCR with a real text image."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an image with text
    image = create_test_image_with_text("Hello")
    
    # when: performing OCR
    api = TesseractAPI()
    result = api.init("", "eng")
    assert result == 0
    
    api.set_image(image)
    text = api.get_utf8_text()
    
    # then: we should recognize the text
    assert "Hello" in text or "hello" in text.lower()


def test_ocr_with_numbers():
    """Test OCR with numbers."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an image with numbers
    image = create_test_image_with_text("12345")
    
    # when: performing OCR
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image)
    text = api.get_utf8_text()
    
    # then: we should recognize the numbers
    assert any(digit in text for digit in "12345")


def test_multiple_ocr_operations():
    """Test multiple OCR operations on the same API instance."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an API instance
    api = TesseractAPI()
    api.init("", "eng")
    
    # when: performing multiple OCR operations
    image1 = create_test_image_with_text("First")
    api.set_image(image1)
    text1 = api.get_utf8_text()
    
    image2 = create_test_image_with_text("Second")
    api.set_image(image2)
    text2 = api.get_utf8_text()
    
    # then: each should return different results
    assert text1 != text2


def test_empty_image():
    """Test OCR on an empty/white image."""
    from tesseract_nanobind import TesseractAPI
    
    # given: a white image with no text
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    # when: performing OCR
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image)
    text = api.get_utf8_text()
    
    # then: result should be empty or minimal
    assert len(text.strip()) == 0 or len(text.strip()) < 5


def test_get_bounding_boxes():
    """Test getting bounding boxes for recognized text."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an image with text
    image = create_test_image_with_text("Test")
    
    # when: getting bounding boxes
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image)
    
    # Recognize first
    api.recognize()
    
    # Get bounding boxes
    boxes = api.get_bounding_boxes()
    
    # then: we should have bounding boxes
    assert isinstance(boxes, list)
    assert len(boxes) > 0
    
    # Each box should have coordinates
    for box in boxes:
        assert 'text' in box
        assert 'left' in box
        assert 'top' in box
        assert 'width' in box
        assert 'height' in box
        assert 'confidence' in box


def test_get_confidence_scores():
    """Test getting confidence scores for recognized text."""
    from tesseract_nanobind import TesseractAPI
    
    # given: an image with clear text
    image = create_test_image_with_text("ABC")
    
    # when: performing OCR and getting confidence
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image)
    api.recognize()
    
    confidence = api.get_mean_confidence()
    
    # then: confidence should be reasonable
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 100
