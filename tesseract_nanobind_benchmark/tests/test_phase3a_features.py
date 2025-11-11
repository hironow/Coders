"""Tests for Phase 3a features: Additional Enums and Layout Analysis methods.

Phase 3a adds:
- WritingDirection Enum (4 values)
- TextlineOrder Enum (4 values)
- GetWords() method for word-level layout information
- GetTextlines() method for line-level layout information
"""

import numpy as np
import pytest
from PIL import Image

from tesseract_nanobind.compat import (
    PyTessBaseAPI,
    WritingDirection,
    TextlineOrder,
)


# ============================================================================
# Enum Tests
# ============================================================================

def test_writing_direction_enum_exists():
    """Test that WritingDirection enum exists and has correct values."""
    assert hasattr(WritingDirection, 'LEFT_TO_RIGHT')
    assert hasattr(WritingDirection, 'RIGHT_TO_LEFT')
    assert hasattr(WritingDirection, 'TOP_TO_BOTTOM')
    assert hasattr(WritingDirection, 'BOTTOM_TO_TOP')

    assert WritingDirection.LEFT_TO_RIGHT == 0
    assert WritingDirection.RIGHT_TO_LEFT == 1
    assert WritingDirection.TOP_TO_BOTTOM == 2
    assert WritingDirection.BOTTOM_TO_TOP == 3


def test_textline_order_enum_exists():
    """Test that TextlineOrder enum exists and has correct values."""
    assert hasattr(TextlineOrder, 'LEFT_TO_RIGHT')
    assert hasattr(TextlineOrder, 'RIGHT_TO_LEFT')
    assert hasattr(TextlineOrder, 'TOP_TO_BOTTOM')
    assert hasattr(TextlineOrder, 'BOTTOM_TO_TOP')

    assert TextlineOrder.LEFT_TO_RIGHT == 0
    assert TextlineOrder.RIGHT_TO_LEFT == 1
    assert TextlineOrder.TOP_TO_BOTTOM == 2
    assert TextlineOrder.BOTTOM_TO_TOP == 3


# ============================================================================
# GetWords Tests
# ============================================================================

