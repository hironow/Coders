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


class PT:
    """PolyBlockType enumeration for layout analysis."""
    UNKNOWN = 0
    FLOWING_TEXT = 1
    HEADING_TEXT = 2
    PULLOUT_TEXT = 3
    EQUATION = 4
    INLINE_EQUATION = 5
    TABLE = 6
    VERTICAL_TEXT = 7
    CAPTION_TEXT = 8
    FLOWING_IMAGE = 9
    HEADING_IMAGE = 10
    PULLOUT_IMAGE = 11
    HORZ_LINE = 12
    VERT_LINE = 13
    NOISE = 14
    COUNT = 15


class Orientation:
    """Page orientation enumeration."""
    PAGE_UP = 0
    PAGE_RIGHT = 1
    PAGE_DOWN = 2
    PAGE_LEFT = 3


class WritingDirection:
    """Writing direction enumeration."""
    LEFT_TO_RIGHT = 0
    RIGHT_TO_LEFT = 1
    TOP_TO_BOTTOM = 2
    BOTTOM_TO_TOP = 3


class TextlineOrder:
    """Textline order enumeration."""
    LEFT_TO_RIGHT = 0
    RIGHT_TO_LEFT = 1
    TOP_TO_BOTTOM = 2
    BOTTOM_TO_TOP = 3


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

        Raises:
            RuntimeError: If API not initialized or recognition fails
        """
        if not self._initialized:
            raise RuntimeError("API not initialized. Call Init() first.")

        result = self._api.recognize()
        if result != 0:
            raise RuntimeError(f"Recognition failed with error code: {result}")
        return True
    
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
        """Set page segmentation mode.

        Args:
            psm: Page segmentation mode (PSM enum value)
        """
        if not self._initialized:
            return
        self._api.set_page_seg_mode(psm)

    def GetPageSegMode(self):
        """Get page segmentation mode.

        Returns:
            int: Current PSM value
        """
        if not self._initialized:
            return PSM.AUTO
        return self._api.get_page_seg_mode()

    def SetVariable(self, name, value):
        """Set a Tesseract variable.

        Args:
            name: Variable name
            value: Variable value (will be converted to string)

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._initialized:
            return False
        return self._api.set_variable(name, str(value))
    
    def GetInitLanguagesAsString(self):
        """Get initialized languages.

        Returns:
            str: Language string
        """
        if not self._initialized:
            return ''
        return self._api.get_init_languages_as_string()

    def DetectOrientationScript(self):
        """Detect page orientation and script.

        Returns:
            tuple: (orientation_deg, orientation_conf, script_name, script_conf)
                orientation_deg: Orientation in degrees (0, 90, 180, 270)
                orientation_conf: Confidence for orientation (0-100)
                script_name: Detected script name (e.g., 'Latin', 'Han')
                script_conf: Confidence for script (0-100)
        """
        if not self._initialized:
            return (0, 0.0, '', 0.0)
        return self._api.detect_orientation_script()

    def GetComponentImages(self, level, text_only=True):
        """Get bounding boxes for components at specified level.

        Args:
            level: RIL level (BLOCK, PARA, TEXTLINE, WORD, SYMBOL)
            text_only: If True, only return text components

        Returns:
            list: List of tuples (x, y, w, h) for each component
        """
        if not self._initialized:
            return []
        return self._api.get_component_images(level, text_only)

    def GetWords(self):
        """Get all words with text, confidence, and bounding boxes.

        Returns:
            list: List of tuples (word, confidence, x, y, w, h)
                word: UTF-8 text
                confidence: Confidence score (0-100)
                x, y: Top-left corner coordinates
                w, h: Width and height
        """
        if not self._initialized:
            return []
        return self._api.get_words()

    def GetTextlines(self):
        """Get all text lines with text, confidence, and bounding boxes.

        Returns:
            list: List of tuples (line, confidence, x, y, w, h)
                line: UTF-8 text
                confidence: Confidence score (0-100)
                x, y: Top-left corner coordinates
                w, h: Width and height
        """
        if not self._initialized:
            return []
        return self._api.get_textlines()

    def GetThresholdedImage(self):
        """Get the thresholded (binarized) image used for OCR.

        Returns:
            numpy.ndarray: Thresholded image as 2D array (height, width)
                Values are typically 0 (black) or 255 (white)
                Returns empty array if no image has been set

        Note:
            The returned array is always CPU-based (NumPy).
            Tesseract is a CPU library and does not support GPU processing.
        """
        if not self._initialized:
            return np.array([[]], dtype=np.uint8)

        # C++ returns (height, width, bytes_data)
        height, width, data_bytes = self._api.get_thresholded_image()

        if height == 0 or width == 0:
            return np.array([[]], dtype=np.uint8)

        # Convert bytes to numpy array
        # Use .copy() to make it writable (frombuffer creates read-only array)
        data = np.frombuffer(data_bytes, dtype=np.uint8).copy()
        return data.reshape((height, width))

    def SetRectangle(self, left, top, width, height):
        """Set recognition rectangle to restrict OCR to a sub-image.

        Args:
            left: Left coordinate
            top: Top coordinate
            width: Width
            height: Height
        """
        if not self._initialized:
            return
        self._api.set_rectangle(left, top, width, height)

    def GetHOCRText(self, page_number=0):
        """Get OCR result in hOCR format.

        Args:
            page_number: Page number (default: 0)

        Returns:
            str: OCR result in hOCR format
        """
        if not self._initialized:
            return ""
        return self._api.get_hocr_text(page_number)

    def GetTSVText(self, page_number=0):
        """Get OCR result in TSV format.

        Args:
            page_number: Page number (default: 0)

        Returns:
            str: OCR result in TSV format
        """
        if not self._initialized:
            return ""
        return self._api.get_tsv_text(page_number)

    def GetBoxText(self, page_number=0):
        """Get OCR result in box file format.

        Args:
            page_number: Page number (default: 0)

        Returns:
            str: OCR result in box file format
        """
        if not self._initialized:
            return ""
        return self._api.get_box_text(page_number)

    def GetUNLVText(self):
        """Get OCR result in UNLV format.

        Returns:
            str: OCR result in UNLV format
        """
        if not self._initialized:
            return ""
        return self._api.get_unlv_text()

    def Clear(self):
        """Clear recognition results without freeing loaded language data."""
        if self._initialized:
            self._api.clear()

    def ClearAdaptiveClassifier(self):
        """Clear the adaptive classifier."""
        if self._initialized:
            self._api.clear_adaptive_classifier()

    def GetDatapath(self):
        """Get tessdata path.

        Returns:
            str: Path to tessdata directory
        """
        if not self._initialized:
            return ""
        return self._api.get_datapath()

    def GetIntVariable(self, name):
        """Get an integer Tesseract variable.

        Args:
            name: Variable name

        Returns:
            int or None: Variable value if found, None otherwise
        """
        if not self._initialized:
            return None
        value = [0]  # mutable container for output parameter
        if self._api.get_int_variable(name, value):
            return value[0]
        return None

    def GetBoolVariable(self, name):
        """Get a boolean Tesseract variable.

        Args:
            name: Variable name

        Returns:
            bool or None: Variable value if found, None otherwise
        """
        if not self._initialized:
            return None
        value = [False]  # mutable container for output parameter
        if self._api.get_bool_variable(name, value):
            return value[0]
        return None

    def GetDoubleVariable(self, name):
        """Get a double Tesseract variable.

        Args:
            name: Variable name

        Returns:
            float or None: Variable value if found, None otherwise
        """
        if not self._initialized:
            return None
        value = [0.0]  # mutable container for output parameter
        if self._api.get_double_variable(name, value):
            return value[0]
        return None

    def GetStringVariable(self, name):
        """Get a string Tesseract variable.

        Args:
            name: Variable name

        Returns:
            str: Variable value (empty string if not found)
        """
        if not self._initialized:
            return ""
        return self._api.get_string_variable(name)


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
    'OEM', 'PSM', 'RIL', 'PT', 'Orientation', 'WritingDirection', 'TextlineOrder',
    'image_to_text', 'file_to_text',
    'get_languages', 'tesseract_version',
]
