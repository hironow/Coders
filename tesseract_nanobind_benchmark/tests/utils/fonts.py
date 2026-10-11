"""Real fonts for repeatable OCR test images."""

from pathlib import Path

from PIL import ImageFont

FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def load_test_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH.is_file():
        return ImageFont.truetype(str(FONT_PATH), size)
    return ImageFont.load_default(size=size)
