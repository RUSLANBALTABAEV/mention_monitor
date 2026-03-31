import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_image(image_bytes: bytes, lang='rus+eng') -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""