# API Reference

## Core Classes

### Factory

Factory for initializing the MLT framework.

#### Methods

- **`__init__()`**: Create a Factory instance
- **`init(directory: str = "")`**: Initialize MLT framework
  - `directory`: Optional path to MLT modules directory
- **`close()`**: Close MLT framework and free resources

#### Example

```python
factory = mlt_nb.Factory()
factory.init()
```

---

### Profile

Represents MLT profile settings (resolution, frame rate, etc.).

#### Methods

- **`__init__(name: str = "")`**: Create a Profile
  - `name`: Optional profile name (e.g., "atsc_1080p_25")
- **`width() -> int`**: Get frame width in pixels
- **`height() -> int`**: Get frame height in pixels
- **`fps() -> float`**: Get frames per second
- **`frame_rate_num() -> int`**: Get frame rate numerator
- **`frame_rate_den() -> int`**: Get frame rate denominator

#### Example

```python
profile = mlt_nb.Profile()
print(f"{profile.width()}x{profile.height()} @ {profile.fps()} fps")
```

**Note**: In MLT 7.x, Profile does not expose the Properties interface. Use Producer/Consumer/Filter properties for dynamic configuration.

---

### Producer

Produces media frames (video/audio).

#### Constructor

```python
Producer(profile: Profile, service: str, resource: str = "")
```

- `profile`: Profile instance
- `service`: Service name or file path (e.g., "color:red", "/path/to/file.mp4")
- `resource`: Optional resource parameter

#### Methods

- **`is_valid() -> bool`**: Check if producer is valid
- **`get_frame(index: int = 0) -> Frame`**: Get a frame
  - `index`: Frame index (default: 0 for next frame)
  - Returns: Frame instance
- **`get_length() -> int`**: Get total number of frames
- **`get_in() -> int`**: Get in point (start frame)
- **`get_out() -> int`**: Get out point (end frame)
- **`set_in_and_out(in: int, out: int)`**: Set in/out points
- **`set(name: str, value: str)`**: Set a property
- **`get(name: str) -> str`**: Get a property value

#### Example

```python
producer = mlt_nb.Producer(profile, "color:blue")
if producer.is_valid():
    frame = producer.get_frame()
```

---

### Frame

Represents a single video/audio frame.

#### Methods

- **`get_image() -> np.ndarray`**: Get frame image as NumPy array (zero-copy)
  - Returns: NumPy array with shape `(height, width, channels)`
  - dtype: `uint8`
  - Channels: 3 (RGB) or 4 (RGBA)
- **`get_int(name: str) -> int`**: Get an integer property
- **`set(name: str, value: str)`**: Set a property

#### Example

```python
frame = producer.get_frame()
image = frame.get_image()  # NumPy array
print(image.shape)  # (height, width, channels)
```

---

### Consumer

Consumes media frames (for playback, encoding, etc.).

#### Constructor

```python
Consumer(profile: Profile, id: str, service: str = "")
```

- `profile`: Profile instance
- `id`: Consumer type (e.g., "sdl2", "avformat", "null")
- `service`: Optional service parameter

#### Methods

- **`is_valid() -> bool`**: Check if consumer is valid
- **`connect(producer: Producer) -> int`**: Connect a producer
  - Returns: 0 on success
- **`start() -> int`**: Start consuming frames
  - Returns: 0 on success
- **`stop() -> int`**: Stop consuming frames
  - Returns: 0 on success
- **`is_stopped() -> bool`**: Check if consumer is stopped
- **`set(name: str, value: str)`**: Set a property
- **`get(name: str) -> str`**: Get a property value

#### Example

```python
consumer = mlt_nb.Consumer(profile, "null")
consumer.connect(producer)
consumer.start()
```

---

### Playlist

Ordered list of producers with in/out points.

#### Constructor

```python
Playlist(profile: Profile)
```

#### Methods

