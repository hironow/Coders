"""Performance benchmark comparing mlt-nb (nanobind) vs mlt-python (SWIG)."""

import time
import sys
from pathlib import Path

try:
    import numpy as np
    import mlt_nb
    HAS_MLT_NB = True
except ImportError:
    HAS_MLT_NB = False
    print("Warning: mlt_nb not available. Install with: pip install -e .")

try:
    import mlt7 as mlt_swig
    HAS_MLT_SWIG = True
except ImportError:
    HAS_MLT_SWIG = False
    print("Warning: mlt-python (SWIG) not available.")


def benchmark_factory_init(implementation, iterations=1000):
    """Benchmark factory initialization."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        start = time.perf_counter()
        for _ in range(iterations):
            factory.init()
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        start = time.perf_counter()
        for _ in range(iterations):
            factory.init()
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_profile_creation(implementation, iterations=10000):
    """Benchmark profile creation."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        start = time.perf_counter()
        for _ in range(iterations):
            profile = mlt_nb.Profile()
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        start = time.perf_counter()
        for _ in range(iterations):
            profile = mlt_swig.Profile()
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_producer_creation(implementation, iterations=1000):
    """Benchmark producer creation."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()
        start = time.perf_counter()
        for _ in range(iterations):
            producer = mlt_nb.Producer(profile, "color:red")
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()
        start = time.perf_counter()
        for _ in range(iterations):
            producer = mlt_swig.Producer(profile, "color:red")
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_frame_get(implementation, iterations=1000):
    """Benchmark getting frames from producer."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()
        producer = mlt_nb.Producer(profile, "color:blue")
        start = time.perf_counter()
        for _ in range(iterations):
            frame = producer.get_frame()
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()
        producer = mlt_swig.Producer(profile, "color:blue")
        start = time.perf_counter()
        for _ in range(iterations):
            frame = producer.get_frame()
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_image_get(implementation, iterations=100):
    """Benchmark getting image data from frames."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()
        producer = mlt_nb.Producer(profile, "color:green")
        start = time.perf_counter()
        for _ in range(iterations):
            frame = producer.get_frame()
            image = frame.get_image()
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()
        producer = mlt_swig.Producer(profile, "color:green")
        start = time.perf_counter()
        for _ in range(iterations):
            frame = producer.get_frame()
            # SWIG returns binary data, not NumPy array
            image = mlt_swig.frame_get_image(
                frame, mlt_swig.mlt_image_rgba,
                profile.width(), profile.height()
            )
        end = time.perf_counter()

    return (end - start) / iterations


def benchmark_playlist_operations(implementation, iterations=100):
    """Benchmark playlist operations."""
    if implementation == "nanobind":
        factory = mlt_nb.Factory()
        factory.init()
        profile = mlt_nb.Profile()
        start = time.perf_counter()
        for _ in range(iterations):
            playlist = mlt_nb.Playlist(profile)
            producer = mlt_nb.Producer(profile, "color:yellow")
            playlist.append(producer)
        end = time.perf_counter()
    else:  # SWIG
        factory = mlt_swig.Factory()
        factory.init()
        profile = mlt_swig.Profile()
        start = time.perf_counter()
        for _ in range(iterations):
            playlist = mlt_swig.Playlist(profile)
            producer = mlt_swig.Producer(profile, "color:yellow")
            playlist.append(producer)
        end = time.perf_counter()

    return (end - start) / iterations


def run_benchmarks():
    """Run all benchmarks and display results."""
    benchmarks = [
        ("Factory Init", benchmark_factory_init, 1000),
        ("Profile Creation", benchmark_profile_creation, 10000),
        ("Producer Creation", benchmark_producer_creation, 1000),
        ("Frame Get", benchmark_frame_get, 1000),
        ("Image Get (zero-copy)", benchmark_image_get, 100),
        ("Playlist Operations", benchmark_playlist_operations, 100),
    ]

    print("\n" + "=" * 80)
    print("MLT nanobind vs SWIG Performance Benchmark")
    print("=" * 80)
    print(f"{'Benchmark':<30} {'nanobind (μs)':<20} {'SWIG (μs)':<20} {'Speedup':<10}")
    print("-" * 80)

    results = []
    for name, bench_func, iterations in benchmarks:
        if HAS_MLT_NB:
            try:
                nb_time = bench_func("nanobind", iterations) * 1_000_000  # Convert to μs
            except Exception as e:
                nb_time = None
                print(f"Error in nanobind {name}: {e}")
        else:
            nb_time = None

        if HAS_MLT_SWIG:
            try:
                swig_time = bench_func("swig", iterations) * 1_000_000  # Convert to μs
            except Exception as e:
                swig_time = None
                print(f"Error in SWIG {name}: {e}")
        else:
            swig_time = None

        if nb_time is not None and swig_time is not None:
            speedup = swig_time / nb_time
            print(f"{name:<30} {nb_time:>18.2f}  {swig_time:>18.2f}  {speedup:>8.2f}x")
            results.append((name, nb_time, swig_time, speedup))
        elif nb_time is not None:
            print(f"{name:<30} {nb_time:>18.2f}  {'N/A':<20} {'N/A':<10}")
        elif swig_time is not None:
            print(f"{name:<30} {'N/A':<20} {swig_time:>18.2f}  {'N/A':<10}")
        else:
            print(f"{name:<30} {'N/A':<20} {'N/A':<20} {'N/A':<10}")

    print("-" * 80)

    if results:
        avg_speedup = sum(r[3] for r in results) / len(results)
        print(f"\nAverage speedup: {avg_speedup:.2f}x")
        print(f"\nnanobind is {avg_speedup:.1f}x faster than SWIG on average")
    else:
        print("\nNo complete benchmark results available.")
        print("Please ensure both mlt-nb and mlt-python are installed.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    if not HAS_MLT_NB and not HAS_MLT_SWIG:
        print("Error: Neither mlt-nb nor mlt-python is available.")
        print("Please install at least one implementation.")
        sys.exit(1)

    run_benchmarks()
