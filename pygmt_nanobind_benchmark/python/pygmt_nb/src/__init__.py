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
from pygmt_nb.src.plot3d import plot3d
from pygmt_nb.src.grdview import grdview
from pygmt_nb.src.inset import inset
from pygmt_nb.src.subplot import subplot
from pygmt_nb.src.shift_origin import shift_origin
from pygmt_nb.src.psconvert import psconvert
from pygmt_nb.src.hlines import hlines
from pygmt_nb.src.vlines import vlines
from pygmt_nb.src.meca import meca
from pygmt_nb.src.rose import rose
from pygmt_nb.src.solar import solar
from pygmt_nb.src.ternary import ternary
from pygmt_nb.src.tilemap import tilemap
from pygmt_nb.src.timestamp import timestamp

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
    "plot3d",
    "grdview",
    "inset",
    "subplot",
    "shift_origin",
    "psconvert",
    "hlines",
    "vlines",
    "meca",
    "rose",
    "solar",
    "ternary",
    "tilemap",
    "timestamp",
]
