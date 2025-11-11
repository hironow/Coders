"""
grdproject - Forward and inverse map transformation of grids.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def grdproject(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    projection: Optional[str] = None,
    inverse: bool = False,
    region: Optional[Union[str, List[float]]] = None,
    spacing: Optional[Union[str, List[float]]] = None,
    center: Optional[Union[str, List[float]]] = None,
    **kwargs
):
    """
    Forward and inverse map transformation of grids.

    Reads a grid and performs forward or inverse map projection
    transformation. Can be used to project geographic grids to
    Cartesian coordinates or vice versa.

    Based on PyGMT's grdproject implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name.
    projection : str, optional
        Map projection. Examples:
        - "M10c" : Mercator, 10 cm width
        - "U+10c" : UTM, 10 cm width
        - "X" : Cartesian (for inverse projection)
        Required for forward projection.
    inverse : bool, optional
        Perform inverse transformation (projected → geographic).
        Default: False (forward: geographic → projected).
    region : str or list, optional
        Output region. Format: [xmin, xmax, ymin, ymax]
        If not specified, computed from input.
    spacing : str or list, optional
        Output grid spacing. Format: "xinc/yinc" or [xinc, yinc]
        If not specified, computed from input.
    center : str or list, optional
        Projection center. Format: [lon, lat] or "lon/lat"
        Used for certain projections.

    Examples
    --------
    >>> import pygmt
    >>> # Forward projection: geographic to Mercator
    >>> pygmt.grdproject(
    ...     grid="@earth_relief_01d",
    ...     outgrid="mercator.nc",
    ...     projection="M10c",
    ...     region=[0, 10, 0, 10]
    ... )
    >>>
    >>> # Inverse projection: Mercator back to geographic
    >>> pygmt.grdproject(
    ...     grid="mercator.nc",
    ...     outgrid="geographic.nc",
    ...     projection="M10c",
    ...     inverse=True
    ... )
    >>>
    >>> # UTM projection with specific zone
    >>> pygmt.grdproject(
    ...     grid="geographic.nc",
    ...     outgrid="utm.nc",
    ...     projection="U+32/10c",
    ...     region=[-120, -110, 30, 40]
    ... )

    Notes
    -----
    This function is commonly used for:
    - Converting geographic grids to projected coordinates
    - Converting projected grids back to geographic
    - Preparing grids for distance calculations
    - Matching different grid coordinate systems

    Projection types:
    - M : Mercator
    - U : Universal Transverse Mercator (UTM)
    - T : Transverse Mercator
    - L : Lambert Conic
    - And many others supported by GMT

    Important considerations:
    - Forward projection: geographic (lon/lat) → projected (x/y)
    - Inverse projection: projected (x/y) → geographic (lon/lat)
    - Spacing and region may need adjustment for projected grids
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Projection (-J option) - required for most operations
    if projection is not None:
        args.append(f"-J{projection}")
    else:
        if not inverse:
            raise ValueError("projection parameter is required for forward projection")

    # Inverse transformation (-I option)
    if inverse:
        args.append("-I")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Spacing (-I option for output spacing, but -D is used in grdproject)
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-D{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-D{spacing}")

    # Center (-C option)
    if center is not None:
        if isinstance(center, list):
            args.append(f"-C{'/'.join(str(x) for x in center)}")
        else:
            args.append(f"-C{center}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdproject", " ".join(args))
