# Usage Guide

## Installation

### Prerequisites

Before installing mlt-nb, ensure you have:

1. **MLT Framework** (7.x or later)
   - macOS: `brew install mlt`
   - Ubuntu/Debian: `sudo apt-get install libmlt-dev libmlt++-dev`
   - Fedora: `sudo dnf install mlt-devel`

2. **Python** 3.10 or later

3. **CMake** 3.16 or later

### Install from Source

```bash
git clone <repository-url>
cd mlt_nanobind_benchmark
pip install -e ".[dev,test,benchmark]"
```

### Custom MLT Path

If MLT is installed in a non-standard location:

```bash
export MLT_INCLUDE_DIR=/path/to/mlt/include
export MLT_LIBRARY_DIR=/path/to/mlt/lib
pip install -e .
```

## Basic Usage

### Initialize MLT

```python
import mlt_nb

# Initialize the MLT factory
factory = mlt_nb.Factory()
factory.init()
```

### Create a Profile

```python
# Use default profile
profile = mlt_nb.Profile()

# Or specify a profile name
profile = mlt_nb.Profile("atsc_1080p_25")

# Access profile properties
print(f"Resolution: {profile.width()}x{profile.height()}")
print(f"Frame rate: {profile.fps()} fps")
```

### Create a Producer

```python
# Create a color producer
producer = mlt_nb.Producer(profile, "color:red")

# Create a producer from a file
producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

# Check if producer is valid
if producer.is_valid():
    print("Producer created successfully")
```

### Get Frames as NumPy Arrays (Zero-Copy)

```python
import numpy as np

# Get a frame
frame = producer.get_frame()

# Get image as NumPy array (zero-copy!)
image = frame.get_image()

# Now you can use NumPy operations
print(f"Image shape: {image.shape}")  # (height, width, channels)
print(f"Image dtype: {image.dtype}")  # uint8

# Example: Get average color
avg_color = image.mean(axis=(0, 1))
print(f"Average color: {avg_color}")
```

### Work with Playlists

```python
# Create a playlist
playlist = mlt_nb.Playlist(profile)

# Create some producers
red_producer = mlt_nb.Producer(profile, "color:red")
blue_producer = mlt_nb.Producer(profile, "color:blue")

# Append to playlist
playlist.append(red_producer)
playlist.append(blue_producer)

# Check playlist count
print(f"Playlist has {playlist.count()} clips")
```

### Use Consumers

```python
# Create a consumer
consumer = mlt_nb.Consumer(profile, "sdl2")

# Connect producer to consumer
consumer.connect(producer)

# Start playback
consumer.start()

# Wait for playback to finish
import time
while not consumer.is_stopped():
    time.sleep(0.1)
```

### Apply Filters

```python
# Create a filter
brightness_filter = mlt_nb.Filter(profile, "brightness")

# Set filter properties
brightness_filter.set("level", "1.5")
```

### Properties

All MLT objects support properties:

```python
# Set a property
producer.set("aspect_ratio", "1.777")

# Get a property
aspect_ratio = producer.get("aspect_ratio")
print(f"Aspect ratio: {aspect_ratio}")
```

## Advanced Usage

### Working with Multitrack

```python
multitrack = mlt_nb.Multitrack()

# Create tracks
video_track = mlt_nb.Producer(profile, "color:blue")
audio_track = mlt_nb.Producer(profile, "tone:")

# Connect tracks
multitrack.connect(video_track, 0)
multitrack.connect(audio_track, 1)
```

### Using Transitions

```python
transition = mlt_nb.Transition(profile, "mix")
transition.set("start", "0.0")
transition.set("end", "1.0")
```

### Image Processing with NumPy

```python
# Get frame image
frame = producer.get_frame()
image = frame.get_image()

# Apply NumPy operations (zero-copy means this is fast!)
# Example: Convert to grayscale
gray = image.mean(axis=2).astype(np.uint8)

# Example: Brighten image
brightened = np.clip(image * 1.5, 0, 255).astype(np.uint8)

# Example: Get histogram
histogram = np.histogram(image.flatten(), bins=256, range=(0, 256))
```

## Performance Tips

1. **Zero-Copy Image Access**: The `get_image()` method returns a NumPy array that directly references MLT's internal buffer, avoiding copies.

2. **Reuse Objects**: Create Profile and Factory objects once and reuse them.

3. **Batch Operations**: Use NumPy vectorized operations on images instead of loops.

4. **Profile Selection**: Choose the appropriate profile for your content to avoid unnecessary scaling.

## Comparison with SWIG Binding

### mlt-python (SWIG)
```python
import mlt7 as mlt

factory = mlt.Factory()
factory.init()
profile = mlt.Profile()
producer = mlt.Producer(profile, "color:red")
frame = producer.get_frame()

# SWIG returns binary data
image_data = mlt.frame_get_image(frame, mlt.mlt_image_rgba,
                                  profile.width(), profile.height())
# Must convert to NumPy manually
image = np.frombuffer(image_data, dtype=np.uint8).reshape(
    (profile.height(), profile.width(), 4)
)
```

### mlt-nb (nanobind)
```python
import mlt_nb

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()
producer = mlt_nb.Producer(profile, "color:red")
frame = producer.get_frame()

# Direct NumPy array (zero-copy!)
image = frame.get_image()
```

**Key Differences:**
- mlt-nb returns NumPy arrays directly
- mlt-nb uses zero-copy when possible
- mlt-nb has a cleaner, more Pythonic API
- mlt-nb provides comparable or better performance (0.93x-1.08x SWIG in benchmarks)

## Troubleshooting

### Import Error: _mlt_nb_core not found

Make sure MLT is installed and accessible:
```bash
export LD_LIBRARY_PATH=/path/to/mlt/lib:$LD_LIBRARY_PATH
```

### Build Fails: MLT headers not found

Specify MLT paths:
```bash
export MLT_INCLUDE_DIR=/path/to/mlt/include
export MLT_LIBRARY_DIR=/path/to/mlt/lib
```

### Runtime Error: Failed to get image data

Ensure the producer is valid before getting frames:
```python
if not producer.is_valid():
    print("Producer is invalid!")
```

## Examples

See the `examples/` directory (if available) for complete working examples.
