from celery import shared_task
from app.utils.ocr import extract_text_from_image
from app.utils.ai_vision import analyze_image
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_story_image(image_bytes: bytes, story_id: int):
    try:
        text = extract_text_from_image(image_bytes)
        ai_result = analyze_image(image_bytes)
        logger.info(f"Processed story {story_id}: OCR length {len(text)}")
        return {"text": text, "ai": ai_result}
    except Exception as e:
        logger.error(f"Error processing story {story_id}: {e}")
        return {"error": str(e)}