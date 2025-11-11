#!/usr/bin/env python3
"""
Visual comparison of PyGMT vs pygmt_nb outputs.
Convert PostScript to PNG and compare pixel-by-pixel.
"""

import sys
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

# Add pygmt_nb to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

try:
    import pygmt
    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False
    print("PyGMT not available")
    sys.exit(1)

import pygmt_nb


def convert_ps_to_png(ps_file: Path, png_file: Path, dpi: int = 150):
    """Convert PostScript to PNG using GMT's psconvert."""
    try:
        # Use GMT's psconvert
        cmd = [
            "gmt", "psconvert",
            str(ps_file),
            "-A",  # Adjust BoundingBox
            "-P",  # Portrait mode
            "-E" + str(dpi),  # Resolution
            "-Tg",  # PNG format
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # psconvert creates filename.png, rename it
        auto_png = ps_file.with_suffix('.png')
        if auto_png.exists():
            auto_png.rename(png_file)
            return True
        return False
    except Exception as e:
        print(f"Error converting {ps_file}: {e}")
        return False


def compare_images(img1_path: Path, img2_path: Path):
    """Compare two images pixel by pixel."""
    try:
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')

        # Check dimensions
        if img1.size != img2.size:
            print(f"  ⚠️  Image sizes differ: {img1.size} vs {img2.size}")
            # Resize to compare
            min_width = min(img1.size[0], img2.size[0])
            min_height = min(img1.size[1], img2.size[1])
            img1 = img1.crop((0, 0, min_width, min_height))
            img2 = img2.crop((0, 0, min_width, min_height))

        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Calculate differences
        diff = np.abs(arr1.astype(float) - arr2.astype(float))
        max_diff = diff.max()
        mean_diff = diff.mean()

        # Count different pixels
        pixel_diff = (diff.sum(axis=2) > 0).sum()
        total_pixels = arr1.shape[0] * arr1.shape[1]
        similarity = 100 * (1 - pixel_diff / total_pixels)

        print(f"  Size: {img1.size}")
        print(f"  Max pixel difference: {max_diff:.2f} / 255")
        print(f"  Mean pixel difference: {mean_diff:.4f} / 255")
        print(f"  Different pixels: {pixel_diff:,} / {total_pixels:,}")
        print(f"  Similarity: {similarity:.2f}%")

        # Create difference image
        diff_img = Image.fromarray(diff.mean(axis=2).astype(np.uint8))
        return similarity, diff_img

    except Exception as e:
        print(f"  ❌ Error comparing images: {e}")
        return None, None


def test_visual_comparison():
    """Compare visual outputs."""
    print("=" * 70)
    print("VISUAL COMPARISON TEST")
    print("=" * 70)

    output_dir = Path("/tmp/validation_test")
    output_dir.mkdir(exist_ok=True)

    # Create test outputs
    print("\n[Creating test basemap outputs...]")

    # pygmt_nb
    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    ps_nb = output_dir / "visual_basemap_nb.ps"
    fig_nb.savefig(str(ps_nb))
    print(f"  ✓ pygmt_nb: {ps_nb}")

    # PyGMT
    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    ps_pygmt = output_dir / "visual_basemap_pygmt.eps"
    fig_pygmt.savefig(str(ps_pygmt))
    print(f"  ✓ PyGMT: {ps_pygmt}")

    # Convert to PNG
    print("\n[Converting to PNG...]")
    png_nb = output_dir / "visual_basemap_nb.png"
    png_pygmt = output_dir / "visual_basemap_pygmt.png"

    if convert_ps_to_png(ps_nb, png_nb):
        print(f"  ✓ pygmt_nb PNG: {png_nb}")
    else:
        print(f"  ❌ Failed to convert pygmt_nb")
        return

    if convert_ps_to_png(ps_pygmt, png_pygmt):
        print(f"  ✓ PyGMT PNG: {png_pygmt}")
    else:
        print(f"  ❌ Failed to convert PyGMT")
        return

    # Compare
    print("\n[Comparing images...]")
    similarity, diff_img = compare_images(png_nb, png_pygmt)

    if similarity is not None:
        if similarity > 99.9:
            print(f"\n  ✅ Images are nearly identical!")
        elif similarity > 95:
            print(f"\n  ✓ Images are very similar")
        elif similarity > 90:
            print(f"\n  ⚠️  Images have some differences")
        else:
            print(f"\n  ❌ Images are significantly different!")

        if diff_img:
            diff_path = output_dir / "difference.png"
            diff_img.save(diff_path)
            print(f"  Difference map saved to: {diff_path}")

    print(f"\n  Visual comparison files saved to: {output_dir}")


def test_plot_visual_comparison():
    """Compare visual outputs for plot."""
    print("\n" + "=" * 70)
    print("PLOT VISUAL COMPARISON TEST")
    print("=" * 70)

    output_dir = Path("/tmp/validation_test")
    output_dir.mkdir(exist_ok=True)

    # Same data for both
    np.random.seed(42)
    x = np.random.uniform(0, 10, 50)
    y = np.random.uniform(0, 10, 50)

    print("\n[Creating test plot outputs...]")

    # pygmt_nb
    fig_nb = pygmt_nb.Figure()
    fig_nb.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    fig_nb.plot(x=x, y=y, style="c0.2c", color="red", pen="0.5p,black")
    ps_nb = output_dir / "visual_plot_nb.ps"
    fig_nb.savefig(str(ps_nb))
    print(f"  ✓ pygmt_nb: {ps_nb}")

    # PyGMT
    fig_pygmt = pygmt.Figure()
    fig_pygmt.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
    fig_pygmt.plot(x=x, y=y, style="c0.2c", fill="red", pen="0.5p,black")
    ps_pygmt = output_dir / "visual_plot_pygmt.eps"
    fig_pygmt.savefig(str(ps_pygmt))
    print(f"  ✓ PyGMT: {ps_pygmt}")

    # Convert to PNG
    print("\n[Converting to PNG...]")
    png_nb = output_dir / "visual_plot_nb.png"
    png_pygmt = output_dir / "visual_plot_pygmt.png"

    if convert_ps_to_png(ps_nb, png_nb):
        print(f"  ✓ pygmt_nb PNG: {png_nb}")
    else:
        print(f"  ❌ Failed to convert pygmt_nb")
        return

    if convert_ps_to_png(ps_pygmt, png_pygmt):
        print(f"  ✓ PyGMT PNG: {png_pygmt}")
    else:
        print(f"  ❌ Failed to convert PyGMT")
        return

    # Compare
    print("\n[Comparing images...]")
    similarity, diff_img = compare_images(png_nb, png_pygmt)

    if similarity is not None:
        if similarity > 99.9:
            print(f"\n  ✅ Images are nearly identical!")
        elif similarity > 95:
            print(f"\n  ✓ Images are very similar")
        elif similarity > 90:
            print(f"\n  ⚠️  Images have some differences")
        else:
            print(f"\n  ❌ Images are significantly different!")

        if diff_img:
            diff_path = output_dir / "plot_difference.png"
            diff_img.save(diff_path)
            print(f"  Difference map saved to: {diff_path}")


def main():
    """Run visual comparison tests."""
    test_visual_comparison()
    test_plot_visual_comparison()

    print("\n" + "=" * 70)
    print("VISUAL COMPARISON COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
