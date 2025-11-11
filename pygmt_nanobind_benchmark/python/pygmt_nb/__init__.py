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

__all__ = ["Session", "Grid", "Figure", "makecpt", "__version__"]
