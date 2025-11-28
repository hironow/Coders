"""Real-world scenario benchmarks comparing mlt-nb (nanobind) vs mlt-python (SWIG)."""

import time
import sys
import numpy as np

try:
    import mlt_nb
    HAS_MLT_NB = True
except ImportError:
    HAS_MLT_NB = False
    print("Warning: mlt_nb not available.")

try:
    import mlt7 as mlt_swig
    HAS_MLT_SWIG = True
except ImportError:
    HAS_MLT_SWIG = False
    print("Warning: mlt-python (SWIG) not available.")


def benchmark_video_editing_workflow(implementation, iterations=100):
    """
    Benchmark a typical video editing workflow:
    - Create multiple clips (producers)
    - Add them to a playlist with in/out points
    - Apply filters
    - Set properties
    """
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            # Create playlist for timeline
            playlist = mlt_nb.Playlist(profile)

            # Add 5 color clips simulating video segments
            for i, color in enumerate(["red", "green", "blue", "yellow", "cyan"]):
                producer = mlt_nb.Producer(profile, f"color:{color}")
                producer.set("length", "100")
                producer.set_in_and_out(0, 99)
                playlist.append(producer)

            # Apply a filter to the playlist
            brightness = mlt_nb.Filter(profile, "brightness", "")
            brightness.set("level", "1.2")
        end = time.perf_counter()

    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            # Create playlist for timeline
            playlist = mlt_swig.Playlist(profile)

            # Add 5 color clips simulating video segments
            for i, color in enumerate(["red", "green", "blue", "yellow", "cyan"]):
                producer = mlt_swig.Producer(profile, f"color:{color}")
                producer.set("length", "100")
                producer.set_in_and_out(0, 99)
                playlist.append(producer)

            # Apply a filter to the playlist
            brightness = mlt_swig.Filter(profile, "brightness", "")
            brightness.set("level", "1.2")
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_frame_processing_pipeline(implementation, iterations=50):
    """
    Benchmark frame processing pipeline:
    - Get multiple frames sequentially
    - Extract image data as NumPy arrays
    - Perform simple image processing (calculate mean pixel value)
    """
    frames_per_iteration = 10

    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()
        producer = mlt_nb.Producer(profile, "color:blue")

        # Warmup
        for _ in range(5):
            frame = producer.get_frame()
            image = frame.get_image()

        start = time.perf_counter()
        for _ in range(iterations):
            total_mean = 0.0
            for frame_idx in range(frames_per_iteration):
                frame = producer.get_frame()
                image = frame.get_image()
                # Simulate real processing: calculate mean pixel value
                total_mean += np.mean(image)
        end = time.perf_counter()

    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()
        producer = mlt_swig.Producer(profile, "color:blue")

        # Warmup
        for _ in range(5):
            frame = producer.get_frame()
            data = mlt_swig.frame_get_image(
                frame, mlt_swig.mlt_image_rgba,
                profile.width(), profile.height()
            )

        start = time.perf_counter()
        for _ in range(iterations):
            total_mean = 0.0
            for frame_idx in range(frames_per_iteration):
                frame = producer.get_frame()
                # SWIG returns bytes, convert to numpy for fair comparison
                data = mlt_swig.frame_get_image(
                    frame, mlt_swig.mlt_image_rgba,
                    profile.width(), profile.height()
                )
                # Convert bytes to numpy array
                width = profile.width()
                height = profile.height()
                image = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)
                # Simulate real processing
                total_mean += np.mean(image)
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_multi_track_composition(implementation, iterations=50):
    """
    Benchmark multi-track composition:
    - Create multiple tracks
    - Add producers to different tracks
    - Apply transitions between tracks
    - Use tractor to combine tracks
    """
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            # Create two playlists for two video tracks
            track0 = mlt_nb.Playlist(profile)
            track1 = mlt_nb.Playlist(profile)

            # Add clips to track 0
            producer0 = mlt_nb.Producer(profile, "color:red")
            producer0.set("length", "100")
            track0.append(producer0)

            # Add clips to track 1
            producer1 = mlt_nb.Producer(profile, "color:green")
            producer1.set("length", "100")
            track1.append(producer1)

            # Create tractor to combine tracks
            tractor = mlt_nb.Tractor(profile)

            # Create transition between tracks
            transition = mlt_nb.Transition(profile, "mix", "")
            transition.set("start", "0.0")
            transition.set("end", "1.0")
        end = time.perf_counter()

    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            # Create two playlists for two video tracks
            track0 = mlt_swig.Playlist(profile)
            track1 = mlt_swig.Playlist(profile)

            # Add clips to track 0
            producer0 = mlt_swig.Producer(profile, "color:red")
            producer0.set("length", "100")
            track0.append(producer0)

            # Add clips to track 1
            producer1 = mlt_swig.Producer(profile, "color:green")
            producer1.set("length", "100")
            track1.append(producer1)

            # Create tractor to combine tracks
            tractor = mlt_swig.Tractor(profile)

            # Create transition between tracks
            transition = mlt_swig.Transition(profile, "mix", "")
            transition.set("start", "0.0")
            transition.set("end", "1.0")
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_complex_timeline(implementation, iterations=20):
    """
    Benchmark complex timeline operations:
    - Create playlist with many clips
    - Mix of different producers
    - Multiple filters
    - Property queries and modifications
    """
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            playlist = mlt_nb.Playlist(profile)

            # Add 20 clips with various settings
            colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
            for i in range(20):
                color = colors[i % len(colors)]
                producer = mlt_nb.Producer(profile, f"color:{color}")
                producer.set("length", "50")

                # Set various properties
                producer.set("aspect_ratio", "1.0")

                # Query properties
                length = producer.get_length()
                in_point = producer.get_in()

                playlist.append(producer, 0, 49)

            # Query playlist info
            count = playlist.count()

            # Apply multiple filters
            for filter_name in ["brightness", "brightness"]:
                f = mlt_nb.Filter(profile, filter_name, "")
                f.set("level", "1.1")
        end = time.perf_counter()

    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()

        start = time.perf_counter()
        for _ in range(iterations):
            playlist = mlt_swig.Playlist(profile)

            # Add 20 clips with various settings
            colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
            for i in range(20):
                color = colors[i % len(colors)]
                producer = mlt_swig.Producer(profile, f"color:{color}")
                producer.set("length", "50")

                # Set various properties
                producer.set("aspect_ratio", "1.0")

                # Query properties
                length = producer.get_length()
                in_point = producer.get_in()

                playlist.append(producer, 0, 49)

            # Query playlist info
            count = playlist.count()

            # Apply multiple filters
            for filter_name in ["brightness", "brightness"]:
                f = mlt_swig.Filter(profile, filter_name, "")
                f.set("level", "1.1")
        end = time.perf_counter()

    return (end - start) / iterations


