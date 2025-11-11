"""
grdinfo - Extract information from grids.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path
import tempfile
import os

from pygmt_nb.clib import Session


def grdinfo(
    grid: Union[str, Path],
    region: Optional[Union[str, List[float]]] = None,
    per_column: bool = False,
    **kwargs
) -> str:
    """
    Extract information from 2-D grids or 3-D cubes.

    Reads a grid file and reports statistics and metadata about the grid.

    Based on PyGMT's grdinfo implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Path to grid file (NetCDF, GMT format, etc.)
    region : str or list, optional
        Limit the report to a subregion. Format: [xmin, xmax, ymin, ymax]
    per_column : bool, default False
        Format output as tab-separated fields on a single line.
        Output: name w e s n z0 z1 dx dy nx ny ...
    **kwargs
        Additional GMT options.

    Returns
    -------
    output : str
        Grid information string.

    Examples
    --------
    >>> import pygmt
    >>> # Get info about a grid file
    >>> info = pygmt.grdinfo("@earth_relief_01d")
    >>> print(info)
    @earth_relief_01d: Title: ...
    ...
    >>>
    >>> # Get tabular output
    >>> info = pygmt.grdinfo("grid.nc", per_column=True)
    """
    # Build GMT command arguments
    args = []

    # Grid file (required)
    args.append(str(grid))

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Per-column format (-C option)
    if per_column:
        args.append("-C")

    # Execute via nanobind session and capture output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        outfile = f.name

    try:
        with Session() as session:
            session.call_module("grdinfo", " ".join(args) + f" ->{outfile}")

        # Read output
        with open(outfile, 'r') as f:
            output = f.read().strip()
    finally:
        os.unlink(outfile)

    return output
