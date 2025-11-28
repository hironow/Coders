# Examples

## Basic Examples

### Example 1: Create a Color Frame and Extract as NumPy Array

```python
import mlt_nb
import numpy as np

# Initialize MLT
factory = mlt_nb.Factory()
factory.init()

# Create profile
profile = mlt_nb.Profile()

# Create a red color producer
producer = mlt_nb.Producer(profile, "color:#ff0000")

# Get frame and extract image
frame = producer.get_frame()
image = frame.get_image()  # Zero-copy NumPy array!

# Print image information
print(f"Image shape: {image.shape}")
print(f"Image dtype: {image.dtype}")
print(f"Red channel average: {image[:, :, 0].mean():.1f}")
```

### Example 2: Process Video Frames with NumPy

```python
import mlt_nb
import numpy as np

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

# Create producer from video file
producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

if not producer.is_valid():
    print("Failed to load video")
    exit(1)

# Process first 100 frames
for i in range(100):
    frame = producer.get_frame()
    image = frame.get_image()

    # Example: Calculate brightness
    brightness = image.mean()
    print(f"Frame {i}: brightness = {brightness:.2f}")

    # Example: Detect dark frames
    if brightness < 50:
        print(f"  -> Dark frame detected!")
```

### Example 3: Create a Simple Playlist

```python
import mlt_nb

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

# Create playlist
playlist = mlt_nb.Playlist(profile)

# Add multiple color clips
colors = ["red", "green", "blue", "yellow"]
for color in colors:
    producer = mlt_nb.Producer(profile, f"color:{color}")
    # Each clip lasts 50 frames
    producer.set_in_and_out(0, 49)
    playlist.append(producer)

print(f"Created playlist with {playlist.count()} clips")
```

### Example 4: Real-time Playback with SDL2

```python
import mlt_nb
import time

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

# Create producer
producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

# Create SDL2 consumer for display
consumer = mlt_nb.Consumer(profile, "sdl2")

if not consumer.is_valid():
    print("SDL2 consumer not available")
    exit(1)

# Connect and start
consumer.connect(producer)
consumer.start()

# Wait for playback to finish
while not consumer.is_stopped():
    time.sleep(0.1)

print("Playback finished")
```

### Example 5: Apply Brightness Filter

```python
import mlt_nb

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

# Create producer
producer = mlt_nb.Producer(profile, "color:gray")

# Create and configure brightness filter
brightness_filter = mlt_nb.Filter(profile, "brightness")
brightness_filter.set("level", "1.5")  # 150% brightness

# Note: Attaching filters requires MLT service methods
# This example shows filter creation
```

## Advanced Examples

### Example 6: Analyze Video Colors

```python
import mlt_nb
import numpy as np
import matplotlib.pyplot as plt

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

# Collect color statistics from first 10 frames
red_means = []
green_means = []
blue_means = []

for i in range(10):
    frame = producer.get_frame()
    image = frame.get_image()

    # Calculate mean color per channel
    red_means.append(image[:, :, 0].mean())
    green_means.append(image[:, :, 1].mean())
    blue_means.append(image[:, :, 2].mean())

# Plot results
plt.plot(red_means, 'r-', label='Red')
plt.plot(green_means, 'g-', label='Green')
plt.plot(blue_means, 'b-', label='Blue')
plt.xlabel('Frame')
plt.ylabel('Mean Pixel Value')
plt.legend()
plt.title('Color Analysis')
plt.savefig('color_analysis.png')
```

### Example 7: Detect Scene Changes

```python
import mlt_nb
import numpy as np

def detect_scene_change(frame1, frame2, threshold=30.0):
    """Detect scene change between two frames."""
    # Calculate mean absolute difference
    diff = np.abs(frame1.astype(float) - frame2.astype(float))
    mean_diff = diff.mean()
    return mean_diff > threshold

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

prev_image = None
scene_changes = []

for i in range(producer.get_length()):
    frame = producer.get_frame()
    image = frame.get_image()

    if prev_image is not None:
        if detect_scene_change(prev_image, image):
            scene_changes.append(i)
            print(f"Scene change detected at frame {i}")

    prev_image = image.copy()

print(f"\nTotal scene changes: {len(scene_changes)}")
```

