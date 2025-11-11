"""
plot3d - Plot lines, polygons, and symbols in 3D.

Figure method (imported into Figure class).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def plot3d(
    self,
    data=None,
    x=None,
    y=None,
    z=None,
    region: Optional[Union[str, List[float]]] = None,
    projection: Optional[str] = None,
    perspective: Optional[Union[str, List[float]]] = None,
    frame: Optional[Union[bool, str, list]] = None,
    style: Optional[str] = None,
    color: Optional[str] = None,
    fill: Optional[str] = None,
    pen: Optional[str] = None,
    size: Optional[Union[str, float]] = None,
    intensity: Optional[float] = None,
    transparency: Optional[float] = None,
    label: Optional[str] = None,
    **kwargs
):
    """
    Plot lines, polygons, and symbols in 3-D.

    Takes a matrix, (x,y,z) triplets, or a file name as input and plots
    lines, polygons, or symbols in 3-D.

    Based on PyGMT's plot3d implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Data to plot. Can be a 2-D numpy array with x, y, z columns
        or a file name.
    x, y, z : array-like, optional
        x, y, and z coordinates as separate 1-D arrays.
    region : str or list, optional
        Map region. Format: [xmin, xmax, ymin, ymax, zmin, zmax]
        or "xmin/xmax/ymin/ymax/zmin/zmax"
    projection : str, optional
        Map projection. Example: "X10c/8c" for Cartesian.
    perspective : str or list, optional
        3-D view perspective. Format: [azimuth, elevation] or "azimuth/elevation"
        Example: [135, 30] for azimuth=135°, elevation=30°
    frame : bool, str, or list, optional
        Frame and axes settings. Example: "af" for auto annotations and frame.
    style : str, optional
        Symbol style. Examples: "c0.3c" (circle, 0.3cm), "s0.5c" (square, 0.5cm).
    color : str, optional
        Symbol or line color. Example: "red", "blue", "#FF0000".
    fill : str, optional
        Fill color for symbols. Example: "red", "lightblue".
    pen : str, optional
        Pen attributes for lines/symbol outlines. Example: "1p,black".
    size : str or float, optional
        Symbol size. Can be a single value or vary per point.
    intensity : float, optional
        Intensity value for color shading (0-1).
    transparency : float, optional
        Transparency level (0-100, where 0 is opaque, 100 is fully transparent).
    label : str, optional
        Label for legend entry.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> # Create 3D scatter plot
    >>> x = np.arange(0, 5, 0.5)
    >>> y = np.arange(0, 5, 0.5)
    >>> z = x**2 + y**2
    >>> fig.plot3d(
    ...     x=x, y=y, z=z,
    ...     region=[0, 5, 0, 5, 0, 50],
    ...     projection="X10c/8c",
    ...     perspective=[135, 30],
    ...     style="c0.3c",
    ...     fill="red",
    ...     frame=["af", "zaf"]
    ... )
    >>> fig.show()
    >>>
    >>> # 3D line plot
    >>> t = np.linspace(0, 4*np.pi, 100)
    >>> x = np.cos(t)
    >>> y = np.sin(t)
    >>> z = t
    >>> fig.plot3d(x=x, y=y, z=z, pen="1p,blue")

    Notes
    -----
    This function wraps the GMT plot3d (psxyz) module for 3-D plotting.
    Useful for visualizing 3-dimensional data as scatter plots, line plots,
    or 3-D trajectories.
    """
    # Build GMT command arguments
    args = []

    # Region (-R option) - includes z range for 3D
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Projection (-J option)
    if projection is not None:
        args.append(f"-J{projection}")

    # Perspective (-p option)
    if perspective is not None:
        if isinstance(perspective, list):
            args.append(f"-p{'/'.join(str(x) for x in perspective)}")
        else:
            args.append(f"-p{perspective}")

    # Frame (-B option)
    if frame is not None:
        if isinstance(frame, bool):
            if frame:
                args.append("-B")
        elif isinstance(frame, list):
            for f in frame:
                args.append(f"-B{f}")
        else:
            args.append(f"-B{frame}")

    # Style (-S option)
    if style is not None:
        args.append(f"-S{style}")
    elif size is not None:
        # Default to circle if size given but no style
        args.append(f"-Sc{size}")

    # Color/Fill (-G option)
    if fill is not None:
        args.append(f"-G{fill}")
    elif color is not None:
        args.append(f"-G{color}")

    # Pen (-W option)
    if pen is not None:
        args.append(f"-W{pen}")

    # Intensity (-I option)
    if intensity is not None:
        args.append(f"-I{intensity}")

    # Transparency (-t option)
    if transparency is not None:
        args.append(f"-t{transparency}")

    # Label for legend (-l option)
    if label is not None:
        args.append(f"-l{label}")

    # Handle data input and call GMT
    if data is not None:
        if isinstance(data, (str, Path)):
            # File input
            self._session.call_module("plot3d", f"{data} " + " ".join(args))
        else:
            # Array input - use virtual file
            data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

            # Check for at least 3 columns (x, y, z)
            if data_array.shape[1] < 3:
                raise ValueError(
                    f"data array must have at least 3 columns (x, y, z), got {data_array.shape[1]}"
                )

            # Create vectors for virtual file
            vectors = [data_array[:, i] for i in range(data_array.shape[1])]

            with self._session.virtualfile_from_vectors(*vectors) as vfile:
                self._session.call_module("plot3d", f"{vfile} " + " ".join(args))

    elif x is not None and y is not None and z is not None:
        # Separate x, y, z arrays
        x_array = np.asarray(x, dtype=np.float64).ravel()
        y_array = np.asarray(y, dtype=np.float64).ravel()
        z_array = np.asarray(z, dtype=np.float64).ravel()

        with self._session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
            self._session.call_module("plot3d", f"{vfile} " + " ".join(args))
    else:
        raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")
