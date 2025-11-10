"""
Tests for Figure class - PyGMT drop-in replacement API.

Following TDD (Test-Driven Development) principles:
1. Write failing tests first (Red)
2. Implement minimum code to pass (Green)
3. Refactor while keeping tests green
"""

import unittest
from pathlib import Path
import tempfile
import os
import subprocess
import sys

# Check if Ghostscript is available
def ghostscript_available():
    """Check if Ghostscript is installed."""
    try:
        subprocess.run(
            ["gs", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

GHOSTSCRIPT_AVAILABLE = ghostscript_available()


class TestFigureCreation(unittest.TestCase):
    """Test Figure creation and basic properties."""

    def test_figure_can_be_created(self) -> None:
        """Test that a Figure can be created."""
        from pygmt_nb import Figure

        fig = Figure()
        assert fig is not None

    def test_figure_creates_internal_session(self) -> None:
        """Test that Figure creates and manages its own GMT session."""
        from pygmt_nb import Figure

        fig = Figure()
        # Figure should have an internal session
        assert hasattr(fig, '_session')
        assert fig._session is not None


class TestFigureGrdimage(unittest.TestCase):
    """Test Figure.grdimage() method for grid visualization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_grid = Path(__file__).parent / "data" / "test_grid.nc"
        assert self.test_grid.exists(), f"Test grid not found: {self.test_grid}"

    def test_figure_has_grdimage_method(self) -> None:
        """Test that Figure has grdimage method."""
        from pygmt_nb import Figure

        fig = Figure()
        assert hasattr(fig, 'grdimage')
        assert callable(fig.grdimage)

    def test_grdimage_accepts_grid_file_path(self) -> None:
        """Test that grdimage accepts a grid file path."""
        from pygmt_nb import Figure

        fig = Figure()
        # Should not raise an exception
        fig.grdimage(grid=str(self.test_grid))

    @unittest.skip("Grid object support not yet implemented")
    def test_grdimage_accepts_grid_object(self) -> None:
        """Test that grdimage accepts a Grid object."""
        from pygmt_nb import Figure, Session, Grid

        with Session() as session:
            grid = Grid(session, str(self.test_grid))
            fig = Figure()
            # Should not raise an exception
            fig.grdimage(grid=grid)

    def test_grdimage_with_projection(self) -> None:
        """Test that grdimage accepts projection parameter."""
        from pygmt_nb import Figure

        fig = Figure()
        # Should not raise an exception
        fig.grdimage(grid=str(self.test_grid), projection="X10c")

    def test_grdimage_with_region(self) -> None:
        """Test that grdimage accepts region parameter."""
        from pygmt_nb import Figure

        fig = Figure()
        # Should not raise an exception
        fig.grdimage(grid=str(self.test_grid), region=[0, 10, 0, 10])


class TestFigureSavefig(unittest.TestCase):
    """Test Figure.savefig() method for image output."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_grid = Path(__file__).parent / "data" / "test_grid.nc"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_figure_has_savefig_method(self) -> None:
        """Test that Figure has savefig method."""
        from pygmt_nb import Figure

        fig = Figure()
        assert hasattr(fig, 'savefig')
        assert callable(fig.savefig)

    @unittest.skipIf(not GHOSTSCRIPT_AVAILABLE, "Ghostscript not installed")
    def test_savefig_creates_png_file(self) -> None:
        """Test that savefig creates a PNG file."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.grdimage(grid=str(self.test_grid))

        output_file = Path(self.temp_dir) / "test_output.png"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists(), f"Output file not created: {output_file}"
        # File should not be empty
        assert output_file.stat().st_size > 0, "Output file is empty"

    @unittest.skipIf(not GHOSTSCRIPT_AVAILABLE, "Ghostscript not installed")
    def test_savefig_creates_pdf_file(self) -> None:
        """Test that savefig creates a PDF file."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.grdimage(grid=str(self.test_grid))

        output_file = Path(self.temp_dir) / "test_output.pdf"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists(), f"Output file not created: {output_file}"
        # File should not be empty
        assert output_file.stat().st_size > 0, "Output file is empty"

    def test_savefig_creates_ps_file(self) -> None:
        """Test that savefig creates a PostScript file (no Ghostscript needed)."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.grdimage(grid=str(self.test_grid))

        output_file = Path(self.temp_dir) / "test_output.ps"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists(), f"Output file not created: {output_file}"
        # File should not be empty
        assert output_file.stat().st_size > 0, "Output file is empty"

        # Verify it's a valid PostScript (check magic bytes)
        with open(output_file, 'rb') as f:
            header = f.read(4)
            assert header == b'%!PS', "Not a valid PostScript file"

    @unittest.skipIf(not GHOSTSCRIPT_AVAILABLE, "Ghostscript not installed")
    def test_savefig_creates_jpg_file(self) -> None:
        """Test that savefig creates a JPG file."""
        from pygmt_nb import Figure

        fig = Figure()
        fig.grdimage(grid=str(self.test_grid))

        output_file = Path(self.temp_dir) / "test_output.jpg"
        fig.savefig(str(output_file))

        # File should exist
        assert output_file.exists(), f"Output file not created: {output_file}"
        # File should not be empty
        assert output_file.stat().st_size > 0, "Output file is empty"


class TestFigureIntegration(unittest.TestCase):
    """Integration tests for complete Figure workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_grid = Path(__file__).parent / "data" / "test_grid.nc"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @unittest.skipIf(not GHOSTSCRIPT_AVAILABLE, "Ghostscript not installed")
    def test_complete_workflow_grid_to_image(self) -> None:
        """Test complete workflow: load grid, create figure, save image."""
        from pygmt_nb import Figure

        # Create figure
        fig = Figure()

        # Add grid image
        fig.grdimage(grid=str(self.test_grid), projection="X10c")

        # Save to file
        output_file = Path(self.temp_dir) / "workflow_test.png"
        fig.savefig(str(output_file))

        # Verify output
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify it's a valid PNG (check magic bytes)
        with open(output_file, 'rb') as f:
            header = f.read(8)
            # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
            assert header[:4] == b'\x89PNG', "Not a valid PNG file"

    @unittest.skipIf(not GHOSTSCRIPT_AVAILABLE, "Ghostscript not installed")
    def test_multiple_operations_on_same_figure(self) -> None:
        """Test that multiple operations can be performed on same figure."""
        from pygmt_nb import Figure

        fig = Figure()

        # Multiple grdimage calls should work (last one wins)
        fig.grdimage(grid=str(self.test_grid))
        fig.grdimage(grid=str(self.test_grid), projection="X5c")

        # Should be able to save
        output_file = Path(self.temp_dir) / "multi_op_test.png"
        fig.savefig(str(output_file))

        assert output_file.exists()


class TestFigureResourceManagement(unittest.TestCase):
    """Test Figure memory management and cleanup."""

    def test_figure_cleans_up_automatically(self) -> None:
        """Test that Figure is cleaned up when out of scope."""
        from pygmt_nb import Figure

        # Create figure
        fig = Figure()
        fig_id = id(fig)

        # Use figure
        test_grid = Path(__file__).parent / "data" / "test_grid.nc"
        fig.grdimage(grid=str(test_grid))

        # Delete should not raise exception
        del fig

        # No exception means cleanup succeeded


if __name__ == "__main__":
    unittest.main()
