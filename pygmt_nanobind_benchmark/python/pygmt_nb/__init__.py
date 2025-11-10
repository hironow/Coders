"""
PyGMT nanobind - High-performance PyGMT reimplementation

This package provides a drop-in replacement for PyGMT using nanobind
for improved performance.
"""

__version__ = "0.1.0"

# Re-export Session class for compatibility
from pygmt_nb.clib import Session

__all__ = ["Session", "__version__"]
