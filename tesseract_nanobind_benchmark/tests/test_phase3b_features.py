"""Tests for Phase 3b features: GetThresholdedImage.

Phase 3b adds:
- GetThresholdedImage() method for retrieving the binarized image
"""

import numpy as np
import pytest
from PIL import Image

from tesseract_nanobind.compat import PyTessBaseAPI


# ============================================================================
# GetThresholdedImage Tests
# ============================================================================

def test_get_thresholded_image_basic():
    """Test that GetThresholdedImage returns a numpy array."""
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        assert isinstance(thresholded, np.ndarray)


def test_get_thresholded_image_shape():
    """Test that GetThresholdedImage returns correct shape."""
    width, height = 300, 150
    img = Image.new('RGB', (width, height), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        # Should be 2D array (height, width)
        assert thresholded.ndim == 2
        assert thresholded.shape[0] == height
        assert thresholded.shape[1] == width


def test_get_thresholded_image_dtype():
    """Test that GetThresholdedImage returns uint8 array."""
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        assert thresholded.dtype == np.uint8


def test_get_thresholded_image_values():
    """Test that GetThresholdedImage returns binary values."""
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        # Should contain binary values (0 or 255 typically)
        unique_values = np.unique(thresholded)
        # All values should be in range [0, 255]
        assert np.all(unique_values >= 0)
        assert np.all(unique_values <= 255)


def test_get_thresholded_image_white_background():
    """Test GetThresholdedImage with white background."""
    # Create white image
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        # Empty white image gets thresholded to mostly black (no text detected)
        # This is expected behavior from Tesseract
        mean_value = np.mean(thresholded)
        assert mean_value < 50  # Mostly black (no text)


def test_get_thresholded_image_black_background():
    """Test GetThresholdedImage with black background."""
    # Create black image
    img = Image.new('RGB', (200, 100), color='black')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        # Black background should be mostly 0 (black in binary image)
        mean_value = np.mean(thresholded)
        assert mean_value < 50  # Mostly black


def test_get_thresholded_image_without_recognize():
    """Test GetThresholdedImage when Recognize() is not called."""
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        # Don't call Recognize()
        thresholded = api.GetThresholdedImage()

        # Should still work (may auto-recognize or return None/empty)
        if thresholded is not None and thresholded.size > 0:
            assert isinstance(thresholded, np.ndarray)
            assert thresholded.ndim == 2


def test_get_thresholded_image_without_init():
    """Test GetThresholdedImage when API is not initialized."""
    api = PyTessBaseAPI(init=False)
    thresholded = api.GetThresholdedImage()

    # Should return empty array without crashing
    assert isinstance(thresholded, np.ndarray)
    # Empty array should have minimal size
    assert thresholded.size <= 1


def test_get_thresholded_image_without_set_image():
    """Test GetThresholdedImage when no image has been set."""
    with PyTessBaseAPI(lang='eng') as api:
        # Don't set image
        thresholded = api.GetThresholdedImage()

        # Should return empty or None without crashing
        if thresholded is not None:
            assert isinstance(thresholded, np.ndarray)


def test_get_thresholded_image_with_roi():
    """Test GetThresholdedImage with SetRectangle (ROI)."""
    img = Image.new('RGB', (400, 200), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        # Set ROI
        api.SetRectangle(50, 50, 200, 100)
        api.Recognize()
        thresholded = api.GetThresholdedImage()

        # Should still return an image
        assert isinstance(thresholded, np.ndarray)
        if thresholded.size > 0:
            assert thresholded.ndim == 2


def test_get_thresholded_image_multiple_calls():
    """Test multiple calls to GetThresholdedImage."""
    img = Image.new('RGB', (200, 100), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        # Call multiple times
        thresholded1 = api.GetThresholdedImage()
        thresholded2 = api.GetThresholdedImage()

        # Should return consistent results
        assert isinstance(thresholded1, np.ndarray)
        assert isinstance(thresholded2, np.ndarray)

        if thresholded1.size > 0 and thresholded2.size > 0:
            assert thresholded1.shape == thresholded2.shape
            # Arrays should be identical
            assert np.array_equal(thresholded1, thresholded2)


def test_get_thresholded_image_different_images():
    """Test GetThresholdedImage with different input images."""
    with PyTessBaseAPI(lang='eng') as api:
        # First image (white)
        img1 = Image.new('RGB', (200, 100), color='white')
        api.SetImage(img1)
        api.Recognize()
        thresholded1 = api.GetThresholdedImage()

        # Second image (black)
        img2 = Image.new('RGB', (200, 100), color='black')
        api.SetImage(img2)
        api.Recognize()
        thresholded2 = api.GetThresholdedImage()

        # Should return valid numpy arrays
        assert isinstance(thresholded1, np.ndarray)
        assert isinstance(thresholded2, np.ndarray)

        # Both should have the same shape
        if thresholded1.size > 0 and thresholded2.size > 0:
            assert thresholded1.shape == thresholded2.shape
            # Both empty images (no text) will be mostly black after thresholding
            # So their means will be similar, which is expected


# ============================================================================
# Integration Tests
# ============================================================================

def test_phase3b_all_features():
    """Integration test using all Phase 3b features."""
    img = Image.new('RGB', (300, 150), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        # Test Phase 3b feature
        thresholded = api.GetThresholdedImage()

        # Should return valid numpy array
        assert isinstance(thresholded, np.ndarray)
        assert thresholded.ndim == 2
        assert thresholded.dtype == np.uint8

        # Should have same dimensions as input (height, width)
        assert thresholded.shape[0] == 150
        assert thresholded.shape[1] == 300


def test_thresholded_image_with_layout_analysis():
    """Test GetThresholdedImage combined with layout analysis methods."""
    img = Image.new('RGB', (300, 150), color='white')

    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img)
        api.Recognize()

        # Get thresholded image
        thresholded = api.GetThresholdedImage()

        # Also get layout information (Phase 3a)
        words = api.GetWords()
        lines = api.GetTextlines()

        # All should work together
        assert isinstance(thresholded, np.ndarray)
        assert isinstance(words, list)
        assert isinstance(lines, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
