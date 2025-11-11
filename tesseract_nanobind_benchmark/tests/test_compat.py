"""Tests for tesserocr compatibility layer."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_test_image_with_text(text="Test", width=200, height=100):
    """Create a simple test image with text."""
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    
    draw.text((10, 30), text, fill='black', font=font)
    return image


def test_import_compat():
    """Test that compat module can be imported."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    assert PyTessBaseAPI is not None


def test_pytessbaseapi_init():
    """Test PyTessBaseAPI initialization."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    api = PyTessBaseAPI(lang='eng')
    assert api is not None


def test_pytessbaseapi_context_manager():
    """Test PyTessBaseAPI as context manager."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    with PyTessBaseAPI(lang='eng') as api:
        assert api is not None


def test_set_image_pil():
    """Test SetImage with PIL Image."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Hello")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        text = api.GetUTF8Text()
        assert isinstance(text, str)


def test_get_utf8_text():
    """Test GetUTF8Text method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("World")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        text = api.GetUTF8Text()
        assert "World" in text or "world" in text.lower()


def test_mean_text_conf():
    """Test MeanTextConf method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Test")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()
        conf = api.MeanTextConf()
        assert isinstance(conf, (int, float))
        assert 0 <= conf <= 100


def test_all_word_confidences():
    """Test AllWordConfidences method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Hello World")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        confs = api.AllWordConfidences()
        assert isinstance(confs, list)
        assert len(confs) > 0


def test_all_words():
    """Test AllWords method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Test Text")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        words = api.AllWords()
        assert isinstance(words, list)
        assert len(words) > 0


def test_map_word_confidences():
    """Test MapWordConfidences method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Test")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        pairs = api.MapWordConfidences()
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        # Each pair should be (word, confidence)
        for word, conf in pairs:
            assert isinstance(word, str)
            assert isinstance(conf, (int, float))


def test_image_to_text_helper():
    """Test image_to_text helper function."""
    from tesseract_nanobind.compat import image_to_text
    
    image = create_test_image_with_text("Helper")
    text = image_to_text(image, lang='eng')
    
    assert isinstance(text, str)
    assert "Helper" in text or "helper" in text.lower()


def test_tesseract_version():
    """Test tesseract_version helper."""
    from tesseract_nanobind.compat import tesseract_version
    
    version = tesseract_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_version_static_method():
    """Test Version static method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    version = PyTessBaseAPI.Version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_enums_exist():
    """Test that enum classes exist."""
    from tesseract_nanobind.compat import OEM, PSM, RIL
    
    assert hasattr(OEM, 'DEFAULT')
    assert hasattr(PSM, 'AUTO')
    assert hasattr(RIL, 'WORD')


def test_setimage_numpy_array():
    """Test SetImage with NumPy array."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("NumPy")
    image_array = np.array(image)
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image_array)
        text = api.GetUTF8Text()
        assert isinstance(text, str)


def test_recognize_method():
    """Test Recognize method returns True on success."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    image = create_test_image_with_text("Test")
    
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        result = api.Recognize()
        assert result is True


def test_get_init_languages():
    """Test GetInitLanguagesAsString method."""
    from tesseract_nanobind.compat import PyTessBaseAPI
    
    with PyTessBaseAPI(lang='eng') as api:
        lang = api.GetInitLanguagesAsString()
        assert lang == 'eng'
