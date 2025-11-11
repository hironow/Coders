"""Tesserocr compatibility layer for tesseract_nanobind.

This module provides a tesserocr-compatible API, allowing users to simply
change their import statements from:
    from tesserocr import PyTessBaseAPI
to:
    from tesseract_nanobind.compat import PyTessBaseAPI

Most common tesserocr operations are supported.
"""

import numpy as np
from PIL import Image
from ._tesseract_nanobind import TesseractAPI as _TesseractAPI


# Enum classes matching tesserocr
class OEM:
    """OCR Engine Mode enumeration."""
    TESSERACT_ONLY = 0
    LSTM_ONLY = 1
    TESSERACT_LSTM_COMBINED = 2
    DEFAULT = 3


class PSM:
    """Page Segmentation Mode enumeration."""
    OSD_ONLY = 0
    AUTO_OSD = 1
    AUTO_ONLY = 2
    AUTO = 3
    SINGLE_COLUMN = 4
    SINGLE_BLOCK_VERT_TEXT = 5
    SINGLE_BLOCK = 6
    SINGLE_LINE = 7
    SINGLE_WORD = 8
    CIRCLE_WORD = 9
    SINGLE_CHAR = 10
    SPARSE_TEXT = 11
    SPARSE_TEXT_OSD = 12
    RAW_LINE = 13
    COUNT = 14


class RIL:
    """Page Iterator Level enumeration."""
    BLOCK = 0
    PARA = 1
    TEXTLINE = 2
    WORD = 3
    SYMBOL = 4


class PyTessBaseAPI:
    """Tesserocr-compatible wrapper around TesseractAPI.
    
    This class provides API compatibility with tesserocr's PyTessBaseAPI,
    allowing existing tesserocr code to work with minimal changes.
    
    Usage:
        >>> api = PyTessBaseAPI(lang='eng')
        >>> api.SetImage(image)
        >>> text = api.GetUTF8Text()
        >>> api.End()
    
    Or as context manager:
        >>> with PyTessBaseAPI(lang='eng') as api:
        ...     api.SetImage(image)
        ...     text = api.GetUTF8Text()
    """
    
    def __init__(self, path='', lang='eng', oem=OEM.DEFAULT, psm=PSM.AUTO,
                 configs=None, variables=None, set_only_non_debug_params=False,
                 init=True):
        """Initialize the API.
        
        Args:
            path: Data path for tessdata (empty string uses system default)
            lang: Language code (default: 'eng')
            oem: OCR Engine Mode (ignored, uses direct API)
            psm: Page Segmentation Mode (not fully implemented)
            configs: Config files (not fully implemented)
            variables: Variables dict (not fully implemented)
            set_only_non_debug_params: Whether to set only non-debug params
            init: Whether to initialize immediately
        """
        self._api = _TesseractAPI()
        self._lang = lang
        self._path = path
        self._initialized = False
        
        if init:
            self.Init(path, lang, oem, psm)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.End()
    
    @staticmethod
    def Version():
        """Get Tesseract version string."""
        return _TesseractAPI.version()
    
    def Init(self, path='', lang='eng', oem=OEM.DEFAULT, psm=PSM.AUTO):
        """Initialize the API with language and data path.
        
        Args:
            path: Data path for tessdata (empty string uses system default)
            lang: Language code
            oem: OCR Engine Mode (ignored)
            psm: Page Segmentation Mode (not fully implemented)
        
        Raises:
            RuntimeError: If initialization fails
        """
        result = self._api.init(path, lang)
        if result != 0:
            raise RuntimeError(f"Failed to initialize Tesseract with lang={lang}")
        self._initialized = True
        self._lang = lang
        self._path = path
    
    def End(self):
        """End API session and free resources."""
        # Our API handles cleanup automatically
        self._initialized = False
    
    def SetImage(self, image):
        """Set image for OCR.
        
        Args:
            image: PIL Image object
        
        Raises:
            RuntimeError: If image cannot be set
        """
        if not self._initialized:
            raise RuntimeError("API not initialized. Call Init() first.")
        
        # Convert PIL Image to NumPy array
        if isinstance(image, Image.Image):
            # Ensure RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image)
        elif isinstance(image, np.ndarray):
            image_array = image
        else:
            raise TypeError(f"Image must be PIL.Image or numpy.ndarray, got {type(image)}")
        
        self._api.set_image(image_array)
    
    def SetImageFile(self, filename):
        """Set image from file.
        
        Args:
            filename: Path to image file
        
        Raises:
            RuntimeError: If file cannot be loaded
        """
        try:
            image = Image.open(filename)
            self.SetImage(image)
        except Exception as e:
            raise RuntimeError(f"Failed to load image from {filename}: {e}")
    
    def GetUTF8Text(self):
        """Get recognized text as UTF-8 string.
        
        Returns:
            str: Recognized text
        
        Raises:
            RuntimeError: If no image set or recognition fails
        """
        if not self._initialized:
            raise RuntimeError("API not initialized. Call Init() first.")
        
        return self._api.get_utf8_text()
    
    def Recognize(self, timeout=0):
        """Recognize the image.
        
        Args:
            timeout: Timeout in milliseconds (ignored in this implementation)
        
        Returns:
            bool: True on success
        """
        if not self._initialized:
            return False
        
        result = self._api.recognize()
        return result == 0
    
    def GetIterator(self):
        """Get result iterator (not fully implemented).
        
        Returns:
            None (not implemented)
        """
        # Not implemented - would require wrapping the iterator
        return None
    
    def MeanTextConf(self):
        """Get mean text confidence.
        
        Returns:
            int: Confidence score 0-100
        """
        if not self._initialized:
            return 0
        
        return self._api.get_mean_confidence()
    
    def AllWordConfidences(self):
        """Get confidence for all words.
        
        Returns:
            list: List of confidence scores
        """
        if not self._initialized:
            return []
        
        # Get bounding boxes which include confidence
        self._api.recognize()
        boxes = self._api.get_bounding_boxes()
        return [int(box['confidence']) for box in boxes]
    
    def AllWords(self):
        """Get all detected words.
        
        Returns:
            list: List of words
        """
        if not self._initialized:
            return []
        
        self._api.recognize()
        boxes = self._api.get_bounding_boxes()
        return [box['text'] for box in boxes]
    
    def MapWordConfidences(self):
        """Get word and confidence pairs.
        
        Returns:
            list: List of (word, confidence) tuples
        """
        if not self._initialized:
            return []
        
        self._api.recognize()
        boxes = self._api.get_bounding_boxes()
        return [(box['text'], int(box['confidence'])) for box in boxes]
    
    def SetPageSegMode(self, psm):
        """Set page segmentation mode (not fully implemented).
        
        Args:
            psm: Page segmentation mode
        """
        # Not implemented - would require C++ API extension
        pass
    
    def GetPageSegMode(self):
        """Get page segmentation mode.
        
        Returns:
            int: Current PSM (always returns AUTO)
        """
        return PSM.AUTO
    
    def SetVariable(self, name, value):
        """Set a Tesseract variable (not fully implemented).
        
        Args:
            name: Variable name
            value: Variable value
        
        Returns:
            bool: False (not implemented)
        """
        # Not implemented
        return False
    
    def GetInitLanguagesAsString(self):
        """Get initialized languages.
        
        Returns:
            str: Language string
        """
        return self._lang if self._initialized else ''
    
    def SetRectangle(self, left, top, width, height):
        """Set recognition rectangle (not implemented).
        
        Args:
            left: Left coordinate
            top: Top coordinate
            width: Width
            height: Height
        """
        # Not implemented - would require C++ API extension
        pass


