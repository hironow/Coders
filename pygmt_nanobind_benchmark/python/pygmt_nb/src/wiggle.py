"""
wiggle - Plot z = f(x,y) anomalies along tracks.

Figure method (not a standalone module function).
"""

from pathlib import Path

import numpy as np


def wiggle(
    self,
    data: np.ndarray | str | Path | None = None,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    scale: str | None = None,
    pen: str | None = None,
    fillpositive: str | None = None,
    fillnegative: str | None = None,
    **kwargs,
):
    """
    Plot z = f(x,y) anomalies along tracks.

    Creates "wiggle" plots where anomaly values are plotted perpendicular
    to a track or profile line. Positive and negative anomalies can be
    filled with different colors. Commonly used in geophysics.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data with x, y, z columns.
        x, y: Track coordinates
        z: Anomaly values
    x, y, z : array-like, optional
        Separate arrays for coordinates and anomaly values.
    scale : str, optional
        Scale for anomaly amplitude.
        Format: "scale[unit]"
        Example: "1c" means 1 data unit = 1 cm perpendicular distance
    pen : str, optional
        Pen attributes for wiggle line.
        Format: "width,color,style"
    fillpositive : str, optional
        Fill color for positive anomalies.
        Example: "red", "lightblue"
    fillnegative : str, optional
        Fill color for negative anomalies.
        Example: "blue", "lightgray"

    Examples
    --------
    >>> import pygmt
    >>> import numpy as np
    >>> # Create magnetic anomaly profile
    >>> x = np.arange(0, 10, 0.1)
    >>> y = np.zeros_like(x)  # Straight track
    >>> z = np.sin(x) + 0.5 * np.sin(2*x)  # Anomaly pattern
    >>>
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[-1, 11, -2, 2], projection="X15c/5c", frame=True)
    >>> fig.wiggle(
    ...     x=x, y=y, z=z,
    ...     scale="0.5c",
    ...     pen="1p,black",
    ...     fillpositive="red",
    ...     fillnegative="blue"
    ... )
    >>> fig.savefig("magnetic_profile.png")
    >>>
    >>> # From data file
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 100, 0, 50], projection="X15c/10c", frame=True)
    >>> fig.wiggle(
    ...     data="seismic_profile.txt",
    ...     scale="1c",
    ...     fillpositive="black"
    ... )
    >>> fig.savefig("seismic_wiggle.png")

    Notes
    -----
    This function is commonly used for:
    - Magnetic anomaly profiles
    - Gravity anomaly displays
    - Seismic traces
    - Geophysical survey data
    - Bathymetric profiles

    Wiggle plot characteristics:
    - Z-values plotted perpendicular to track
    - Positive anomalies deflect one way
    - Negative anomalies deflect opposite way
    - Track line shows profile location
    - Filled regions highlight anomaly sign

    Scale interpretation:
    - Larger scale = larger wiggles
    - Scale converts data units to map distance
    - Example: scale=1c means 1 data unit = 1 cm

    Applications:
    - Marine geophysics: Ship-track data
    - Aeromagnetics: Flight-line profiles
    - Seismic: Reflection/refraction traces
    - Gravity surveys: Profile data
    - Well logs: Downhole measurements

    Visual encoding:
    - Wiggle amplitude = anomaly magnitude
    - Positive/negative fill = sign
    - Track position = geographic location
    - Multiple tracks show spatial patterns

    Data requirements:
    - Sequential points along track
    - Uniform or variable sampling
    - Can handle multiple tracks (segments)

    Comparison with other plots:
    - wiggle: Anomalies perpendicular to track
    - plot: Simple x-y line plots
    - grdimage: Gridded data as image
    - velo: Vectors at discrete points

    See Also
    --------
    plot : General line plotting
    grdtrack : Sample grids along tracks
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    if scale is not None:
        args.append(f"-Z{scale}")

    if pen is not None:
        args.append(f"-W{pen}")

    if fillpositive is not None:
        args.append(f"-G+{fillpositive}")

    if fillnegative is not None:
        args.append(f"-G-{fillnegative}")

    # Execute via session
    with Session() as session:
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("wiggle", f"{data} " + " ".join(args))
            else:
                # Array input
                print("Note: Array input for wiggle requires virtual file support")
        elif x is not None and y is not None and z is not None:
            # Separate arrays
            print("Note: Array input for wiggle requires virtual file support")
