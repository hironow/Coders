"""Validation tests to ensure mlt-nb outputs match mlt-python (SWIG) outputs."""

import pytest

try:
    import numpy as np
    import mlt_nb
    HAS_MLT_NB = True
except ImportError:
    HAS_MLT_NB = False

try:
    import mlt7 as mlt_swig
    HAS_MLT_SWIG = True
except ImportError:
    HAS_MLT_SWIG = False

pytestmark = pytest.mark.skipif(
    not (HAS_MLT_NB and HAS_MLT_SWIG),
    reason="Both mlt-nb and mlt-python required for validation"
)


def test_profile_properties_match():
    """Test that Profile properties match between implementations."""
    # Given: Profiles from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()

    # Then: Properties should match
    assert nb_profile.width() == swig_profile.width()
    assert nb_profile.height() == swig_profile.height()
    assert abs(nb_profile.fps() - swig_profile.fps()) < 0.01


def test_producer_validity_matches():
    """Test that producer validity matches between implementations."""
    # Given: Color producers from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_producer = mlt_nb.Producer(nb_profile, "color:red")

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_producer = mlt_swig.Producer(swig_profile, "color:red")

    # Then: Both should be valid
    assert nb_producer.is_valid() == swig_producer.is_valid()
    assert nb_producer.is_valid() is True


def test_frame_dimensions_match():
    """Test that frame dimensions match between implementations."""
    # Given: Frames from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_producer = mlt_nb.Producer(nb_profile, "color:blue")
    nb_frame = nb_producer.get_frame()

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_producer = mlt_swig.Producer(swig_profile, "color:blue")
    swig_frame = swig_producer.get_frame()

    # Then: Frame dimensions should match
    nb_width = nb_frame.get_int("width")
    nb_height = nb_frame.get_int("height")
    swig_width = swig_frame.get_int("width")
    swig_height = swig_frame.get_int("height")

    assert nb_width == swig_width
    assert nb_height == swig_height


def test_image_data_shape_matches():
    """Test that image data shape matches between implementations."""
    # Given: Images from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_producer = mlt_nb.Producer(nb_profile, "color:green")
    nb_frame = nb_producer.get_frame()
    nb_image = nb_frame.get_image()

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_producer = mlt_swig.Producer(swig_profile, "color:green")
    swig_frame = swig_producer.get_frame()

    # SWIG returns binary data, convert to NumPy for comparison
    swig_image_data = mlt_swig.frame_get_image(
        swig_frame,
        mlt_swig.mlt_image_rgba,
        swig_profile.width(),
        swig_profile.height()
    )
    swig_image = np.frombuffer(swig_image_data, dtype=np.uint8).reshape(
        (swig_profile.height(), swig_profile.width(), 4)
    )

    # Then: Shapes should match
    assert nb_image.shape == swig_image.shape


def test_color_producer_pixel_values_match():
    """Test that color producer generates matching pixel values."""
    # Given: Red color producers from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_producer = mlt_nb.Producer(nb_profile, "color:#ff0000")
    nb_frame = nb_producer.get_frame()
    nb_image = nb_frame.get_image()

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_producer = mlt_swig.Producer(swig_profile, "color:#ff0000")
    swig_frame = swig_producer.get_frame()
    swig_image_data = mlt_swig.frame_get_image(
        swig_frame,
        mlt_swig.mlt_image_rgba,
        swig_profile.width(),
        swig_profile.height()
    )
    swig_image = np.frombuffer(swig_image_data, dtype=np.uint8).reshape(
        (swig_profile.height(), swig_profile.width(), 4)
    )

    # Then: Center pixels should match (within tolerance for encoding differences)
    center_y = nb_image.shape[0] // 2
    center_x = nb_image.shape[1] // 2

    nb_pixel = nb_image[center_y, center_x]
    swig_pixel = swig_image[center_y, center_x]

    # Allow small differences due to format conversions
    assert np.allclose(nb_pixel, swig_pixel, atol=5)


def test_playlist_count_matches():
    """Test that playlist operations produce matching results."""
    # Given: Playlists from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_playlist = mlt_nb.Playlist(nb_profile)
    nb_producer1 = mlt_nb.Producer(nb_profile, "color:red")
    nb_producer2 = mlt_nb.Producer(nb_profile, "color:blue")
    nb_playlist.append(nb_producer1)
    nb_playlist.append(nb_producer2)

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_playlist = mlt_swig.Playlist(swig_profile)
    swig_producer1 = mlt_swig.Producer(swig_profile, "color:red")
    swig_producer2 = mlt_swig.Producer(swig_profile, "color:blue")
    swig_playlist.append(swig_producer1)
    swig_playlist.append(swig_producer2)

    # Then: Playlist counts should match
    assert nb_playlist.count() == swig_playlist.count()
    assert nb_playlist.count() == 2


def test_consumer_validity_matches():
    """Test that consumer creation matches between implementations."""
    # Given: Null consumers from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_consumer = mlt_nb.Consumer(nb_profile, "null")

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_consumer = mlt_swig.Consumer(swig_profile, "null")

    # Then: Both should be valid
    assert nb_consumer.is_valid() == swig_consumer.is_valid()


def test_properties_set_get_matches():
    """Test that properties set/get work the same way."""
    # Given: Properties set on profiles from both implementations
    mlt_nb_factory = mlt_nb.Factory()
    mlt_nb_factory.init()
    nb_profile = mlt_nb.Profile()
    nb_profile.set("test_prop", "test_value")

    mlt_swig_factory = mlt_swig.Factory()
    mlt_swig_factory.init()
    swig_profile = mlt_swig.Profile()
    swig_profile.set("test_prop", "test_value")

    # Then: Retrieved values should match
    assert nb_profile.get("test_prop") == swig_profile.get("test_prop")
    assert nb_profile.get("test_prop") == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
