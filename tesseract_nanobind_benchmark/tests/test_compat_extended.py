"""Extended tests for tesserocr compatibility layer - comprehensive API coverage."""
import pytest
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile


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


# ============================================================================
# Enum Completeness Tests
# ============================================================================

def test_oem_enum_all_values():
    """Test that OEM enum has all tesserocr values."""
    from tesseract_nanobind.compat import OEM

    # given: OEM enum
    # when: checking all expected values
    # then: all values should be present
    assert hasattr(OEM, 'TESSERACT_ONLY')
    assert hasattr(OEM, 'LSTM_ONLY')
    assert hasattr(OEM, 'TESSERACT_LSTM_COMBINED')
    assert hasattr(OEM, 'DEFAULT')

    assert OEM.TESSERACT_ONLY == 0
    assert OEM.LSTM_ONLY == 1
    assert OEM.TESSERACT_LSTM_COMBINED == 2
    assert OEM.DEFAULT == 3


def test_psm_enum_all_values():
    """Test that PSM enum has all tesserocr values."""
    from tesseract_nanobind.compat import PSM

    # given: PSM enum
    # when: checking all 14 expected values
    # then: all values should be present with correct numbers
    assert PSM.OSD_ONLY == 0
    assert PSM.AUTO_OSD == 1
    assert PSM.AUTO_ONLY == 2
    assert PSM.AUTO == 3
    assert PSM.SINGLE_COLUMN == 4
    assert PSM.SINGLE_BLOCK_VERT_TEXT == 5
    assert PSM.SINGLE_BLOCK == 6
    assert PSM.SINGLE_LINE == 7
    assert PSM.SINGLE_WORD == 8
    assert PSM.CIRCLE_WORD == 9
    assert PSM.SINGLE_CHAR == 10
    assert PSM.SPARSE_TEXT == 11
    assert PSM.SPARSE_TEXT_OSD == 12
    assert PSM.RAW_LINE == 13
    assert PSM.COUNT == 14


def test_ril_enum_all_values():
    """Test that RIL enum has all tesserocr values."""
    from tesseract_nanobind.compat import RIL

    # given: RIL enum
    # when: checking all 5 expected values
    # then: all values should be present with correct numbers
    assert RIL.BLOCK == 0
    assert RIL.PARA == 1
    assert RIL.TEXTLINE == 2
    assert RIL.WORD == 3
    assert RIL.SYMBOL == 4


# ============================================================================
# Stub Method Behavior Tests
# ============================================================================

def test_set_page_seg_mode_stub():
    """Test SetPageSegMode stub behavior (accepts but ignores)."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: calling SetPageSegMode
        result = api.SetPageSegMode(PSM.SINGLE_LINE)

        # then: should not raise error, returns None
        assert result is None


def test_get_page_seg_mode_stub():
    """Test GetPageSegMode returns current mode."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: calling GetPageSegMode (default mode)
        psm = api.GetPageSegMode()

        # then: should return valid PSM value
        # Default is usually SINGLE_BLOCK (6) or AUTO (3)
        assert psm in [PSM.AUTO, PSM.SINGLE_BLOCK, PSM.SINGLE_COLUMN]


def test_set_variable_stub():
    """Test SetVariable now works."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: calling SetVariable with valid variable
        result = api.SetVariable('tessedit_char_whitelist', '0123456789')

        # then: should return True (implemented)
        assert result is True


def test_set_rectangle_stub():
    """Test SetRectangle stub behavior (accepts but ignores)."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API with image
    image = create_test_image_with_text("Test")
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)

        # when: calling SetRectangle
        result = api.SetRectangle(10, 10, 50, 50)

        # then: should not raise error, returns None
        assert result is None


