"""
contour - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from pathlib import Path

import numpy as np


def contour(
    self,
    data: np.ndarray | str | Path | None = None,
    x=None,
    y=None,
    z=None,
    region: str | list[float] | None = None,
    projection: str | None = None,
    frame: bool | str | list[str] | None = None,
    levels: str | int | list | None = None,
    annotation: str | int | None = None,
    pen: str | None = None,
    **kwargs,
):
    """
    Contour table data by direct triangulation.

    Takes a matrix, (x, y, z) triplets, or a file name as input and plots
    contour lines on the map.

    Based on PyGMT's contour implementation for API compatibility.

    Parameters
    ----------
    data : array or str or Path, optional
        Input data. Can be:
        - 2-D array with columns [x, y, z]
        - Path to ASCII data file
        Must provide either `data` or `x`, `y`, `z`.
    x, y, z : array-like, optional
        Arrays of x, y coordinates and z values.
        Alternative to `data` parameter.
    region : str or list, optional
        Map region. Format: [xmin, xmax, ymin, ymax]
    projection : str, optional
        Map projection (e.g., "X10c" for Cartesian)
    frame : bool or str or list, optional
        Frame and axes configuration
    levels : str or int or list, optional
        Contour levels specification. Can be:
        - String: "min/max/interval" (e.g., "0/100/10")
        - Int: number of levels
        - List: specific level values
    annotation : str or int, optional
        Annotation interval for contours.
    pen : str, optional
        Pen attributes for contour lines (e.g., "0.5p,black")
    **kwargs
        Additional GMT options

    Examples
    --------
    >>> import numpy as np
    >>> fig = pygmt.Figure()
    >>> x = np.arange(0, 10, 0.5)
    >>> y = np.arange(0, 10, 0.5)
    >>> X, Y = np.meshgrid(x, y)
    >>> Z = np.sin(X) + np.cos(Y)
    >>> fig.contour(x=X.ravel(), y=Y.ravel(), z=Z.ravel(),
    ...             region=[0, 10, 0, 10], projection="X10c",
    ...             levels="0.2", frame=True)
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

    # Contour levels (-C option)
    if levels is not None:
        if isinstance(levels, int):
            args.append(f"-C{levels}")
        elif isinstance(levels, list):
            args.append(f"-C{','.join(str(x) for x in levels)}")
        else:
            args.append(f"-C{levels}")

    # Annotation (-A option)
    if annotation is not None:
        args.append(f"-A{annotation}")

    # Pen (-W option) - required by GMT
    if pen is not None:
        args.append(f"-W{pen}")
    else:
        # Default pen if not specified
        args.append("-W0.25p,black")

    # Handle data input
    if data is not None:
        if isinstance(data, str | Path):
            # File path
            args.append(str(data))
            self._session.call_module("contour", " ".join(args))
        else:
            # Array data
            data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))
            if data_array.shape[1] < 3:
                raise ValueError("Data must have at least 3 columns (x, y, z)")

            vectors = [data_array[:, i] for i in range(data_array.shape[1])]
            with self._session.virtualfile_from_vectors(*vectors) as vfile:
                self._session.call_module("contour", f"{vfile} " + " ".join(args))
    elif x is not None and y is not None and z is not None:
        # x, y, z arrays
        x_array = np.asarray(x, dtype=np.float64).ravel()
        y_array = np.asarray(y, dtype=np.float64).ravel()
        z_array = np.asarray(z, dtype=np.float64).ravel()

        with self._session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
            self._session.call_module("contour", f"{vfile} " + " ".join(args))
    else:
        raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
