"""
makecpt - Make GMT color palette tables.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def makecpt(
    cmap: str | None = None,
    series: str | list[float] | None = None,
    reverse: bool = False,
    continuous: bool = False,
    output: str | Path | None = None,
    **kwargs,
):
    """
    Make GMT color palette tables (CPTs).

    Creates static color palette tables for use with GMT plotting functions.
    By default, the CPT is saved as the current CPT of the session.

    Based on PyGMT's makecpt implementation for API compatibility.

    Parameters
    ----------
    cmap : str, optional
        Name of GMT master color palette table (e.g., "viridis", "jet", "hot").
        See GMT documentation for available colormaps.
    series : str or list, optional
        Color range specification. Format: "min/max/inc" or [min, max, inc].
        Example: "0/100/10" or [0, 100, 10]
    reverse : bool, default False
        Reverse the color palette.
    continuous : bool, default False
        Create a continuous color palette instead of discrete.
    output : str or Path, optional
        File path to save the CPT. If not provided, CPT becomes current session CPT.
    **kwargs
        Additional GMT options.

    Examples
    --------
    >>> import pygmt
    >>> # Create a color palette for elevation data
    >>> pygmt.makecpt(cmap="geo", series="-8000/8000/1000")
    >>>
    >>> # Save to file
    >>> pygmt.makecpt(
    ...     cmap="viridis",
    ...     series=[0, 100, 10],
    ...     output="my_colors.cpt"
    ... )

    Notes
    -----
    This function wraps GMT's makecpt module. The created CPT is automatically
    used by subsequent plotting functions that require color mapping.
    """
    # Build GMT command arguments
    args = []

    # Master colormap (-C option)
    if cmap is not None:
        args.append(f"-C{cmap}")

    # Series/range (-T option)
    if series is not None:
        if isinstance(series, list):
            args.append(f"-T{'/'.join(str(x) for x in series)}")
        else:
            args.append(f"-T{series}")

    # Reverse colormap (-I option)
    if reverse:
        args.append("-I")

    # Continuous palette (-Z option)
    if continuous:
        args.append("-Z")

    # Output file (-H option)
    if output is not None:
        args.append(f"-H>{output}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("makecpt", " ".join(args))
