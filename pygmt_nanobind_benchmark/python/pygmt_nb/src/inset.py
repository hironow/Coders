"""
inset - Manage Figure inset setup and completion.

Figure method (imported into Figure class).
"""

from typing import Union, Optional, List


class InsetContext:
    """
    Context manager for creating inset maps.

    This class manages the GMT inset begin/end commands for creating
    small maps within a larger figure.
    """

    def __init__(
        self,
        session,
        position: str,
        box: Optional[Union[bool, str]] = None,
        offset: Optional[str] = None,
        margin: Optional[Union[str, float, List]] = None,
        **kwargs
    ):
        """
        Initialize inset context.

        Parameters
        ----------
        session : Session
            The GMT session object.
        position : str
            Position and size of inset. Format: "code[+w<width>[/<height>]][+j<justify>]"
            Example: "TR+w3c" for top-right corner, 3cm wide
        box : bool or str, optional
            Draw box around inset. If str, specifies fill/pen attributes.
        offset : str, optional
            Offset from reference point. Format: "dx[/dy]"
        margin : str, float, or list, optional
            Margin around inset. Can be a single value or [top, right, bottom, left]
        """
        self._session = session
        self._position = position
        self._box = box
        self._offset = offset
        self._margin = margin
        self._kwargs = kwargs

    def __enter__(self):
        """Begin inset context."""
        args = []

        # Position (-D option)
        args.append(f"-D{self._position}")

        # Box (-F option)
        if self._box is not None:
            if isinstance(self._box, bool):
                if self._box:
                    args.append("-F")
            else:
                args.append(f"-F{self._box}")

        # Offset (part of -D option)
        if self._offset is not None:
            args[-1] = args[-1] + f"+o{self._offset}"

        # Margin (-C option)
        if self._margin is not None:
            if isinstance(self._margin, list):
                args.append(f"-C{'/'.join(str(x) for x in self._margin)}")
            else:
                args.append(f"-C{self._margin}")

        # Call GMT inset begin
        self._session.call_module("inset", "begin " + " ".join(args))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End inset context."""
        # Call GMT inset end
        self._session.call_module("inset", "end")
        return False


def inset(
    self,
    position: str,
    box: Optional[Union[bool, str]] = None,
    offset: Optional[str] = None,
    margin: Optional[Union[str, float, List]] = None,
    **kwargs
):
    """
    Create a figure inset context for plotting a map within a map.

    This method returns a context manager that handles the setup and
    completion of an inset. All plotting commands within the context
    will be drawn in the inset area.

    Based on PyGMT's inset implementation for API compatibility.

    Parameters
    ----------
    position : str
        Position and size of inset. Format: "code[+w<width>[/<height>]][+j<justify>]"
        Codes: TL (top-left), TR (top-right), BL (bottom-left), BR (bottom-right),
               ML (middle-left), MR (middle-right), TC (top-center), BC (bottom-center)
        Example: "TR+w3c" for top-right corner, 3cm wide
    box : bool or str, optional
        Draw a box around the inset.
        - True: Draw default box
        - str: Box attributes, e.g., "+gwhite+p1p,black" for white fill, black pen
    offset : str, optional
        Offset from the reference point. Format: "dx[/dy]"
        Example: "0.5c/0.5c"
    margin : str, float, or list, optional
        Clearance margin around the inset.
        - Single value: Apply to all sides
        - List of 4 values: [top, right, bottom, left]
        Example: "0.2c" or [0.2, 0.2, 0.2, 0.2]

    Returns
    -------
    InsetContext
        Context manager for the inset.

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> # Main map
    >>> fig.coast(
    ...     region=[-130, -70, 24, 52],
    ...     projection="M10c",
    ...     land="lightgray",
    ...     frame=True
    ... )
    >>> # Create inset map in top-right corner
    >>> with fig.inset(position="TR+w3c", box=True):
    ...     fig.coast(
    ...         region=[-180, 180, -90, 90],
    ...         projection="G-100/35/3c",
    ...         land="gray",
    ...         water="lightblue"
    ...     )
    >>> fig.savefig("map_with_inset.ps")

    Notes
    -----
    The inset method must be used as a context manager (with statement).
    All plotting commands within the context will be drawn in the inset area.
    The original coordinate system is restored after exiting the context.
    """
    return InsetContext(
        session=self._session,
        position=position,
        box=box,
        offset=offset,
        margin=margin,
        **kwargs
    )
