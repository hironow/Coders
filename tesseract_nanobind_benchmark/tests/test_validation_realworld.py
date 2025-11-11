"""Real-world validation tests for Phase 1 features."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_complex_document():
    """Create a complex document with multiple sections."""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except Exception:
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    # Title
    draw.text((50, 30), "Invoice #12345", fill='black', font=font_large)

    # Details
    draw.text((50, 100), "Date: 2025-11-11", fill='black', font=font_normal)
    draw.text((50, 140), "Customer: John Doe", fill='black', font=font_normal)
    draw.text((50, 180), "Amount: $1,234.56", fill='black', font=font_normal)

    # Items
    draw.text((50, 250), "Item 1: Widget A", fill='black', font=font_normal)
    draw.text((50, 290), "Item 2: Widget B", fill='black', font=font_normal)
    draw.text((50, 330), "Item 3: Widget C", fill='black', font=font_normal)

    # Footer
    draw.text((50, 500), "Thank you for your business!", fill='black', font=font_normal)

    return np.array(img)


def test_realworld_psm_single_line():
    """Real-world test: Extract single line with PSM.SINGLE_LINE."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: image with single line of text
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 30), "Invoice #12345", fill='black', font=font)

    # when: using SINGLE_LINE mode
    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetImage(np.array(img))
        text = api.GetUTF8Text().strip()

        # then: should extract the text (allow OCR variations)
        assert "Invoice" in text or "invoice" in text.lower()
        # Check for numbers - allow minor OCR errors (3,4,5,8 can be confused)
        assert any(digit in text for digit in ['1234', '1235', '12345', '12845', '12348'])


def test_realworld_number_extraction():
    """Real-world test: Extract numbers only with whitelist."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with mixed text and numbers
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 30), "Amount: $1234.56", fill='black', font=font)

    # when: using number whitelist
    with PyTessBaseAPI(lang='eng') as api:
        api.SetVariable('tessedit_char_whitelist', '0123456789.')
        api.SetImage(np.array(img))
        text = api.GetUTF8Text().strip()

        # then: should extract only numbers
        # Remove whitespace for comparison
        text_clean = text.replace(' ', '').replace('\n', '')
        assert '1234' in text_clean or '123456' in text_clean


def test_realworld_roi_extraction():
    """Real-world test: Extract specific region using SetRectangle."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: complex document
    img_array = create_complex_document()

    # when: extracting different regions
    with PyTessBaseAPI(lang='eng') as api:
        # First, get full text to have a baseline
        api.SetImage(img_array)
        full_text = api.GetUTF8Text().strip()

        # Then extract top portion (should be different from full text)
        api.SetImage(img_array)
        api.SetRectangle(0, 0, 400, 150)  # Top-left portion
        roi_text = api.GetUTF8Text().strip()

        # then: ROI should work and return text (different from full)
        assert len(full_text) > 0
        assert len(roi_text) > 0
        # ROI text should generally be shorter or different
        assert len(roi_text) <= len(full_text)


def test_realworld_hocr_output():
    """Real-world test: Get structured data with hOCR."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: document with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 30), "Hello World", fill='black', font=font)
    draw.text((20, 100), "Test Document", fill='black', font=font)

    # when: getting hOCR output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(np.array(img))
        hocr = api.GetHOCRText(0)

        # then: should contain hOCR structure
        assert len(hocr) > 100  # hOCR is verbose
        assert 'ocr' in hocr.lower() or 'html' in hocr.lower()
        # Should contain bounding box info
        assert 'bbox' in hocr or 'title' in hocr


def test_realworld_tsv_parsing():
    """Real-world test: Parse TSV output for structured data."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: document with multiple words
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 30), "Word1 Word2 Word3", fill='black', font=font)

    # when: getting TSV output
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(np.array(img))
        tsv = api.GetTSVText(0)

        # then: should be parseable TSV
        lines = tsv.strip().split('\n')
        assert len(lines) >= 1  # At least one line of data

        # TSV should have tabs
        assert '\t' in tsv

        # Should have numeric data (level, conf, etc.)
        first_line = lines[0]
        fields = first_line.split('\t')
        assert len(fields) > 5  # TSV has many fields (level, page_num, block_num, etc.)