def test_get_iterator_stub():
    """Test GetIterator stub behavior (always returns None)."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API with recognized image
    image = create_test_image_with_text("Test")
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()

        # when: calling GetIterator
        iterator = api.GetIterator()

        # then: should return None (not implemented)
        assert iterator is None


# ============================================================================
# Helper Function Tests
# ============================================================================

def test_file_to_text_helper():
    """Test file_to_text helper function."""
    from tesseract_nanobind.compat import file_to_text

    # given: temporary image file
    image = create_test_image_with_text("FileTest")
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image.save(f.name)
        temp_path = f.name

    try:
        # when: converting file to text
        text = file_to_text(temp_path, lang='eng')

        # then: should return text containing expected content
        assert isinstance(text, str)
        assert "FileTest" in text or "filetest" in text.lower()
    finally:
        # cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_get_languages_helper():
    """Test get_languages helper function."""
    from tesseract_nanobind.compat import get_languages

    # given: no specific path
    # when: calling get_languages
    path, languages = get_languages()

    # then: should return tuple with path and language list
    assert isinstance(path, str)
    assert isinstance(languages, list)
    assert 'eng' in languages


def test_get_languages_with_custom_path():
    """Test get_languages with custom path."""
    from tesseract_nanobind.compat import get_languages

    # given: custom path
    custom_path = '/custom/tessdata/'

    # when: calling get_languages with path
    path, languages = get_languages(custom_path)

    # then: should return the custom path
    assert path == custom_path
    assert isinstance(languages, list)


# ============================================================================
# Initialization and Configuration Tests
# ============================================================================

def test_init_without_auto_init():
    """Test initialization with init=False parameter."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API created without auto-init
    # when: creating API with init=False
    api = PyTessBaseAPI(lang='eng', init=False)

    # then: API should not be initialized
    assert api is not None
    assert not api._initialized


def test_manual_init():
    """Test manual Init() call after creation."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API created without auto-init
    api = PyTessBaseAPI(lang='eng', init=False)

    # when: manually calling Init
    api.Init(path='', lang='eng')

    # then: API should be initialized
    assert api._initialized


def test_init_with_different_oem():
    """Test initialization with different OEM values."""
    from tesseract_nanobind.compat import PyTessBaseAPI, OEM

    # given: different OEM values
    oem_values = [OEM.TESSERACT_ONLY, OEM.LSTM_ONLY, OEM.DEFAULT]

    for oem in oem_values:
        # when: initializing with OEM value
        with PyTessBaseAPI(lang='eng', oem=oem) as api:
            # then: should initialize successfully (OEM is ignored but accepted)
            assert api._initialized


def test_init_with_different_psm():
    """Test initialization with different PSM values."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: different PSM values
    psm_values = [PSM.AUTO, PSM.SINGLE_LINE, PSM.SINGLE_WORD]

    for psm in psm_values:
        # when: initializing with PSM value
        with PyTessBaseAPI(lang='eng', psm=psm) as api:
            # then: should initialize successfully (PSM is ignored but accepted)
            assert api._initialized


def test_end_method():
    """Test End() method marks API as uninitialized."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    api = PyTessBaseAPI(lang='eng')
    assert api._initialized

    # when: calling End
    api.End()

    # then: should mark as uninitialized
    assert not api._initialized


# ============================================================================
# Image Input Tests
# ============================================================================

def test_set_image_file_method():
    """Test SetImageFile method with file path."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: temporary image file
    image = create_test_image_with_text("ImageFile")
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image.save(f.name)
        temp_path = f.name

    try:
        # when: setting image from file
        with PyTessBaseAPI(lang='eng') as api:
            api.SetImageFile(temp_path)
            text = api.GetUTF8Text()

            # then: should read and process the image
            assert isinstance(text, str)
    finally:
        # cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_set_image_file_nonexistent():
    """Test SetImageFile with nonexistent file raises error."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: nonexistent file path
    nonexistent_path = '/tmp/nonexistent_image_12345.png'

    # when/then: should raise RuntimeError
    with PyTessBaseAPI(lang='eng') as api:
        with pytest.raises(RuntimeError):
            api.SetImageFile(nonexistent_path)


def test_set_image_grayscale_conversion():
    """Test SetImage with grayscale PIL Image (auto-converts to RGB)."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: grayscale PIL Image
    gray_image = Image.new('L', (200, 100), color=255)
    draw = ImageDraw.Draw(gray_image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 30), "Gray", fill=0, font=font)

    # when: setting grayscale image
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(gray_image)
        text = api.GetUTF8Text()

        # then: should auto-convert and process
        assert isinstance(text, str)


