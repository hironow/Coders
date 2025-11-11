"""
info - Get information about data tables.

Module-level function (not a Figure method).
"""

from typing import Union, List, Optional
from pathlib import Path
import numpy as np
import tempfile
import os

from pygmt_nb.clib import Session


def info(
    data: Union[np.ndarray, List, str, Path],
    spacing: Optional[Union[str, List[float]]] = None,
    per_column: bool = False,
    **kwargs
) -> Union[np.ndarray, str]:
    """
    Get information about data tables.

    Reads data and finds the extreme values (min/max) in each column.
    Can optionally round the extent to nearest multiples of specified spacing.

    Based on PyGMT's info implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array (n_rows, n_cols)
        - Python list
        - Path to ASCII data file
    spacing : str or list, optional
        Spacing increments for rounding extent. Format: "dx/dy" or [dx, dy].
        Output will be [w, e, s, n] rounded to nearest multiples.
    per_column : bool, default False
        Report min/max values per column in separate columns.
    **kwargs
        Additional GMT options.

    Returns
    -------
    output : str or ndarray
        Data range information. Format depends on options:
        - Default: String with min/max for each column
        - With spacing: ndarray [w, e, s, n]
        - With per_column: String with separate columns

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> data = np.array([[1, 2], [3, 4], [5, 6]])
    >>> result = pygmt.info(data)
    >>> print(result)
    <stdin>: N = 3 <1/5> <2/6>
    >>>
    >>> # Get region with spacing
    >>> region = pygmt.info(data, spacing="1/1")
    >>> print(region)
    [1. 5. 2. 6.]
    """
    # Build GMT command arguments
    args = []

    # Spacing (-I option) - for region output
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")

    # Per-column output (-C option)
    if per_column:
        args.append("-C")

    # Handle data input
    with Session() as session:
        if isinstance(data, (str, Path)):
            # File path - direct input
            cmd_args = f"{data} " + " ".join(args)

            # For output capture, write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                outfile = f.name

            try:
                session.call_module("info", f"{cmd_args} ->{outfile}")

                # Read output
                with open(outfile, 'r') as f:
                    output = f.read().strip()
            finally:
                os.unlink(outfile)
        else:
            # Array-like data - use virtual file
            data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

            # Create virtual file from data
            if data_array.ndim == 1:
                # 1-D array - treat as single column
                data_array = data_array.reshape(-1, 1)

            # Prepare vectors for virtual file
            vectors = [data_array[:, i] for i in range(data_array.shape[1])]

            # Output file for capturing result
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                outfile = f.name

            try:
                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("info", f"{vfile} " + " ".join(args) + f" ->{outfile}")

                # Read output
                with open(outfile, 'r') as f:
                    output = f.read().strip()
            finally:
                os.unlink(outfile)

    # Parse output if spacing was used (returns region)
    if spacing is not None:
        # Output format: "w e s n" - parse to numpy array
        try:
            values = output.split()
            if len(values) >= 4:
                return np.array([float(values[0]), float(values[1]),
                               float(values[2]), float(values[3])])
        except (ValueError, IndexError):
            pass

    # Return raw string output
    return output