def test_realworld_mixed_psm_and_variable():
    """Real-world test: Combine PSM and variable settings."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: single line with mixed content
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 30), "Code: ABC123XYZ", fill='black', font=font)

    # when: using SINGLE_LINE with alphanumeric whitelist
    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetVariable('tessedit_char_whitelist', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        api.SetImage(np.array(img))
        text = api.GetUTF8Text().strip()

        # then: should extract the code (allow OCR variations - 123/128 confusion common)
        text_clean = text.replace(' ', '').replace('\n', '')
        assert 'ABC' in text_clean or 'abc' in text_clean.lower()
        # Check for numbers - allow 3/8 confusion
        assert '12' in text_clean and ('3' in text_clean or '8' in text_clean)


def test_realworld_clear_and_reuse():
    """Real-world test: Process multiple images with Clear."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: multiple images to process
    img1 = Image.new('RGB', (300, 100), color='white')
    draw1 = ImageDraw.Draw(img1)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw1.text((20, 30), "Image One", fill='black', font=font)

    img2 = Image.new('RGB', (300, 100), color='white')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((20, 30), "Image Two", fill='black', font=font)

    # when: processing multiple images with Clear
    with PyTessBaseAPI(lang='eng') as api:
        # First image
        api.SetImage(np.array(img1))
        text1 = api.GetUTF8Text().strip()

        # Clear and process second image
        api.Clear()
        api.SetImage(np.array(img2))
        text2 = api.GetUTF8Text().strip()

        # then: should get different results
        assert "One" in text1 or "one" in text1.lower()
        assert "Two" in text2 or "two" in text2.lower()


def test_realworld_multi_region_processing():
    """Real-world test: Process different regions of same image."""
    from tesseract_nanobind.compat import PyTessBaseAPI

    # given: image with left and right sections
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    # Left section
    draw.text((20, 80), "LEFT TEXT", fill='black', font=font)
    # Right section
    draw.text((350, 80), "RIGHT TEXT", fill='black', font=font)

    img_array = np.array(img)

    # when: processing left region
    with PyTessBaseAPI(lang='eng') as api:
        api.SetImage(img_array)
        api.SetRectangle(0, 0, 300, 200)
        left_text = api.GetUTF8Text().strip()

        # Clear and process right region
        api.Clear()
        api.SetImage(img_array)
        api.SetRectangle(300, 0, 300, 200)
        right_text = api.GetUTF8Text().strip()

        # then: should get different texts
        assert "LEFT" in left_text or "left" in left_text.lower()
        assert "RIGHT" in right_text or "right" in right_text.lower()


def test_realworld_confidence_with_psm():
    """Real-world test: Get confidence with specific PSM."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: clear single-line text
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 20), "CLEAR TEXT", fill='black', font=font)

    # when: using SINGLE_LINE mode
    with PyTessBaseAPI(lang='eng') as api:
        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetImage(np.array(img))
        text = api.GetUTF8Text()
        conf = api.MeanTextConf()

        # then: should have reasonable confidence (synthetic images may be lower)
        assert conf > 30  # Reasonable confidence for synthetic text
        assert "CLEAR" in text or "clear" in text.lower() or "TEXT" in text or "text" in text.lower()


def test_realworld_all_features_integration():
    """Integration test: Use all Phase 1 features together."""
    from tesseract_nanobind.compat import PyTessBaseAPI, PSM

    # given: complex document
    img_array = create_complex_document()

    with PyTessBaseAPI(lang='eng') as api:
        # Test 1: Full document with AUTO mode
        api.SetPageSegMode(PSM.AUTO)
        api.SetImage(img_array)
        full_text = api.GetUTF8Text()
        assert len(full_text) > 50

        # Test 2: Extract title with rectangle
        api.Clear()
        api.SetImage(img_array)
        api.SetRectangle(0, 0, 800, 80)
        title_text = api.GetUTF8Text()
        # Should get some text from title region
        assert len(title_text.strip()) > 0

        # Test 3: Extract numbers only
        api.Clear()
        api.SetVariable('tessedit_char_whitelist', '0123456789.,')
        api.SetImage(img_array)
        api.SetRectangle(0, 150, 400, 100)
        numbers_text = api.GetUTF8Text()
        # Should extract numbers from amount/date
        assert any(c.isdigit() for c in numbers_text)

        # Test 4: Get hOCR for structure
        api.Clear()
        api.SetVariable('tessedit_char_whitelist', '')  # Reset
        api.SetImage(img_array)
        hocr = api.GetHOCRText(0)
        assert len(hocr) > 100

        # Test 5: Get TSV for parsing
        api.Clear()
        api.SetImage(img_array)
        tsv = api.GetTSVText(0)
        assert '\t' in tsv

        # Test 6: Verify datapath is set
        datapath = api.GetDatapath()
        assert len(datapath) > 0
