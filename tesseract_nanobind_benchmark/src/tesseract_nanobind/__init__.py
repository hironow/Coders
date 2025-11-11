"""Tesseract nanobind - High-performance Python bindings for Tesseract OCR."""

__version__ = "0.1.0"

from ._tesseract_nanobind import TesseractAPI

__all__ = ["TesseractAPI", "__version__"]
