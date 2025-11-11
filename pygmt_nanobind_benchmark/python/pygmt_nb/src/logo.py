"""
logo - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def logo(
    self,
    position: Optional[str] = None,
    box: bool = False,
    style: Optional[str] = None,
    projection: Optional[str] = None,
    region: Optional[Union[str, List[float]]] = None,
    transparency: Optional[Union[int, float]] = None,
    **kwargs
):
    """
    Add the GMT logo to the figure.

    Modern mode version (uses 'gmtlogo' command).

    Parameters:
        position: Position specification
        box: Draw a rectangular border around the logo
        style: Logo style ("standard", "url", "no_label")
        projection: Map projection
        region: Map region
        transparency: Transparency level (0-100)
    """
    args = []

    # Position
    if position:
        args.append(f"-D{position}")

    # Box
    if box:
        args.append("-F+p1p+gwhite")

    # Style
    if style:
        style_map = {
            "standard": "l",
            "url": "u",
            "no_label": "n"
        }
        style_code = style_map.get(style, style)
        args.append(f"-S{style_code}")

    # Projection
    if projection:
        args.append(f"-J{projection}")

    # Region
    if region:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Transparency
    if transparency is not None:
        args.append(f"-t{transparency}")

    self._session.call_module("gmtlogo", " ".join(args))

