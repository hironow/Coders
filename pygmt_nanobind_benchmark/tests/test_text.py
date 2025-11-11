"""
Test Figure.text.

Based on PyGMT's test_text.py, adapted for pygmt_nb.
"""

import os
import tempfile
import unittest
from pathlib import Path


class TestText(unittest.TestCase):
    """Test Figure.text() method for plotting text."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.region = [0, 5, 0, 2.5]
        self.projection = "x10c"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_figure_has_text_method(self) -> None:
        """Test that Figure has text method."""
        from pygmt_nb import Figure

        fig = Figure()
        assert hasattr(fig, "text")
        assert callable(fig.text)

    def test_text_single_line(self) -> None:
        """Place a single line of text at some x, y location."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.text(
            region=self.region,
            projection=self.projection,
            x=1.2,
            y=2.4,
            text="This is a line of text",
        )

        output_file = Path(self.temp_dir) / "text_single.ps"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists()
        # File should not be empty
        assert output_file.stat().st_size > 0

        # Verify it's a valid PostScript
        with open(output_file, "rb") as f:
            header = f.read(4)
            assert header == b"%!PS"

    def test_text_multiple_lines(self) -> None:
        """Place multiple lines of text at their respective x, y locations."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.text(
            region=self.region,
            projection=self.projection,
            x=[1.2, 1.6],
            y=[0.6, 0.3],
            text=["This is a line of text", "This is another line of text"],
        )

        output_file = Path(self.temp_dir) / "text_multiple.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_text_with_font(self) -> None:
        """Test text with font specification."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.text(
            region=self.region,
            projection=self.projection,
            x=1.5,
            y=1.5,
            text="Large Text",
            font="18p,Helvetica-Bold,red",
        )

        output_file = Path(self.temp_dir) / "text_font.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_text_with_angle(self) -> None:
        """Test text with rotation angle."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.text(
            region=self.region,
            projection=self.projection,
            x=2.0,
            y=1.0,
            text="Rotated Text",
            angle=45,
        )

        output_file = Path(self.temp_dir) / "text_angle.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_text_with_justify(self) -> None:
        """Test text with justification."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.text(
            region=self.region,
            projection=self.projection,
            x=2.5,
            y=1.5,
            text="Centered Text",
            justify="MC",  # Middle Center
        )

        output_file = Path(self.temp_dir) / "text_justify.ps"
        fig.savefig(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_text_fail_no_data(self) -> None:
        """Text should raise an exception if no data is given."""
        from pygmt_nb import Figure

        fig = Figure()
        # No x, y, or text
        with self.assertRaises(ValueError):
            fig.text(
                region=self.region,
                projection=self.projection,
            )

        # Only x, no y or text
        with self.assertRaises(ValueError):
            fig.text(
                x=1.0,
                region=self.region,
                projection=self.projection,
            )

        # x and y, but no text
        with self.assertRaises(ValueError):
            fig.text(
                x=1.0,
                y=1.0,
                region=self.region,
                projection=self.projection,
            )

    def test_text_region_required(self) -> None:
        """Test that region is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.text(x=1.0, y=1.0, text="Test", projection=self.projection)

    def test_text_projection_required(self) -> None:
        """Test that projection is required."""
        from pygmt_nb import Figure

        fig = Figure()
        with self.assertRaises(ValueError):
            fig.text(x=1.0, y=1.0, text="Test", region=self.region)


if __name__ == "__main__":
    unittest.main()
