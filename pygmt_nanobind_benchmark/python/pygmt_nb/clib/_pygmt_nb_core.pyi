"""
PyGMT nanobind core module - High-performance GMT bindings

This module provides Python bindings to GMT (Generic Mapping Tools)
using nanobind for improved performance over ctypes.

Requirements:
  - GMT 6.5.0 or later must be installed on your system
  - GMT library must be accessible (libgmt.so/dylib/dll)

Example:
  >>> from pygmt_nb import Session
  >>> with Session() as lib:
  ...     info = lib.info()
  ...     print(info['gmt_version'])
"""

from collections.abc import Sequence
from typing import Annotated

import numpy
from numpy.typing import NDArray
from typing_extensions import CapsuleType

class Session:
    """
    GMT session manager

    This class wraps a GMT API session and provides context manager support.
    Always use it in a 'with' statement to ensure proper cleanup.
    """

    def __init__(self) -> None:
        """
        Create a new GMT session.

        Raises:
            RuntimeError: If GMT is not installed or session creation fails
        """

    def info(self) -> dict[str, str]:
        """
        Get GMT session information.

        Returns:
            dict: Dictionary with keys:
                - gmt_version: Full version string
                - gmt_version_major: Major version number
                - gmt_version_minor: Minor version number
                - gmt_version_patch: Patch version number
        """

    def call_module(self, module: str, args: str = "") -> None:
        """
        Execute a GMT module.

        Args:
            module (str): Module name (e.g., 'gmtset', 'basemap')
            args (str): Module arguments as space-separated string

        Raises:
            RuntimeError: If module execution fails
        """

    @property
    def session_pointer(self) -> CapsuleType:
        """
        Get raw GMT session pointer (advanced usage only).

        Returns:
            int: Pointer address as integer
        """

    @property
    def is_active(self) -> bool:
        """
        Check if session is active.

        Returns:
            bool: True if session is active
        """

    def get_last_error(self) -> str:
        """
        Get last error message.

        Returns:
            str: Last error message, or empty string
        """

    def get_constant(self, name: str) -> int:
        """
        Get GMT constant value by name.

        Args:
            name (str): Constant name (e.g., 'GMT_IS_DATASET')

        Returns:
            int: Constant value

        Raises:
            RuntimeError: If constant name is not recognized
        """

    def create_data(self, family: int, geometry: int, mode: int, dim: Sequence[int]) -> CapsuleType:
        """
        Create a GMT data container.

        Args:
            family (int): Data family constant
            geometry (int): Data geometry constant
            mode (int): Creation mode constant
            dim (list): Dimensions [n_columns, n_rows, data_type, unused]

        Returns:
            int: Pointer to GMT data structure

        Raises:
            RuntimeError: If data creation fails
        """

    def put_vector(
        self,
        dataset: CapsuleType,
        column: int,
        type: int,
        vector: Annotated[NDArray[numpy.float64], {"shape": (None,), "order": "C"}],
    ) -> None:
        """
        Attach numpy array to GMT dataset as column.

        Args:
            dataset (int): GMT dataset pointer
            column (int): Column index (0-based)
            type (int): GMT data type constant
            vector (ndarray): Contiguous numpy array

        Raises:
            RuntimeError: If operation fails
        """

    def open_virtualfile(
        self, family: int, geometry: int, direction: int, data: CapsuleType
    ) -> str:
        """
        Open a GMT virtual file.

        Args:
            family (int): Data family constant
            geometry (int): Data geometry constant
            direction (int): Direction constant (GMT_IN/GMT_OUT)
            data (int): GMT data pointer or 0 for output

        Returns:
            str: Virtual file name

        Raises:
            RuntimeError: If virtual file creation fails
        """

    def close_virtualfile(self, vfname: str) -> None:
        """
        Close a GMT virtual file.

        Args:
            vfname (str): Virtual file name

        Raises:
            RuntimeError: If closing fails
        """

class Grid:
    """
    GMT Grid data container

    This class wraps GMT grid data and provides NumPy array access.
    Grids are automatically cleaned up when the object is destroyed.
    """

    def __init__(self, session: Session, filename: str) -> None:
        """
        Create Grid by reading from file.

        Args:
            session (Session): Active GMT session
            filename (str): Path to grid file (GMT format, e.g., .nc, .grd)

        Raises:
            RuntimeError: If file cannot be read or is invalid
        """

    @property
    def shape(self) -> tuple[int, int]:
        """
        Get grid shape.

        Returns:
            tuple: (n_rows, n_columns)
        """

    @property
    def region(self) -> tuple[float, float, float, float]:
        """
        Get grid region.

        Returns:
            tuple: (west, east, south, north)
        """

    @property
    def registration(self) -> int:
        """
        Get grid registration type.

        Returns:
            int: 0 for node registration, 1 for pixel registration
        """

    def data(self) -> NDArray[numpy.float32]:
        """
        Get grid data as NumPy array.

        Returns:
            ndarray: 2D NumPy array of float32 with shape (n_rows, n_columns)
        """

    @property
    def grid_pointer(self) -> CapsuleType:
        """
        Get raw GMT_GRID pointer (advanced usage only).

        Returns:
            int: Pointer address as integer
        """
