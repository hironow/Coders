"""
hlines - Plot horizontal lines.

Figure method (not a standalone module function).
"""



def hlines(
    self,
    y: float | list[float],
    pen: str | None = None,
    label: str | None = None,
    **kwargs,
):
    """
    Plot horizontal lines.

    Plot one or more horizontal lines at specified y-coordinates across
    the entire plot region.

    Parameters
    ----------
    y : float or list of float
        Y-coordinate(s) for horizontal line(s).
        Can be a single value or list of values.
    pen : str, optional
        Pen attribute for the line(s).
        Format: "width,color,style"
        Examples: "1p,black", "2p,red,dashed", "0.5p,blue,dotted"
    label : str, optional
        Label for legend entry.

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> # Single horizontal line at y=5
    >>> fig.hlines(y=5, pen="1p,black")
    >>> fig.savefig("hline.png")
    >>>
    >>> # Multiple horizontal lines
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.hlines(y=[2, 5, 8], pen="1p,red,dashed")
    >>> fig.savefig("hlines_multiple.png")
    >>>
    >>> # Horizontal line with custom pen
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.hlines(y=7, pen="2p,blue,dotted")
    >>> fig.savefig("hline_styled.png")

    Notes
    -----
    This is a convenience function that wraps GMT's plot module with
    horizontal line functionality. It's useful for:
    - Adding reference lines
    - Marking thresholds or targets
    - Separating plot regions
    - Adding grid-like visual guides

    The lines extend across the entire x-range of the current plot region.

    See Also
    --------
    vlines : Plot vertical lines
    plot : General plotting function
    """
    from pygmt_nb.clib import Session

    # Convert single value to list for uniform processing
    if not isinstance(y, list | tuple):
        y = [y]

    # Build GMT command for each line
    with Session() as session:
        for y_val in y:
            # Create data for horizontal line spanning plot region
            # Use > to separate segments if multiple lines
            # GMT plot with -W for pen
            args = []

            if pen is not None:
                args.append(f"-W{pen}")

            # For horizontal line, we use plot with two points at xmin and xmax
            # But we need to know the region, which is stored in the session
            # For now, use a simple approach: plot command with line data

            # Build command - we'll use the current region
            cmd = "plot"
            if args:
                cmd += " " + " ".join(args)

            # Create horizontal line data: use very large x-range to span any region
            # GMT will clip to actual region
            line_data = f"-10000 {y_val}\n10000 {y_val}\n"

            # Use plot with data via here-document syntax
            session.call_module("plot", f"-W{pen if pen else '0.5p,black'}", input_data=line_data)
