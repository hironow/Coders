"""
Tests for GMT Grid data type bindings.

Following TDD (Test-Driven Development) principles:
1. Write failing tests first
2. Implement minimum code to pass
3. Refactor while keeping tests green
"""

import unittest
from pathlib import Path


class TestGridCreation(unittest.TestCase):
    """Test Grid creation and basic properties."""

    def test_grid_can_be_created_from_file(self) -> None:
        """Test that a Grid can be created from a GMT grid file."""
        from pygmt_nb.clib import Session, Grid

        # This test will fail until we implement Grid class
        with Session() as session:
            # We'll use a sample grid file (to be created)
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"

            # For now, we test the API we want to have
            # This will raise AttributeError until Grid is implemented
            grid = Grid(session, str(grid_file))
            assert grid is not None


class TestGridProperties(unittest.TestCase):
    """Test Grid properties and metadata access."""

    def test_grid_has_shape_property(self) -> None:
        """Test that Grid exposes shape (n_rows, n_columns)."""
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"
            grid = Grid(session, str(grid_file))

            # Grid should expose shape as (n_rows, n_columns)
            assert hasattr(grid, "shape")
            assert len(grid.shape) == 2
            assert grid.shape[0] > 0  # n_rows
            assert grid.shape[1] > 0  # n_columns

    def test_grid_has_region_property(self) -> None:
        """Test that Grid exposes region (west, east, south, north)."""
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"
            grid = Grid(session, str(grid_file))

            # Grid should expose region as tuple
            assert hasattr(grid, "region")
            region = grid.region
            assert len(region) == 4  # (west, east, south, north)

    def test_grid_has_registration_property(self) -> None:
        """Test that Grid exposes registration type."""
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"
            grid = Grid(session, str(grid_file))

            # Grid should expose registration (0=node, 1=pixel)
            assert hasattr(grid, "registration")
            assert grid.registration in [0, 1]


class TestGridDataAccess(unittest.TestCase):
    """Test Grid data array access via NumPy."""

    def test_grid_data_returns_numpy_array(self) -> None:
        """Test that Grid.data() returns a NumPy array."""
        import numpy as np
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"
            grid = Grid(session, str(grid_file))

            # Grid.data() should return NumPy array
            data = grid.data()
            assert isinstance(data, np.ndarray)
            assert data.ndim == 2  # 2D grid
            assert data.shape == grid.shape

    def test_grid_data_has_correct_dtype(self) -> None:
        """Test that Grid data has correct dtype (float32 by default)."""
        import numpy as np
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"
            grid = Grid(session, str(grid_file))

            data = grid.data()
            # GMT uses float32 by default (gmt_grdfloat)
            assert data.dtype == np.float32


class TestGridResourceManagement(unittest.TestCase):
    """Test Grid memory management and cleanup."""

    def test_grid_cleans_up_automatically(self) -> None:
        """Test that Grid is cleaned up when out of scope."""
        from pygmt_nb.clib import Session, Grid

        with Session() as session:
            grid_file = Path(__file__).parent / "data" / "test_grid.nc"

            # Create grid
            grid = Grid(session, str(grid_file))
            assert grid is not None

            # Grid should be cleaned up automatically when out of scope
            # (This is handled by C++ destructor)
            del grid
            # No exception should be raised


if __name__ == "__main__":
    unittest.main()
