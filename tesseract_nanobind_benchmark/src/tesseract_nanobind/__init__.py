"""Tesseract nanobind - High-performance Python bindings for Tesseract OCR."""

__version__ = "0.1.0"

from ._tesseract_nanobind import TesseractAPI

# Export compat module for tesserocr compatibility
from . import compat

__all__ = ["TesseractAPI", "compat", "__version__"]
