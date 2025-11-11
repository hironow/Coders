#!/usr/bin/env python3
"""Basic usage example for tesseract_nanobind."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tesseract_nanobind import TesseractAPI


def main():
    """Demonstrate basic OCR functionality."""
    # Create a simple test image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    
    draw.text((20, 80), "Hello Tesseract!", fill='black', font=font)
    
    # Convert to numpy array
    image_array = np.array(img)
    
    # Initialize Tesseract
    api = TesseractAPI()
    print(f"Tesseract version: {TesseractAPI.version()}")
    
    # Initialize with English language
    result = api.init("", "eng")
    if result != 0:
        print("Failed to initialize Tesseract")
        return
    
    print("\n=== Basic Text Extraction ===")
    api.set_image(image_array)
    text = api.get_utf8_text()
    print(f"Extracted text: {text.strip()}")
    
    # Get confidence score
    print("\n=== Confidence Score ===")
    api.set_image(image_array)
    api.recognize()
    confidence = api.get_mean_confidence()
    print(f"Mean confidence: {confidence}%")
    
    # Get bounding boxes
    print("\n=== Word Bounding Boxes ===")
    api.set_image(image_array)
    api.recognize()
    boxes = api.get_bounding_boxes()
    
    for i, box in enumerate(boxes):
        print(f"Word {i+1}:")
        print(f"  Text: {box['text']}")
        print(f"  Position: ({box['left']}, {box['top']})")
        print(f"  Size: {box['width']}x{box['height']}")
        print(f"  Confidence: {box['confidence']:.1f}%")


if __name__ == "__main__":
    main()
