"""
Test Figure.plot.

Based on PyGMT's test_plot.py, adapted for pygmt_nb.
"""

import unittest
from pathlib import Path
import tempfile
import os
import numpy as np


class TestPlot(unittest.TestCase):
    """Test Figure.plot() method for plotting data points."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Sample data points
        self.x = np.array([10, 20, 30, 40, 50])
        self.y = np.array([5, 7, 3, 9, 6])
        self.region = [0, 60, 0, 10]

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_figure_has_plot_method(self) -> None:
        """Test that Figure has plot method."""
        from pygmt_nb import Figure

        fig = Figure()
        assert hasattr(fig, 'plot')
        assert callable(fig.plot)

    def test_plot_red_circles(self) -> None:
        """Plot data in red circles passing in vectors."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.plot(
            x=self.x,
            y=self.y,
            region=self.region,
            projection="X10c",
            style="c0.2c",
            fill="red",
            frame="afg",
        )

        output_file = Path(self.temp_dir) / "plot_red_circles.ps"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists()
        # File should not be empty
        assert output_file.stat().st_size > 0

        # Verify it's a valid PostScript
        with open(output_file, 'rb') as f:
            header = f.read(4)
            assert header == b'%!PS'

    def test_plot_green_squares(self) -> None:
        """Plot data in green squares."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.plot(
            x=self.x,
            y=self.y,
            region=self.region,
            projection="X10c",
            style="s0.3c",
            fill="green",
            frame="af",
        )

        output_file = Path(self.temp_dir) / "plot_green_squares.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_plot_with_pen(self) -> None:
        """Plot data with pen (outline) specification."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.plot(
            x=self.x,
            y=self.y,
            region=self.region,
            projection="X10c",
            style="c0.3c",
            fill="lightblue",
            pen="1p,black",
            frame="af",
        )

        output_file = Path(self.temp_dir) / "plot_with_pen.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_plot_lines(self) -> None:
        """Plot data as connected lines."""
        from pygmt_nb import Figure

        fig = Figure()
        # No style means draw lines
        fig.plot(
            x=self.x,
            y=self.y,
            region=self.region,
            projection="X10c",
            pen="2p,blue",
            frame="af",
        )

        output_file = Path(self.temp_dir) / "plot_lines.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_plot_fail_no_data(self) -> None:
        """Plot should raise an exception if no data is given."""
        from pygmt_nb import Figure

        fig = Figure()
        # No x or y
        with self.assertRaises(ValueError):
            fig.plot(
                region=self.region,
                projection="X10c",
                style="c0.2c",
                fill="red",
                frame="afg"
            )

        # Only x, no y
        with self.assertRaises(ValueError):
            fig.plot(
                x=self.x,
                region=self.region,
                projection="X10c",
                style="c0.2c",
                fill="red",
                frame="afg"
            )

        # Only y, no x
        with self.assertRaises(ValueError):
            fig.plot(
                y=self.y,
                region=self.region,
                projection="X10c",
                style="c0.2c",
                fill="red",
                frame="afg"
            )

    def test_plot_region_required(self) -> None:
        """Test that region is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.plot(x=self.x, y=self.y, projection="X10c")

    def test_plot_projection_required(self) -> None:
        """Test that projection is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.plot(x=self.x, y=self.y, region=self.region)

    def test_plot_with_basemap(self) -> None:
        """Test plot combined with basemap."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.basemap(region=self.region, projection="X10c", frame="afg")
        # Modern mode: region/projection automatically inherited from basemap
        # Can be provided explicitly if needed to override
        fig.plot(
            x=self.x,
            y=self.y,
            # region and projection inherited from basemap() call above
            style="c0.2c",
            fill="red"
        )

        output_file = Path(self.temp_dir) / "plot_with_basemap.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


if __name__ == "__main__":
    unittest.main()
