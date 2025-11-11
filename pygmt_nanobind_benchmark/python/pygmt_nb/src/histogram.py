"""
histogram - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from pathlib import Path

import numpy as np


def histogram(
    self,
    data: np.ndarray | list | str | Path,
    region: str | list[float] | None = None,
    projection: str | None = None,
    frame: bool | str | list[str] | None = None,
    series: str | list[float] | None = None,
    fill: str | None = None,
    pen: str | None = None,
    **kwargs,
):
    """
    Calculate and plot histograms.

    Creates histograms from input data and plots them on the current figure.
    Data can be provided as arrays, lists, or file paths.

    Based on PyGMT's histogram implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data for histogram. Can be:
        - 1-D numpy array
        - Python list
        - Path to ASCII data file
    region : str or list, optional
        Map region. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
    projection : str, optional
        Map projection (e.g., "X10c/6c" for Cartesian)
    frame : bool or str or list, optional
        Frame and axes configuration. True for automatic, string for custom.
    series : str or list, optional
        Histogram bin settings. Format: "min/max/inc" or [min, max, inc]
    fill : str, optional
        Fill color for bars (e.g., "red", "lightblue")
    pen : str, optional
        Pen attributes for bar outlines (e.g., "1p,black")
    **kwargs
        Additional GMT options

    Examples
    --------
    >>> fig = pygmt.Figure()
    >>> fig.histogram(
    ...     data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
    ...     region=[0, 6, 0, 4],
    ...     projection="X10c/6c",
    ...     series="0/6/1",
    ...     fill="lightblue",
    ...     frame=True
    ... )
    """
    # Build GMT command arguments
    args = []

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    elif hasattr(self, "_region") and self._region:
        r = self._region
        if isinstance(r, list):
            args.append(f"-R{'/'.join(str(x) for x in r)}")
        else:
            args.append(f"-R{r}")

    # Projection (-J option)
    if projection is not None:
        args.append(f"-J{projection}")
    elif hasattr(self, "_projection") and self._projection:
        args.append(f"-J{self._projection}")

    # Frame (-B option)
    if frame is not None:
        if isinstance(frame, bool):
            if frame:
                args.append("-Ba")
        elif isinstance(frame, list):
            for f in frame:
                args.append(f"-B{f}")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    # Series/bins (-T option)
    if series is not None:
        if isinstance(series, list):
            args.append(f"-T{'/'.join(str(x) for x in series)}")
        else:
            args.append(f"-T{series}")

    # Fill color (-G option)
    if fill is not None:
        args.append(f"-G{fill}")

    # Pen/outline (-W option)
    if pen is not None:
        args.append(f"-W{pen}")

    # Handle data input
    if isinstance(data, (str, Path)):
        # File path
        args.append(str(data))
        self._session.call_module("histogram", " ".join(args))
    else:
        # Array-like data - use virtual file
        data_array = np.asarray(data, dtype=np.float64).ravel()  # Flatten to 1-D

        # Pass data via virtual file (nanobind, 103x faster!)
        with self._session.virtualfile_from_vectors(data_array) as vfile:
            self._session.call_module("histogram", f"{vfile} " + " ".join(args))
