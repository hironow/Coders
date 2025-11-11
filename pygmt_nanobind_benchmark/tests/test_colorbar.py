"""
Tests for Figure.colorbar() method.

Following TDD (Test-Driven Development) principles:
1. Write failing tests first (Red)
2. Implement minimum code to pass (Green)
3. Refactor while keeping tests green
"""

import unittest
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygmt_nb import Figure


class TestColorbar(unittest.TestCase):
    """Test Figure.colorbar() method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_grid = Path(__file__).parent / "data" / "test_grid.nc"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_figure_has_colorbar_method(self) -> None:
        """Test that Figure has colorbar method."""
        fig = Figure()
        assert hasattr(fig, 'colorbar')
        assert callable(fig.colorbar)

    def test_colorbar_simple(self) -> None:
        """Create a simple colorbar."""
        fig = Figure()
        # Need to create an image first (colorbar shows the color scale)
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        fig.colorbar()

        # Save to verify it works
        output = Path(self.temp_dir) / "colorbar_simple.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_with_frame(self) -> None:
        """Create a colorbar with frame annotations."""
        fig = Figure()
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        fig.colorbar(frame="af")

        output = Path(self.temp_dir) / "colorbar_frame.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_with_position(self) -> None:
        """Create a colorbar with custom position."""
        fig = Figure()
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        # Position: x/y+w+h+j
        # 5c/1c = 5cm from left, 1cm from bottom, +w8c = width 8cm, +h = horizontal, +jBC = justify bottom center
        fig.colorbar(position="5c/1c+w8c+h+jBC")

        output = Path(self.temp_dir) / "colorbar_position.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_horizontal(self) -> None:
        """Create a horizontal colorbar."""
        fig = Figure()
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        # Horizontal colorbar at bottom center
        fig.colorbar(position="5c/1c+w10c+h+jBC")

        output = Path(self.temp_dir) / "colorbar_horizontal.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_with_label(self) -> None:
        """Create a colorbar with label."""
        fig = Figure()
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        fig.colorbar(frame=["af", "x+lElevation", "y+lm"])

        output = Path(self.temp_dir) / "colorbar_label.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_after_basemap(self) -> None:
        """Create a colorbar after basemap and grdimage."""
        fig = Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        fig.grdimage(grid=str(self.test_grid), cmap="geo")
        # Vertical colorbar on right side: 13cm from left, 5cm from bottom, 4cm wide
        fig.colorbar(position="13c/5c+w4c+jML")

        output = Path(self.temp_dir) / "colorbar_with_basemap.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_colorbar_vertical(self) -> None:
        """Create a vertical colorbar."""
        fig = Figure()
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        # Vertical colorbar on right side: 13cm from left, 5cm from bottom, 4cm wide
        fig.colorbar(position="13c/5c+w4c+jML")

        output = Path(self.temp_dir) / "colorbar_vertical.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0


if __name__ == '__main__':
    unittest.main()
