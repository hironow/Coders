"""
PyGMT nanobind - High-performance PyGMT reimplementation

This package provides a drop-in replacement for PyGMT using nanobind
for improved performance.
"""

__version__ = "0.1.0"

# Re-export core classes for easy access
from pygmt_nb.clib import Session, Grid

__all__ = ["Session", "Grid", "__version__"]
