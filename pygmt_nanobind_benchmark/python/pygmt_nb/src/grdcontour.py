"""
grdcontour - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def grdcontour(
    self,
    grid: Union[str, Path],
    region: Optional[Union[str, List[float]]] = None,
    projection: Optional[str] = None,
    interval: Optional[Union[int, float, str]] = None,
    annotation: Optional[Union[int, float, str]] = None,
    pen: Optional[str] = None,
    limit: Optional[List[float]] = None,
    frame: Union[bool, str, List[str], None] = None,
    **kwargs
):
    """
    Draw contour lines from a grid file.

    Modern mode version.

    Parameters:
        grid: Grid file path
        region: Map region
        projection: Map projection
        interval: Contour interval
        annotation: Annotation interval
        pen: Contour pen specification
        limit: Contour limits [low, high]
        frame: Frame settings
    """
    args = [str(grid)]

    # Contour interval
    if interval is not None:
        args.append(f"-C{interval}")

    # Annotation
    if annotation is not None:
        args.append(f"-A{annotation}")

    # Projection
    if projection:
        args.append(f"-J{projection}")

    # Region
    if region:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Pen
    if pen:
        args.append(f"-W{pen}")

    # Limits
    if limit:
        args.append(f"-L{limit[0]}/{limit[1]}")

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    self._session.call_module("grdcontour", " ".join(args))

