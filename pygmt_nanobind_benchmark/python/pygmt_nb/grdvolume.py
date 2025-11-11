"""
grdvolume - Calculate grid volume and area.

Module-level function (not a Figure method).
"""

import tempfile
from pathlib import Path

from pygmt_nb.clib import Session


def grdvolume(
    grid: str | Path,
    output: str | Path | None = None,
    contour: float | list[float] | None = None,
    unit: str | None = None,
    region: str | list[float] | None = None,
    **kwargs,
):
    """
    Calculate grid volume and area.

    Reads a grid and calculates the area, volume, and other statistics
    above or below a given contour level. Can also compute cumulative
    volume and area as a function of contour level.

    Based on PyGMT's grdvolume implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    output : str or Path, optional
        Output file name for results. If not specified, returns as string.
    contour : float or list of float, optional
        Contour value(s) at which to calculate volume.
        - Single value: Calculate volume above/below that level
        - Two values [low, high]: Calculate between two levels
        - If not specified, uses grid's minimum value
    unit : str, optional
        Append unit to report area and volume in:
        - "k" : km and km^3
        - "M" : miles and miles^3
        - "n" : nautical miles and nautical miles^3
        - "u" : survey feet and survey feet^3
        Default uses the grid's length unit
    region : str or list, optional
        Subregion of grid to use. Format: [xmin, xmax, ymin, ymax]
        If not specified, uses entire grid.

    Returns
    -------
    str or None
        If output is None, returns volume statistics as string.
        Otherwise writes to file and returns None.

    Examples
    --------
    >>> import pygmt
    >>> # Calculate volume above z=0
    >>> result = pygmt.grdvolume(
    ...     grid="@earth_relief_01d",
    ...     contour=0
    ... )
    >>> print(result)
    >>>
    >>> # Calculate volume between two levels
    >>> result = pygmt.grdvolume(
    ...     grid="topography.nc",
    ...     contour=[0, 1000]
    ... )
    >>>
    >>> # Save results to file
    >>> pygmt.grdvolume(
    ...     grid="data.nc",
    ...     output="volume_stats.txt",
    ...     contour=0,
    ...     unit="k"  # report in km and km^3
    ... )
    >>>
    >>> # Calculate for subregion only
    >>> result = pygmt.grdvolume(
    ...     grid="global.nc",
    ...     region=[120, 150, -50, -20],
    ...     contour=0
    ... )

    Notes
    -----
    This function is commonly used for:
    - Volume calculations (topography, bathymetry)
    - Area computations above/below thresholds
    - Material volume estimates
    - Cumulative distribution functions

    Output format:
    The output contains columns:
    - Contour value
    - Area (above contour)
    - Volume (above contour)
    - Maximum height
    - Mean height

    Volume calculation:
    - Integrates grid values above/below contour
    - Accounts for grid spacing
    - Uses trapezoidal rule for integration
    - Positive volume = above contour
    - Negative volume = below contour

    Applications:
    - Topography: Calculate mountain volumes
    - Bathymetry: Calculate ocean basin volumes
    - Geophysics: Integrate anomaly magnitudes
    - Hydrology: Compute water volumes

    Workflow:
    1. Specify grid and contour level
    2. Optionally set region and units
    3. Calculate area and volume above/below contour
    4. Output statistics or cumulative curves

    Comparison with related functions:
    - grdvolume: Calculate volumes and areas
    - grdinfo: Basic grid statistics (min, max, mean)
    - grdmath: Arbitrary grid calculations
    - surface: Create grid from data
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Contour level (-C option)
    if contour is not None:
        if isinstance(contour, list):
            args.append(f"-C{'/'.join(str(x) for x in contour)}")
        else:
            args.append(f"-C{contour}")

    # Unit (-S option)
    if unit is not None:
        args.append(f"-S{unit}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        if output is not None:
            # Write to file using -> syntax
            session.call_module("grdvolume", " ".join(args) + f" ->{output}")
            return None
        else:
            # Return output as string - grdvolume outputs to stdout by default
            # For now, simplify by requiring output parameter
            # or just call with no output capture
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
                outfile = f.name

            try:
                session.call_module("grdvolume", " ".join(args) + f" ->{outfile}")

                # Read result
                with open(outfile) as f:
                    result = f.read()

                return result
            finally:
                import os

                if os.path.exists(outfile):
                    os.unlink(outfile)