# Helper functions matching tesserocr
def image_to_text(image, lang='eng', psm=PSM.AUTO):
    """Convert image to text (tesserocr-compatible helper).
    
    Args:
        image: PIL Image object
        lang: Language code
        psm: Page segmentation mode
    
    Returns:
        str: Recognized text
    """
    with PyTessBaseAPI(lang=lang, psm=psm) as api:
        api.SetImage(image)
        return api.GetUTF8Text()


def file_to_text(filename, lang='eng', psm=PSM.AUTO):
    """Convert file to text (tesserocr-compatible helper).
    
    Args:
        filename: Path to image file
        lang: Language code
        psm: Page segmentation mode
    
    Returns:
        str: Recognized text
    """
    with PyTessBaseAPI(lang=lang, psm=psm) as api:
        api.SetImageFile(filename)
        return api.GetUTF8Text()


def get_languages(path=''):
    """Get available languages (simplified version).
    
    Args:
        path: Tessdata path
    
    Returns:
        tuple: (path, list of languages)
    """
    # Simplified - just return common languages
    # In a full implementation, this would scan the tessdata directory
    return (path or '/usr/share/tesseract-ocr/tessdata/', ['eng'])


def tesseract_version():
    """Get Tesseract version string.
    
    Returns:
        str: Version string
    """
    return PyTessBaseAPI.Version()


__all__ = [
    'PyTessBaseAPI',
    'OEM', 'PSM', 'RIL',
    'image_to_text', 'file_to_text',
    'get_languages', 'tesseract_version',
]
