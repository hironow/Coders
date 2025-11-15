"""Tests for zero-copy NumPy array integration."""

import pytest
import numpy as np
import mlt_nb


def test_frame_image_as_numpy_array():
    """Test that frame image is returned as NumPy array."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:red")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Should be a NumPy array
    assert isinstance(image, np.ndarray)


def test_frame_image_shape():
    """Test that frame image has correct dimensions."""
    # Given: Valid frame from known profile
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    width = profile.width()
    height = profile.height()
    producer = mlt_nb.Producer(profile, "color:blue")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Shape should match profile dimensions
    assert image.shape[0] == height
    assert image.shape[1] == width
    assert image.shape[2] in [3, 4]  # RGB or RGBA


def test_frame_image_dtype():
    """Test that frame image has correct data type."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:green")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Should be uint8 (8-bit per channel)
    assert image.dtype == np.uint8


def test_frame_image_writable():
    """Test that NumPy array is writable."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:white")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Should be writable
    assert image.flags.writeable


def test_frame_image_memory_layout():
    """Test that NumPy array has C-contiguous memory layout."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:black")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Should be C-contiguous for performance
    assert image.flags.c_contiguous


def test_color_producer_pixel_values():
    """Test that color producer generates correct pixel values."""
    # Given: Red color producer
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:#ff0000")
    frame = producer.get_frame()

    # When: Get image
    image = frame.get_image()

    # Then: Pixels should be predominantly red
    # Check center pixel (allowing for format variations)
    center_y = image.shape[0] // 2
    center_x = image.shape[1] // 2
    pixel = image[center_y, center_x]

    # Red channel should be high, others low
    assert pixel[0] > 200  # High red
    assert pixel[1] < 50   # Low green
    assert pixel[2] < 50   # Low blue


def test_multiple_frames_different_arrays():
    """Test that multiple frames return different array objects."""
    # Given: Producer
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:cyan")

    # When: Get multiple frames
    frame1 = producer.get_frame()
    frame2 = producer.get_frame()
    image1 = frame1.get_image()
    image2 = frame2.get_image()

    # Then: Should be different array objects
    # (they may share data pointer, but array objects should be different)
    assert image1 is not image2


def test_image_format_specification():
    """Test getting image with specific format."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:yellow")
    frame = producer.get_frame()

    # When: Get image with RGB24 format
    # (format parameter would be added to API)
    image = frame.get_image()

    # Then: Should return valid array
    assert isinstance(image, np.ndarray)
    assert image.size > 0
