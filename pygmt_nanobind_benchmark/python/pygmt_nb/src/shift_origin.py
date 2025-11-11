"""
shift_origin - Shift plot origin in x and/or y direction.

Figure method (imported into Figure class).
"""

from typing import Union, Optional, List


def shift_origin(
    self,
    xshift: Optional[Union[str, float]] = None,
    yshift: Optional[Union[str, float]] = None,
    **kwargs
):
    """
    Shift the plot origin in x and/or y directions.

    This method shifts the plot origin for all subsequent plotting commands.
    Used to position multiple plots or subplot panels on the same page.

    Based on PyGMT's shift_origin implementation for API compatibility.

    Parameters
    ----------
    xshift : str or float, optional
        Amount to shift the plot origin in the x direction.
        Can be specified with units (e.g., "5c", "2i") or as a float
        (interpreted as centimeters).
        Positive values shift right, negative left.
    yshift : str or float, optional
        Amount to shift the plot origin in the y direction.
        Can be specified with units (e.g., "5c", "2i") or as a float
        (interpreted as centimeters).
        Positive values shift up, negative down.

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> # First plot
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X5c", frame=True)
    >>> fig.plot(x=[2, 5, 8], y=[3, 7, 4], pen="1p,red")
    >>>
    >>> # Shift origin to the right by 7cm
    >>> fig.shift_origin(xshift="7c")
    >>>
    >>> # Second plot (to the right of first)
    >>> fig.basemap(region=[0, 5, 0, 5], projection="X5c", frame=True)
    >>> fig.plot(x=[1, 3, 4], y=[1, 4, 2], pen="1p,blue")
    >>>
    >>> # Shift down by 7cm (and back left)
    >>> fig.shift_origin(xshift="-7c", yshift="-7c")
    >>>
    >>> # Third plot (below first)
    >>> fig.basemap(region=[0, 20, 0, 20], projection="X5c", frame=True)
    >>> fig.savefig("multi_plot.ps")

    Notes
    -----
    This method is particularly useful for:
    - Creating custom multi-panel layouts without using subplot
    - Positioning plots at specific locations on the page
    - Building complex figure layouts with fine-grained control

    In GMT modern mode, this corresponds to shifting the plot origin
    for subsequent plotting commands. The shift is cumulative - each
    call adds to the previous position.
    """
    # Build GMT command arguments
    args = []

    # X shift
    if xshift is not None:
        if isinstance(xshift, (int, float)):
            # Convert numeric to string with cm units
            args.append(f"-X{xshift}c")
        else:
            args.append(f"-X{xshift}")

    # Y shift
    if yshift is not None:
        if isinstance(yshift, (int, float)):
            # Convert numeric to string with cm units
            args.append(f"-Y{yshift}c")
        else:
            args.append(f"-Y{yshift}")

    # If no shifts specified, do nothing
    if not args:
        return

    # In GMT modern mode, we use the plot command with just -X/-Y to shift origin
    # This is a no-op plot that just shifts the origin
    self._session.call_module("plot", " ".join(args) + " -T")
