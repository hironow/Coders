"""
Test Figure.basemap.

Based on PyGMT's test_basemap.py, adapted for pygmt_nb.
"""

import os
import tempfile
import unittest
from pathlib import Path


class TestBasemap(unittest.TestCase):
    """Test Figure.basemap() method for drawing map frames."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_basemap_simple(self) -> None:
        """Create a simple basemap plot."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(region=[10, 70, -3, 8], projection="X8c/6c", frame="afg")

        output_file = Path(self.temp_dir) / "basemap_simple.ps"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists()
        # File should not be empty
        assert output_file.stat().st_size > 0

        # Verify it's a valid PostScript
        with open(output_file, "rb") as f:
            header = f.read(4)
            assert header == b"%!PS"

    def test_basemap_loglog(self) -> None:
        """Create a loglog basemap plot."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(
            region=[1, 10000, 1e20, 1e25],
            projection="X16cl/12cl",
            frame=["WS", "x2+lWavelength", "ya1pf3+lPower"],
        )

        output_file = Path(self.temp_dir) / "basemap_loglog.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_basemap_power_axis(self) -> None:
        """Create a power axis basemap plot."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(
            region=[0, 100, 0, 5000],
            projection="x1p0.5/-0.001",
            frame=["x1p+lCrustal age", "y500+lDepth"],
        )

        output_file = Path(self.temp_dir) / "basemap_power.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_basemap_polar(self) -> None:
        """Create a polar basemap plot."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(region=[0, 360, 0, 1000], projection="P8c", frame="afg")

        output_file = Path(self.temp_dir) / "basemap_polar.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_basemap_winkel_tripel(self) -> None:
        """Create a Winkel Tripel basemap plot."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(region=[90, 450, -90, 90], projection="R270/20c", frame="afg")

        output_file = Path(self.temp_dir) / "basemap_winkel.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_basemap_frame_sequence_true(self) -> None:
        """Test that passing a sequence with True works."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=[True, "WSen"])

        output_file = Path(self.temp_dir) / "basemap_frame_seq.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_basemap_region_required(self) -> None:
        """Test that region is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.basemap(projection="X10c")

    def test_basemap_projection_required(self) -> None:
        """Test that projection is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.basemap(region=[0, 10, 0, 10])

    def test_basemap_frame_default(self) -> None:
        """Test basemap with default frame (minimal frame)."""
        from pygmt_nb import Figure

        fig = Figure()
        # Should not raise an exception with minimal frame
        fig.basemap(region=[0, 10, 0, 10], projection="X10c")

        output_file = Path(self.temp_dir) / "basemap_frame_default.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


if __name__ == "__main__":
    unittest.main()
