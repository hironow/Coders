"""
grdtrack - Sample grids at specified (x,y) locations.

Module-level function (not a Figure method).
"""

import os
import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def grdtrack(
    points: np.ndarray | list | str | Path,
    grid: str | Path | list[str | Path],
    output: str | Path | None = None,
    newcolname: str | None = None,
    interpolation: str | None = None,
    no_skip: bool = False,
    **kwargs,
) -> np.ndarray | None:
    """
    Sample grids at specified (x,y) locations.

    Reads one or more grid files and a table with (x,y) positions and
    samples the grid(s) at those positions. Can be used to extract
    profiles, cross-sections, or values along tracks.

    Based on PyGMT's grdtrack implementation for API compatibility.

    Parameters
    ----------
    points : array-like or str or Path
        Points to sample. Can be:
        - 2-D numpy array with x, y columns (and optionally other columns)
        - Path to ASCII data file with x, y columns
    grid : str, Path, or list
        Grid file(s) to sample. Can be:
        - Single grid file name
        - List of grid files (samples all grids at each point)
    output : str or Path, optional
        Output file name. If not specified, returns numpy array.
    newcolname : str, optional
        Name for new column(s) in output.
    interpolation : str, optional
        Interpolation method:
        - "l" : Linear (default)
        - "c" : Cubic spline
        - "n" : Nearest neighbor
    no_skip : bool, optional
        Do not skip points that are outside grid bounds (default: False).
        If True, assigns NaN to outside points.

    Returns
    -------
    result : ndarray or None
        Array with original columns plus sampled grid value(s) if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Sample grid along a line
    >>> x = np.linspace(0, 10, 50)
    >>> y = np.linspace(0, 10, 50)
    >>> points = np.column_stack([x, y])
    >>> profile = pygmt.grdtrack(
    ...     points=points,
    ...     grid="@earth_relief_01d"
    ... )
    >>> print(profile.shape)
    (50, 3)  # x, y, z columns
    >>>
    >>> # Sample multiple grids
    >>> result = pygmt.grdtrack(
    ...     points=points,
    ...     grid=["grid1.nc", "grid2.nc"]
    ... )
    >>> print(result.shape)
    (50, 4)  # x, y, z1, z2 columns
    >>>
    >>> # From file with cubic interpolation
    >>> pygmt.grdtrack(
    ...     points="track.txt",
    ...     grid="topography.nc",
    ...     output="sampled.txt",
    ...     interpolation="c"
    ... )

    Notes
    -----
    This function is commonly used for:
    - Extracting elevation profiles from DEMs
    - Sampling oceanographic data along ship tracks
    - Creating cross-sections through gridded data
    - Extracting values at specific locations

    Interpolation methods:
    - Linear: Fast, suitable for most cases
    - Cubic: Smoother, better for continuous data
    - Nearest: Fast, preserves original values

    Output format:
    - Input columns are preserved
    - Sampled grid values are appended as new columns
    - One column per grid file
    """
    # Build GMT command arguments
    args = []

    # Grid file(s) (-G option)
    if isinstance(grid, list):
        for g in grid:
            args.append(f"-G{g}")
    else:
        args.append(f"-G{grid}")

    # Interpolation (-n option)
    if interpolation is not None:
        args.append(f"-n{interpolation}")

    # No skip (-A option)
    if no_skip:
        args.append("-A")

    # New column name (-Z option in some versions, but not standard)
    # GMT typically doesn't have this option, so we'll skip it

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
            # Handle points input
            if isinstance(points, str | Path):
                # File input
                session.call_module("grdtrack", f"{points} " + " ".join(args) + f" ->{outfile}")
            else:
                # Array input - use virtual file
                points_array = np.atleast_2d(np.asarray(points, dtype=np.float64))

                # Create vectors for virtual file
                vectors = [points_array[:, i] for i in range(points_array.shape[1])]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("grdtrack", f"{vfile} " + " ".join(args) + f" ->{outfile}")

        # Read output if returning array
        if return_array:
            result = np.loadtxt(outfile)
            # Ensure 2D array
            if result.ndim == 1:
                result = result.reshape(1, -1)
            return result
        else:
            return None
    finally:
        if return_array and os.path.exists(outfile):
            os.unlink(outfile)
