"""
PyGMT-compatible plotting methods for pygmt_nb.

This module contains individual GMT plotting functions that are designed
to be used as Figure methods following PyGMT's architecture pattern.
"""

from pygmt_nb.src.basemap import basemap
from pygmt_nb.src.coast import coast
from pygmt_nb.src.plot import plot
from pygmt_nb.src.text import text
from pygmt_nb.src.grdimage import grdimage
from pygmt_nb.src.colorbar import colorbar
from pygmt_nb.src.grdcontour import grdcontour
from pygmt_nb.src.logo import logo
from pygmt_nb.src.legend import legend
from pygmt_nb.src.histogram import histogram
from pygmt_nb.src.image import image
from pygmt_nb.src.contour import contour

__all__ = [
    "basemap",
    "coast",
    "plot",
    "text",
    "grdimage",
    "colorbar",
    "grdcontour",
    "logo",
    "legend",
    "histogram",
    "image",
    "contour",
]
