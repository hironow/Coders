"""
sphinterpolate - Spherical gridding in tension of data on a sphere.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np

from pygmt_nb.clib import Session


def sphinterpolate(
    data: Optional[Union[np.ndarray, str, Path]] = None,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    z: Optional[np.ndarray] = None,
    outgrid: Union[str, Path] = "sphinterpolate_output.nc",
    region: Union[str, List[float]] = None,
    spacing: Union[str, List[float]] = None,
    tension: Optional[float] = None,
    **kwargs
):
    """
    Spherical gridding in tension of data on a sphere.

    Reads (lon, lat, z) data and performs Delaunay triangulation
    on a sphere, then interpolates the data to a regular grid using
    spherical splines in tension.

    Based on PyGMT's sphinterpolate implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data. Can be:
        - 2-D or 3-D numpy array with lon, lat, z columns
        - Path to ASCII data file with lon, lat, z columns
    x, y, z : array-like, optional
        Longitude, latitude, and Z values as separate 1-D arrays.
    outgrid : str or Path
        Output grid file name. Default: "sphinterpolate_output.nc"
    region : str or list
        Grid bounds. Format: [lonmin, lonmax, latmin, latmax]
        Required parameter.
    spacing : str or list
        Grid spacing. Format: "xinc[unit][/yinc[unit]]" or [xinc, yinc]
        Required parameter.
    tension : float, optional
        Tension factor between 0 and 1. Default is 0 (minimum curvature).
        Higher values (e.g., 0.25-0.75) create tighter fits to data.

    Returns
    -------
    None
        Writes grid to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered data on sphere
    >>> lon = np.array([0, 90, 180, 270, 45, 135, 225, 315])
    >>> lat = np.array([0, 30, 0, -30, 60, -60, 45, -45])
    >>> z = np.array([1.0, 2.0, 1.5, 0.5, 3.0, 0.2, 2.5, 1.8])
    >>>
    >>> # Interpolate to regular grid
    >>> pygmt.sphinterpolate(
    ...     x=lon, y=lat, z=z,
    ...     outgrid="interpolated.nc",
    ...     region=[0, 360, -90, 90],
    ...     spacing=5
    ... )
    >>>
    >>> # With tension for tighter fit
    >>> pygmt.sphinterpolate(
    ...     x=lon, y=lat, z=z,
    ...     outgrid="interpolated_tension.nc",
    ...     region=[0, 360, -90, 90],
    ...     spacing=5,
    ...     tension=0.5
    ... )
    >>>
    >>> # From data array
    >>> data = np.column_stack([lon, lat, z])
    >>> pygmt.sphinterpolate(
    ...     data=data,
    ...     outgrid="grid.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing=2
    ... )

    Notes
    -----
    This function is commonly used for:
    - Global data interpolation respecting spherical geometry
    - Geophysical data on spherical surfaces
    - Meteorological/climate data gridding
    - Satellite data interpolation

    Spherical interpolation:
    - Uses Delaunay triangulation on sphere
    - Respects great circle distances
    - Accounts for poles and dateline
    - More accurate than Cartesian for global data

    Tension parameter:
    - tension=0: Minimum curvature (smooth)
    - tension=0.5: Balanced (typical)
    - tension→1: Tighter fit to data (less smooth)
    - Higher tension reduces overshoots between points

    Applications:
    - Global temperature/precipitation grids
    - Geoid and gravity field modeling
    - Satellite altimetry interpolation
    - Spherical harmonic analysis preprocessing

    Comparison with related functions:
    - sphinterpolate: Spherical splines, respects sphere geometry
    - surface: Cartesian splines with tension
    - nearneighbor: Simple nearest neighbor (faster, less smooth)
    - triangulate: Just triangulation, no interpolation

    Advantages:
    - Proper spherical distance calculation
    - Handles polar regions correctly
    - No distortion from map projections
    - Suitable for global datasets

    Workflow:
    1. Collect scattered data (lon, lat, z)
    2. Choose appropriate region and spacing
    3. Set tension (0-1, typically 0.25-0.75)
    4. Interpolate to regular grid
    5. Visualize or analyze results
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
        raise ValueError("region parameter is required for sphinterpolate()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for sphinterpolate()")

    # Tension (-T option)
    if tension is not None:
        args.append(f"-T{tension}")

    # Execute via nanobind session
    with Session() as session:
        # Handle data input
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("sphinterpolate", f"{data} " + " ".join(args))
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Check for at least 3 columns (lon, lat, z)
                if data_array.shape[1] < 3:
                    raise ValueError(
                        f"data array must have at least 3 columns (lon, lat, z), got {data_array.shape[1]}"
                    )

                # Create vectors for virtual file
                vectors = [data_array[:, i] for i in range(3)]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("sphinterpolate", f"{vfile} " + " ".join(args))

        elif x is not None and y is not None and z is not None:
            # Separate x, y, z arrays
            x_array = np.asarray(x, dtype=np.float64).ravel()
            y_array = np.asarray(y, dtype=np.float64).ravel()
            z_array = np.asarray(z, dtype=np.float64).ravel()

            with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                session.call_module("sphinterpolate", f"{vfile} " + " ".join(args))
        else:
            raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
