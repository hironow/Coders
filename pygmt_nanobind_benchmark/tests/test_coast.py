"""
Test Figure.coast.

Based on PyGMT's test_coast.py, adapted for pygmt_nb.
"""

import os
import tempfile
import unittest
from pathlib import Path


class TestCoast(unittest.TestCase):
    """Test Figure.coast() method for drawing coastlines."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_coast_region_code(self) -> None:
        """Test plotting a regional map with coastlines using region code."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(region="JP", projection="M10c", frame=True, land="gray", shorelines=1)

        output_file = Path(self.temp_dir) / "coast_region.ps"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists()
        # File should not be empty
        assert output_file.stat().st_size > 0

        # Verify it's a valid PostScript
        with open(output_file, "rb") as f:
            header = f.read(4)
            assert header == b"%!PS"

    def test_coast_world_mercator(self) -> None:
        """Test generating a global Mercator map with coastlines."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[-180, 180, -80, 80],
            projection="M15c",
            frame="af",
            land="#aaaaaa",
            resolution="crude",
            water="white",
        )

        output_file = Path(self.temp_dir) / "coast_world.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_required_args(self) -> None:
        """Test that coast requires both region and projection."""
        from pygmt_nb import Figure

        fig = Figure()
        # Region without projection should fail
        with self.assertRaises(ValueError):
            fig.coast(region="EG")

        # Projection without region should fail
        with self.assertRaises(ValueError):
            fig.coast(projection="M10c")

    def test_coast_dcw_single(self) -> None:
        """Test passing a single country code to dcw."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[-10, 15, 25, 44],
            frame="a",
            projection="M15c",
            land="brown",
            dcw="ES+gbisque+pblue",
        )

        output_file = Path(self.temp_dir) / "coast_dcw_single.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_dcw_list(self) -> None:
        """Test passing a list of country codes and fill arguments to dcw."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[-10, 15, 25, 44],
            frame="a",
            projection="M15c",
            land="brown",
            dcw=["ES+gbisque+pgreen", "IT+gcyan+pblue"],
        )

        output_file = Path(self.temp_dir) / "coast_dcw_list.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_resolution_long_form(self) -> None:
        """Test using long-form resolution names."""
        from pygmt_nb import Figure

        fig = Figure()
        # Test each resolution level
        for resolution in ["crude", "low", "intermediate", "high", "full"]:
            fig = Figure()
            fig.coast(
                region=[-10, 10, -10, 10],
                projection="M10c",
                resolution=resolution,
                land="gray",
            )

            output_file = Path(self.temp_dir) / f"coast_res_{resolution}.ps"
            fig.savefig(str(output_file))

            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_coast_resolution_short_form(self) -> None:
        """Test using short-form resolution names."""
        from pygmt_nb import Figure

        # Test each short-form resolution
        for resolution in ["c", "l", "i", "h", "f"]:
            fig = Figure()
            fig.coast(
                region=[-10, 10, -10, 10],
                projection="M10c",
                resolution=resolution,
                land="gray",
            )

            output_file = Path(self.temp_dir) / f"coast_res_short_{resolution}.ps"
            fig.savefig(str(output_file))

            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_coast_borders(self) -> None:
        """Test drawing political borders."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[-10, 30, 30, 50],
            projection="M10c",
            land="gray",
            borders="1",  # National borders
            frame=True,
        )

        output_file = Path(self.temp_dir) / "coast_borders.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_shorelines_bool(self) -> None:
        """Test shorelines with boolean True."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[0, 10, 0, 10],
            projection="M10c",
            shorelines=True,
        )

        output_file = Path(self.temp_dir) / "coast_shorelines_bool.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_shorelines_string(self) -> None:
        """Test shorelines with string parameter."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.coast(
            region=[0, 10, 0, 10],
            projection="M10c",
            shorelines="1/0.5p,black",
        )

        output_file = Path(self.temp_dir) / "coast_shorelines_string.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_coast_default_shorelines(self) -> None:
        """Test coast with default (draws shorelines when no other option)."""
        from pygmt_nb import Figure

        fig = Figure()
        # No land, water, or explicit shorelines - should default to shorelines
        fig.coast(
            region=[0, 10, 0, 10],
            projection="M10c",
        )

        output_file = Path(self.temp_dir) / "coast_default.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


if __name__ == "__main__":
    unittest.main()
