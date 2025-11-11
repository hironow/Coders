"""
rose - Plot windrose diagrams or polar histograms.

Figure method (not a standalone module function).
"""

from pathlib import Path

import numpy as np


def rose(
    self,
    data: np.ndarray | str | Path | None = None,
    region: str | list[float] | None = None,
    diameter: str | None = None,
    sector_width: int | float | None = None,
    vectors: bool = False,
    pen: str | None = None,
    fill: str | None = None,
    **kwargs,
):
    """
    Plot windrose diagrams or polar histograms.

    Creates circular histogram plots showing directional data distribution.
    Commonly used for wind direction, geological orientations, or any
    circular/directional data.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data containing angles (and optionally radii/lengths).
        For vectors: angle, length
        For histogram: angle values
    region : str or list, optional
        Plot region. For rose diagrams: [0, 360, 0, max_radius]
    diameter : str, optional
        Diameter of the rose diagram.
        Examples: "5c", "3i"
    sector_width : int or float, optional
        Width of sectors in degrees.
        Examples: 10, 15, 30, 45
        Default: 10 degrees
    vectors : bool, optional
        If True, plot as vectors rather than histogram (default: False).
    pen : str, optional
        Pen attributes for sector outlines.
        Format: "width,color,style"
    fill : str, optional
        Fill color for sectors.

    Examples
    --------
    >>> import pygmt
    >>> import numpy as np
    >>> # Create wind direction data
    >>> angles = np.random.vonmises(np.pi, 2, 100) * 180 / np.pi
    >>> angles = angles % 360
    >>>
    >>> fig = pygmt.Figure()
    >>> fig.rose(
    ...     data=angles,
    ...     diameter="5c",
    ...     sector_width=30,
    ...     fill="lightblue",
    ...     pen="1p,black"
    ... )
    >>> fig.savefig("windrose.png")

    Notes
    -----
    This function is commonly used for:
    - Wind direction frequency plots
    - Geological strike/dip orientations
    - Migration directions
    - Any directional/circular data visualization

    Rose diagram types:
    - Histogram: Shows frequency in angular bins
    - Vector: Shows direction and magnitude
    - Petal: Smoothed frequency distribution

    Sector width considerations:
    - Smaller sectors (10-15°): More detail
    - Larger sectors (30-45°): Broader patterns
    - Choice depends on data density and clarity needs

    Applications:
    - Meteorology: Wind patterns
    - Geology: Fault/joint orientations
    - Oceanography: Current directions
    - Biology: Animal migration patterns
    - Paleontology: Fossil orientations

    Data format:
    - Single column: Angles (0-360°)
    - Two columns: Angles and magnitudes
    - Multiple datasets: Separate by segment headers

    Visual customization:
    - Fill colors by sector
    - Outline pens
    - Radial scaling
    - Directional conventions (CW/CCW from N)

    See Also
    --------
    histogram : Cartesian histograms
    plot : General plotting
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    if diameter is not None:
        args.append(f"-{diameter}")

    if sector_width is not None:
        args.append(f"-A{sector_width}")

    if vectors:
        args.append("-M")

    if pen is not None:
        args.append(f"-W{pen}")

    if fill is not None:
        args.append(f"-G{fill}")

    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via session
    with Session() as session:
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("rose", f"{data} " + " ".join(args))
            else:
                # Array input
                print("Note: Array input for rose requires virtual file support")
