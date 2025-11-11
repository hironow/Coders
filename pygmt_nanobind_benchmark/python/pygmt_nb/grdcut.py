"""
grdcut - Extract subregion from a grid.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def grdcut(
    grid: str | Path,
    outgrid: str | Path,
    region: str | list[float] | None = None,
    projection: str | None = None,
    **kwargs,
):
    """
    Extract subregion from a grid or image.

    Produces a new output grid file which is a subregion of the input grid.
    The subregion is specified with the region parameter.

    Based on PyGMT's grdcut implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file path.
    outgrid : str or Path
        Output grid file path for the cut region.
    region : str or list, optional
        Subregion to extract. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        Required parameter - specifies the area to cut out.
    projection : str, optional
        Map projection for oblique projections to determine rectangular region.
    **kwargs
        Additional GMT options.

    Examples
    --------
    >>> import pygmt
    >>> # Cut a subregion from a grid
    >>> pygmt.grdcut(
    ...     grid="@earth_relief_01d",
    ...     outgrid="regional.nc",
    ...     region=[130, 150, 30, 45]
    ... )
    >>>
    >>> # With projection
    >>> pygmt.grdcut(
    ...     grid="input.nc",
    ...     outgrid="output.nc",
    ...     region="g",
    ...     projection="G140/35/15c"
    ... )

    Notes
    -----
    The specified region must not exceed the range of the input grid
    (unless using the extend option). Use pygmt.grdinfo() to check the
    grid's range before cutting.
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Region (-R option) - required for grdcut
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for grdcut()")

    # Projection (-J option)
    if projection is not None:
        args.append(f"-J{projection}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdcut", " ".join(args))
