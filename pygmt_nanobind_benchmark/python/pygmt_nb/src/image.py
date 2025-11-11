"""
image - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def image(
    self,
    imagefile: Union[str, Path],
    position: Optional[str] = None,
    box: Union[bool, str] = False,
    monochrome: bool = False,
    **kwargs
):
    """
    Plot raster or EPS images.

    Reads Encapsulated PostScript (EPS) or raster image files and plots them
    on the figure. Images can be scaled, positioned, and optionally framed.

    Based on PyGMT's image implementation for API compatibility.

    Parameters
    ----------
    imagefile : str or Path
        Path to image file. Supported formats:
        - EPS (Encapsulated PostScript) with BoundingBox
        - Raster images (PNG, JPG, TIFF, etc.) via GDAL
    position : str, optional
        Position specification for the image. Format:
        [g|j|J|n|x]refpoint+r<dpi>+w<width>[/<height>][+j<justify>][+o<dx>/<dy>]
        Example: "x0/0+w5c" places image at x=0,y=0 with width 5cm
    box : bool or str, default False
        Draw a box around the image. If True, draws default box.
        If string, specifies box attributes (e.g., "+gwhite+p1p").
    monochrome : bool, default False
        Convert colored images to grayscale using YIQ transformation.
    **kwargs
        Additional GMT options.

    Examples
    --------
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.image("logo.png", position="x5/5+w3c")
    >>> fig.savefig("map_with_image.ps")
    """
    # Build GMT command arguments
    args = []

    # Image file (required)
    args.append(str(imagefile))

    # Position (-D option)
    if position is not None:
        args.append(f"-D{position}")

    # Box around image (-F option)
    if box:
        if isinstance(box, str):
            args.append(f"-F{box}")
        else:
            args.append("-F")  # Default box

    # Monochrome conversion (-M option)
    if monochrome:
        args.append("-M")

    # Execute via nanobind
    self._session.call_module("image", " ".join(args))
