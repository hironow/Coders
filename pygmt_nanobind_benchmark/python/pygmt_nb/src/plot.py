"""
plot - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import subprocess
import numpy as np


def plot(
    self,
    x=None,
    y=None,
    data=None,
    region: Optional[Union[str, List[float]]] = None,
    projection: Optional[str] = None,
    style: Optional[str] = None,
    color: Optional[str] = None,
    pen: Optional[str] = None,
    frame: Union[bool, str, List[str], None] = None,
    **kwargs
):
    """
    Plot lines, polygons, and symbols.

    Modern mode version.

    Parameters:
        x, y: X and Y coordinates (arrays or lists)
        data: Alternative data input (not yet fully supported)
        region: Map region
        projection: Map projection
        style: Symbol style (e.g., "c0.2c" for 0.2cm circles)
        color: Fill color (e.g., "red", "blue")
        pen: Outline pen (e.g., "1p,black")
        frame: Frame settings
    """
    # Use stored region/projection from basemap() if not provided
    if region is None:
        region = self._region
    if projection is None:
        projection = self._projection

    # Validate that we have region and projection (either from parameters or stored)
    if region is None:
        raise ValueError("region parameter is required (either explicitly or from basemap())")
    if projection is None:
        raise ValueError("projection parameter is required (either explicitly or from basemap())")

    # Validate data input
    if x is None and y is None and data is None:
        raise ValueError("Must provide either x/y or data")
    if (x is None and y is not None) or (x is not None and y is None):
        raise ValueError("Must provide both x and y (not just one)")

    args = []

    # Region (optional in modern mode if already set by basemap)
    if region is not None:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Projection (optional in modern mode if already set by basemap)
    if projection is not None:
        args.append(f"-J{projection}")

    # Style/Symbol
    if style:
        args.append(f"-S{style}")

    # Color
    if color:
        args.append(f"-G{color}")

    # Pen
    if pen:
        args.append(f"-W{pen}")

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    # For now, use echo to pass data via stdin
    # TODO: Implement proper data passing via virtual files
    if x is not None and y is not None:
        import subprocess
        data_str = "\n".join(f"{xi} {yi}" for xi, yi in zip(x, y))

        # Use subprocess for data input (temporary solution)
        cmd = ["gmt", "plot"] + args
        try:
            subprocess.run(
                cmd,
                input=data_str,
                text=True,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GMT plot failed: {e.stderr}") from e
    else:
        # No data case - still need to call the module
        self._session.call_module("plot", " ".join(args))

