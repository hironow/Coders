"""
PyGMT nanobind - High-performance PyGMT reimplementation

This package provides a drop-in replacement for PyGMT using nanobind
for improved performance.
"""

__version__ = "0.1.0"

# Re-export core classes for easy access
from pygmt_nb.clib import Session, Grid
from pygmt_nb.figure import Figure
from pygmt_nb.makecpt import makecpt
from pygmt_nb.info import info
from pygmt_nb.grdinfo import grdinfo
from pygmt_nb.select import select
from pygmt_nb.grdcut import grdcut
from pygmt_nb.grd2xyz import grd2xyz
from pygmt_nb.xyz2grd import xyz2grd
from pygmt_nb.grdfilter import grdfilter
from pygmt_nb.project import project
from pygmt_nb.triangulate import triangulate
from pygmt_nb.surface import surface
from pygmt_nb.grdgradient import grdgradient
from pygmt_nb.grdsample import grdsample
from pygmt_nb.nearneighbor import nearneighbor
from pygmt_nb.grdproject import grdproject
from pygmt_nb.grdtrack import grdtrack
from pygmt_nb.filter1d import filter1d
from pygmt_nb.grdclip import grdclip
from pygmt_nb.grdfill import grdfill
from pygmt_nb.blockmean import blockmean
from pygmt_nb.blockmedian import blockmedian
from pygmt_nb.blockmode import blockmode
from pygmt_nb.grd2cpt import grd2cpt

__all__ = ["Session", "Grid", "Figure", "makecpt", "info", "grdinfo", "select", "grdcut", "grd2xyz", "xyz2grd", "grdfilter", "project", "triangulate", "surface", "grdgradient", "grdsample", "nearneighbor", "grdproject", "grdtrack", "filter1d", "grdclip", "grdfill", "blockmean", "blockmedian", "blockmode", "grd2cpt", "__version__"]
