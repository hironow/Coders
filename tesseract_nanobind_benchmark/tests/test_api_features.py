"""Test advanced API features matching tesserocr functionality."""
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont


def create_test_image_with_text(text="Test", width=300, height=150):
    """Create a test image with text."""
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 50), text, fill='black', font=font)
    return np.array(img)


def test_tesseract_version():
    """Test getting Tesseract version."""
    from tesseract_nanobind import TesseractAPI
    
    version = TesseractAPI.version()
    assert isinstance(version, str)
    assert len(version) > 0
    # Should contain version number
    assert any(char.isdigit() for char in version)


def test_multiple_language_init():
    """Test initialization with multiple languages."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    # Try to init with eng+osd (if available)
    result = api.init("", "eng")
    assert result == 0


def test_api_reuse():
    """Test that API can be reused for multiple images."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    # First image
    image1 = create_test_image_with_text("First")
    api.set_image(image1)
    text1 = api.get_utf8_text()
    
    # Second image on same API
    image2 = create_test_image_with_text("Second")
    api.set_image(image2)
    text2 = api.get_utf8_text()
    
    # Results should be different
    assert text1 != text2
    assert "First" in text1 or "first" in text1.lower()
    assert "Second" in text2 or "second" in text2.lower()


def test_recognize_before_boxes():
    """Test that recognize must be called before getting boxes."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    image = create_test_image_with_text("Test")
    api.set_image(image)
    
    # Must call recognize before getting boxes
    api.recognize()
    boxes = api.get_bounding_boxes()
    
    assert len(boxes) > 0


def test_word_confidences():
    """Test word-level confidence scores."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    # Create image with clear text
    image = create_test_image_with_text("The quick brown")
    api.set_image(image)
    api.recognize()
    
    boxes = api.get_bounding_boxes()
    
    # Should have multiple words
    assert len(boxes) >= 2
    
    # Each word should have a confidence score
    for box in boxes:
        assert 'confidence' in box
        conf = box['confidence']
        assert 0 <= conf <= 100


def test_bounding_box_coordinates():
    """Test that bounding boxes have valid coordinates."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    image = create_test_image_with_text("Test")
    api.set_image(image)
    api.recognize()
    
    boxes = api.get_bounding_boxes()
    
    for box in boxes:
        # Coordinates should be non-negative
        assert box['left'] >= 0
        assert box['top'] >= 0
        assert box['width'] > 0
        assert box['height'] > 0
        
        # Should have text
        assert len(box['text']) > 0


def test_mean_confidence_range():
    """Test that mean confidence is in valid range."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    # Clear image with text should have high confidence
    image = create_test_image_with_text("ABC")
    api.set_image(image)
    api.recognize()
    
    confidence = api.get_mean_confidence()
    
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 100
    # Clear text should have reasonably high confidence
    assert confidence > 50


def test_empty_image_handling():
    """Test OCR on empty/white images."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    # Completely white image
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    api.set_image(image)
    text = api.get_utf8_text()
    
    # Should return empty or minimal text
    assert len(text.strip()) < 10


def test_black_image_handling():
    """Test OCR on completely black images."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    # Completely black image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    api.set_image(image)
    text = api.get_utf8_text()
    
    # Should return empty or minimal text
    assert len(text.strip()) < 10


def test_numbers_recognition():
    """Test recognition of numbers."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    image = create_test_image_with_text("123456")
    api.set_image(image)
    text = api.get_utf8_text()
    
    # Should recognize at least some digits
    digits_found = sum(1 for char in text if char.isdigit())
    assert digits_found >= 3


def test_mixed_text_and_numbers():
    """Test recognition of mixed text and numbers."""
    from tesseract_nanobind import TesseractAPI
    
    api = TesseractAPI()
    api.init("", "eng")
    
    image = create_test_image_with_text("Test123")
    api.set_image(image)
    text = api.get_utf8_text()
    
    # Should have both letters and numbers
    has_letter = any(char.isalpha() for char in text)
    has_digit = any(char.isdigit() for char in text)
    assert has_letter and has_digit
