#!/usr/bin/env python3
"""
Quick benchmark for a single operation.
Usage: python scripts/quick_benchmark.py [basemap|plot|coast|info]
"""

import sys
import time
from pathlib import Path

import numpy as np

# Add pygmt_nb to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

# Output directory
output_root = project_root / "output" / "benchmarks"
output_root.mkdir(parents=True, exist_ok=True)

try:
    import pygmt
    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False
    print("⚠️  PyGMT not available - will only test pygmt_nb")

import pygmt_nb


def benchmark_basemap(iterations=10):
    """Benchmark basemap operation."""
    print("\n" + "=" * 60)
    print("BASEMAP BENCHMARK")
    print("=" * 60)

    # pygmt_nb
    print("\n[pygmt_nb]")
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.savefig(str(output_root / "quick_bench_nb.ps"))
        end = time.perf_counter()
        times.append((end - start) * 1000)

    avg = sum(times) / len(times)
    print(f"  Average: {avg:.2f} ms")
    print(f"  Min/Max: {min(times):.2f} - {max(times):.2f} ms")

    if not PYGMT_AVAILABLE:
        return

    # PyGMT
    print("\n[PyGMT]")
    times_pygmt = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.savefig(str(output_root / "quick_bench_pygmt.eps"))
        end = time.perf_counter()
        times_pygmt.append((end - start) * 1000)

    avg_pygmt = sum(times_pygmt) / len(times_pygmt)
    print(f"  Average: {avg_pygmt:.2f} ms")
    print(f"  Min/Max: {min(times_pygmt):.2f} - {max(times_pygmt):.2f} ms")

    # Compare
    speedup = avg_pygmt / avg
    print(f"\n🚀 Speedup: {speedup:.2f}x faster with pygmt_nb")


def benchmark_plot(iterations=10):
    """Benchmark plot operation."""
    print("\n" + "=" * 60)
    print("PLOT BENCHMARK")
    print("=" * 60)

    # Prepare data
    x = np.random.uniform(0, 10, 100)
    y = np.random.uniform(0, 10, 100)

    # pygmt_nb
    print("\n[pygmt_nb]")
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.plot(x=x, y=y, style="c0.1c", color="red")
        fig.savefig(str(output_root / "quick_plot_nb.ps"))
        end = time.perf_counter()
        times.append((end - start) * 1000)

    avg = sum(times) / len(times)
    print(f"  Average: {avg:.2f} ms")
    print(f"  Min/Max: {min(times):.2f} - {max(times):.2f} ms")

    if not PYGMT_AVAILABLE:
        return

    # PyGMT
    print("\n[PyGMT]")
    times_pygmt = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.plot(x=x, y=y, style="c0.1c", fill="red")
        fig.savefig(str(output_root / "quick_plot_pygmt.eps"))
        end = time.perf_counter()
        times_pygmt.append((end - start) * 1000)

    avg_pygmt = sum(times_pygmt) / len(times_pygmt)
    print(f"  Average: {avg_pygmt:.2f} ms")
    print(f"  Min/Max: {min(times_pygmt):.2f} - {max(times_pygmt):.2f} ms")

    # Compare
    speedup = avg_pygmt / avg
    print(f"\n🚀 Speedup: {speedup:.2f}x faster with pygmt_nb")


def benchmark_coast(iterations=10):
    """Benchmark coast operation."""
    print("\n" + "=" * 60)
    print("COAST BENCHMARK")
    print("=" * 60)

    # pygmt_nb
    print("\n[pygmt_nb]")
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt_nb.Figure()
        fig.basemap(region=[130, 150, 30, 45], projection="M10c", frame=True)
        fig.coast(land="tan", water="lightblue", shorelines="thin")
        fig.savefig(str(output_root / "quick_coast_nb.ps"))
        end = time.perf_counter()
        times.append((end - start) * 1000)

    avg = sum(times) / len(times)
    print(f"  Average: {avg:.2f} ms")
    print(f"  Min/Max: {min(times):.2f} - {max(times):.2f} ms")

    if not PYGMT_AVAILABLE:
        return

    # PyGMT
    print("\n[PyGMT]")
    times_pygmt = []
    for i in range(iterations):
        start = time.perf_counter()
        fig = pygmt.Figure()
        fig.basemap(region=[130, 150, 30, 45], projection="M10c", frame=True)
        fig.coast(land="tan", water="lightblue", shorelines="thin")
        fig.savefig(str(output_root / "quick_coast_pygmt.eps"))
        end = time.perf_counter()
        times_pygmt.append((end - start) * 1000)

    avg_pygmt = sum(times_pygmt) / len(times_pygmt)
    print(f"  Average: {avg_pygmt:.2f} ms")
    print(f"  Min/Max: {min(times_pygmt):.2f} - {max(times_pygmt):.2f} ms")

    # Compare
    speedup = avg_pygmt / avg
    print(f"\n🚀 Speedup: {speedup:.2f}x faster with pygmt_nb")


def benchmark_info(iterations=10):
    """Benchmark info module function."""
    print("\n" + "=" * 60)
    print("INFO BENCHMARK")
    print("=" * 60)

    # Prepare data
    data_file = str(output_root / "quick_data.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    np.savetxt(data_file, np.column_stack([x, y]))

    # pygmt_nb
    print("\n[pygmt_nb]")
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        result = pygmt_nb.info(data_file)
        end = time.perf_counter()
        times.append((end - start) * 1000)

    avg = sum(times) / len(times)
    print(f"  Average: {avg:.2f} ms")
    print(f"  Min/Max: {min(times):.2f} - {max(times):.2f} ms")

    if not PYGMT_AVAILABLE:
        return

    # PyGMT
    print("\n[PyGMT]")
    times_pygmt = []
    for i in range(iterations):
        start = time.perf_counter()
        result = pygmt.info(data_file)
        end = time.perf_counter()
        times_pygmt.append((end - start) * 1000)

    avg_pygmt = sum(times_pygmt) / len(times_pygmt)
    print(f"  Average: {avg_pygmt:.2f} ms")
    print(f"  Min/Max: {min(times_pygmt):.2f} - {max(times_pygmt):.2f} ms")

    # Compare
    speedup = avg_pygmt / avg
    print(f"\n🚀 Speedup: {speedup:.2f}x faster with pygmt_nb")


def main():
    """Run quick benchmark."""
    if len(sys.argv) > 1:
        operation = sys.argv[1].lower()
    else:
        operation = "basemap"

    operations = {
        "basemap": benchmark_basemap,
        "plot": benchmark_plot,
        "coast": benchmark_coast,
        "info": benchmark_info,
    }

    if operation not in operations:
        print(f"Unknown operation: {operation}")
        print(f"Available: {', '.join(operations.keys())}")
        sys.exit(1)

    print("=" * 60)
    print("QUICK BENCHMARK")
    print(f"Operation: {operation}")
    print(f"Iterations: 10")
    print("=" * 60)

    operations[operation]()


if __name__ == "__main__":
    main()
