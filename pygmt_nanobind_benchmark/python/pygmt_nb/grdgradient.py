"""
grdgradient - Calculate directional gradients from a grid.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def grdgradient(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    azimuth: Optional[Union[float, str]] = None,
    direction: Optional[str] = None,
    normalize: Optional[Union[bool, str]] = None,
    slope_file: Optional[Union[str, Path]] = None,
    radiance: Optional[Union[str, float]] = None,
    region: Optional[Union[str, List[float]]] = None,
    **kwargs
):
    """
    Compute the directional derivative of a grid.

    Computes the directional derivative in a given direction, or to find
    the direction of the maximal gradient of the data. Can also compute
    the magnitude of the gradient.

    Based on PyGMT's grdgradient implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name for gradient.
    azimuth : float or str, optional
        Azimuthal direction for directional derivative.
        Format: angle in degrees (0-360) or special values:
        - 0 or 360: gradient in x-direction (east)
        - 90: gradient in y-direction (north)
        - 180: gradient in negative x-direction (west)
        - 270: gradient in negative y-direction (south)
    direction : str, optional
        Direction mode:
        - "a" : Compute aspect (direction of steepest descent)
        - "c" : Compute combination of slope and aspect
        - "g" : Compute magnitude of gradient
        - "n" : Compute direction of steepest descent (azimuth)
    normalize : bool or str, optional
        Normalize gradient output:
        - True or "t" : Normalize by RMS amplitude
        - "e" : Normalize by Laplacian
        - str : Custom normalization method
    slope_file : str or Path, optional
        Grid file to save slope magnitudes.
    radiance : str or float, optional
        Radiance settings for shaded relief.
        Format: "azimuth/elevation" or just elevation.
    region : str or list, optional
        Subregion to operate on. Format: [xmin, xmax, ymin, ymax]

    Examples
    --------
    >>> import pygmt
    >>> # Compute gradient in east direction
    >>> pygmt.grdgradient(
    ...     grid="@earth_relief_01d",
    ...     outgrid="gradient_east.nc",
    ...     azimuth=90,
    ...     region=[0, 10, 0, 10]
    ... )
    >>>
    >>> # Compute illumination for shaded relief
    >>> pygmt.grdgradient(
    ...     grid="@earth_relief_01d",
    ...     outgrid="illumination.nc",
    ...     azimuth=315,
    ...     normalize=True,
    ...     region=[0, 10, 0, 10]
    ... )
    >>>
    >>> # Compute magnitude of gradient
    >>> pygmt.grdgradient(
    ...     grid="topography.nc",
    ...     outgrid="gradient_magnitude.nc",
    ...     direction="g"
    ... )

    Notes
    -----
    This function is commonly used for:
    - Creating shaded relief maps (illumination)
    - Computing slope and aspect from DEMs
    - Enhancing features in gridded data
    - Detecting edges and boundaries in grids

    The gradient direction convention:
    - 0°/360° points East
    - 90° points North
    - 180° points West
    - 270° points South
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Azimuth (-A option)
    if azimuth is not None:
        args.append(f"-A{azimuth}")

    # Direction mode (-D option)
    if direction is not None:
        args.append(f"-D{direction}")

    # Normalize (-N option)
    if normalize is not None:
        if isinstance(normalize, bool):
            if normalize:
                args.append("-N")
        else:
            args.append(f"-N{normalize}")

    # Slope file (-S option)
    if slope_file is not None:
        args.append(f"-S{slope_file}")

    # Radiance (-E option for Peucker algorithm)
    if radiance is not None:
        args.append(f"-E{radiance}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdgradient", " ".join(args))
