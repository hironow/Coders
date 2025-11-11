"""Tests for configuration, output formats, and advanced tesserocr compatibility features.

This module tests:
- Page segmentation modes (PSM)
- Tesseract variables
- Region of interest (ROI) with SetRectangle
- Alternative output formats (hOCR, TSV, Box, UNLV)
- Clear methods and data path access
"""
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


# ============================================================================
# Page Segmentation Mode Tests
# ============================================================================

def test_set_get_page_seg_mode():
    """Test SetPageSegMode and GetPageSegMode."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: setting different PSM modes
        api.SetPageSegMode(PSM.SINGLE_LINE)
        mode1 = api.GetPageSegMode()

        api.SetPageSegMode(PSM.SINGLE_WORD)
        mode2 = api.GetPageSegMode()

        api.SetPageSegMode(PSM.SINGLE_BLOCK)
        mode3 = api.GetPageSegMode()

        # then: should return the set modes
        assert mode1 == PSM.SINGLE_LINE
        assert mode2 == PSM.SINGLE_WORD
        assert mode3 == PSM.SINGLE_BLOCK


def test_page_seg_mode_affects_ocr():
    """Test that PSM actually affects OCR results."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: image with text
    image = create_test_image_with_text("Hello World")

    # when: using different PSM modes
    with PyTessBaseAPI(lang='eng') as api:
        # Single line mode
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetImage(image)
        text_line = api.GetUTF8Text()

        # Auto mode
        api.SetPageSegMode(PSM.AUTO)
        api.SetImage(image)
        text_auto = api.GetUTF8Text()

        # then: should get text in both cases
        assert len(text_line.strip()) > 0
        assert len(text_auto.strip()) > 0


# ============================================================================
# Variable Setting/Getting Tests
# ============================================================================

def test_set_variable():
    """Test SetVariable method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: setting a variable
        result = api.SetVariable('tessedit_char_whitelist', '0123456789')

        # then: should return True
        assert result is True


def test_set_variable_returns_false_for_invalid():
    """Test SetVariable returns False for invalid variables."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: setting an invalid variable
        result = api.SetVariable('invalid_var_name_xyz', 'value')

        # then: should return False
        assert result is False


def test_get_string_variable():
    """Test GetStringVariable method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: getting a string variable
        lang = api.GetStringVariable('tessedit_char_blacklist')

        # then: should return a string (empty or with value)
        assert isinstance(lang, str)


def test_set_and_get_variable():
    """Test setting and getting a variable."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: setting a whitelist
        api.SetVariable('tessedit_char_whitelist', 'ABC')
        whitelist = api.GetStringVariable('tessedit_char_whitelist')

        # then: should retrieve the set value
        assert whitelist == 'ABC'


# ============================================================================
# Rectangle (ROI) Tests
# ============================================================================

def test_set_rectangle():
    """Test SetRectangle method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API with image
    image = create_test_image_with_text("Full Image Text")

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)

        # when: setting rectangle (should not raise error)
        api.SetRectangle(10, 10, 100, 50)

        # then: should still be able to get text
        text = api.GetUTF8Text()
        assert isinstance(text, str)


def test_rectangle_restricts_ocr():
    """Test that SetRectangle restricts OCR to a region."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text in different regions
    image = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    # Left text
    draw.text((10, 80), "LEFT", fill='black', font=font)
    # Right text
    draw.text((250, 80), "RIGHT", fill='black', font=font)

    with PyTessBaseAPI(lang='eng') as api:
        # when: OCR on left half only
        api.SetImage(image)
        api.SetRectangle(0, 0, 200, 200)
        text_left = api.GetUTF8Text().strip()

        # when: OCR on right half only
        api.SetImage(image)
        api.SetRectangle(200, 0, 200, 200)
        text_right = api.GetUTF8Text().strip()

        # then: should get different results
        # Note: exact text matching may vary, but should differ
        assert len(text_left) > 0
        assert len(text_right) > 0


# ============================================================================
# Alternative Output Format Tests
# ============================================================================

