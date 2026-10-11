"""Tesseract nanobind - High-performance Python bindings for Tesseract OCR."""

__version__ = "0.1.0"

# Export compat module for tesserocr compatibility
from . import compat
from ._tesseract_nanobind import TesseractAPI

__all__ = ["TesseractAPI", "__version__", "compat"]
