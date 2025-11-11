#!/usr/bin/env python3
"""
Pixel-Identical Validation for pygmt_nb vs PyGMT

This script validates that pygmt_nb produces pixel-identical (or nearly identical)
outputs compared to PyGMT for the same code.

Validation process:
1. Generate plots using PyGMT (EPS format)
2. Generate identical plots using pygmt_nb (PS format)
3. Convert both to PNG using ImageMagick (if available) or Ghostscript
4. Compare pixels using PIL/Pillow
5. Report differences with tolerance for minor antialiasing variations
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

# Add pygmt_nb to path (dynamically resolve project root)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

try:
    import pygmt

    PYGMT_AVAILABLE = True
    print("✓ PyGMT available")
except ImportError:
    PYGMT_AVAILABLE = False
    print("✗ PyGMT not available - cannot perform pixel comparison")
    sys.exit(1)

try:
    from PIL import Image

    PIL_AVAILABLE = True
    print("✓ PIL/Pillow available")
except ImportError:
    PIL_AVAILABLE = False
    print("✗ PIL/Pillow not available - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True)
    from PIL import Image

    PIL_AVAILABLE = True

import pygmt_nb


class PixelComparisonTest:
    """Base class for pixel-identical validation tests."""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.temp_dir = Path(tempfile.mkdtemp())

        # Output files
        self.pygmt_eps = self.temp_dir / "pygmt_output.eps"
        self.pygmt_png = self.temp_dir / "pygmt_output.png"
        self.pygmt_nb_ps = self.temp_dir / "pygmt_nb_output.ps"
        self.pygmt_nb_png = self.temp_dir / "pygmt_nb_output.png"
        self.diff_png = self.temp_dir / "diff.png"

        # Check for conversion tools
        self.gs_available = shutil.which("gs") is not None
        self.convert_available = shutil.which("convert") is not None

    def run_pygmt(self):
        """Run with PyGMT - to be overridden."""
        raise NotImplementedError

    def run_pygmt_nb(self):
        """Run with pygmt_nb - to be overridden."""
        raise NotImplementedError

    def convert_to_png(self, input_file, output_file, format_type="eps"):
        """
        Convert PS/EPS to PNG using Ghostscript.

        Args:
            input_file: Path to PS/EPS file
            output_file: Path to output PNG
            format_type: "eps" or "ps"
        """
        if not self.gs_available:
            raise RuntimeError(
                "Ghostscript (gs) not found. Please install: brew install ghostscript"
            )

        # Ensure input file exists
        if not Path(input_file).exists():
            print(f"  ✗ Input file not found: {input_file}")
            return False

        # Use Ghostscript for conversion with consistent DPI
        cmd = [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-dQUIET",  # Suppress info messages
            "-sDEVICE=png16m",
            "-r150",  # DPI (resolution)
            "-dGraphicsAlphaBits=4",  # Anti-aliasing
            "-dTextAlphaBits=4",
            f"-sOutputFile={output_file}",
            str(input_file),
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            # Verify output file was created
            if not Path(output_file).exists():
                # Check for numbered output (e.g., output-1.png)
                output_numbered = Path(str(output_file).replace(".png", "-1.png"))
                if output_numbered.exists():
                    output_numbered.rename(output_file)
                else:
                    print(f"  ✗ Output file not created: {output_file}")
                    print(f"     Stderr: {result.stderr}")
                    return False
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Conversion failed: {e.stderr}")
            return False

    def compare_images(self, img1_path, img2_path, tolerance=5):
        """
        Compare two PNG images pixel-by-pixel.

        Args:
            img1_path: Path to first image (PyGMT)
            img2_path: Path to second image (pygmt_nb)
            tolerance: Maximum allowed pixel difference (0-255)

        Returns:
            dict: Comparison results with metrics
        """
        img1 = Image.open(img1_path).convert("RGB")
        img2 = Image.open(img2_path).convert("RGB")

        # Check dimensions
        if img1.size != img2.size:
            return {
                "identical": False,
                "reason": f"Size mismatch: {img1.size} vs {img2.size}",
                "pixel_diff_pct": 100.0,
            }

        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Compute pixel differences
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        max_diff = diff.max()

        # Count pixels exceeding tolerance
        pixels_different = (diff > tolerance).sum()
        total_pixels = diff.size
        diff_pct = (pixels_different / total_pixels) * 100

        # Create difference visualization
        diff_img = Image.fromarray(np.uint8(diff * 10))  # Amplify differences for visibility
        diff_img.save(self.diff_png)

        # Determine if images are identical within tolerance
        identical = diff_pct < 0.01  # Less than 0.01% different pixels

        return {
            "identical": identical,
            "max_diff": max_diff,
            "pixel_diff_pct": diff_pct,
            "pixels_different": pixels_different,
            "total_pixels": total_pixels,
            "tolerance": tolerance,
            "diff_image": str(self.diff_png),
        }

    def validate(self):
        """Run pixel-identical validation."""
        print(f"\n{'=' * 70}")
        print(f"Pixel Validation: {self.name}")
        print(f"Description: {self.description}")
        print(f"{'=' * 70}")

        results = {
            "name": self.name,
            "description": self.description,
            "pygmt_success": False,
            "pygmt_nb_success": False,
            "conversion_success": False,
            "comparison": None,
            "pixel_identical": False,
        }

        # Step 1: Run PyGMT
        print("\n[1/5] Running PyGMT...")
        try:
            self.run_pygmt()
            if self.pygmt_eps.exists():
                results["pygmt_success"] = True
                print(
                    f"  ✓ Generated: {self.pygmt_eps.name} ({self.pygmt_eps.stat().st_size} bytes)"
                )
            else:
                print("  ✗ Output file not created")
                return results
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return results

        # Step 2: Run pygmt_nb
        print("\n[2/5] Running pygmt_nb...")
        try:
            self.run_pygmt_nb()
            if self.pygmt_nb_ps.exists():
                results["pygmt_nb_success"] = True
                print(
                    f"  ✓ Generated: {self.pygmt_nb_ps.name} ({self.pygmt_nb_ps.stat().st_size} bytes)"
                )
            else:
                print("  ✗ Output file not created")
                return results
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return results

        # Step 3: Convert to PNG
        print("\n[3/5] Converting to PNG...")
        try:
            if self.convert_to_png(self.pygmt_eps, self.pygmt_png, "eps"):
                print(f"  ✓ PyGMT → PNG: {self.pygmt_png.name}")
            else:
                print("  ✗ PyGMT conversion failed")
                return results

            if self.convert_to_png(self.pygmt_nb_ps, self.pygmt_nb_png, "ps"):
                print(f"  ✓ pygmt_nb → PNG: {self.pygmt_nb_png.name}")
                results["conversion_success"] = True
            else:
                print("  ✗ pygmt_nb conversion failed")
                return results
        except Exception as e:
            print(f"  ✗ Conversion error: {e}")
            return results

        # Step 4: Compare pixels
        print("\n[4/5] Comparing pixels...")
        try:
            comparison = self.compare_images(self.pygmt_png, self.pygmt_nb_png, tolerance=5)
            results["comparison"] = comparison
            results["pixel_identical"] = comparison["identical"]

            print(f"  Max pixel difference: {comparison['max_diff']}")
            print(f"  Different pixels: {comparison['pixel_diff_pct']:.4f}%")
            print(f"  Tolerance: {comparison['tolerance']}")

            if comparison["identical"]:
                print("  ✅ PIXEL-IDENTICAL (within tolerance)")
            else:
                print("  ⚠️  DIFFERENCES DETECTED")
                print(f"     Diff image saved: {comparison['diff_image']}")
        except Exception as e:
            print(f"  ✗ Comparison error: {e}")
            return results

        # Step 5: Summary
        print("\n[5/5] Summary")
        if results["pixel_identical"]:
            print("  ✅ PASS: Outputs are pixel-identical")
        else:
            print(f"  ⚠️  PARTIAL: Outputs differ by {comparison['pixel_diff_pct']:.4f}%")

        return results


# =============================================================================
# Test Cases
# =============================================================================


class SimpleBasemapTest(PixelComparisonTest):
    """Test basic basemap rendering."""

    def __init__(self):
        super().__init__("Simple Basemap", "Basic Cartesian frame with annotations")

    def run_pygmt(self):
        fig = pygmt.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.savefig(str(self.pygmt_eps))

    def run_pygmt_nb(self):
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.savefig(str(self.pygmt_nb_ps))


class CoastlineMapTest(PixelComparisonTest):
    """Test coastline rendering."""

    def __init__(self):
        super().__init__("Coastline Map", "Regional map with land/water and shorelines")

    def run_pygmt(self):
        fig = pygmt.Figure()
        fig.basemap(region=[130, 150, 30, 45], projection="M10c", frame=True)
        fig.coast(land="tan", water="lightblue", shorelines="thin")
        fig.savefig(str(self.pygmt_eps))

    def run_pygmt_nb(self):
        fig = pygmt_nb.Figure()
        fig.basemap(region=[130, 150, 30, 45], projection="M10c", frame=True)
        fig.coast(land="tan", water="lightblue", shorelines="thin")
        fig.savefig(str(self.pygmt_nb_ps))


class DataPlotTest(PixelComparisonTest):
    """Test data plotting."""

    def __init__(self):
        super().__init__("Data Plot", "Scatter plot with colored circles")
        self.x = [2, 4, 6, 8]
        self.y = [3, 5, 4, 7]

    def run_pygmt(self):
        fig = pygmt.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.plot(x=self.x, y=self.y, style="c0.3c", fill="red", pen="1p,black")
        fig.savefig(str(self.pygmt_eps))

    def run_pygmt_nb(self):
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.plot(x=self.x, y=self.y, style="c0.3c", color="red", pen="1p,black")
        fig.savefig(str(self.pygmt_nb_ps))


class TextAnnotationTest(PixelComparisonTest):
    """Test text annotations."""

    def __init__(self):
        super().__init__("Text Annotations", "Map with text labels")

    def run_pygmt(self):
        fig = pygmt.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.text(x=5, y=5, text="Center", font="12p,Helvetica,black")
        fig.savefig(str(self.pygmt_eps))

    def run_pygmt_nb(self):
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.text(x=5, y=5, text="Center", font="12p,Helvetica,black")
        fig.savefig(str(self.pygmt_nb_ps))


# =============================================================================
# Main Execution
# =============================================================================


def main():
    """Run pixel-identical validation suite."""
    print("=" * 70)
    print("PIXEL-IDENTICAL VALIDATION SUITE")
    print("Comparing pygmt_nb vs PyGMT outputs")
    print("=" * 70)

    # Check prerequisites
    print("\nPrerequisites:")
    print(f"  PyGMT: {'✓' if PYGMT_AVAILABLE else '✗'}")
    print(f"  PIL/Pillow: {'✓' if PIL_AVAILABLE else '✗'}")
    print(f"  Ghostscript: {'✓' if shutil.which('gs') else '✗'}")

    if not PYGMT_AVAILABLE:
        print("\n✗ PyGMT not available - cannot run pixel comparison")
        return

    if not shutil.which("gs"):
        print("\n✗ Ghostscript not available - installing...")
        print("  Run: brew install ghostscript")
        return

    # Define test suite
    tests = [
        SimpleBasemapTest(),
        CoastlineMapTest(),
        DataPlotTest(),
        TextAnnotationTest(),
    ]

    # Run all tests
    all_results = []
    for test in tests:
        results = test.validate()
        all_results.append(results)

    # Summary
    print("\n" + "=" * 70)
    print("PIXEL-IDENTICAL VALIDATION SUMMARY")
    print("=" * 70)
    print(f"\n{'Test':<30} {'Status':<15} {'Diff %'}")
    print("-" * 70)

    total_tests = len(all_results)
    passed = 0

    for result in all_results:
        name = result["name"]
        if result.get("pixel_identical"):
            status = "✅ IDENTICAL"
            passed += 1
        elif result.get("comparison"):
            status = "⚠️  DIFFERENT"
        else:
            status = "❌ FAILED"

        comparison = result.get("comparison")
        if comparison and isinstance(comparison, dict):
            diff_pct = comparison.get("pixel_diff_pct", 0)
        else:
            diff_pct = 0
        print(f"{name:<30} {status:<15} {diff_pct:.4f}%")

    print("-" * 70)
    print(f"\nTotal Tests: {total_tests}")
    print(f"Pixel-Identical: {passed}")
    print(f"Success Rate: {(passed / total_tests) * 100:.1f}%")

    if passed == total_tests:
        print("\n🎉 ALL TESTS PASSED - PIXEL-IDENTICAL VALIDATION COMPLETE ✅")
    else:
        print(f"\n⚠️  {total_tests - passed} test(s) with pixel differences")
        print("   Note: Minor differences may be due to:")
        print("   - Antialiasing variations")
        print("   - Font rendering differences")
        print("   - Color space conversions (PS vs EPS)")


if __name__ == "__main__":
    main()
