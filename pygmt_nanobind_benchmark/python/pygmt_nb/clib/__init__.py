"""
Core library interface

This module provides the Session class, Grid class, and low-level GMT API bindings.
"""

import contextlib
import numpy as np
from typing import Sequence, Generator

from pygmt_nb.clib._pygmt_nb_core import Session as _CoreSession
from pygmt_nb.clib._pygmt_nb_core import Grid


class Session(_CoreSession):
    """
    GMT Session wrapper with context manager support.

    This class wraps the C++ Session class and adds Python context manager
    protocol (__enter__ and __exit__) as well as high-level virtual file methods.
    """

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        # Cleanup is handled by C++ destructor
        # Return None (False) to propagate exceptions
        return None

    @contextlib.contextmanager
    def virtualfile_from_vectors(self, *vectors: Sequence) -> Generator[str, None, None]:
        """
        Store 1-D arrays as columns in a virtual file for passing to GMT modules.

        This method creates a GMT dataset from numpy arrays and opens a virtual
        file that can be passed as a filename argument to GMT modules. The virtual
        file is automatically closed when exiting the context manager.

        Based on PyGMT's virtualfile_from_vectors implementation.

        Parameters
        ----------
        *vectors : sequence of array-like
            One or more 1-D arrays to store as columns. All must have the same length.
            Arrays will be converted to numpy arrays if needed.

        Yields
        ------
        vfname : str
            Virtual file name (e.g., "?GMTAPI@12345") that can be passed to GMT modules.

        Examples
        --------
        >>> import numpy as np
        >>> with Session() as lib:
        ...     x = np.array([0, 1, 2, 3, 4])
        ...     y = np.array([5, 6, 7, 8, 9])
        ...     with lib.virtualfile_from_vectors(x, y) as vfile:
        ...         lib.call_module("info", vfile)

        Raises
        ------
        ValueError
            If arrays have different lengths or are empty.
        RuntimeError
            If GMT data creation or virtual file operations fail.
        """
        # Convert all vectors to numpy arrays and ensure C-contiguous
        arrays = []
        for vec in vectors:
            arr = np.ascontiguousarray(vec, dtype=np.float64)
            if arr.ndim != 1:
                raise ValueError(f"All vectors must be 1-D, got shape {arr.shape}")
            arrays.append(arr)

        if not arrays:
            raise ValueError("At least one vector is required")

        n_columns = len(arrays)
        n_rows = len(arrays[0])

        # Check all arrays have same length
        if not all(len(arr) == n_rows for arr in arrays):
            raise ValueError(
                f"All arrays must have same length. Got lengths: "
                f"{[len(arr) for arr in arrays]}"
            )

        # Get GMT constants
        family = self.get_constant("GMT_IS_DATASET") | self.get_constant("GMT_VIA_VECTOR")
        geometry = self.get_constant("GMT_IS_POINT")
        mode = self.get_constant("GMT_CONTAINER_ONLY")
        dtype = self.get_constant("GMT_DOUBLE")

        # Create GMT dataset container
        # dim = [n_columns, n_rows, data_type, unused]
        dataset = self.create_data(
            family,
            geometry,
            mode,
            [n_columns, n_rows, dtype, 0]
        )

        try:
            # Attach each vector as a column
            for col, array in enumerate(arrays):
                self.put_vector(dataset, col, dtype, array)

            # Open virtual file with dataset
            direction = self.get_constant("GMT_IN") | self.get_constant("GMT_IS_REFERENCE")
            vfname = self.open_virtualfile(family, geometry, direction, dataset)

            try:
                yield vfname
            finally:
                # Close virtual file
                self.close_virtualfile(vfname)
        except Exception as e:
            raise RuntimeError(f"Virtual file operation failed: {e}") from e


__all__ = ["Session", "Grid"]