- **`count() -> int`**: Get number of clips in playlist
- **`append(producer: Producer, in: int = -1, out: int = -1) -> int`**: Append a clip
  - `producer`: Producer to append
  - `in`: In point (-1 for producer's in point)
  - `out`: Out point (-1 for producer's out point)
  - Returns: 0 on success
- **`insert(producer: Producer, in: int, out: int, position: int) -> int`**: Insert a clip
- **`remove(index: int) -> int`**: Remove a clip at index
- **`clear()`**: Remove all clips

#### Example

```python
playlist = mlt_nb.Playlist(profile)
playlist.append(producer1)
playlist.append(producer2)
print(f"Playlist has {playlist.count()} clips")
```

---

### Filter

Applies effects to frames.

#### Constructor

```python
Filter(profile: Profile, id: str, service: str = "")
```

- `profile`: Profile instance
- `id`: Filter type (e.g., "brightness", "greyscale")
- `service`: Optional service parameter

#### Methods

- **`is_valid() -> bool`**: Check if filter is valid
- **`set(name: str, value: str)`**: Set a property
- **`get(name: str) -> str`**: Get a property value

#### Example

```python
brightness = mlt_nb.Filter(profile, "brightness")
brightness.set("level", "1.5")
```

---

### Transition

Blends between two producers.

#### Constructor

```python
Transition(profile: Profile, id: str, service: str = "")
```

- `profile`: Profile instance
- `id`: Transition type (e.g., "mix", "luma")
- `service`: Optional service parameter

#### Methods

- **`is_valid() -> bool`**: Check if transition is valid
- **`set(name: str, value: str)`**: Set a property
- **`get(name: str) -> str`**: Get a property value

#### Example

```python
mix = mlt_nb.Transition(profile, "mix")
mix.set("start", "0.0")
mix.set("end", "1.0")
```

---

### Multitrack

Container for multiple producer tracks.

#### Constructor

```python
Multitrack()
```

**Note**: In MLT 7.x, Multitrack no longer requires a Profile parameter in its constructor.

#### Methods

- **`count() -> int`**: Get number of tracks
- **`connect(producer: Producer, track: int) -> int`**: Connect producer to track
  - Returns: 0 on success

#### Example

```python
multitrack = mlt_nb.Multitrack()
multitrack.connect(video_track, 0)
multitrack.connect(audio_track, 1)
```

---

### Tractor

Combines multitrack with field (filters/transitions).

#### Constructor

```python
Tractor(profile: Profile)
```

#### Methods

- **`is_valid() -> bool`**: Check if tractor is valid
- **`count() -> int`**: Get number of tracks

#### Example

```python
tractor = mlt_nb.Tractor(profile)
```

---

### Properties

Generic key-value properties container.

#### Methods

- **`__init__()`**: Create a Properties instance
- **`set(name: str, value: str)`**: Set a string property
- **`get(name: str) -> str`**: Get a string property
- **`get_int(name: str) -> int`**: Get an integer property
- **`get_double(name: str) -> float`**: Get a float property

#### Example

```python
props = mlt_nb.Properties()
props.set("key", "value")
print(props.get("key"))
```

---

### Repository

Repository of available services (producers, filters, etc.).

Created by `Factory.init()`.

---

### Service

Base class for MLT services.

---

## Image Formats

When calling `Frame.get_image()`, the returned NumPy array format depends on MLT's internal format:

- **RGB (3 channels)**: shape `(height, width, 3)`, dtype `uint8`
- **RGBA (4 channels)**: shape `(height, width, 4)`, dtype `uint8`

The array uses **zero-copy** when possible, meaning it directly references MLT's internal buffer for maximum performance.

## Common Properties

### Producer Properties

- `"aspect_ratio"`: Pixel aspect ratio
- `"length"`: Length in frames
- `"resource"`: Resource path/name
- `"eof"`: End-of-file behavior

### Consumer Properties

- `"buffer"`: Buffer size
- `"prefill"`: Prefill buffer count
- `"real_time"`: Real-time mode (-1, 0, 1)

### Filter Properties

- `"in"`: In point
- `"out"`: Out point
- `"track"`: Track number

Refer to [MLT documentation](https://www.mltframework.org/docs/) for comprehensive property lists.

## Error Handling

Methods that can fail typically return:
- **Integer codes**: 0 for success, non-zero for failure
- **Boolean**: `is_valid()` returns `True` if object is valid
- **Exceptions**: `RuntimeError` for critical failures (e.g., `get_image()` failure)

## Thread Safety

MLT is generally not thread-safe. Use appropriate locking if accessing MLT objects from multiple threads.

## Memory Management

mlt-nb uses smart pointers internally to manage object lifetimes. Objects are automatically freed when no longer referenced.

For zero-copy NumPy arrays from `Frame.get_image()`, the Frame object must remain alive while the array is in use.
