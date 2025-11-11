"""
grdclip - Clip grid values.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def grdclip(
    grid: str | Path,
    outgrid: str | Path,
    above: str | list | None = None,
    below: str | list | None = None,
    between: str | list | None = None,
    region: str | list[float] | None = None,
    **kwargs,
):
    """
    Clip grid values.

    Sets all values in a grid that fall outside or inside specified ranges
    to constant values. Can be used to remove outliers, cap extreme values,
    or create masks.

    Based on PyGMT's grdclip implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name.
    above : str or list, optional
        Replace all values above a threshold.
        Format: [high, new_value] or "high/new_value"
        Example: [100, 100] clips all values >100 to 100
    below : str or list, optional
        Replace all values below a threshold.
        Format: [low, new_value] or "low/new_value"
        Example: [0, 0] clips all values <0 to 0
    between : str or list, optional
        Replace all values between two thresholds.
        Format: [low, high, new_value] or "low/high/new_value"
        Example: [-1, 1, 0] sets all values in [-1, 1] to 0
    region : str or list, optional
        Subregion to operate on. Format: [xmin, xmax, ymin, ymax]

    Examples
    --------
    >>> import pygmt
    >>> # Clip values above 100
    >>> pygmt.grdclip(
    ...     grid="input.nc",
    ...     outgrid="clipped.nc",
    ...     above=[100, 100]
    ... )
    >>>
    >>> # Clip values below 0 to 0
    >>> pygmt.grdclip(
    ...     grid="elevation.nc",
    ...     outgrid="nonnegative.nc",
    ...     below=[0, 0]
    ... )
    >>>
    >>> # Clip outliers on both ends
    >>> pygmt.grdclip(
    ...     grid="data.nc",
    ...     outgrid="cleaned.nc",
    ...     above=[1000, 1000],
    ...     below=[-1000, -1000]
    ... )
    >>>
    >>> # Replace values in range with constant
    >>> pygmt.grdclip(
    ...     grid="data.nc",
    ...     outgrid="masked.nc",
    ...     between=[-10, 10, 0]
    ... )

    Notes
    -----
    This function is commonly used for:
    - Removing outliers from grids
    - Creating value masks
    - Capping extreme values
    - Setting valid data ranges

    Operations are applied in this order:
    1. below: Values less than threshold
    2. above: Values greater than threshold
    3. between: Values within range

    Special values:
    - Use "NaN" or np.nan as new_value to set to NaN
    - Multiple operations can be combined
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Above threshold (-Sa option)
    if above is not None:
        if isinstance(above, list):
            args.append(f"-Sa{'/'.join(str(x) for x in above)}")
        else:
            args.append(f"-Sa{above}")

    # Below threshold (-Sb option)
    if below is not None:
        if isinstance(below, list):
            args.append(f"-Sb{'/'.join(str(x) for x in below)}")
        else:
            args.append(f"-Sb{below}")

    # Between thresholds (-Si option)
    if between is not None:
        if isinstance(between, list):
            args.append(f"-Si{'/'.join(str(x) for x in between)}")
        else:
            args.append(f"-Si{between}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdclip", " ".join(args))