def run_real_world_benchmarks():
    """Run all real-world benchmarks and display results."""
    benchmarks = [
        ("Video Editing Workflow", benchmark_video_editing_workflow, 100),
        ("Frame Processing Pipeline", benchmark_frame_processing_pipeline, 50),
        ("Multi-track Composition", benchmark_multi_track_composition, 50),
        ("Complex Timeline (20 clips)", benchmark_complex_timeline, 20),
    ]

    print("\n" + "=" * 80)
    print("Real-World MLT Workflow Benchmarks")
    print("=" * 80)
    print(f"{'Scenario':<35} {'nanobind (ms)':<20} {'SWIG (ms)':<20} {'Speedup':<10}")
    print("-" * 80)

    results = []
    for name, bench_func, iterations in benchmarks:
        if HAS_MLT_NB:
            try:
                nb_time = bench_func("nanobind", iterations) * 1000  # Convert to ms
            except Exception as e:
                nb_time = None
                print(f"Error in nanobind {name}: {e}")
        else:
            nb_time = None

        if HAS_MLT_SWIG:
            try:
                swig_time = bench_func("swig", iterations) * 1000  # Convert to ms
            except Exception as e:
                swig_time = None
                print(f"Error in SWIG {name}: {e}")
        else:
            swig_time = None

        if nb_time is not None and swig_time is not None:
            speedup = swig_time / nb_time
            print(f"{name:<35} {nb_time:>18.2f}  {swig_time:>18.2f}  {speedup:>8.2f}x")
            results.append((name, nb_time, swig_time, speedup))
        elif nb_time is not None:
            print(f"{name:<35} {nb_time:>18.2f}  {'N/A':<20} {'N/A':<10}")
        elif swig_time is not None:
            print(f"{name:<35} {'N/A':<20} {swig_time:>18.2f}  {'N/A':<10}")
        else:
            print(f"{name:<35} {'N/A':<20} {'N/A':<20} {'N/A':<10}")

    print("-" * 80)

    if results:
        avg_speedup = sum(r[3] for r in results) / len(results)
        print(f"\nAverage speedup: {avg_speedup:.2f}x")

        if avg_speedup >= 0.95:
            print(f"✅ nanobind achieves performance parity with SWIG in real-world scenarios")
        elif avg_speedup >= 0.90:
            print(f"✅ nanobind is within 10% of SWIG performance in real-world scenarios")
        else:
            print(f"⚠️  nanobind is {(1-avg_speedup)*100:.0f}% slower than SWIG in real-world scenarios")
    else:
        print("\nNo complete benchmark results available.")
        print("Please ensure both mlt-nb and mlt-python are installed.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    if not HAS_MLT_NB and not HAS_MLT_SWIG:
        print("Error: Neither mlt-nb nor mlt-python is available.")
        print("Please install at least one implementation.")
        sys.exit(1)

    run_real_world_benchmarks()
