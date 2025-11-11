"""
subplot - Manage Figure subplot configuration and panel selection.

Figure method (imported into Figure class).
"""

from typing import Union, Optional, List, Tuple


class SubplotContext:
    """
    Context manager for creating subplot layouts.

    This class manages the GMT subplot begin/end/set commands for creating
    multi-panel figures.
    """

    def __init__(
        self,
        session,
        nrows: int,
        ncols: int,
        figsize: Optional[Union[str, List, Tuple]] = None,
        autolabel: Optional[Union[bool, str]] = None,
        margins: Optional[Union[str, List]] = None,
        title: Optional[str] = None,
        frame: Optional[Union[str, List]] = None,
        **kwargs
    ):
        """
        Initialize subplot context.

        Parameters
        ----------
        session : Session
            The GMT session object.
        nrows : int
            Number of subplot rows.
        ncols : int
            Number of subplot columns.
        figsize : str, list, or tuple, optional
            Figure size. Format: "width/height" or [width, height]
        autolabel : bool or str, optional
            Automatic subplot labeling. True for default (a), or str for custom format.
        margins : str or list, optional
            Margins between subplots. Format: "margin" or [top, right, bottom, left]
        title : str, optional
            Main title for the entire subplot figure.
        frame : str or list, optional
            Frame settings for all panels.
        """
        self._session = session
        self._nrows = nrows
        self._ncols = ncols
        self._figsize = figsize
        self._autolabel = autolabel
        self._margins = margins
        self._title = title
        self._frame = frame
        self._kwargs = kwargs

    def __enter__(self):
        """Begin subplot context."""
        args = []

        # Number of rows and columns
        args.append(f"{self._nrows}x{self._ncols}")

        # Figure size (-F option)
        if self._figsize is not None:
            if isinstance(self._figsize, (list, tuple)):
                args.append(f"-F{'/'.join(str(x) for x in self._figsize)}")
            else:
                args.append(f"-F{self._figsize}")

        # Autolabel (-A option)
        if self._autolabel is not None:
            if isinstance(self._autolabel, bool):
                if self._autolabel:
                    args.append("-A")
            else:
                args.append(f"-A{self._autolabel}")

        # Margins (-M option)
        if self._margins is not None:
            if isinstance(self._margins, list):
                args.append(f"-M{'/'.join(str(x) for x in self._margins)}")
            else:
                args.append(f"-M{self._margins}")

        # Title (-T option)
        if self._title is not None:
            args.append(f"-T\"{self._title}\"")

        # Frame (-B option for all panels)
        if self._frame is not None:
            if isinstance(self._frame, list):
                for f in self._frame:
                    args.append(f"-B{f}")
            else:
                args.append(f"-B{self._frame}")

        # Call GMT subplot begin
        self._session.call_module("subplot", "begin " + " ".join(args))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End subplot context."""
        # Call GMT subplot end
        self._session.call_module("subplot", "end")
        return False

    def set_panel(
        self,
        panel: Union[int, Tuple[int, int], List[int]],
        fixedlabel: Optional[str] = None,
        **kwargs
    ):
        """
        Set the current subplot panel for plotting.

        Parameters
        ----------
        panel : int, tuple, or list
            Panel to activate. Can be:
            - int: Panel number (0-indexed, row-major order)
            - tuple/list: (row, col) indices (0-indexed)
        fixedlabel : str, optional
            Override automatic label for this panel.
        """
        args = []

        # Panel specification
        if isinstance(panel, int):
            # Convert linear index to (row, col)
            row = panel // self._ncols
            col = panel % self._ncols
            args.append(f"{row},{col}")
        elif isinstance(panel, (tuple, list)):
            args.append(f"{panel[0]},{panel[1]}")
        else:
            raise ValueError(f"Invalid panel specification: {panel}")

        # Fixed label (-A option)
        if fixedlabel is not None:
            args.append(f"-A\"{fixedlabel}\"")

        # Call GMT subplot set
        self._session.call_module("subplot", "set " + " ".join(args))


def subplot(
    self,
    nrows: int = 1,
    ncols: int = 1,
    figsize: Optional[Union[str, List, Tuple]] = None,
    autolabel: Optional[Union[bool, str]] = None,
    margins: Optional[Union[str, List]] = None,
    title: Optional[str] = None,
    frame: Optional[Union[str, List]] = None,
    **kwargs
):
    """
    Create a subplot context for multi-panel figures.

    This method returns a context manager that handles the setup and
    completion of subplots. Use set_panel() to activate specific panels
    for plotting.

    Based on PyGMT's subplot implementation for API compatibility.

    Parameters
    ----------
    nrows : int, optional
        Number of subplot rows (default: 1).
    ncols : int, optional
        Number of subplot columns (default: 1).
    figsize : str, list, or tuple, optional
        Size of the entire figure. Format: "width/height" or [width, height]
        Example: "15c/10c" or ["15c", "10c"]
    autolabel : bool or str, optional
        Automatic panel labeling.
        - True: Use default labeling (a, b, c, ...)
        - str: Custom format, e.g., "(a)" or "A)"
    margins : str or list, optional
        Margins/spacing between panels.
        - str: Single value for all margins, e.g., "0.5c"
        - list: [horizontal, vertical] or [top, right, bottom, left]
    title : str, optional
        Main title for the entire subplot figure.
    frame : str or list, optional
        Default frame settings applied to all panels.

    Returns
    -------
    SubplotContext
        Context manager for the subplot with set_panel() method.

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> # Create 2x2 subplot layout
    >>> with fig.subplot(nrows=2, ncols=2, figsize=["15c", "12c"],
    ...                  autolabel=True, margins="0.5c",
    ...                  title="Multi-Panel Figure") as subplt:
    ...     # Top-left panel (0, 0)
    ...     subplt.set_panel(panel=(0, 0))
    ...     fig.basemap(region=[0, 10, 0, 10], projection="X5c", frame=True)
    ...     fig.plot(x=[2, 5, 8], y=[3, 7, 4], pen="1p,red")
    ...
    ...     # Top-right panel (0, 1)
    ...     subplt.set_panel(panel=(0, 1))
    ...     fig.basemap(region=[0, 5, 0, 5], projection="X5c", frame=True)
    ...
    ...     # Bottom-left panel (1, 0)
    ...     subplt.set_panel(panel=(1, 0))
    ...     fig.coast(region=[-10, 10, 35, 45], projection="M5c",
    ...               land="tan", water="lightblue", frame=True)
    ...
    ...     # Bottom-right panel (1, 1) - using linear index
    ...     subplt.set_panel(panel=3)  # Same as (1, 1) in 2x2 grid
    ...     fig.basemap(region=[0, 20, 0, 20], projection="X5c", frame=True)
    >>> fig.savefig("subplots.ps")

    Notes
    -----
    The subplot method must be used as a context manager (with statement).
    Use the returned context's set_panel() method to activate each panel
    before plotting. Panels are indexed from (0, 0) at top-left.
    """
    return SubplotContext(
        session=self._session,
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        autolabel=autolabel,
        margins=margins,
        title=title,
        frame=frame,
        **kwargs
    )
