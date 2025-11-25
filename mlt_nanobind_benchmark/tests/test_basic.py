"""Basic tests for MLT nanobind binding."""

import pytest
import mlt_nb


def test_factory_init():
    """Test MLT factory initialization."""
    # Given: MLT factory
    factory = mlt_nb.Factory()

    # When: Initialize MLT (should not raise exception)
    factory.init()

    # Then: Should complete successfully
    assert True


def test_profile_creation():
    """Test profile creation."""
    # Given: Initialized MLT
    factory = mlt_nb.Factory()
    factory.init()

    # When: Create a profile
    profile = mlt_nb.Profile()

    # Then: Profile should be valid
    assert profile is not None
    assert profile.width() > 0
    assert profile.height() > 0
    assert profile.fps() > 0


def test_producer_creation_with_color():
    """Test producer creation with color generator."""
    # Given: Profile
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()

    # When: Create a color producer
    producer = mlt_nb.Producer(profile, "color:red")

    # Then: Producer should be valid
    assert producer is not None
    assert producer.is_valid()


def test_producer_get_frame():
    """Test getting a frame from producer."""
    # Given: Valid producer
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:blue")

    # When: Get a frame
    frame = producer.get_frame()

    # Then: Frame should be valid
    assert frame is not None


def test_frame_get_image():
    """Test getting image data from frame."""
    # Given: Valid frame
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:green")
    frame = producer.get_frame()

    # When: Get image from frame
    image = frame.get_image()

    # Then: Image should be a NumPy array with correct shape
    assert image is not None
    assert hasattr(image, 'shape')
    assert len(image.shape) == 3
    assert image.shape[2] in [3, 4]  # RGB or RGBA


def test_properties_get_set():
    """Test properties get and set."""
    # Given: Producer with properties
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color", "blue")

    # When: Set a property
    producer.set("test_key", "test_value")

    # Then: Should be able to get the property
    assert producer.get("test_key") == "test_value"


def test_playlist_creation():
    """Test playlist creation."""
    # Given: Profile
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()

    # When: Create a playlist
    playlist = mlt_nb.Playlist(profile)

    # Then: Playlist should be valid
    assert playlist is not None
    assert playlist.count() == 0


def test_playlist_append():
    """Test appending to playlist."""
    # Given: Playlist and producer
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    playlist = mlt_nb.Playlist(profile)
    producer = mlt_nb.Producer(profile, "color:yellow")

    # When: Append producer to playlist
    result = playlist.append(producer)

    # Then: Playlist should have one clip
    assert result == 0  # Success
    assert playlist.count() == 1


def test_consumer_creation():
    """Test consumer creation."""
    # Given: Profile
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()

    # When: Create a consumer (using null consumer for testing)
    consumer = mlt_nb.Consumer(profile, "null")

    # Then: Consumer should be valid
    assert consumer is not None
    assert consumer.is_valid()


def test_filter_creation():
    """Test filter creation."""
    # Given: Profile
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()

    # When: Create a filter
    filter_obj = mlt_nb.Filter(profile, "brightness")

    # Then: Filter should be valid
    assert filter_obj is not None


def test_producer_consumer_connection():
    """Test connecting producer to consumer."""
    # Given: Producer and consumer
    factory = mlt_nb.Factory()
    factory.init()
    profile = mlt_nb.Profile()
    producer = mlt_nb.Producer(profile, "color:magenta")
    consumer = mlt_nb.Consumer(profile, "null")

    # When: Connect producer to consumer
    result = consumer.connect(producer)

    # Then: Connection should succeed
    assert result == 0  # Success
