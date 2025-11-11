"""
grdsample - Resample a grid onto a new lattice.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def grdsample(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    spacing: Optional[Union[str, List[float]]] = None,
    region: Optional[Union[str, List[float]]] = None,
    registration: Optional[str] = None,
    translate: bool = False,
    **kwargs
):
    """
    Resample a grid onto a new lattice.

    Reads a grid and interpolates it to create a new grid with
    different spacing and/or registration. Several interpolation
    methods are available.

    Based on PyGMT's grdsample implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name.
    spacing : str or list, optional
        Output grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]"
        or [xinc, yinc].
        If not specified, uses input grid spacing.
    region : str or list, optional
        Output grid region. Format: [xmin, xmax, ymin, ymax] or
        "xmin/xmax/ymin/ymax".
        If not specified, uses input grid region.
    registration : str, optional
        Grid registration type:
        - "g" : gridline registration
        - "p" : pixel registration
        If not specified, uses input grid registration.
    translate : bool, optional
        Just translate between grid and pixel registration;
        no resampling (default: False).

    Examples
    --------
    >>> import pygmt
    >>> # Resample to coarser resolution
    >>> pygmt.grdsample(
    ...     grid="@earth_relief_01d",
    ...     outgrid="coarse.nc",
    ...     spacing="0.5",
    ...     region=[0, 10, 0, 10]
    ... )
    >>>
    >>> # Resample to finer resolution
    >>> pygmt.grdsample(
    ...     grid="input.nc",
    ...     outgrid="fine.nc",
    ...     spacing="0.01/0.01"
    ... )
    >>>
    >>> # Change registration
    >>> pygmt.grdsample(
    ...     grid="gridline.nc",
    ...     outgrid="pixel.nc",
    ...     registration="p",
    ...     translate=True
    ... )

    Notes
    -----
    This function is commonly used for:
    - Changing grid resolution (upsampling or downsampling)
    - Converting between grid and pixel registration
    - Extracting subregions at different resolutions
    - Matching grid resolutions for operations

    Interpolation methods:
    - Default: Bilinear interpolation
    - For coarsening: Box-car filter to prevent aliasing
    - For translate: Simple grid/pixel conversion

    Performance notes:
    - Downsampling (coarser) is fast
    - Upsampling (finer) requires more computation
    - translate mode is fastest (no interpolation)
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Spacing (-I option)
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Registration (-r option for pixel, default is gridline)
    if registration is not None:
        if registration == "p":
            args.append("-r")

    # Translate mode (-T option)
    if translate:
        args.append("-T")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdsample", " ".join(args))
