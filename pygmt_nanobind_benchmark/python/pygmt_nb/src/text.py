"""
text - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import subprocess
import numpy as np


def text(
    self,
    x=None,
    y=None,
    text=None,
    region: Optional[Union[str, List[float]]] = None,
    projection: Optional[str] = None,
    font: Optional[str] = None,
    justify: Optional[str] = None,
    angle: Optional[Union[int, float]] = None,
    frame: Union[bool, str, List[str], None] = None,
    **kwargs
):
    """
    Plot text strings.

    Modern mode version.

    Parameters:
        x, y: Text position coordinates
        text: Text string(s) to plot
        region: Map region
        projection: Map projection
        font: Font specification (e.g., "12p,Helvetica,black")
        justify: Text justification (e.g., "MC", "TL")
        angle: Text rotation angle in degrees
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

    if x is None or y is None or text is None:
        raise ValueError("Must provide x, y, and text")

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

    # Font
    if font:
        args.append(f"-F+f{font}")
    elif justify or angle is not None:
        # Need -F for justify/angle even without font
        f_args = []
        if font:
            f_args.append(f"+f{font}")
        if justify:
            f_args.append(f"+j{justify}")
        if angle is not None:
            f_args.append(f"+a{angle}")
        if f_args:
            args.append("-F" + "".join(f_args))

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    # Prepare text data
    import subprocess

    # Handle single or multiple text entries
    if isinstance(text, str):
        text = [text]
    if not isinstance(x, list):
        x = [x]
    if not isinstance(y, list):
        y = [y]

    data_str = "\n".join(f"{xi} {yi} {t}" for xi, yi, t in zip(x, y, text))

    cmd = ["gmt", "text"] + args
    try:
        subprocess.run(
            cmd,
            input=data_str,
            text=True,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"GMT text failed: {e.stderr}") from e

