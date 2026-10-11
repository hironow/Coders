"""Tesseract OCR nanobind extension"""

from typing import overload

import numpy.typing

class TesseractAPI:
    def __init__(self) -> None: ...
    def init(self, datapath: str, language: str) -> int:
        """Initialize Tesseract with datapath and language"""

    def set_image(self, image: numpy.typing.NDArray, /) -> None:
        """Set image from NumPy array (height, width, 3)"""

    def get_utf8_text(self) -> str:
        """Get OCR result as UTF-8 text"""

    def recognize(self) -> int:
        """Recognize the image"""

    def get_mean_confidence(self) -> int:
        """Get mean confidence score (0-100)"""

    def get_bounding_boxes(self) -> list:
        """Get bounding boxes with text and confidence for each word"""

    @staticmethod
    def version() -> str:
        """Get Tesseract version"""

    def set_page_seg_mode(self, mode: int) -> None:
        """Set page segmentation mode"""

    def get_page_seg_mode(self) -> int:
        """Get current page segmentation mode"""

    def set_variable(self, name: str, value: str) -> bool:
        """Set a Tesseract variable"""

    @overload
    def get_int_variable(self, name: str) -> int | None:
        """Get a variable value, or None if it does not exist"""

    @overload
    def get_int_variable(self, name: str, value: int) -> bool:
        """Get an integer variable value"""

    @overload
    def get_bool_variable(self, name: str) -> bool | None:
        """Get a variable value, or None if it does not exist"""

    @overload
    def get_bool_variable(self, name: str, value: bool) -> bool:
        """Get a boolean variable value"""

    @overload
    def get_double_variable(self, name: str) -> float | None:
        """Get a variable value, or None if it does not exist"""

    @overload
    def get_double_variable(self, name: str, value: float) -> bool:
        """Get a double variable value"""

    def get_string_variable(self, name: str) -> str:
        """Get a string variable value"""

    def set_rectangle(self, left: int, top: int, width: int, height: int) -> None:
        """Set rectangle to restrict recognition to a sub-image"""

    def get_hocr_text(self, page_number: int = 0) -> str:
        """Get OCR result in hOCR format"""

    def get_tsv_text(self, page_number: int = 0) -> str:
        """Get OCR result in TSV format"""

    def get_box_text(self, page_number: int = 0) -> str:
        """Get OCR result in box file format"""

    def get_unlv_text(self) -> str:
        """Get OCR result in UNLV format"""

    def clear(self) -> None:
        """Clear recognition results"""

    def clear_adaptive_classifier(self) -> None:
        """Clear adaptive classifier"""

    def get_datapath(self) -> str:
        """Get tessdata path"""

    def get_init_languages_as_string(self) -> str:
        """Get initialized languages as string"""

    def detect_orientation_script(self) -> tuple:
        """Detect page orientation and script"""

    def get_component_images(self, level: int, text_only: bool = True) -> list:
        """Get component images at specified level"""

    def get_words(self) -> list:
        """Get all words with text, confidence, and bounding boxes"""

    def get_textlines(self) -> list:
        """Get all text lines with text, confidence, and bounding boxes"""

    def get_thresholded_image(self) -> tuple:
        """Get the thresholded (binarized) image as a numpy array"""