### Example 8: Extract Thumbnails

```python
import mlt_nb
import numpy as np
from PIL import Image

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

producer = mlt_nb.Producer(profile, "/path/to/video.mp4")
total_frames = producer.get_length()

# Extract thumbnails at 10%, 50%, 90%
positions = [0.1, 0.5, 0.9]

for pos in positions:
    frame_num = int(total_frames * pos)

    # Seek to position (simplified; actual seeking may require more setup)
    frame = producer.get_frame()
    image = frame.get_image()

    # Convert to PIL Image and save
    pil_image = Image.fromarray(image[:, :, :3])  # RGB only
    pil_image.thumbnail((320, 240))
    pil_image.save(f"thumbnail_{int(pos*100)}pct.png")
    print(f"Saved thumbnail at {pos*100}%")
```

### Example 9: Multitrack Composition

```python
import mlt_nb

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

# Create multitrack
multitrack = mlt_nb.Multitrack()

# Create video and audio tracks
video_track = mlt_nb.Producer(profile, "/path/to/video.mp4")
audio_track = mlt_nb.Producer(profile, "/path/to/audio.mp3")

# Connect to different tracks
multitrack.connect(video_track, 0)
multitrack.connect(audio_track, 1)

print(f"Multitrack has {multitrack.count()} tracks")
```

### Example 10: Batch Processing with Zero-Copy

```python
import mlt_nb
import numpy as np
import time

factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()

producer = mlt_nb.Producer(profile, "/path/to/video.mp4")

# Process frames with zero-copy efficiency
start_time = time.time()
frame_count = 0
brightness_sum = 0.0

# Process up to 1000 frames
max_frames = min(1000, producer.get_length())

for i in range(max_frames):
    frame = producer.get_frame()
    image = frame.get_image()  # Zero-copy!

    # Fast NumPy operation
    brightness_sum += image.mean()
    frame_count += 1

elapsed = time.time() - start_time
fps = frame_count / elapsed

print(f"Processed {frame_count} frames in {elapsed:.2f}s")
print(f"Processing rate: {fps:.1f} fps")
print(f"Average brightness: {brightness_sum/frame_count:.2f}")
```

## Performance Comparison Example

```python
import mlt_nb
import time

# Benchmark: Get 100 frames and extract images
factory = mlt_nb.Factory()
factory.init()
profile = mlt_nb.Profile()
producer = mlt_nb.Producer(profile, "color:blue")

start = time.perf_counter()
for _ in range(100):
    frame = producer.get_frame()
    image = frame.get_image()  # Zero-copy NumPy array
    # Do something with image
    _ = image.mean()
end = time.perf_counter()

print(f"mlt-nb: {(end-start)*1000:.2f}ms for 100 frame+image operations")
print(f"Average per frame: {(end-start)*10:.2f}ms")

# Compare with SWIG binding (if available)
try:
    import mlt7 as mlt_swig
    import numpy as np

    factory_swig = mlt_swig.Factory()
    factory_swig.init()
    profile_swig = mlt_swig.Profile()
    producer_swig = mlt_swig.Producer(profile_swig, "color:blue")

    start = time.perf_counter()
    for _ in range(100):
        frame = producer_swig.get_frame()
        # SWIG requires manual conversion
        image_data = mlt_swig.frame_get_image(
            frame, mlt_swig.mlt_image_rgba,
            profile_swig.width(), profile_swig.height()
        )
        image = np.frombuffer(image_data, dtype=np.uint8)
        _ = image.mean()
    end = time.perf_counter()

    print(f"mlt-python (SWIG): {(end-start)*1000:.2f}ms for 100 frame+image operations")
    print(f"Average per frame: {(end-start)*10:.2f}ms")
except ImportError:
    print("mlt-python (SWIG) not available for comparison")
```

## Tips

1. **Always initialize**: Call `factory.init()` before creating other objects
2. **Check validity**: Use `is_valid()` to ensure objects were created successfully
3. **Zero-copy benefits**: `get_image()` returns NumPy arrays without copying data
4. **Profile reuse**: Create one Profile and reuse it for multiple objects
5. **Resource cleanup**: Python's garbage collection handles cleanup automatically
