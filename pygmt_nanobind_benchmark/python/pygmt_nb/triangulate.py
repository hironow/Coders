"""
triangulate - Delaunay triangulation or Voronoi partitioning of data.

Module-level function (not a Figure method).
"""

import os
import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def triangulate(
    data: np.ndarray | list | str | Path | None = None,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    region: str | list[float] | None = None,
    output: str | Path | None = None,
    grid: str | Path | None = None,
    spacing: str | list[float] | None = None,
    **kwargs,
) -> np.ndarray | None:
    """
    Delaunay triangulation or Voronoi partitioning of Cartesian data.

    Reads one or more data tables and performs Delaunay triangulation,
    i.e., it finds how the points should be connected to give the most
    equilateral triangulation possible.

    Based on PyGMT's triangulate implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array with x, y columns (and optionally z)
        - Path to ASCII data file
    x, y : array-like, optional
        x and y coordinates as separate arrays. Used with z for 3-column input.
    z : array-like, optional
        z values for each point (optional third column).
    region : str or list, optional
        Bounding region. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
    output : str or Path, optional
        Output file for edge information. If not specified, returns array.
    grid : str or Path, optional
        Grid file to create from triangulated data (requires spacing).
    spacing : str or list, optional
        Grid spacing when creating a grid. Format: "xinc/yinc" or [xinc, yinc]

    Returns
    -------
    result : ndarray or None
        Array of triangle edges if output is None and grid is None.
        None if data is saved to file or grid.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Triangulate random points
    >>> x = np.array([0, 1, 0.5, 0.25, 0.75])
    >>> y = np.array([0, 0, 1, 0.5, 0.5])
    >>> edges = pygmt.triangulate(x=x, y=y)
    >>> print(f"Generated {len(edges)} triangle edges")
    Generated 12 triangle edges
    >>>
    >>> # Triangulate with region bounds
    >>> data = np.random.rand(20, 2) * 10
    >>> edges = pygmt.triangulate(data=data, region=[0, 10, 0, 10])
    >>>
    >>> # Create gridded surface from scattered points
    >>> x = np.random.rand(100) * 10
    >>> y = np.random.rand(100) * 10
    >>> z = np.sin(x) * np.cos(y)
    >>> pygmt.triangulate(
    ...     x=x, y=y, z=z,
    ...     grid="surface.nc",
    ...     spacing=0.5,
    ...     region=[0, 10, 0, 10]
    ... )

    Notes
    -----
    Triangulation is the first step in grid construction from scattered data.
    The resulting triangular network can be used for:
    - Contouring irregular data
    - Interpolating between points
    - Creating continuous surfaces from discrete points
    """
    # Build GMT command arguments
    args = []

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Grid output (-G option)
    if grid is not None:
        args.append(f"-G{grid}")

        # Spacing required for grid output (-I option)
        if spacing is not None:
            if isinstance(spacing, list):
                args.append(f"-I{'/'.join(str(x) for x in spacing)}")
            else:
                args.append(f"-I{spacing}")
        else:
            raise ValueError("spacing parameter is required when grid is specified")

        # Grid output doesn't return array
        return_array = False
        outfile = None
    else:
        # Prepare output for edge list
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
            # Handle data input
            if data is not None:
                if isinstance(data, (str, Path)):
                    # File input
                    cmd = f"{data} " + " ".join(args)
                    if outfile:
                        cmd += f" ->{outfile}"
                    session.call_module("triangulate", cmd)
                else:
                    # Array input - use virtual file
                    data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))
                    vectors = [data_array[:, i] for i in range(data_array.shape[1])]

                    with session.virtualfile_from_vectors(*vectors) as vfile:
                        cmd = f"{vfile} " + " ".join(args)
                        if outfile:
                            cmd += f" ->{outfile}"
                        session.call_module("triangulate", cmd)

            elif x is not None and y is not None:
                # Separate x, y (and optionally z) arrays
                x_array = np.asarray(x, dtype=np.float64).ravel()
                y_array = np.asarray(y, dtype=np.float64).ravel()

                if z is not None:
                    z_array = np.asarray(z, dtype=np.float64).ravel()
                    with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                        cmd = f"{vfile} " + " ".join(args)
                        if outfile:
                            cmd += f" ->{outfile}"
                        session.call_module("triangulate", cmd)
                else:
                    with session.virtualfile_from_vectors(x_array, y_array) as vfile:
                        cmd = f"{vfile} " + " ".join(args)
                        if outfile:
                            cmd += f" ->{outfile}"
                        session.call_module("triangulate", cmd)
            else:
                raise ValueError("Must provide either 'data' or 'x' and 'y' parameters")

        # Read output if returning array
        if return_array and outfile:
            result = np.loadtxt(outfile)
            # Ensure 2D array
            if result.ndim == 1:
                result = result.reshape(1, -1)
            return result
        else:
            return None
    finally:
        if return_array and outfile and os.path.exists(outfile):
            os.unlink(outfile)
