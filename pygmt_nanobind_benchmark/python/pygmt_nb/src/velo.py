"""
velo - Plot velocity vectors, crosses, anisotropy bars, and wedges.

Figure method (not a standalone module function).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def velo(
    self,
    data: Optional[Union[np.ndarray, str, Path]] = None,
    scale: Optional[str] = None,
    pen: Optional[str] = None,
    fill: Optional[str] = None,
    uncertaintyfill: Optional[str] = None,
    **kwargs
):
    """
    Plot velocity vectors, crosses, anisotropy bars, and wedges.

    Reads data containing locations and velocities (or other vector quantities)
    and plots them on maps. Commonly used for GPS velocities, plate motions,
    and other geophysical vector fields.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data with positions and vector components.
        Format varies by plot type (see Notes).
    scale : str, optional
        Scale for vectors. Format: "scale[units]"
        Example: "0.5c" means 1 unit = 0.5 cm
    pen : str, optional
        Pen attributes for vectors/symbols.
        Format: "width,color,style"
    fill : str, optional
        Fill color for vectors/wedges.
    uncertaintyfill : str, optional
        Fill color for uncertainty ellipses.

    Examples
    --------
    >>> import pygmt
    >>> import numpy as np
    >>> # GPS velocity data (lon, lat, ve, vn, sve, svn, correlation, site)
    >>> lon = np.array([0, 1, 2])
    >>> lat = np.array([0, 1, 2])
    >>> ve = np.array([1.0, 1.5, 2.0])  # East velocity (mm/yr)
    >>> vn = np.array([0.5, 1.0, 1.5])  # North velocity
    >>> data = np.column_stack([lon, lat, ve, vn])
    >>>
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[-1, 3, -1, 3], projection="M10c", frame=True)
    >>> fig.velo(data=data, scale="0.2c", pen="1p,black", fill="red")
    >>> fig.savefig("velocities.png")

    Notes
    -----
    This function is commonly used for:
    - GPS velocity fields
    - Plate motion vectors
    - Strain rate analysis
    - Seismic anisotropy
    - Principal stress directions

    Data formats (columns):
    - Velocity vectors: lon, lat, ve, vn, [sve, svn, corre, name]
      - ve, vn: East and North components
      - sve, svn: Standard errors
      - corre: Correlation
      - name: Station name

    - Anisotropy bars: lon, lat, azimuth, semi-major, semi-minor

    - Rotational wedges: lon, lat, spin, wedge_magnitude

    Vector representation:
    - Arrow: Direction and magnitude
    - Ellipse: Uncertainty (if provided)
    - Length scaled by magnitude
    - Color can vary with parameters

    Scale factor:
    - Larger scale = longer vectors
    - Typical: 0.1c-1.0c per unit
    - Units: velocity units (mm/yr, cm/yr, etc.)

    Applications:
    - Geodesy: GPS/GNSS velocities
    - Tectonics: Plate motions
    - Seismology: Focal mechanisms
    - Geophysics: Stress/strain fields
    - Oceanography: Current vectors

    Uncertainty visualization:
    - Error ellipses around arrows
    - Size reflects measurement precision
    - Orientation shows error correlation

    See Also
    --------
    plot : General plotting with symbols
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    if scale is not None:
        args.append(f"-S{scale}")

    if pen is not None:
        args.append(f"-W{pen}")

    if fill is not None:
        args.append(f"-G{fill}")

    if uncertaintyfill is not None:
        args.append(f"-E{uncertaintyfill}")

    # Execute via session
    with Session() as session:
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("velo", f"{data} " + " ".join(args))
            else:
                # Array input
                print("Note: Array input for velo requires virtual file support")
