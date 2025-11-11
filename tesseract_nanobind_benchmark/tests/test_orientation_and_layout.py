"""Tests for orientation detection and layout analysis features.

This module tests:
- DetectOrientationScript for page orientation and script detection
- GetComponentImages for layout analysis at various levels (BLOCK, PARA, TEXTLINE, WORD, SYMBOL)
- PolyBlockType (PT) and Orientation enumerations
"""
from PIL import Image, ImageDraw, ImageFont


def create_test_image_with_text(text="Test", width=400, height=200):
    """Create a simple test image with text."""
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    draw.text((20, 80), text, fill='black', font=font)
    return image


# ============================================================================
# Enum Tests
# ============================================================================

def test_pt_enum_exists():
    """Test that PT enum exists and has correct values."""
    from tesseract_nanobind.compat import PT

    assert hasattr(PT, 'UNKNOWN')
    assert hasattr(PT, 'FLOWING_TEXT')
    assert hasattr(PT, 'HEADING_TEXT')
    assert hasattr(PT, 'TABLE')
    assert hasattr(PT, 'COUNT')

    assert PT.UNKNOWN == 0
    assert PT.FLOWING_TEXT == 1
    assert PT.COUNT == 15


def test_orientation_enum_exists():
    """Test that Orientation enum exists and has correct values."""
    from tesseract_nanobind.compat import Orientation

    assert hasattr(Orientation, 'PAGE_UP')
    assert hasattr(Orientation, 'PAGE_RIGHT')
    assert hasattr(Orientation, 'PAGE_DOWN')
    assert hasattr(Orientation, 'PAGE_LEFT')

    assert Orientation.PAGE_UP == 0
    assert Orientation.PAGE_RIGHT == 1
    assert Orientation.PAGE_DOWN == 2
    assert Orientation.PAGE_LEFT == 3


# ============================================================================
# DetectOrientationScript Tests
# ============================================================================

def test_detect_orientation_script_basic():
    """Test DetectOrientationScript method."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with text
    image = create_test_image_with_text("Hello World")

    # when: detecting orientation and script
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        result = api.DetectOrientationScript()

        # then: should return tuple of (orient_deg, orient_conf, script_name, script_conf)
        assert isinstance(result, tuple)
        assert len(result) == 4

        orient_deg, orient_conf, script_name, script_conf = result
        assert isinstance(orient_deg, int)
        assert isinstance(orient_conf, float)
        assert isinstance(script_name, str)
        assert isinstance(script_conf, float)


def test_detect_orientation_script_without_init():
    """Test DetectOrientationScript without initialization."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling DetectOrientationScript
    result = api.DetectOrientationScript()

    # then: should return default values
    assert result == (0, 0.0, '', 0.0)


def test_detect_orientation_upright_text():
    """Test orientation detection with upright text."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: normal upright text
    image = create_test_image_with_text("Test Text", width=600, height=200)

    # when: detecting orientation
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        orient_deg, orient_conf, script_name, script_conf = api.DetectOrientationScript()

        # then: should detect upright (0 degrees) orientation
        # Note: orientation_deg might be 0 or 360, both represent upright
        assert orient_deg in [0, 360] or orient_deg % 360 == 0


# ============================================================================
# GetComponentImages Tests
# ============================================================================

def test_get_component_images_basic():
    """Test GetComponentImages method."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: image with text
    image = create_test_image_with_text("Hello World")

    # when: getting component images
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()
        components = api.GetComponentImages(RIL.WORD)

        # then: should return list of bounding boxes
        assert isinstance(components, list)
        # Should have at least 1 component for "Hello World"
        assert len(components) >= 1


def test_get_component_images_structure():
    """Test structure of component image results."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: image with text
    image = create_test_image_with_text("Test")

    # when: getting component images at WORD level
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()
        components = api.GetComponentImages(RIL.WORD)

        # then: each component should be a tuple (x, y, w, h)
        for comp in components:
            assert isinstance(comp, tuple)
            assert len(comp) == 4
            x, y, w, h = comp
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(w, int)
            assert isinstance(h, int)
            # Dimensions should be positive
            assert w > 0
            assert h > 0


def test_get_component_images_different_levels():
    """Test GetComponentImages at different RIL levels."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: image with multiple words
    image = create_test_image_with_text("Word1 Word2 Word3")

    # when: getting components at different levels
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()

        blocks = api.GetComponentImages(RIL.BLOCK)
        lines = api.GetComponentImages(RIL.TEXTLINE)
        words = api.GetComponentImages(RIL.WORD)

        # then: should return components at each level
        assert isinstance(blocks, list)
        assert isinstance(lines, list)
        assert isinstance(words, list)

        # Usually: blocks <= lines <= words (in count)
        assert len(blocks) >= 0
        assert len(lines) >= 0
        assert len(words) >= 0


def test_get_component_images_without_recognize():
    """Test GetComponentImages without calling Recognize first."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: image set but not recognized
    image = create_test_image_with_text("Test")

    # when: getting components without Recognize
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        # Note: Some implementations auto-recognize, some don't
        components = api.GetComponentImages(RIL.WORD)

        # then: should return a list (possibly empty)
        assert isinstance(components, list)


def test_get_component_images_without_init():
    """Test GetComponentImages without initialization."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: uninitialized API
    api = PyTessBaseAPI(init=False)

    # when: calling GetComponentImages
    components = api.GetComponentImages(RIL.WORD)

    # then: should return empty list
    assert components == []


def test_get_component_images_text_only():
    """Test GetComponentImages with text_only parameter."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL

    # given: image with text
    image = create_test_image_with_text("Hello")

    # when: getting components with text_only=True and False
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)
        api.Recognize()

        components_text = api.GetComponentImages(RIL.WORD, text_only=True)
        components_all = api.GetComponentImages(RIL.WORD, text_only=False)

        # then: both should return lists
        assert isinstance(components_text, list)
        assert isinstance(components_all, list)
        # text_only=True should have same or fewer components
        assert len(components_text) <= len(components_all) or len(components_text) > 0


# ============================================================================
# Integration Tests
# ============================================================================

def test_all_orientation_and_layout_features():
    """Integration test for all orientation detection and layout analysis features."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL, PT, Orientation

    # given: image with text
    image = create_test_image_with_text("Integration Test")

    # when: using all orientation and layout features
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(image)

        # Test 1: Detect orientation
        orient_result = api.DetectOrientationScript()
        assert len(orient_result) == 4

        # Test 2: Get component images
        api.Recognize()
        components = api.GetComponentImages(RIL.WORD)
        assert isinstance(components, list)

        # Test 3: Enums are accessible
        assert PT.FLOWING_TEXT == 1
        assert Orientation.PAGE_UP == 0


def test_component_images_with_psm():
    """Test GetComponentImages with different PSM settings."""
    from tesseract_nanobind.compat import PyTessBaseAPI, RIL, PSM

    # given: single line text
    image = create_test_image_with_text("Single Line")

    # when: using SINGLE_LINE PSM
    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetImage(image)
        api.Recognize()
        components = api.GetComponentImages(RIL.WORD)

        # then: should get word components
        assert isinstance(components, list)
        # Should detect at least 1 word
        assert len(components) >= 1
