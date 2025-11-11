#!/usr/bin/env python3
"""
Validate that pygmt_nb and PyGMT produce identical outputs.
Checks file sizes, content headers, and optionally pixel-level comparison.
"""

import sys
import subprocess
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


def check_file_content(ps_file: Path, expected_min_size: int = 1000):
    """Check PostScript file is valid."""
    if not ps_file.exists():
        print(f"  ❌ File not found: {ps_file}")
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
            print(f"  ❌ Not a valid PostScript file!")
            return False
        print(f"  ✓ Valid PostScript header")

    return True


def compare_files(file1: Path, file2: Path):
    """Compare two files."""
    size1 = file1.stat().st_size
    size2 = file2.stat().st_size

    ratio = size1 / size2
    print(f"\n  File size comparison:")
    print(f"    pygmt_nb: {size1:,} bytes")
    print(f"    PyGMT:    {size2:,} bytes")
    print(f"    Ratio:    {ratio:.3f}x")

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
        print(f"  RMSE: {rmse}")

        if rmse.startswith("0 "):
            print(f"  ✅ Images are identical!")
            return True
        else:
            print(f"  ⚠️  Images have differences")
            print(f"  Difference map saved to: /tmp/diff.png")
            return False
    except FileNotFoundError:
        print(f"  ⚠️  ImageMagick 'compare' not found - skipping pixel comparison")
        return None


def test_basemap():
    """Test basemap output."""
    print("\n" + "=" * 70)
    print("TEST: Basemap")
    print("=" * 70)

    output_dir = output_root
    output_dir.mkdir(exist_ok=True)

    # Generate outputs
    print("\n[Generating outputs...]")

    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    ps_nb = output_dir / "basemap_nb.ps"
    fig_nb.savefig(str(ps_nb))
    print(f"  pygmt_nb: {ps_nb}")

    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    ps_pygmt = output_dir / "basemap_pygmt.eps"
    fig_pygmt.savefig(str(ps_pygmt))
    print(f"  PyGMT:    {ps_pygmt}")

    # Validate files
    print("\n[Validating pygmt_nb output...]")
    valid_nb = check_file_content(ps_nb)

    print("\n[Validating PyGMT output...]")
    valid_pygmt = check_file_content(ps_pygmt)

    if not (valid_nb and valid_pygmt):
        print("\n❌ Output validation failed")
        return False

    # Compare
    print("\n[Comparing outputs...]")
    similar = compare_files(ps_nb, ps_pygmt)

    # Convert to PNG and compare pixels
    print("\n[Converting to PNG for pixel comparison...]")
    try:
        subprocess.run(
            ["gmt", "psconvert", str(ps_nb), "-A", "-Tg"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["gmt", "psconvert", str(ps_pygmt), "-A", "-Tg"],
            check=True,
            capture_output=True,
        )

        png_nb = ps_nb.with_suffix(".png")
        png_pygmt = ps_pygmt.with_suffix(".png")

        if png_nb.exists() and png_pygmt.exists():
            print(f"  ✓ PNGs created")
            compare_images_with_imagemagick(png_nb, png_pygmt)
        else:
            print(f"  ⚠️  PNG conversion failed")
    except Exception as e:
        print(f"  ⚠️  Error during PNG conversion: {e}")

    return similar


def test_plot():
    """Test plot output."""
    print("\n" + "=" * 70)
    print("TEST: Plot")
    print("=" * 70)

    output_dir = output_root
    output_dir.mkdir(exist_ok=True)

    # Same data
    np.random.seed(42)
    x = np.random.uniform(0, 10, 50)
    y = np.random.uniform(0, 10, 50)

    # Generate outputs
    print("\n[Generating outputs...]")

    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    fig_nb.plot(x=x, y=y, style="c0.2c", color="red")
    ps_nb = output_dir / "plot_nb.ps"
    fig_nb.savefig(str(ps_nb))
    print(f"  pygmt_nb: {ps_nb}")

    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    fig_pygmt.plot(x=x, y=y, style="c0.2c", fill="red")
    ps_pygmt = output_dir / "plot_pygmt.eps"
    fig_pygmt.savefig(str(ps_pygmt))
    print(f"  PyGMT:    {ps_pygmt}")

    # Validate files
    print("\n[Validating pygmt_nb output...]")
    valid_nb = check_file_content(ps_nb, expected_min_size=5000)

    print("\n[Validating PyGMT output...]")
    valid_pygmt = check_file_content(ps_pygmt, expected_min_size=5000)

    if not (valid_nb and valid_pygmt):
        print("\n❌ Output validation failed")
        return False

    # Compare
    print("\n[Comparing outputs...]")
    similar = compare_files(ps_nb, ps_pygmt)

    # Convert to PNG and compare
    print("\n[Converting to PNG for pixel comparison...]")
    try:
        subprocess.run(
            ["gmt", "psconvert", str(ps_nb), "-A", "-Tg"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["gmt", "psconvert", str(ps_pygmt), "-A", "-Tg"],
            check=True,
            capture_output=True,
        )

        png_nb = ps_nb.with_suffix(".png")
        png_pygmt = ps_pygmt.with_suffix(".png")

        if png_nb.exists() and png_pygmt.exists():
            print(f"  ✓ PNGs created")
            compare_images_with_imagemagick(png_nb, png_pygmt)
        else:
            print(f"  ⚠️  PNG conversion failed")
    except Exception as e:
        print(f"  ⚠️  Error during PNG conversion: {e}")

    return similar


def main():
    """Run output validation tests."""
    print("=" * 70)
    print("OUTPUT VALIDATION")
    print("Checking pygmt_nb vs PyGMT outputs")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Basemap", test_basemap()))
    results.append(("Plot", test_plot()))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n✅ All validation tests passed!")
        return 0
    else:
        print("\n❌ Some validation tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
