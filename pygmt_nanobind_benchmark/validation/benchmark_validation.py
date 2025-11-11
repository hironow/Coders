#!/usr/bin/env python3
"""
Validate benchmark results by checking actual file outputs.
This ensures both libraries are actually generating correct outputs.
"""

import sys
import time
from pathlib import Path

import numpy as np

# Add pygmt_nb to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

try:
    import pygmt
    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False
    print("PyGMT not available - validation cannot proceed")
    sys.exit(1)

import pygmt_nb


def test_basemap_output():
    """Test basemap output and file sizes."""
    print("\n" + "=" * 70)
    print("Testing Basemap Output")
    print("=" * 70)

    output_dir = Path("/tmp/validation_test")
    output_dir.mkdir(exist_ok=True)

    # Test pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    pygmt_nb_file = output_dir / "basemap_pygmt_nb.ps"
    fig_nb.savefig(str(pygmt_nb_file))
    end = time.perf_counter()
    pygmt_nb_time = (end - start) * 1000

    # Check file exists and get size
    if pygmt_nb_file.exists():
        pygmt_nb_size = pygmt_nb_file.stat().st_size
        print(f"  ✓ File created: {pygmt_nb_file}")
        print(f"  ✓ File size: {pygmt_nb_size:,} bytes")
        print(f"  ✓ Time: {pygmt_nb_time:.2f} ms")

        # Check file has content
        with open(pygmt_nb_file, 'rb') as f:
            first_bytes = f.read(100)
            print(f"  ✓ First bytes: {first_bytes[:50]}")
    else:
        print(f"  ❌ File not created!")
        pygmt_nb_size = 0

    # Test PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    pygmt_file = output_dir / "basemap_pygmt.eps"
    fig_pygmt.savefig(str(pygmt_file))
    end = time.perf_counter()
    pygmt_time = (end - start) * 1000

    # Check file exists and get size
    if pygmt_file.exists():
        pygmt_size = pygmt_file.stat().st_size
        print(f"  ✓ File created: {pygmt_file}")
        print(f"  ✓ File size: {pygmt_size:,} bytes")
        print(f"  ✓ Time: {pygmt_time:.2f} ms")

        # Check file has content
        with open(pygmt_file, 'rb') as f:
            first_bytes = f.read(100)
            print(f"  ✓ First bytes: {first_bytes[:50]}")
    else:
        print(f"  ❌ File not created!")
        pygmt_size = 0

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {pygmt_nb_size:,} bytes in {pygmt_nb_time:.2f} ms")
    print(f"  PyGMT:    {pygmt_size:,} bytes in {pygmt_time:.2f} ms")

    if pygmt_nb_size > 0 and pygmt_size > 0:
        speedup = pygmt_time / pygmt_nb_time
        size_ratio = pygmt_nb_size / pygmt_size
        print(f"  Speed ratio: {speedup:.2f}x")
        print(f"  Size ratio: {size_ratio:.2f}x")

        # Warning if suspicious
        if pygmt_nb_size < pygmt_size * 0.5:
            print(f"  ⚠️  WARNING: pygmt_nb file is much smaller than PyGMT!")
        if pygmt_nb_size < 1000:
            print(f"  ⚠️  WARNING: pygmt_nb file is very small (< 1KB)!")

    return output_dir


def test_plot_output():
    """Test plot output with actual data."""
    print("\n" + "=" * 70)
    print("Testing Plot Output")
    print("=" * 70)

    output_dir = Path("/tmp/validation_test")
    output_dir.mkdir(exist_ok=True)

    # Prepare data
    x = np.random.uniform(0, 10, 100)
    y = np.random.uniform(0, 10, 100)

    # Test pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig_nb.plot(x=x, y=y, style="c0.1c", color="red", pen="0.5p,black")
    pygmt_nb_file = output_dir / "plot_pygmt_nb.ps"
    fig_nb.savefig(str(pygmt_nb_file))
    end = time.perf_counter()
    pygmt_nb_time = (end - start) * 1000

    # Check file
    if pygmt_nb_file.exists():
        pygmt_nb_size = pygmt_nb_file.stat().st_size
        print(f"  ✓ File created: {pygmt_nb_file}")
        print(f"  ✓ File size: {pygmt_nb_size:,} bytes")
        print(f"  ✓ Time: {pygmt_nb_time:.2f} ms")
    else:
        print(f"  ❌ File not created!")
        pygmt_nb_size = 0

    # Test PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig_pygmt.plot(x=x, y=y, style="c0.1c", fill="red", pen="0.5p,black")
    pygmt_file = output_dir / "plot_pygmt.eps"
    fig_pygmt.savefig(str(pygmt_file))
    end = time.perf_counter()
    pygmt_time = (end - start) * 1000

    # Check file
    if pygmt_file.exists():
        pygmt_size = pygmt_file.stat().st_size
        print(f"  ✓ File created: {pygmt_file}")
        print(f"  ✓ File size: {pygmt_size:,} bytes")
        print(f"  ✓ Time: {pygmt_time:.2f} ms")
    else:
        print(f"  ❌ File not created!")
        pygmt_size = 0

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {pygmt_nb_size:,} bytes in {pygmt_nb_time:.2f} ms")
    print(f"  PyGMT:    {pygmt_size:,} bytes in {pygmt_time:.2f} ms")

    if pygmt_nb_size > 0 and pygmt_size > 0:
        speedup = pygmt_time / pygmt_nb_time
        size_ratio = pygmt_nb_size / pygmt_size
        print(f"  Speed ratio: {speedup:.2f}x")
        print(f"  Size ratio: {size_ratio:.2f}x")

        # Warning if suspicious
        if pygmt_nb_size < pygmt_size * 0.5:
            print(f"  ⚠️  WARNING: pygmt_nb file is much smaller than PyGMT!")


def main():
    """Run validation tests."""
    print("=" * 70)
    print("BENCHMARK VALIDATION")
    print("Checking if both libraries generate valid outputs")
    print("=" * 70)

    output_dir = test_basemap_output()
    test_plot_output()

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print(f"Output files saved to: {output_dir}")
    print("Please manually inspect the generated files!")
    print("=" * 70)


if __name__ == "__main__":
    main()
