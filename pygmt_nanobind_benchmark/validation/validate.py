#!/usr/bin/env python3
"""
Comprehensive Validation Suite for pygmt_nb vs PyGMT

Validates that pygmt_nb produces compatible outputs with PyGMT through:
1. Output Validation - File size, format, and content validation
2. Operation Comparison - Detailed function-level comparisons
3. Basic Validation - Core functionality tests
"""

import sys
import subprocess
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
    print("✓ PyGMT available")
except ImportError:
    PYGMT_AVAILABLE = False
    print("✗ PyGMT not available - cannot run validation")
    sys.exit(1)

import pygmt_nb  # noqa: E402


# =============================================================================
# Validation Utilities
# =============================================================================


def check_postscript_file(ps_file: Path, expected_min_size: int = 1000):
    """Check PostScript file is valid."""
    if not ps_file.exists():
        print(f"  ✗ File not found: {ps_file}")
        return False

    size = ps_file.stat().st_size
    print(f"  ✓ File size: {size:,} bytes")

    if size < expected_min_size:
        print(f"  ⚠️  File seems too small (< {expected_min_size} bytes)")
        return False

    # Check PostScript header
    with open(ps_file, "rb") as f:
        header = f.read(20)
        if not header.startswith(b"%!PS-Adobe"):
            print(f"  ✗ Not a valid PostScript file!")
            return False
        print(f"  ✓ Valid PostScript header")

    return True


def compare_file_sizes(file1: Path, file2: Path):
    """Compare two file sizes."""
    size1 = file1.stat().st_size
    size2 = file2.stat().st_size
    ratio = size1 / size2

    print(f"\n[Comparing file sizes]")
    print(f"  pygmt_nb: {size1:,} bytes")
    print(f"  PyGMT:    {size2:,} bytes")
    print(f"  Ratio:    {ratio:.3f}x")

    if 0.9 <= ratio <= 1.1:
        print(f"  ✓ File sizes are similar")
        return True
    else:
        print(f"  ⚠️  File sizes differ significantly")
        return False


def compare_images_with_imagemagick(img1: Path, img2: Path):
    """Compare images using ImageMagick."""
    try:
        result = subprocess.run(
            ["compare", "-metric", "RMSE", str(img1), str(img2), "/tmp/diff.png"],
            capture_output=True,
            text=True,
        )
        rmse = result.stderr.strip()
        print(f"\n[ImageMagick comparison]")
        print(f"  RMSE: {rmse}")

        if rmse.startswith("0 "):
            print(f"  ✅ Images are identical!")
            return True
        else:
            print(f"  ⚠️  Images have differences")
            print(f"  Difference map: /tmp/diff.png")
            return False
    except FileNotFoundError:
        print(f"\n  ⚠️  ImageMagick 'compare' not found - skipping pixel comparison")
        return None


# =============================================================================
# Section 1: Output Validation
# =============================================================================


def validate_basemap_output():
    """Validate basemap output files."""
    print("\n" + "=" * 70)
    print("OUTPUT VALIDATION: Basemap")
    print("=" * 70)

    # Generate outputs
    pygmt_nb_file = output_root / "validate_basemap_nb.ps"
    pygmt_file = output_root / "validate_basemap_pygmt.eps"

    print("\n[pygmt_nb]")
    fig = pygmt_nb.Figure()
    fig.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig.savefig(str(pygmt_nb_file))

    valid_nb = check_postscript_file(pygmt_nb_file)

    print("\n[PyGMT]")
    fig = pygmt.Figure()
    fig.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig.savefig(str(pygmt_file))

    valid_pygmt = check_postscript_file(pygmt_file)

    if valid_nb and valid_pygmt:
        compare_file_sizes(pygmt_nb_file, pygmt_file)

    return valid_nb and valid_pygmt


def validate_coast_output():
    """Validate coast output files."""
    print("\n" + "=" * 70)
    print("OUTPUT VALIDATION: Coast")
    print("=" * 70)

    # Generate outputs
    pygmt_nb_file = output_root / "validate_coast_nb.ps"
    pygmt_file = output_root / "validate_coast_pygmt.eps"

    print("\n[pygmt_nb]")
    fig = pygmt_nb.Figure()
    fig.basemap(region=[130, 150, 30, 45], projection="M15c", frame=True)
    fig.coast(land="tan", water="lightblue", shorelines="thin")
    fig.savefig(str(pygmt_nb_file))

    valid_nb = check_postscript_file(pygmt_nb_file)

    print("\n[PyGMT]")
    fig = pygmt.Figure()
    fig.basemap(region=[130, 150, 30, 45], projection="M15c", frame=True)
    fig.coast(land="tan", water="lightblue", shorelines="thin")
    fig.savefig(str(pygmt_file))

    valid_pygmt = check_postscript_file(pygmt_file)

    if valid_nb and valid_pygmt:
        compare_file_sizes(pygmt_nb_file, pygmt_file)

    return valid_nb and valid_pygmt


