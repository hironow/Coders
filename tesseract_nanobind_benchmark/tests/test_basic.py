"""Basic tests for tesseract_nanobind."""
import numpy as np


def test_import():
    """Test that the module can be imported."""
    import tesseract_nanobind
    assert tesseract_nanobind is not None


def test_version():
    """Test that version information is available."""
    import tesseract_nanobind
    assert hasattr(tesseract_nanobind, '__version__')
    assert isinstance(tesseract_nanobind.__version__, str)


def test_tesseract_api_constructor():
    """Test TesseractAPI can be constructed."""
    from tesseract_nanobind import TesseractAPI
    api = TesseractAPI()
    assert api is not None


def test_tesseract_api_init():
    """Test TesseractAPI can be initialized."""
    from tesseract_nanobind import TesseractAPI
    api = TesseractAPI()
    # Init with empty datapath uses system tessdata
    result = api.init("", "eng")
    assert result == 0  # 0 means success


def test_simple_ocr():
    """Test simple OCR on a black and white image with text."""
    from tesseract_nanobind import TesseractAPI
    
    # given: a simple image with white text on black background
    # Create a simple 100x100 image (will be replaced with real test data)
    width, height = 100, 100
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # when: performing OCR
    api = TesseractAPI()
    api.init("", "eng")
    api.set_image(image)
    text = api.get_utf8_text()
    
    # then: we should get a string result (even if empty for blank image)
    assert isinstance(text, str)