def test_set_image_rgba_conversion():
    """Test SetImage with RGBA PIL Image (auto-converts to RGB)."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: RGBA PIL Image
    rgba_image = Image.new('RGBA', (200, 100), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(rgba_image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 30), "RGBA", fill=(0, 0, 0, 255), font=font)

    # when: setting RGBA image
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(rgba_image)
        text = api.GetUTF8Text()

        # then: should auto-convert and process
        assert isinstance(text, str)


def test_set_image_invalid_type():
    """Test SetImage with invalid type raises TypeError."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: invalid image type (string)
    invalid_image = "not an image"

    # when/then: should raise TypeError
    with PyTessBaseAPI(lang='eng') as api:
        with pytest.raises(TypeError):
            api.SetImage(invalid_image)


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_init_with_invalid_language():
    """Test Init with invalid language raises RuntimeError."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API created without auto-init
    api = PyTessBaseAPI(init=False)

    # when/then: initializing with invalid language should raise
    with pytest.raises(RuntimeError) as exc_info:
        api.Init(path='', lang='nonexistent_xyz')

    assert 'Failed to initialize' in str(exc_info.value)


def test_get_utf8_text_without_init():
    """Test GetUTF8Text without initialization raises RuntimeError."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when/then: calling GetUTF8Text should raise
    with pytest.raises(RuntimeError) as exc_info:
        api.GetUTF8Text()

    assert 'not initialized' in str(exc_info.value).lower()


def test_set_image_without_init():
    """Test SetImage without initialization raises RuntimeError."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)
    image = create_test_image_with_text("Test")

    # when/then: calling SetImage should raise
    with pytest.raises(RuntimeError) as exc_info:
        api.SetImage(image)

    assert 'not initialized' in str(exc_info.value).lower()


def test_recognize_without_init():
    """Test Recognize without initialization raises RuntimeError."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when/then: calling Recognize should raise RuntimeError
    with pytest.raises(RuntimeError, match="API not initialized"):
        api.Recognize()


def test_mean_text_conf_without_init():
    """Test MeanTextConf without initialization returns 0."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling MeanTextConf
    conf = api.MeanTextConf()

    # then: should return 0
    assert conf == 0


def test_all_word_confidences_without_init():
    """Test AllWordConfidences without initialization returns empty list."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling AllWordConfidences
    confs = api.AllWordConfidences()

    # then: should return empty list
    assert confs == []


def test_all_words_without_init():
    """Test AllWords without initialization returns empty list."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling AllWords
    words = api.AllWords()

    # then: should return empty list
    assert words == []


def test_get_init_languages_without_init():
    """Test GetInitLanguagesAsString without initialization returns empty string."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling GetInitLanguagesAsString
    lang = api.GetInitLanguagesAsString()

    # then: should return empty string
    assert lang == ''


# ============================================================================
# Integration Tests
# ============================================================================

def test_multiple_images_same_api():
    """Test processing multiple images with the same API instance."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: multiple test images
    image1 = create_test_image_with_text("First")
    image2 = create_test_image_with_text("Second")

    # when: processing multiple images with same API
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image1)
        text1 = api.GetUTF8Text()

        api.SetImage(image2)
        text2 = api.GetUTF8Text()

        # then: should process both correctly
        assert "First" in text1 or "first" in text1.lower()
        assert "Second" in text2 or "second" in text2.lower()


def test_context_manager_automatic_cleanup():
    """Test context manager properly cleans up resources."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API used as context manager
    api = None
    with PyTessBaseAPI(lang='eng') as api_instance:
        api = api_instance
        assert api._initialized

    # when: exiting context manager
    # then: API should be cleaned up
    assert not api._initialized


def test_recognize_returns_true_on_success():
    """Test that Recognize returns True on successful recognition."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: valid image
    image = create_test_image_with_text("Success")

    # when: performing recognition
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        result = api.Recognize(timeout=0)

        # then: should return True
        assert result is True


def test_word_confidences_match_words():
    """Test that AllWordConfidences matches AllWords in length."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Match Test")

    # when: getting words and confidences
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        words = api.AllWords()
        confs = api.AllWordConfidences()

        # then: should have same length
        assert len(words) == len(confs)


def test_map_word_confidences_completeness():
    """Test MapWordConfidences returns all words with confidences."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Complete")

    # when: getting map of word confidences
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        pairs = api.MapWordConfidences()
        words = api.AllWords()

        # then: should have same number of items
        assert len(pairs) == len(words)

        # then: each word should have a confidence
        for word, conf in pairs:
            assert word in words
            assert 0 <= conf <= 100
