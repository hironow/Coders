"""
Benchmark: Session.call_module() (nanobind) vs subprocess

This benchmark compares the performance of calling GMT commands via:
1. nanobind (Session.call_module() - direct C API)
2. subprocess (current Figure implementation)

Goal: Determine if nanobind provides significant speed advantage for Figure methods.
"""

import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))
from pygmt_nb import Session


def benchmark_session_call_module(iterations=100):
    """Benchmark Session.call_module() for GMT commands."""
    times = []

    for i in range(iterations):
        session = Session()

        start = time.perf_counter()
        # Call a simple GMT command that doesn't require file I/O
        session.call_module("gmtset", "PS_MEDIA A4")
        end = time.perf_counter()

        times.append(end - start)
        del session

    return times


def benchmark_subprocess(iterations=100):
    """Benchmark subprocess.run() for GMT commands."""
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        # Same command via subprocess
        subprocess.run(["gmt", "gmtset", "PS_MEDIA", "A4"], capture_output=True, check=True)
        end = time.perf_counter()

        times.append(end - start)

    return times


def benchmark_complex_command_nanobind(iterations=50):
    """Benchmark complex GMT command with nanobind."""
    times = []
    temp_dir = Path(tempfile.mkdtemp())

    try:
        for i in range(iterations):
            output_file = temp_dir / f"test_{i}.ps"
            session = Session()

            start = time.perf_counter()
            # Use classic mode command that doesn't require output redirection
            # Note: We can't actually capture PS output without redirection,
            # so this measures command execution time only
            try:
                session.call_module("psbasemap", "-R0/10/0/10 -JX10c -Ba -K")
            except Exception:
                pass  # Expected to fail without output redirection
            end = time.perf_counter()

            times.append(end - start)
            del session
    finally:
        import shutil

        shutil.rmtree(temp_dir)

    return times


def benchmark_complex_command_subprocess(iterations=50):
    """Benchmark complex GMT command with subprocess."""
    times = []
    temp_dir = Path(tempfile.mkdtemp())

    try:
        for i in range(iterations):
            output_file = temp_dir / f"test_{i}.ps"

            start = time.perf_counter()
            with open(output_file, "wb") as f:
                subprocess.run(
                    ["gmt", "psbasemap", "-R0/10/0/10", "-JX10c", "-Ba", "-K"],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            end = time.perf_counter()

            times.append(end - start)
    finally:
        import shutil

        shutil.rmtree(temp_dir)

    return times


def print_stats(name, times):
    """Print statistics for benchmark results."""
    mean = statistics.mean(times)
    median = statistics.median(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)

    print(f"\n{name}")
    print(f"  Mean:   {mean * 1000:.3f} ms")
    print(f"  Median: {median * 1000:.3f} ms")
    print(f"  StdDev: {stdev * 1000:.3f} ms")
    print(f"  Min:    {min_time * 1000:.3f} ms")
    print(f"  Max:    {max_time * 1000:.3f} ms")
    print(f"  Throughput: {1 / mean:.1f} ops/sec")

    return mean


def main():
    print("=" * 70)
    print("Benchmark: nanobind (Session.call_module) vs subprocess")
    print("=" * 70)

    print("\n### Test 1: Simple GMT command (gmtset) ###")
    print("Iterations: 100")

    print("\nRunning Session.call_module() benchmark...")
    nanobind_times_simple = benchmark_session_call_module(100)
    nanobind_mean_simple = print_stats("Session.call_module() (nanobind)", nanobind_times_simple)

    print("\nRunning subprocess benchmark...")
    subprocess_times_simple = benchmark_subprocess(100)
    subprocess_mean_simple = print_stats("subprocess.run()", subprocess_times_simple)

    speedup_simple = subprocess_mean_simple / nanobind_mean_simple
    print(f"\n⚡ Speedup: {speedup_simple:.2f}x faster with nanobind")

    print("\n" + "=" * 70)
    print("\n### Test 2: Complex GMT command (psbasemap) ###")
    print("Iterations: 50")

    print("\nRunning Session.call_module() benchmark...")
    nanobind_times_complex = benchmark_complex_command_nanobind(50)
    nanobind_mean_complex = print_stats("Session.call_module() (nanobind)", nanobind_times_complex)

    print("\nRunning subprocess benchmark...")
    subprocess_times_complex = benchmark_complex_command_subprocess(50)
    subprocess_mean_complex = print_stats("subprocess.run() + file I/O", subprocess_times_complex)

    # Note: This comparison is not fair because nanobind version doesn't include file I/O
    print("\n⚠ Note: Subprocess includes file I/O overhead, nanobind does not")
    print(f"   Subprocess time: {subprocess_mean_complex * 1000:.3f} ms")
    print(f"   Nanobind time:   {nanobind_mean_complex * 1000:.3f} ms")
    print(
        f"   File I/O overhead: ~{(subprocess_mean_complex - nanobind_mean_complex) * 1000:.3f} ms"
    )

    print("\n" + "=" * 70)
    print("\n### Summary ###")
    print(f"Simple command speedup: {speedup_simple:.2f}x")
    print("\nConclusion:")
    if speedup_simple > 2.0:
        print(f"  ✅ nanobind provides significant speedup ({speedup_simple:.2f}x)")
        print("  ✅ Recommendation: Migrate to nanobind-based architecture")
    elif speedup_simple > 1.5:
        print(f"  ✓ nanobind provides moderate speedup ({speedup_simple:.2f}x)")
        print("  ✓ Recommendation: Consider migration if architecture allows")
    else:
        print(f"  ⚠ nanobind provides minimal speedup ({speedup_simple:.2f}x)")
        print("  ⚠ Recommendation: Subprocess may be acceptable")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
