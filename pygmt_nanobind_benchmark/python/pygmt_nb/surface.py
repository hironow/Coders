"""
surface - Grid table data using adjustable tension continuous curvature splines.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np

from pygmt_nb.clib import Session


def surface(
    data: Optional[Union[np.ndarray, List, str, Path]] = None,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    z: Optional[np.ndarray] = None,
    outgrid: Union[str, Path] = "surface_output.nc",
    region: Optional[Union[str, List[float]]] = None,
    spacing: Optional[Union[str, List[float]]] = None,
    tension: Optional[float] = None,
    convergence: Optional[float] = None,
    mask: Optional[Union[str, Path]] = None,
    searchradius: Optional[Union[str, float]] = None,
    **kwargs
):
    """
    Grid table data using adjustable tension continuous curvature splines.

    Reads randomly-spaced (x,y,z) data and produces a binary grid with
    continuous curvature splines in tension. The algorithm uses an
    iterative method that converges to a solution.

    Based on PyGMT's surface implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array with x, y, z columns
        - Path to ASCII data file with x, y, z columns
    x, y, z : array-like, optional
        x, y, and z coordinates as separate 1-D arrays.
    outgrid : str or Path, optional
        Name of output grid file (default: "surface_output.nc").
    region : str or list, optional
        Grid bounds. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        Required parameter.
    spacing : str or list, optional
        Grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter.
    tension : float, optional
        Tension factor in range [0, 1].
        - 0: Minimum curvature (smoothest)
        - 1: Maximum tension (less smooth, closer to data)
        Default is 0 (minimum curvature surface).
    convergence : float, optional
        Convergence limit. Iteration stops when maximum change in grid
        values is less than this limit. Default is 0.001 of data range.
    mask : str or Path, optional
        Grid mask file. Only compute surface where mask is not NaN.
    searchradius : str or float, optional
        Search radius for nearest neighbor. Can include units.
        Example: "5k" for 5 kilometers.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered data points
    >>> x = np.random.rand(100) * 10
    >>> y = np.random.rand(100) * 10
    >>> z = np.sin(x) * np.cos(y)
    >>> # Grid the data
    >>> pygmt.surface(
    ...     x=x, y=y, z=z,
    ...     outgrid="interpolated.nc",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.1
    ... )
    >>>
    >>> # Use data array
    >>> data = np.column_stack([x, y, z])
    >>> pygmt.surface(
    ...     data=data,
    ...     outgrid="interpolated2.nc",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.1,
    ...     tension=0.25
    ... )
    >>>
    >>> # From file
    >>> pygmt.surface(
    ...     data="input_points.txt",
    ...     outgrid="interpolated3.nc",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.1
    ... )

    Notes
    -----
    The surface algorithm:
    - Uses continuous curvature splines in tension
    - Iteratively adjusts grid to honor data constraints
    - Can interpolate or smooth depending on tension parameter
    - Useful for creating DEMs from scattered elevation points

    Tension parameter guide:
    - 0.0: Minimum curvature (very smooth, may overshoot)
    - 0.25-0.35: Good for topography with moderate relief
    - 0.5-0.75: Tighter fit, less smooth
    - 1.0: Maximum tension (tight fit, may be rough)
    """
    # Build GMT command arguments
    args = []

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Region (-R option) - required
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for surface()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for surface()")

    # Tension (-T option)
    if tension is not None:
        args.append(f"-T{tension}")

    # Convergence (-C option)
    if convergence is not None:
        args.append(f"-C{convergence}")

    # Mask (-M option)
    if mask is not None:
        args.append(f"-M{mask}")

    # Search radius (-S option)
    if searchradius is not None:
        args.append(f"-S{searchradius}")

    # Execute via nanobind session
    with Session() as session:
        # Handle data input
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("surface", f"{data} " + " ".join(args))
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Check for 3 columns (x, y, z)
                if data_array.shape[1] < 3:
                    raise ValueError(
                        f"data array must have at least 3 columns (x, y, z), got {data_array.shape[1]}"
                    )

                # Create vectors for virtual file (x, y, z)
                vectors = [data_array[:, i] for i in range(min(3, data_array.shape[1]))]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("surface", f"{vfile} " + " ".join(args))

        elif x is not None and y is not None and z is not None:
            # Separate x, y, z arrays
            x_array = np.asarray(x, dtype=np.float64).ravel()
            y_array = np.asarray(y, dtype=np.float64).ravel()
            z_array = np.asarray(z, dtype=np.float64).ravel()

            with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                session.call_module("surface", f"{vfile} " + " ".join(args))
        else:
            raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