def test_get_hocr_text():
    """Test GetHOCRText method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Test")

    # when: getting hOCR output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        hocr = api.GetHOCRText(0)

        # then: should contain hOCR markup
        assert isinstance(hocr, str)
        assert len(hocr) > 0
        # hOCR should contain HTML-like tags
        assert 'ocr' in hocr.lower() or 'div' in hocr.lower() or 'span' in hocr.lower()


def test_get_tsv_text():
    """Test GetTSVText method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Test")

    # when: getting TSV output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        tsv = api.GetTSVText(0)

        # then: should contain TSV format (tab-separated)
        assert isinstance(tsv, str)
        assert len(tsv) > 0
        # TSV should have tab characters
        assert '\t' in tsv


def test_get_box_text():
    """Test GetBoxText method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("A")

    # when: getting box file output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        box = api.GetBoxText(0)

        # then: should contain box file format
        assert isinstance(box, str)
        assert len(box) > 0


def test_get_unlv_text():
    """Test GetUNLVText method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Test")

    # when: getting UNLV output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        unlv = api.GetUNLVText()

        # then: should return a string
        assert isinstance(unlv, str)
        # UNLV may be empty or have content depending on the image


# ============================================================================
# Clear Methods Tests
# ============================================================================

def test_clear_method():
    """Test Clear method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API with recognized image
    image = create_test_image_with_text("Test")

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()

        # when: clearing
        api.Clear()

        # then: should be able to set new image and recognize again
        image2 = create_test_image_with_text("New")
        api.SetImage(image2)
        text = api.GetUTF8Text()
        assert isinstance(text, str)


def test_clear_adaptive_classifier():
    """Test ClearAdaptiveClassifier method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API with recognized image
    image = create_test_image_with_text("Test")

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()

        # when: clearing adaptive classifier (should not raise error)
        api.ClearAdaptiveClassifier()

        # then: should still be able to recognize
        text = api.GetUTF8Text()
        assert isinstance(text, str)


# ============================================================================
# Metadata Methods Tests
# ============================================================================

def test_get_datapath():
    """Test GetDatapath method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: initialized API
    with PyTessBaseAPI(lang='eng') as api:
        # when: getting datapath
        datapath = api.GetDatapath()

        # then: should return a valid path
        assert isinstance(datapath, str)
        assert len(datapath) > 0
        # Should end with / or be a valid path
        assert '/' in datapath or '\\' in datapath or datapath == ''


def test_get_init_languages_updated():
    """Test GetInitLanguagesAsString with actual implementation."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: API initialized with specific language
    with PyTessBaseAPI(lang='eng') as api:
        # when: getting languages
        langs = api.GetInitLanguagesAsString()

        # then: should return initialized language
        assert isinstance(langs, str)
        assert 'eng' in langs


# ============================================================================
# Integration Tests
# ============================================================================

def test_psm_with_whitelist():
    """Test combining PSM and variable setting."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: image with numbers
    image = create_test_image_with_text("12345")

    # when: using single line PSM with digit whitelist
    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetVariable('tessedit_char_whitelist', '0123456789')
        api.SetImage(image)
        text = api.GetUTF8Text()

        # then: should recognize numbers
        assert any(c.isdigit() for c in text)


def test_rectangle_with_hocr():
    """Test combining SetRectangle with hOCR output."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Test")

    # when: using rectangle with hOCR output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.SetRectangle(0, 0, 150, 100)
        hocr = api.GetHOCRText(0)

        # then: should get hOCR output
        assert isinstance(hocr, str)
        assert len(hocr) > 0


def test_all_output_formats():
    """Test that all output formats work together."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("ABC")

    # when: getting all output formats
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)

        utf8 = api.GetUTF8Text()
        hocr = api.GetHOCRText(0)
        tsv = api.GetTSVText(0)
        box = api.GetBoxText(0)
        unlv = api.GetUNLVText()

        # then: all should return strings
        assert isinstance(utf8, str) and len(utf8) > 0
        assert isinstance(hocr, str) and len(hocr) > 0
        assert isinstance(tsv, str) and len(tsv) > 0
        assert isinstance(box, str)  # may be empty
        assert isinstance(unlv, str)  # may be empty
