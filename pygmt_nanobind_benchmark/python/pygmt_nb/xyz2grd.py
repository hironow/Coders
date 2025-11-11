"""
xyz2grd - Convert table data to a grid.

Module-level function (not a Figure method).
"""

from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def xyz2grd(
    data: np.ndarray | list | str | Path,
    outgrid: str | Path,
    region: str | list[float] | None = None,
    spacing: str | list[float] | None = None,
    registration: str | None = None,
    **kwargs,
):
    """
    Convert table data to a grid file.

    Reads one or more xyz tables and creates a binary grid file. xyz2grd will
    report if some of the nodes are not filled in with data. Such unconstrained
    nodes are set to NaN.

    Based on PyGMT's xyz2grd implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array with shape (n_points, 3) containing x, y, z columns
        - Python list
        - Path to ASCII data file with x, y, z columns
    outgrid : str or Path
        Name of output grid file.
    region : str or list, optional
        Grid bounds. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        Required unless input is a file that contains region information.
    spacing : str or list, optional
        Grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter - defines the grid resolution.
    registration : str, optional
        Grid registration type:
        - "g" or None : gridline registration (default)
        - "p" : pixel registration

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create grid from XYZ data
    >>> x = np.arange(0, 5, 1)
    >>> y = np.arange(0, 5, 1)
    >>> xx, yy = np.meshgrid(x, y)
    >>> zz = xx * yy
    >>> xyz_data = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
    >>> pygmt.xyz2grd(
    ...     data=xyz_data,
    ...     outgrid="output.nc",
    ...     region=[0, 4, 0, 4],
    ...     spacing=1
    ... )
    >>>
    >>> # From file
    >>> pygmt.xyz2grd(
    ...     data="input.xyz",
    ...     outgrid="output.nc",
    ...     spacing="0.1/0.1"
    ... )

    Notes
    -----
    The xyz triplets do not have to be sorted. Missing data values are
    recognized if they are represented by NaN. All nodes without data are
    set to NaN.
    """
    # Build GMT command arguments
    args = []

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for xyz2grd()")

    # Registration (-r option)
    if registration is not None:
        if registration == "p":
            args.append("-r")  # Pixel registration

    # Execute via nanobind session
    with Session() as session:
        if isinstance(data, (str, Path)):
            # File input
            session.call_module("xyz2grd", f"{data} " + " ".join(args))
        else:
            # Array input - use virtual file
            data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

            # Check shape - should have 3 columns (x, y, z)
            if data_array.shape[1] != 3:
                raise ValueError(
                    f"Input data must have 3 columns (x, y, z), got {data_array.shape[1]}"
                )

            # Create vectors for virtual file
            vectors = [data_array[:, i] for i in range(3)]

            with session.virtualfile_from_vectors(*vectors) as vfile:
                session.call_module("xyz2grd", f"{vfile} " + " ".join(args))
