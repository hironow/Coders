#!/usr/bin/env python3
"""
Compare a single GMT operation between PyGMT and pygmt_nb.
Useful for debugging specific function implementations.

Usage:
    python scripts/compare_operation.py info data.txt
    python scripts/compare_operation.py select data.txt --region 0/10/0/10
"""

import sys
import time
from pathlib import Path

import numpy as np

# Add pygmt_nb to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

# Output directory
output_root = project_root / "output" / "validation"
output_root.mkdir(parents=True, exist_ok=True)

try:
    import pygmt
    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False
    print("❌ PyGMT not available")
    sys.exit(1)

import pygmt_nb


def compare_info():
    """Compare info function."""
    print("\n" + "=" * 60)
    print("COMPARING: info")
    print("=" * 60)

    # Create test data
    data_file = str(output_root / "test_data.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    np.savetxt(data_file, np.column_stack([x, y]))

    print(f"\nTest data: {data_file}")
    print(f"  1000 random points in [0, 10] × [0, 10]")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.info(data_file)
    end = time.perf_counter()
    time_nb = (end - start) * 1000

    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Result:\n{result_nb}")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.info(data_file)
    end = time.perf_counter()
    time_pygmt = (end - start) * 1000

    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Result:\n{result_pygmt}")

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {time_nb:.2f} ms")
    print(f"  PyGMT:    {time_pygmt:.2f} ms")
    print(f"  Speedup:  {time_pygmt / time_nb:.2f}x")

    if result_nb.strip() == result_pygmt.strip():
        print(f"  ✅ Results are identical")
    else:
        print(f"  ⚠️  Results differ!")


def compare_select():
    """Compare select function."""
    print("\n" + "=" * 60)
    print("COMPARING: select")
    print("=" * 60)

    # Create test data
    data_file = str(output_root / "test_data.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    np.savetxt(data_file, np.column_stack([x, y]))

    print(f"\nTest data: {data_file}")
    print(f"  1000 random points in [0, 10] × [0, 10]")
    print(f"  Selecting region: [2, 8, 2, 8]")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.select(data_file, region=[2, 8, 2, 8])
    end = time.perf_counter()
    time_nb = (end - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Selected: {lines_nb} points")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.select(data_file, region=[2, 8, 2, 8])
    end = time.perf_counter()
    time_pygmt = (end - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Selected: {lines_pygmt} points")

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {time_nb:.2f} ms, {lines_nb} points")
    print(f"  PyGMT:    {time_pygmt:.2f} ms, {lines_pygmt} points")
    print(f"  Speedup:  {time_pygmt / time_nb:.2f}x")

    if lines_nb == lines_pygmt:
        print(f"  ✅ Same number of points selected")
    else:
        print(f"  ⚠️  Different number of points!")


def compare_blockmean():
    """Compare blockmean function."""
    print("\n" + "=" * 60)
    print("COMPARING: blockmean")
    print("=" * 60)

    # Create test data
    data_file = str(output_root / "test_data_xyz.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    z = np.sin(x) * np.cos(y)
    np.savetxt(data_file, np.column_stack([x, y, z]))

    print(f"\nTest data: {data_file}")
    print(f"  1000 random points in [0, 10] × [0, 10]")
    print(f"  Block averaging with spacing=1")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.blockmean(
        data_file, region=[0, 10, 0, 10], spacing="1", summary="m"
    )
    end = time.perf_counter()
    time_nb = (end - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Output: {lines_nb} blocks")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.blockmean(
        data_file, region=[0, 10, 0, 10], spacing="1", summary="m"
    )
    end = time.perf_counter()
    time_pygmt = (end - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Output: {lines_pygmt} blocks")

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {time_nb:.2f} ms, {lines_nb} blocks")
    print(f"  PyGMT:    {time_pygmt:.2f} ms, {lines_pygmt} blocks")
    print(f"  Speedup:  {time_pygmt / time_nb:.2f}x")

    if lines_nb == lines_pygmt:
        print(f"  ✅ Same number of blocks")
    else:
        print(f"  ⚠️  Different number of blocks!")


def compare_makecpt():
    """Compare makecpt function."""
    print("\n" + "=" * 60)
    print("COMPARING: makecpt")
    print("=" * 60)

    print("\nGenerating color palette: viridis, range [0, 100]")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.makecpt(cmap="viridis", series=[0, 100])
    end = time.perf_counter()
    time_nb = (end - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Output: {lines_nb} lines")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.makecpt(cmap="viridis", series=[0, 100])
    end = time.perf_counter()
    time_pygmt = (end - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Output: {lines_pygmt} lines")

    # Compare
    print("\n[Comparison]")
    print(f"  pygmt_nb: {time_nb:.2f} ms, {lines_nb} lines")
    print(f"  PyGMT:    {time_pygmt:.2f} ms, {lines_pygmt} lines")
    print(f"  Speedup:  {time_pygmt / time_nb:.2f}x")


def main():
    """Run comparison."""
    operations = {
        "info": compare_info,
        "select": compare_select,
        "blockmean": compare_blockmean,
        "makecpt": compare_makecpt,
    }

    if len(sys.argv) < 2:
        print("Usage: python scripts/compare_operation.py [operation]")
        print(f"Available operations: {', '.join(operations.keys())}")
        sys.exit(1)

    operation = sys.argv[1].lower()

    if operation not in operations:
        print(f"Unknown operation: {operation}")
        print(f"Available: {', '.join(operations.keys())}")
        sys.exit(1)

    print("=" * 60)
    print("OPERATION COMPARISON")
    print("=" * 60)

    operations[operation]()


if __name__ == "__main__":
    main()
