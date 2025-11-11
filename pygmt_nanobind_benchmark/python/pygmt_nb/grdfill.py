"""
grdfill - Interpolate across holes in a grid.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def grdfill(
    grid: str | Path,
    outgrid: str | Path,
    mode: str | None = None,
    region: str | list[float] | None = None,
    **kwargs,
):
    """
    Interpolate across holes (NaN values) in a grid.

    Reads a grid that may have holes (undefined nodes) and fills
    them using one of several interpolation algorithms.

    Based on PyGMT's grdfill implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name with holes filled.
    mode : str, optional
        Algorithm for filling holes:
        - "c" : Constant fill (use with value, e.g., "c0")
        - "n" : Nearest neighbor
        - "s" : Spline interpolation
        - "a[radius]" : Search and fill within radius
        Default: "n" (nearest neighbor)
    region : str or list, optional
        Subregion to operate on. Format: [xmin, xmax, ymin, ymax]

    Examples
    --------
    >>> import pygmt
    >>> # Fill holes using nearest neighbor
    >>> pygmt.grdfill(
    ...     grid="incomplete.nc",
    ...     outgrid="filled.nc",
    ...     mode="n"
    ... )
    >>>
    >>> # Fill with constant value
    >>> pygmt.grdfill(
    ...     grid="incomplete.nc",
    ...     outgrid="filled_zero.nc",
    ...     mode="c0"
    ... )
    >>>
    >>> # Fill with spline interpolation
    >>> pygmt.grdfill(
    ...     grid="incomplete.nc",
    ...     outgrid="filled_smooth.nc",
    ...     mode="s"
    ... )
    >>>
    >>> # Fill within search radius
    >>> pygmt.grdfill(
    ...     grid="incomplete.nc",
    ...     outgrid="filled_local.nc",
    ...     mode="a5"  # 5-node radius
    ... )

    Notes
    -----
    This function is commonly used for:
    - Filling gaps in satellite data
    - Completing incomplete DEMs
    - Removing data holes before interpolation
    - Preparing grids for contouring

    Algorithm comparison:
    - Constant (c): Fast, simple, uniform fill
    - Nearest (n): Fast, preserves nearby values
    - Spline (s): Smooth interpolation, good for gradual changes
    - Search (a): Local averaging within radius

    NaN handling:
    - Only fills existing NaN values
    - Does not modify valid data points
    - Output has same dimensions as input
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Fill mode (-A option)
    if mode is not None:
        args.append(f"-A{mode}")
    else:
        # Default to nearest neighbor
        args.append("-An")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdfill", " ".join(args))
