"""
meca - Plot focal mechanisms (beachballs).

Figure method (not a standalone module function).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def meca(
    self,
    data: Optional[Union[np.ndarray, str, Path]] = None,
    scale: Optional[str] = None,
    convention: Optional[str] = None,
    component: Optional[str] = None,
    pen: Optional[str] = None,
    compressionfill: Optional[str] = None,
    extensionfill: Optional[str] = None,
    **kwargs
):
    """
    Plot focal mechanisms (beachballs).

    Reads focal mechanism data and plots beachball diagrams on maps.
    Commonly used in seismology to visualize earthquake source mechanisms.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data containing focal mechanism parameters.
        Format depends on convention specified.
    scale : str, optional
        Size of beach balls. Format: size[unit]
        Examples: "0.5c", "0.2i", "5p"
    convention : str, optional
        Focal mechanism convention:
        - "aki" : Aki & Richards
        - "gcmt" : Global CMT
        - "mt" : Moment tensor
        - "partial" : Partial
        - "principal_axis" : Principal axes
    component : str, optional
        Component type for plotting.
    pen : str, optional
        Pen attributes for beachball outline.
        Format: "width,color,style"
    compressionfill : str, optional
        Fill color for compressional quadrants.
        Default: "black"
    extensionfill : str, optional
        Fill color for extensional quadrants.
        Default: "white"

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="M10c", frame=True)
    >>> # Plot focal mechanisms
    >>> fig.meca(data="focal_mechanisms.txt", scale="0.5c", convention="aki")
    >>> fig.savefig("beachballs.png")

    Notes
    -----
    This function is commonly used for:
    - Earthquake focal mechanism visualization
    - Seismological fault plane solutions
    - Stress field analysis
    - Tectonic studies

    Focal mechanism representation:
    - Beachball diagrams show earthquake source geometry
    - Compressional quadrants (typically black)
    - Extensional quadrants (typically white)
    - Size proportional to magnitude or moment

    Data formats vary by convention:
    - Aki & Richards: strike, dip, rake
    - GCMT: moment tensor components
    - Principal axes: T, N, P axes

    Applications:
    - Regional seismicity mapping
    - Fault system characterization
    - Stress regime identification
    - Earthquake catalog visualization

    See Also
    --------
    plot : General plotting function
    velo : Plot velocity vectors
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    if scale is not None:
        args.append(f"-S{scale}")

    if convention is not None:
        # Map convention to GMT format code
        conv_map = {
            "aki": "a",
            "gcmt": "c",
            "mt": "m",
            "partial": "p",
            "principal_axis": "x",
        }
        code = conv_map.get(convention, convention)
        args.append(f"-S{code}{scale if scale else '0.5c'}")

    if pen is not None:
        args.append(f"-W{pen}")

    if compressionfill is not None:
        args.append(f"-G{compressionfill}")

    if extensionfill is not None:
        args.append(f"-E{extensionfill}")

    # Execute via session
    with Session() as session:
        if data is not None:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("meca", f"{data} " + " ".join(args))
            else:
                # Array input - would need virtual file support
                # For now, note that full implementation requires virtual file
                print("Note: Array input for meca requires virtual file support")