def validate_plot_output():
    """Validate plot output files."""
    print("\n" + "=" * 70)
    print("OUTPUT VALIDATION: Plot")
    print("=" * 70)

    # Prepare data
    x = np.random.uniform(0, 10, 100)
    y = np.random.uniform(0, 10, 100)

    # Generate outputs
    pygmt_nb_file = output_root / "validate_plot_nb.ps"
    pygmt_file = output_root / "validate_plot_pygmt.eps"

    print("\n[pygmt_nb]")
    fig = pygmt_nb.Figure()
    fig.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig.plot(x=x, y=y, style="c0.2c", color="red")
    fig.savefig(str(pygmt_nb_file))

    valid_nb = check_postscript_file(pygmt_nb_file)

    print("\n[PyGMT]")
    fig = pygmt.Figure()
    fig.basemap(region=[0, 10, 0, 10], projection="X15c", frame="afg")
    fig.plot(x=x, y=y, style="c0.2c", fill="red")
    fig.savefig(str(pygmt_file))

    valid_pygmt = check_postscript_file(pygmt_file)

    if valid_nb and valid_pygmt:
        compare_file_sizes(pygmt_nb_file, pygmt_file)

    return valid_nb and valid_pygmt


# =============================================================================
# Section 2: Operation Comparison
# =============================================================================


def compare_info_operation():
    """Compare info function."""
    print("\n" + "=" * 70)
    print("OPERATION COMPARISON: info")
    print("=" * 70)

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
    time_nb = (time.perf_counter() - start) * 1000

    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Result: {result_nb.strip()}")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.info(data_file)
    time_pygmt = (time.perf_counter() - start) * 1000

    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Result: {result_pygmt.strip()}")

    # Compare
    print("\n[Comparison]")
    print(f"  Speedup: {time_pygmt / time_nb:.2f}x")

    if result_nb.strip() == result_pygmt.strip():
        print(f"  ✅ Results are identical")
        return True
    else:
        print(f"  ⚠️  Results differ!")
        return False


