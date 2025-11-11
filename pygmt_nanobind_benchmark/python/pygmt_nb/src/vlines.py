"""
vlines - Plot vertical lines.

Figure method (not a standalone module function).
"""

from typing import Union, Optional, List


def vlines(
    self,
    x: Union[float, List[float]],
    pen: Optional[str] = None,
    label: Optional[str] = None,
    **kwargs
):
    """
    Plot vertical lines.

    Plot one or more vertical lines at specified x-coordinates across
    the entire plot region.

    Parameters
    ----------
    x : float or list of float
        X-coordinate(s) for vertical line(s).
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
    >>> # Single vertical line at x=5
    >>> fig.vlines(x=5, pen="1p,black")
    >>> fig.savefig("vline.png")
    >>>
    >>> # Multiple vertical lines
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.vlines(x=[2, 5, 8], pen="1p,red,dashed")
    >>> fig.savefig("vlines_multiple.png")
    >>>
    >>> # Vertical line with custom pen
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.vlines(x=7, pen="2p,blue,dotted")
    >>> fig.savefig("vline_styled.png")

    Notes
    -----
    This is a convenience function that wraps GMT's plot module with
    vertical line functionality. It's useful for:
    - Adding reference lines
    - Marking events or transitions
    - Separating plot sections
    - Adding grid-like visual guides

    The lines extend across the entire y-range of the current plot region.

    See Also
    --------
    hlines : Plot horizontal lines
    plot : General plotting function
    """
    from pygmt_nb.clib import Session

    # Convert single value to list for uniform processing
    if not isinstance(x, (list, tuple)):
        x = [x]

    # Build GMT command for each line
    with Session() as session:
        for x_val in x:
            # For vertical line, use plot command
            # Create vertical line data: use very large y-range to span any region
            # GMT will clip to actual region
            line_data = f"{x_val} -10000\n{x_val} 10000\n"

            # Use plot with data via input
            session.call_module("plot", f"-W{pen if pen else '0.5p,black'}", input_data=line_data)