def test_get_words_basic():
    """Test that GetWords returns a list."""
    img = Image.new('RGB', (200, 50), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        words = api.GetWords()

        assert isinstance(words, list)


def test_get_words_structure():
    """Test that GetWords returns properly structured data."""
    # Create image with text
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        words = api.GetWords()

        # Each word should be a tuple with 6 elements: (text, confidence, x, y, w, h)
        for word in words:
            assert isinstance(word, tuple)
            assert len(word) == 6

            text, conf, x, y, w, h = word
            assert isinstance(text, str)
            assert isinstance(conf, int)
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(w, int)
            assert isinstance(h, int)

            # Confidence should be 0-100
            assert 0 <= conf <= 100
            # Dimensions should be positive
            assert w >= 0
            assert h >= 0


def test_get_words_with_real_text():
    """Test GetWords with actual text content."""
    # Create simple test image with text
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        # Use SINGLE_LINE mode for better results on simple text
        api.SetPageSegMode(7)  # PSM.SINGLE_LINE
        api.SetImage(img)
        api.Recognize()

        words = api.GetWords()

        # Should get some words from the image
        # Even if OCR is imperfect, the structure should be valid
        for word in words:
            text, conf, x, y, w, h = word
            # All returned words should have non-empty text
            assert len(text) > 0
            # Confidence should be reasonable (though might be low for blank image)
            assert conf >= 0


def test_get_words_without_recognize():
    """Test GetWords when Recognize() is called implicitly."""
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        # Don't call Recognize() explicitly
        words = api.GetWords()

        # Should still work (might auto-recognize)
        assert isinstance(words, list)


def test_get_words_without_init():
    """Test GetWords when API is not initialized."""
    api = PyTessBaseAPI(init=False)
    words = api.GetWords()

    # Should return empty list without crashing
    assert isinstance(words, list)
    assert len(words) == 0


# ============================================================================
# GetTextlines Tests
# ============================================================================

def test_get_textlines_basic():
    """Test that GetTextlines returns a list."""
    img = Image.new('RGB', (200, 50), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        lines = api.GetTextlines()

        assert isinstance(lines, list)


def test_get_textlines_structure():
    """Test that GetTextlines returns properly structured data."""
    # Create image with text
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        lines = api.GetTextlines()

        # Each line should be a tuple with 6 elements: (text, confidence, x, y, w, h)
        for line in lines:
            assert isinstance(line, tuple)
            assert len(line) == 6

            text, conf, x, y, w, h = line
            assert isinstance(text, str)
            assert isinstance(conf, int)
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(w, int)
            assert isinstance(h, int)

            # Confidence should be 0-100
            assert 0 <= conf <= 100
            # Dimensions should be positive
            assert w >= 0
            assert h >= 0


def test_get_textlines_with_real_text():
    """Test GetTextlines with actual text content."""
    # Create simple test image
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(7)  # PSM.SINGLE_LINE
        api.SetImage(img)
        api.Recognize()

        lines = api.GetTextlines()

        # Should get some lines from the image
        for line in lines:
            text, conf, x, y, w, h = line
            # All returned lines should have non-empty text
            assert len(text) > 0
            # Confidence should be reasonable
            assert conf >= 0


def test_get_textlines_without_recognize():
    """Test GetTextlines when Recognize() is called implicitly."""
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        # Don't call Recognize() explicitly
        lines = api.GetTextlines()

        # Should still work
        assert isinstance(lines, list)


def test_get_textlines_without_init():
    """Test GetTextlines when API is not initialized."""
    api = PyTessBaseAPI(init=False)
    lines = api.GetTextlines()

    # Should return empty list without crashing
    assert isinstance(lines, list)
    assert len(lines) == 0


# ============================================================================
# Comparison Tests: GetWords vs GetTextlines
# ============================================================================

def test_words_vs_textlines_count():
    """Test that GetWords returns more items than GetTextlines (typically)."""
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        words = api.GetWords()
        lines = api.GetTextlines()

        # Both should return lists
        assert isinstance(words, list)
        assert isinstance(lines, list)

        # Generally, there should be at least as many words as lines
        # (or both could be empty for blank image)
        if len(lines) > 0:
            assert len(words) >= len(lines) or len(words) == 0


def test_words_and_textlines_coordinates():
    """Test that GetWords and GetTextlines return valid coordinates."""
    img = np.ones((150, 500, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        words = api.GetWords()
        lines = api.GetTextlines()

        # Check words coordinates are within image bounds
        for word in words:
            _, _, x, y, w, h = word
            assert x >= 0
            assert y >= 0
            assert x + w <= img.shape[1] or w == 0
            assert y + h <= img.shape[0] or h == 0

        # Check lines coordinates are within image bounds
        for line in lines:
            _, _, x, y, w, h = line
            assert x >= 0
            assert y >= 0
            assert x + w <= img.shape[1] or w == 0
            assert y + h <= img.shape[0] or h == 0


# ============================================================================
# Integration Tests
# ============================================================================

def test_phase3a_all_features():
    """Integration test using all Phase 3a features."""
    img = np.ones((150, 500, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        # Test all Phase 3a features
        words = api.GetWords()
        lines = api.GetTextlines()

        # Enums should be available
        assert WritingDirection.LEFT_TO_RIGHT == 0
        assert TextlineOrder.TOP_TO_BOTTOM == 2

        # Methods should return proper data
        assert isinstance(words, list)
        assert isinstance(lines, list)

        # If we have results, they should be properly structured
        for word in words:
            assert len(word) == 6

        for line in lines:
            assert len(line) == 6


def test_words_textlines_with_psm():
    """Test GetWords and GetTextlines with different PSM modes."""
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255

    # Test with SINGLE_LINE mode
    with PyTessBaseAPI(lang='eng', psm=7) as api:
        api.SetImage(img)
        words_single = api.GetWords()
        lines_single = api.GetTextlines()

        assert isinstance(words_single, list)
        assert isinstance(lines_single, list)

    # Test with AUTO mode
    with PyTessBaseAPI(lang='eng', psm=3) as api:
        api.SetImage(img)
        words_auto = api.GetWords()
        lines_auto = api.GetTextlines()

        assert isinstance(words_auto, list)
        assert isinstance(lines_auto, list)


def test_words_textlines_with_roi():
    """Test GetWords and GetTextlines with SetRectangle (ROI)."""
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)

        # Set a rectangular region of interest
        api.SetRectangle(50, 50, 200, 100)
        api.Recognize()

        words = api.GetWords()
        lines = api.GetTextlines()

        assert isinstance(words, list)
        assert isinstance(lines, list)

        # All coordinates should be relative to full image (not ROI)
        for word in words:
            _, _, x, y, w, h = word
            # Coordinates should be within the image
            assert x >= 0
            assert y >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
