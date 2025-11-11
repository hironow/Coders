"""
sphdistance - Create Voronoi distance, node, or natural nearest-neighbor grid on a sphere.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np
import tempfile
import os

from pygmt_nb.clib import Session


def sphdistance(
    data: Optional[Union[np.ndarray, str, Path]] = None,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    outgrid: Union[str, Path] = "sphdistance_output.nc",
    region: Optional[Union[str, List[float]]] = None,
    spacing: Optional[Union[str, List[float]]] = None,
    unit: Optional[str] = None,
    quantity: Optional[str] = None,
    **kwargs
):
    """
    Create Voronoi distance, node, or natural nearest-neighbor grid on a sphere.

    Reads lon,lat locations of points and computes the distance to the
    nearest point for all nodes in the output grid on a sphere. Optionally
    can compute Voronoi polygons or node IDs.

    Based on PyGMT's sphdistance implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data. Can be:
        - 2-D numpy array with lon, lat columns
        - Path to ASCII data file with lon, lat columns
    x, y : array-like, optional
        Longitude and latitude coordinates as separate 1-D arrays.
    outgrid : str or Path, optional
        Output grid file name. Default: "sphdistance_output.nc"
    region : str or list, optional
        Grid bounds. Format: [lonmin, lonmax, latmin, latmax]
        Required parameter.
    spacing : str or list, optional
        Grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter.
    unit : str, optional
        Specify the unit used for distance calculations:
        - "d" : spherical degrees (default)
        - "e" : meters
        - "f" : feet
        - "k" : kilometers
        - "M" : miles
        - "n" : nautical miles
        - "u" : survey feet
    quantity : str, optional
        Specify quantity to compute:
        - "d" : distances to nearest point (default)
        - "n" : node IDs (which point is nearest: 0, 1, 2, ...)
        - "z" : natural nearest-neighbor grid values (requires z column)

    Returns
    -------
    None
        Writes grid to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered points
    >>> lon = [0, 90, 180, 270]
    >>> lat = [0, 30, -30, 60]
    >>> # Compute distance to nearest point in kilometers
    >>> pygmt.sphdistance(
    ...     x=lon, y=lat,
    ...     outgrid="distances.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing=5,
    ...     unit="k"  # distances in km
    ... )
    >>>
    >>> # Compute node IDs (which point is nearest)
    >>> pygmt.sphdistance(
    ...     x=lon, y=lat,
    ...     outgrid="node_ids.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing=5,
    ...     quantity="n"  # node IDs
    ... )
    >>>
    >>> # From data array with distances in degrees
    >>> data = np.array([[0, 0], [90, 30], [180, -30], [270, 60]])
    >>> pygmt.sphdistance(
    ...     data=data,
    ...     outgrid="distances.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing=5,
    ...     unit="d"  # distances in degrees
    ... )

    Notes
    -----
    This function is commonly used for:
    - Spatial proximity analysis on a sphere
    - Creating distance fields around point features
    - Identifying nearest station/sensor for each location
    - Voronoi tessellation on spherical surfaces

    Output types:
    - Distance grid (default): Shows distance to nearest point
    - Node ID grid (-N): Shows which input point is nearest (0, 1, 2, ...)
    - Voronoi distance (-D): Distance in specified units

    Spherical computation:
    - Uses great circle distances on sphere
    - Accounts for Earth's curvature
    - More accurate than Cartesian distance for geographic data

    Applications:
    - Station coverage analysis
    - Nearest facility mapping
    - Interpolation weight computation
    - Data density visualization
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
        raise ValueError("region parameter is required for sphdistance()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for sphdistance()")

    # Unit (-L option)
    if unit is not None:
        args.append(f"-L{unit}")

    # Quantity (-Q option)
    if quantity is not None:
        args.append(f"-Q{quantity}")

    # Execute via nanobind session
    with Session() as session:
        # Handle data input
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("sphdistance", f"{data} " + " ".join(args))
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Check for at least 2 columns (lon, lat)
                if data_array.shape[1] < 2:
                    raise ValueError(
                        f"data array must have at least 2 columns (lon, lat), got {data_array.shape[1]}"
                    )

                # Create vectors for virtual file
                n_cols = min(3, data_array.shape[1]) if quantity else 2
                vectors = [data_array[:, i] for i in range(n_cols)]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("sphdistance", f"{vfile} " + " ".join(args))

        elif x is not None and y is not None:
            # Separate x, y arrays
            x_array = np.asarray(x, dtype=np.float64).ravel()
            y_array = np.asarray(y, dtype=np.float64).ravel()

            with session.virtualfile_from_vectors(x_array, y_array) as vfile:
                session.call_module("sphdistance", f"{vfile} " + " ".join(args))
        else:
            raise ValueError("Must provide either 'data' or 'x', 'y' parameters")
