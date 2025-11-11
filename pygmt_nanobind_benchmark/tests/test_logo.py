"""
Test Figure.logo method.

Tests the logo() method which adds the GMT logo to figures using GMT pslogo command.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pygmt_nb import Figure


class TestLogo(unittest.TestCase):
    """Test suite for Figure.logo() method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.test_output = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_logo_method_exists(self) -> None:
        """Test that the logo method exists."""
        fig = Figure()
        assert hasattr(fig, "logo")
        assert callable(fig.logo)

    def test_logo_simple(self) -> None:
        """Test basic logo plotting."""
        fig = Figure()
        fig.logo()
        output = self.test_output / "logo_simple.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_position(self) -> None:
        """Test logo with custom position."""
        fig = Figure()
        fig.logo(position="x5c/5c+w5c")
        output = self.test_output / "logo_position.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_box(self) -> None:
        """Test logo with background box."""
        fig = Figure()
        fig.logo(box=True)
        output = self.test_output / "logo_box.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_on_map(self) -> None:
        """Test logo plotted on a map."""
        fig = Figure()
        fig.basemap(region=[130, 150, 30, 45], projection="M10c", frame=True)
        fig.logo(position="jTR+o0.5c+w5c", box=True)
        output = self.test_output / "logo_on_map.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_style_standard(self) -> None:
        """Test logo with standard style."""
        fig = Figure()
        fig.logo(style="standard")
        output = self.test_output / "logo_style_standard.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_style_url(self) -> None:
        """Test logo with URL style."""
        fig = Figure()
        fig.logo(style="url")
        output = self.test_output / "logo_style_url.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_style_no_label(self) -> None:
        """Test logo with no label style."""
        fig = Figure()
        fig.logo(style="no_label")
        output = self.test_output / "logo_style_no_label.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_with_transparency(self) -> None:
        """Test logo with transparency."""
        fig = Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
        fig.logo(position="jBL+o0.5c+w4c", transparency=50)
        output = self.test_output / "logo_transparency.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_logo_multiple_on_figure(self) -> None:
        """Test multiple logos on the same figure."""
        fig = Figure()
        fig.basemap(region=[0, 20, 0, 20], projection="X15c", frame=True)
        # First logo in top-right
        fig.logo(position="jTR+o0.5c+w3c")
        # Second logo in bottom-left
        fig.logo(position="jBL+o0.5c+w3c")
        output = self.test_output / "logo_multiple.ps"
        fig.savefig(str(output))
        assert output.exists()
        assert output.stat().st_size > 0


if __name__ == "__main__":
    unittest.main()