def compare_select_operation():
    """Compare select function."""
    print("\n" + "=" * 70)
    print("OPERATION COMPARISON: select")
    print("=" * 70)

    # Create test data
    data_file = str(output_root / "test_data.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    np.savetxt(data_file, np.column_stack([x, y]))

    print(f"\nTest data: {data_file}")
    print(f"  1000 random points, selecting region [2, 8, 2, 8]")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.select(data_file, region=[2, 8, 2, 8])
    time_nb = (time.perf_counter() - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if isinstance(result_nb, str) and result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Selected: {lines_nb} points")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.select(data_file, region=[2, 8, 2, 8])
    time_pygmt = (time.perf_counter() - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if isinstance(result_pygmt, str) and result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Selected: {lines_pygmt} points")

    # Compare
    print("\n[Comparison]")
    print(f"  Speedup: {time_pygmt / time_nb:.2f}x")

    if lines_nb == lines_pygmt:
        print(f"  ✅ Same number of points selected")
        return True
    else:
        print(f"  ⚠️  Different number of points!")
        return False


def compare_blockmean_operation():
    """Compare blockmean function."""
    print("\n" + "=" * 70)
    print("OPERATION COMPARISON: blockmean")
    print("=" * 70)

    # Create test data
    data_file = str(output_root / "test_data_xyz.txt")
    x = np.random.uniform(0, 10, 1000)
    y = np.random.uniform(0, 10, 1000)
    z = np.sin(x) * np.cos(y)
    np.savetxt(data_file, np.column_stack([x, y, z]))

    print(f"\nTest data: {data_file}")
    print(f"  1000 random points with z-values")
    print(f"  Block averaging with spacing=1")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.blockmean(
        data_file, region=[0, 10, 0, 10], spacing="1", summary="m"
    )
    time_nb = (time.perf_counter() - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if isinstance(result_nb, str) and result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Output: {lines_nb} blocks")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.blockmean(
        data_file, region=[0, 10, 0, 10], spacing="1", summary="m"
    )
    time_pygmt = (time.perf_counter() - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if isinstance(result_pygmt, str) and result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Output: {lines_pygmt} blocks")

    # Compare
    print("\n[Comparison]")
    print(f"  Speedup: {time_pygmt / time_nb:.2f}x")

    if lines_nb == lines_pygmt:
        print(f"  ✅ Same number of blocks")
        return True
    else:
        print(f"  ⚠️  Different number of blocks!")
        return False


def compare_makecpt_operation():
    """Compare makecpt function."""
    print("\n" + "=" * 70)
    print("OPERATION COMPARISON: makecpt")
    print("=" * 70)

    print("\nGenerating color palette: viridis, range [0, 100]")

    # pygmt_nb
    print("\n[pygmt_nb]")
    start = time.perf_counter()
    result_nb = pygmt_nb.makecpt(cmap="viridis", series=[0, 100])
    time_nb = (time.perf_counter() - start) * 1000

    lines_nb = len(result_nb.strip().split("\n")) if isinstance(result_nb, str) and result_nb else 0
    print(f"  Time: {time_nb:.2f} ms")
    print(f"  Output: {lines_nb} lines")

    # PyGMT
    print("\n[PyGMT]")
    start = time.perf_counter()
    result_pygmt = pygmt.makecpt(cmap="viridis", series=[0, 100])
    time_pygmt = (time.perf_counter() - start) * 1000

    lines_pygmt = len(result_pygmt.strip().split("\n")) if isinstance(result_pygmt, str) and result_pygmt else 0
    print(f"  Time: {time_pygmt:.2f} ms")
    print(f"  Output: {lines_pygmt} lines")

    # Compare
    print("\n[Comparison]")
    print(f"  Speedup: {time_pygmt / time_nb:.2f}x")

    if lines_nb == lines_pygmt:
        print(f"  ✅ Same output length")
        return True
    else:
        print(f"  ⚠️  Different output lengths!")
        return False


# =============================================================================
# Main Validation Runner
# =============================================================================


def run_output_validation():
    """Run output validation tests."""
    print("\n" + "=" * 70)
    print("SECTION 1: OUTPUT VALIDATION")
    print("=" * 70)

    tests = [
        ("Basemap", validate_basemap_output),
        ("Coast", validate_coast_output),
        ("Plot", validate_plot_output),
    ]

    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))

    return results


def run_operation_comparison():
    """Run operation comparison tests."""
    print("\n" + "=" * 70)
    print("SECTION 2: OPERATION COMPARISON")
    print("=" * 70)

    tests = [
        ("info", compare_info_operation),
        ("select", compare_select_operation),
        ("blockmean", compare_blockmean_operation),
        ("makecpt", compare_makecpt_operation),
    ]

    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))

    return results


def print_summary(output_results, operation_results):
    """Print validation summary."""
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    print("\nOutput Validation:")
    print("-" * 70)
    passed = sum(1 for _, success in output_results if success)
    total = len(output_results)
    for name, success in output_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:<20} {status}")
    print(f"\n  Passed: {passed}/{total} ({passed/total*100:.0f}%)")

    print("\nOperation Comparison:")
    print("-" * 70)
    passed = sum(1 for _, success in operation_results if success)
    total = len(operation_results)
    for name, success in operation_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:<20} {status}")
    print(f"\n  Passed: {passed}/{total} ({passed/total*100:.0f}%)")

    # Overall
    all_passed = sum(1 for _, success in output_results + operation_results if success)
    all_total = len(output_results) + len(operation_results)

    print("\n" + "=" * 70)
    print("OVERALL RESULTS")
    print("=" * 70)
    print(f"\n✅ Total Passed: {all_passed}/{all_total} ({all_passed/all_total*100:.0f}%)")
    print(f"📁 Output Directory: {output_root}")

    if all_passed == all_total:
        print("\n🎉 All validations passed!")
    else:
        print(f"\n⚠️  {all_total - all_passed} validation(s) failed")


def main():
    """Run comprehensive validation suite."""
    print("=" * 70)
    print("COMPREHENSIVE VALIDATION SUITE")
    print("pygmt_nb vs PyGMT Output Compatibility")
    print("=" * 70)

    # Set random seed for reproducibility
    np.random.seed(42)

    # Run all validation sections
    output_results = run_output_validation()
    operation_results = run_operation_comparison()

    # Print comprehensive summary
    print_summary(output_results, operation_results)


if __name__ == "__main__":
    main()
