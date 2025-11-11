"""
binstats - Bin spatial data and compute statistics.

Module-level function (not a Figure method).
"""

import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def binstats(
    data: np.ndarray | str | Path | None = None,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    output: str | Path | None = None,
    outgrid: str | Path | None = None,
    region: str | list[float] = None,
    spacing: str | list[float] = None,
    statistic: str | None = None,
    **kwargs,
):
    """
    Bin spatial data and compute statistics.

    Reads (x, y, z) data and bins them into a grid, computing various
    statistics (mean, median, mode, etc.) for values within each bin.
    Can output results as ASCII table or grid.

    Based on GMT's gmtbinstats module for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data. Can be:
        - 2-D or 3-D numpy array with x, y, z columns
        - Path to ASCII data file with x, y, z columns
    x, y, z : array-like, optional
        X, Y coordinates and Z values as separate 1-D arrays.
    output : str or Path, optional
        Output ASCII file name for table results.
    outgrid : str or Path, optional
        Output grid file name. If specified, creates grid instead of table.
    region : str or list
        Grid/bin bounds. Format: [xmin, xmax, ymin, ymax]
        Required parameter.
    spacing : str or list
        Bin spacing. Format: "xinc[unit][/yinc[unit]]" or [xinc, yinc]
        Required parameter.
    statistic : str, optional
        Statistic to compute per bin:
        - "a" : Mean (default)
        - "d" : Median
        - "g" : Mode (most frequent value)
        - "i" : Minimum
        - "I" : Maximum
        - "l" : Lower quartile (25%)
        - "L" : Lower hinge
        - "m" : Median absolute deviation (MAD)
        - "q" : Upper quartile (75%)
        - "Q" : Upper hinge
        - "r" : Range (max - min)
        - "s" : Standard deviation
        - "u" : Sum
        - "z" : Number of values

    Returns
    -------
    np.ndarray or None
        If output is None and outgrid is None, returns numpy array.
        Otherwise writes to file and returns None.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered data
    >>> x = np.random.uniform(0, 10, 1000)
    >>> y = np.random.uniform(0, 10, 1000)
    >>> z = np.sin(x) * np.cos(y)
    >>>
    >>> # Bin data and compute mean per bin
    >>> result = pygmt.binstats(
    ...     x=x, y=y, z=z,
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.5,
    ...     statistic="a"  # mean
    ... )
    >>>
    >>> # Compute median and output as grid
    >>> pygmt.binstats(
    ...     x=x, y=y, z=z,
    ...     outgrid="median_grid.nc",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.5,
    ...     statistic="d"  # median
    ... )
    >>>
    >>> # From data array, save to table
    >>> data = np.column_stack([x, y, z])
    >>> pygmt.binstats(
    ...     data=data,
    ...     output="binned_data.txt",
    ...     region=[0, 10, 0, 10],
    ...     spacing=1.0,
    ...     statistic="a"
    ... )
    >>>
    >>> # Count number of points per bin
    >>> counts = pygmt.binstats(
    ...     x=x, y=y, z=z,
    ...     region=[0, 10, 0, 10],
    ...     spacing=1.0,
    ...     statistic="z"  # count
    ... )

    Notes
    -----
    This function is commonly used for:
    - Binning scattered data onto regular grid
    - Computing spatial statistics
    - Data density analysis
    - Outlier detection via robust statistics

    Binning process:
    1. Divide region into rectangular bins
    2. Assign each (x,y,z) point to a bin
    3. Compute statistic for all z values in bin
    4. Output bin centers with computed statistic

    Statistics choice:
    - Mean (a): Simple average, sensitive to outliers
    - Median (d): Robust to outliers, slower
    - Mode (g): Most common value, for categorical data
    - Count (z): Number of points per bin (density)
    - Range (r): Variability within bin
    - Std dev (s): Spread of values

    Empty bins:
    - Bins with no data are skipped in output table
    - Grid output: empty bins contain NaN

    Applications:
    - Create gridded datasets from scattered points
    - Compute spatial statistics on irregular data
    - Density mapping (point counts)
    - Robust averaging with median
    - Quality control (check std dev or range)

    Comparison with related functions:
    - binstats: Flexible statistics, table or grid output
    - blockmean: Mean in spatial blocks, table output
    - blockmedian: Median in blocks, table output
    - surface: Smooth interpolation with tension
    - nearneighbor: Nearest neighbor gridding

    Advantages:
    - Multiple statistics available
    - Can output grid directly
    - Handles empty bins gracefully
    - Fast for large datasets

    Workflow:
    1. Define region and bin spacing
    2. Choose appropriate statistic
    3. Bin data and compute statistic
    4. Visualize or analyze results
    """
    # Build GMT command arguments
    args = []

    # Region (-R option) - required
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for binstats()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for binstats()")

    # Statistic (-S option) - default to mean if not specified
    if statistic is not None:
        args.append(f"-S{statistic}")
    else:
        args.append("-Sa")  # Default to mean

    # Output grid (-G option)
    if outgrid is not None:
        args.append(f"-G{outgrid}")

    # Execute via nanobind session
    with Session() as session:
        # Handle data input
        if data is not None:
            if isinstance(data, str | Path):
                # File input
                if output is not None:
                    session.call_module("gmtbinstats", f"{data} " + " ".join(args) + f" ->{output}")
                    return None
                elif outgrid is not None:
                    session.call_module("gmtbinstats", f"{data} " + " ".join(args))
                    return None
                else:
                    # Return as array
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
                        outfile = f.name
                    try:
                        session.call_module(
                            "gmtbinstats", f"{data} " + " ".join(args) + f" ->{outfile}"
                        )
                        result = np.loadtxt(outfile)
                        return result
                    finally:
                        import os

                        if os.path.exists(outfile):
                            os.unlink(outfile)
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Check for at least 3 columns (x, y, z)
                if data_array.shape[1] < 3:
                    raise ValueError(
                        f"data array must have at least 3 columns (x, y, z), got {data_array.shape[1]}"
                    )

                # Create vectors for virtual file
                vectors = [data_array[:, i] for i in range(3)]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    if output is not None:
                        session.call_module(
                            "gmtbinstats", f"{vfile} " + " ".join(args) + f" ->{output}"
                        )
                        return None
                    elif outgrid is not None:
                        session.call_module("gmtbinstats", f"{vfile} " + " ".join(args))
                        return None
                    else:
                        # Return as array
                        with tempfile.NamedTemporaryFile(
                            mode="w+", suffix=".txt", delete=False
                        ) as f:
                            outfile = f.name
                        try:
                            session.call_module(
                                "gmtbinstats", f"{vfile} " + " ".join(args) + f" ->{outfile}"
                            )
                            result = np.loadtxt(outfile)
                            return result
                        finally:
                            import os

                            if os.path.exists(outfile):
                                os.unlink(outfile)

        elif x is not None and y is not None and z is not None:
            # Separate x, y, z arrays
            x_array = np.asarray(x, dtype=np.float64).ravel()
            y_array = np.asarray(y, dtype=np.float64).ravel()
            z_array = np.asarray(z, dtype=np.float64).ravel()

            with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                if output is not None:
                    session.call_module(
                        "gmtbinstats", f"{vfile} " + " ".join(args) + f" ->{output}"
                    )
                    return None
                elif outgrid is not None:
                    session.call_module("gmtbinstats", f"{vfile} " + " ".join(args))
                    return None
                else:
                    # Return as array
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
                        outfile = f.name
                    try:
                        session.call_module(
                            "gmtbinstats", f"{vfile} " + " ".join(args) + f" ->{outfile}"
                        )
                        result = np.loadtxt(outfile)
                        return result
                    finally:
                        import os

                        if os.path.exists(outfile):
                            os.unlink(outfile)
        else:
            raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
