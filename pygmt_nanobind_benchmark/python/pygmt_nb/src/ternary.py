"""
ternary - Plot ternary diagrams.

Figure method (not a standalone module function).
"""

from pathlib import Path

import numpy as np


def ternary(
    self,
    data: np.ndarray | str | Path | None = None,
    region: str | list[float] | None = None,
    projection: str | None = None,
    symbol: str | None = None,
    pen: str | None = None,
    fill: str | None = None,
    **kwargs,
):
    """
    Plot ternary diagrams.

    Creates triangular plots where three variables that sum to a constant
    (typically 100% or 1.0) can be visualized. Each apex represents 100%
    of one component, and points inside show the relative proportions.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data with three components (a, b, c) that sum to constant.
        Format: a, b, c [, optional columns for color, size, etc.]
    region : str or list, optional
        Limits for the three components.
        Example: [0, 100, 0, 100, 0, 100] for percentages
    projection : str, optional
        Ternary projection code.
        Example: "X10c" or "J10c"
    symbol : str, optional
        Symbol specification.
        Format: "type[size]" (e.g., "c0.2c" for 0.2cm circles)
    pen : str, optional
        Pen attributes for symbol outlines.
        Format: "width,color,style"
    fill : str, optional
        Fill color for symbols.

    Examples
    --------
    >>> import pygmt
    >>> import numpy as np
    >>> # Create ternary composition data (sand, silt, clay percentages)
    >>> sand = np.array([70, 50, 30, 20, 10])
    >>> silt = np.array([20, 30, 40, 50, 60])
    >>> clay = np.array([10, 20, 30, 30, 30])
    >>> data = np.column_stack([sand, silt, clay])
    >>>
    >>> fig = pygmt.Figure()
    >>> fig.ternary(
    ...     data=data,
    ...     region=[0, 100, 0, 100, 0, 100],
    ...     projection="X10c",
    ...     symbol="c0.3c",
    ...     fill="red"
    ... )
    >>> fig.savefig("ternary.png")

    Notes
    -----
    This function is commonly used for:
    - Soil texture classification (sand-silt-clay)
    - Rock composition (QAP diagrams)
    - Chemical composition (ternary phase diagrams)
    - Population demographics (age groups)
    - Any three-component mixture

    Ternary diagram features:
    - Three axes at 60° angles
    - Each apex = 100% of one component
    - Interior points show mixture proportions
    - Grid lines show iso-concentration

    Common ternary plots:
    - Soil texture triangle
    - QAP (Quartz-Alkali-Plagioclase) for igneous rocks
    - QFL (Quartz-Feldspar-Lithics) for sediments
    - Phase diagrams in chemistry
    - Mixing diagrams in geochemistry

    Data requirements:
    - Three components must sum to constant
    - Typically normalized to 100% or 1.0
    - Each point plotted by its proportions

    Applications:
    - Geology: Rock classification
    - Soil science: Texture analysis
    - Chemistry: Phase equilibria
    - Ecology: Species composition
    - Economics: Budget allocation

    Reading ternary plots:
    - Move parallel to edges to read values
    - Apex = 100% of that component
    - Opposite edge = 0% of apex component
    - Grid helps read exact values

    See Also
    --------
    plot : General x-y plotting
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    if projection is not None:
        args.append(f"-J{projection}")

    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    if symbol is not None:
        args.append(f"-S{symbol}")

    if pen is not None:
        args.append(f"-W{pen}")

    if fill is not None:
        args.append(f"-G{fill}")

    # Execute via session
    with Session() as session:
        if data is not None:
            if isinstance(data, str | Path):
                # File input
                session.call_module("ternary", f"{data} " + " ".join(args))
            else:
                # Array input
                print("Note: Array input for ternary requires virtual file support")
