"""
nearneighbor - Grid table data using a nearest neighbor algorithm.

Module-level function (not a Figure method).
"""

from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def nearneighbor(
    data: np.ndarray | list | str | Path | None = None,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    outgrid: str | Path = "nearneighbor_output.nc",
    search_radius: str | float | None = None,
    region: str | list[float] | None = None,
    spacing: str | list[float] | None = None,
    sectors: int | str | None = None,
    min_sectors: int | None = None,
    empty: float | None = None,
    **kwargs,
):
    """
    Grid table data using a nearest neighbor algorithm.

    Reads randomly-spaced (x,y,z) data and produces a binary grid
    using a nearest neighbor algorithm. The grid is formed by a weighted
    average of the nearest points within a search radius.

    Based on PyGMT's nearneighbor implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data. Can be:
        - 2-D numpy array with x, y, z columns
        - Path to ASCII data file with x, y, z columns
    x, y, z : array-like, optional
        x, y, and z coordinates as separate 1-D arrays.
    outgrid : str or Path, optional
        Name of output grid file (default: "nearneighbor_output.nc").
    search_radius : str or float, optional
        Search radius for nearest neighbor.
        Format: "radius[unit]" where unit can be:
        - c : cartesian (default)
        - k : kilometers
        - m : miles
        Example: "5k" for 5 kilometers.
        Required parameter.
    region : str or list, optional
        Grid bounds. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        Required parameter.
    spacing : str or list, optional
        Grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter.
    sectors : int or str, optional
        Number of sectors for search (default: 4).
        The search area is divided into this many sectors, and at least
        min_sectors must have data for a valid grid node.
    min_sectors : int, optional
        Minimum number of sectors required to have data (default: 4).
        This ensures better data distribution around each node.
    empty : float, optional
        Value to assign to empty nodes (default: NaN).

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered data points
    >>> x = np.random.rand(100) * 10
    >>> y = np.random.rand(100) * 10
    >>> z = np.sin(x) * np.cos(y)
    >>> # Grid using nearest neighbor
    >>> pygmt.nearneighbor(
    ...     x=x, y=y, z=z,
    ...     outgrid="nn_grid.nc",
    ...     search_radius="1",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.5
    ... )
    >>>
    >>> # Use data array
    >>> data = np.column_stack([x, y, z])
    >>> pygmt.nearneighbor(
    ...     data=data,
    ...     outgrid="nn_grid2.nc",
    ...     search_radius="1",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.5,
    ...     sectors=8,
    ...     min_sectors=4
    ... )
    >>>
    >>> # From file
    >>> pygmt.nearneighbor(
    ...     data="points.txt",
    ...     outgrid="nn_grid3.nc",
    ...     search_radius="2k",
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.1
    ... )

    Notes
    -----
    The nearneighbor algorithm:
    - Finds points within search_radius of each grid node
    - Divides search area into sectors
    - Requires data in min_sectors for valid node
    - Computes weighted average based on distance

    Comparison with other gridding methods:
    - surface: Smooth continuous surface with tension splines
    - nearneighbor: Local averaging, preserves data values better
    - triangulate: Creates triangulated network

    Use nearneighbor when:
    - Data is irregularly spaced
    - Want to preserve local data characteristics
    - Need faster gridding than surface
    - Data has good coverage (not too sparse)
    """
    # Build GMT command arguments
    args = []

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Search radius (-S option) - required
    if search_radius is not None:
        args.append(f"-S{search_radius}")
    else:
        raise ValueError("search_radius parameter is required for nearneighbor()")

    # Region (-R option) - required
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for nearneighbor()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for nearneighbor()")

    # Sectors (-N option)
    if sectors is not None:
        if min_sectors is not None:
            args.append(f"-N{sectors}/{min_sectors}")
        else:
            args.append(f"-N{sectors}")

    # Empty value (-E option)
    if empty is not None:
        args.append(f"-E{empty}")

    # Execute via nanobind session
    with Session() as session:
        # Handle data input
        if data is not None:
            if isinstance(data, str | Path):
                # File input
                session.call_module("nearneighbor", f"{data} " + " ".join(args))
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
                    session.call_module("nearneighbor", f"{vfile} " + " ".join(args))

        elif x is not None and y is not None and z is not None:
            # Separate x, y, z arrays
            x_array = np.asarray(x, dtype=np.float64).ravel()
            y_array = np.asarray(y, dtype=np.float64).ravel()
            z_array = np.asarray(z, dtype=np.float64).ravel()

            with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                session.call_module("nearneighbor", f"{vfile} " + " ".join(args))
        else:
            raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
