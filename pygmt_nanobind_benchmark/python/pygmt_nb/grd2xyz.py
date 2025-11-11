"""
grd2xyz - Convert grid to table data.

Module-level function (not a Figure method).
"""

import os
import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def grd2xyz(
    grid: str | Path,
    output: str | Path | None = None,
    region: str | list[float] | None = None,
    cstyle: str | None = None,
    **kwargs,
) -> np.ndarray | None:
    """
    Convert grid to table data.

    Reads a grid file and writes out xyz-triplets to a table. The output
    order of the coordinates can be specified, as well as the output format.

    Based on PyGMT's grd2xyz implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Name of input grid file.
    output : str or Path, optional
        Name of output file. If not specified, returns numpy array.
    region : str or list, optional
        Subregion to extract. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        If not specified, uses entire grid region.
    cstyle : str, optional
        Format for output coordinates:
        - None (default): Continuous output
        - "f" : Row by row starting at the first column
        - "r" : Row by row starting at the last column
        - "c" : Column by column starting at the first row

    Returns
    -------
    result : ndarray or None
        xyz array with shape (n_points, 3) if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import pygmt
    >>> # Convert grid to XYZ table
    >>> grid = "@earth_relief_01d_g"
    >>> xyz_data = pygmt.grd2xyz(grid=grid, region=[0, 5, 0, 5])
    >>> print(xyz_data.shape)
    (36, 3)
    >>>
    >>> # Save to file
    >>> pygmt.grd2xyz(grid="input.nc", output="output.xyz")

    Notes
    -----
    This function wraps the GMT grd2xyz module for converting gridded data
    to XYZ point data format. Useful for exporting grids to other formats
    or for further data processing.
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Coordinate style (-C option)
    if cstyle is not None:
        args.append(f"-C{cstyle}")

    # Prepare output
    if output is not None:
        outfile = str(output)
        return_array = False
    else:
        # Temp file for array output
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            outfile = f.name
        return_array = True

    try:
        with Session() as session:
            session.call_module("grd2xyz", " ".join(args) + f" ->{outfile}")

        # Read output if returning array
        if return_array:
            # Load XYZ data
            result = np.loadtxt(outfile)
            # Ensure 2D array (handle single point case)
            if result.ndim == 1:
                result = result.reshape(1, -1)
            return result
        else:
            return None
    finally:
        if return_array and os.path.exists(outfile):
            os.unlink(outfile)
