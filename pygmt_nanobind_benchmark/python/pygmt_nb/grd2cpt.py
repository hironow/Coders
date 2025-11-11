"""
grd2cpt - Make GMT color palette table from a grid file.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def grd2cpt(
    grid: str | Path,
    output: str | Path | None = None,
    cmap: str | None = None,
    continuous: bool = False,
    reverse: bool = False,
    truncate: str | list[float] | None = None,
    region: str | list[float] | None = None,
    **kwargs,
):
    """
    Make GMT color palette table from a grid file.

    Reads a grid and creates a color palette table (CPT) that spans
    the data range. The CPT can be based on built-in colormaps or
    custom ranges.

    Based on PyGMT's grd2cpt implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    output : str or Path, optional
        Output CPT file name. If not specified, writes to default GMT CPT.
    cmap : str, optional
        Name of GMT colormap to use as template.
        Examples: "viridis", "jet", "rainbow", "polar", "haxby"
        If not specified, uses "rainbow".
    continuous : bool, optional
        Create a continuous CPT (default: False, discrete).
    reverse : bool, optional
        Reverse the colormap (default: False).
    truncate : str or list, optional
        Truncate colormap to z-range. Format: [zlow, zhigh] or "zlow/zhigh"
        Example: [0, 100] uses only colors for range 0-100
    region : str or list, optional
        Subregion of grid to use. Format: [xmin, xmax, ymin, ymax]

    Examples
    --------
    >>> import pygmt
    >>> # Create CPT from grid data range
    >>> pygmt.grd2cpt(
    ...     grid="@earth_relief_01d",
    ...     output="topo.cpt",
    ...     cmap="geo"
    ... )
    >>>
    >>> # Create continuous CPT
    >>> pygmt.grd2cpt(
    ...     grid="elevation.nc",
    ...     output="elevation.cpt",
    ...     cmap="viridis",
    ...     continuous=True
    ... )
    >>>
    >>> # Create reversed CPT
    >>> pygmt.grd2cpt(
    ...     grid="data.nc",
    ...     output="data_reversed.cpt",
    ...     cmap="jet",
    ...     reverse=True
    ... )
    >>>
    >>> # Truncate to specific range
    >>> pygmt.grd2cpt(
    ...     grid="temperature.nc",
    ...     output="temp.cpt",
    ...     cmap="hot",
    ...     truncate=[0, 40]
    ... )

    Notes
    -----
    This function is commonly used for:
    - Creating colormaps matched to data range
    - Automatic color scaling for grids
    - Custom visualization palettes
    - Preparing CPTs for plotting

    Color palette types:
    - Discrete: Sharp color boundaries (default)
    - Continuous: Smooth color transitions (with -Z)

    Built-in GMT colormaps include:
    - Scientific: viridis, plasma, inferno, magma
    - Traditional: jet, rainbow, hot, cool
    - Diverging: polar, red2green, split
    - Topographic: geo, relief, globe, topo

    Workflow:
    1. Read grid to find data range
    2. Select/create colormap spanning range
    3. Write CPT file
    4. Use CPT with grdimage or other plotting

    The output CPT can be used with:
    - fig.grdimage(cmap="output.cpt")
    - fig.colorbar(cmap="output.cpt")
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Colormap (-C option)
    if cmap is not None:
        args.append(f"-C{cmap}")
    else:
        # Default to rainbow if not specified
        args.append("-Crainbow")

    # Continuous (-Z option)
    if continuous:
        args.append("-Z")

    # Reverse (-I option)
    if reverse:
        args.append("-I")

    # Truncate (-T option)
    if truncate is not None:
        if isinstance(truncate, list):
            args.append(f"-T{'/'.join(str(x) for x in truncate)}")
        else:
            args.append(f"-T{truncate}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        if output is not None:
            # Output redirection
            session.call_module("grd2cpt", " ".join(args) + f" >{output}")
        else:
            session.call_module("grd2cpt", " ".join(args))
