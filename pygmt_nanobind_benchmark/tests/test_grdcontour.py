"""
Tests for Figure.grdcontour() method.

Following TDD (Test-Driven Development) principles:
1. Write failing tests first (Red)
2. Implement minimum code to pass (Green)
3. Refactor while keeping tests green
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pygmt_nb import Figure


class TestGrdcontour(unittest.TestCase):
    """Test Figure.grdcontour() method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_grid = Path(__file__).parent / "data" / "test_grid.nc"
        self.region = [0, 10, 0, 10]
        self.projection = "X10c"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_figure_has_grdcontour_method(self) -> None:
        """Test that Figure has grdcontour method."""
        fig = Figure()
        assert hasattr(fig, "grdcontour")
        assert callable(fig.grdcontour)

    def test_grdcontour_simple(self) -> None:
        """Create simple contours from grid."""
        fig = Figure()
        fig.grdcontour(
            grid=str(self.test_grid), region=self.region, projection=self.projection, frame="afg"
        )

        output = Path(self.temp_dir) / "grdcontour_simple.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_with_interval(self) -> None:
        """Create contours with specific interval."""
        fig = Figure()
        fig.grdcontour(
            grid=str(self.test_grid),
            region=self.region,
            projection=self.projection,
            interval=100,  # Contour every 100 units
            frame="afg",
        )

        output = Path(self.temp_dir) / "grdcontour_interval.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_with_annotation(self) -> None:
        """Create annotated contours."""
        fig = Figure()
        fig.grdcontour(
            grid=str(self.test_grid),
            region=self.region,
            projection=self.projection,
            interval=100,
            annotation=500,  # Annotate every 500 units
            frame="afg",
        )

        output = Path(self.temp_dir) / "grdcontour_annotation.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_with_pen(self) -> None:
        """Create contours with custom pen."""
        fig = Figure()
        fig.grdcontour(
            grid=str(self.test_grid),
            region=self.region,
            projection=self.projection,
            interval=100,
            pen="0.5p,blue",  # Blue thin lines
            frame="afg",
        )

        output = Path(self.temp_dir) / "grdcontour_pen.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_with_limit(self) -> None:
        """Create contours within specific range."""
        fig = Figure()
        fig.grdcontour(
            grid=str(self.test_grid),
            region=self.region,
            projection=self.projection,
            interval=100,
            limit=[-1000, 1000],  # Only contours between -1000 and 1000
            frame="afg",
        )

        output = Path(self.temp_dir) / "grdcontour_limit.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_after_basemap(self) -> None:
        """Create contours after basemap."""
        fig = Figure()
        fig.basemap(region=self.region, projection=self.projection, frame="afg")
        fig.grdcontour(
            grid=str(self.test_grid), region=self.region, projection=self.projection, interval=100
        )

        output = Path(self.temp_dir) / "grdcontour_with_basemap.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0

    def test_grdcontour_with_grdimage(self) -> None:
        """Create contours overlaid on grid image."""
        fig = Figure()
        fig.basemap(region=self.region, projection=self.projection, frame="afg")
        fig.grdimage(grid=str(self.test_grid), cmap="viridis")
        fig.grdcontour(
            grid=str(self.test_grid),
            region=self.region,
            projection=self.projection,
            interval=200,
            pen="0.5p,white",  # White contours on colored background
        )

        output = Path(self.temp_dir) / "grdcontour_overlay.ps"
        fig.savefig(str(output))

        assert output.exists()
        assert output.stat().st_size > 0


if __name__ == "__main__":
    unittest.main()
