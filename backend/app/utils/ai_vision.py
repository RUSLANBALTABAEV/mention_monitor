"""
AI/ML image analysis for Stories content.
Supports Google Vision API (preferred) and OpenCV (fallback).
Detects objects, context phrases (e.g. "looking for apartment", "need marketer"),
and extracts additional text from images.
"""
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# ─── Context keyword patterns for real-estate / services ────────────────────
CONTEXT_PATTERNS = [
    # Real estate
    (["квартир", "апартамент", "студия", "комнат", "жильё", "жилье",
      "снять", "сдать", "купить", "продам", "арендa", "аренда",
      "apartment", "flat", "rent", "buy property"], "ищу/сдаю квартиру"),
    # Recruitment / jobs
    (["маркетолог", "smm", "дизайнер", "разработчик", "программист",
      "вакансия", "ищу работу", "нужен специалист", "требуется",
      "marketer", "designer", "developer", "job", "vacancy"], "поиск специалиста/работы"),
    # Cars
    (["автомобиль", "машина", "авто", "продам авто", "куплю авто",
      "car", "vehicle", "auto"], "объявление о машине"),
    # Food / restaurant
    (["ресторан", "кафе", "еда", "доставка", "restaurant", "cafe",
      "food", "delivery"], "еда/ресторан"),
    # Events
    (["концерт", "вечеринка", "мероприятие", "event", "party",
      "concert", "invitation"], "мероприятие/событие"),
    # Travel
    (["путешествие", "тур", "отдых", "отель", "билет",
      "travel", "trip", "hotel", "ticket"], "путешествие/туризм"),
    # Business offers
    (["бизнес", "партнёр", "инвестиции", "стартап",
      "business", "partner", "investment", "startup"], "бизнес-предложение"),
]


def _detect_context_from_labels(tags: List[str], objects: List[str], text: str = "") -> str:
    """
    Map detected labels / objects / text to a human-readable context phrase.
    Returns the best-matching context or empty string.
    """
    combined = " ".join(tags + objects + [text]).lower()
    for keywords_group, context_label in CONTEXT_PATTERNS:
        if any(kw.lower() in combined for kw in keywords_group):
            return context_label
    return ""


def analyze_image(image_bytes: bytes) -> Dict:
    """
    Main entry point for image analysis.
    Tries Google Vision API first; falls back to enhanced OpenCV analysis.
    Returns: {objects, tags, context, text}
    """
    if not image_bytes:
        return {"objects": [], "tags": [], "context": "", "text": ""}

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    if credentials_path and os.path.exists(credentials_path):
        result = _analyze_with_google_vision(image_bytes)
        if result:
            return result

    return _analyze_with_opencv(image_bytes)


def _analyze_with_google_vision(image_bytes: bytes) -> Optional[Dict]:
    try:
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.annotate_image(
            {
                "image": image,
                "features": [
                    {"type_": vision.Feature.Type.LABEL_DETECTION, "max_results": 30},
                    {"type_": vision.Feature.Type.TEXT_DETECTION},
                    {"type_": vision.Feature.Type.OBJECT_LOCALIZATION, "max_results": 15},
                    {"type_": vision.Feature.Type.SAFE_SEARCH_DETECTION},
                    {"type_": vision.Feature.Type.IMAGE_PROPERTIES},
                ],
            }
        )

        if response.error.message:
            logger.error(f"Google Vision error: {response.error.message}")
            return None

        tags = [label.description for label in response.label_annotations]
        objects = [obj.name for obj in response.localized_object_annotations]
        text = (
            response.text_annotations[0].description.strip()
            if response.text_annotations
            else ""
        )

        context = _detect_context_from_labels(tags, objects, text)
        summary = _build_summary(tags, objects, context)

        return {"objects": objects, "tags": tags, "context": context, "text": text, "summary": summary}

    except Exception as e:
        logger.error(f"Google Vision API: {e}")
        return None


def _analyze_with_opencv(image_bytes: bytes) -> Dict:
    """
    Enhanced OpenCV-based analysis:
    - Face detection (Haar Cascade)
    - Color/brightness analysis
    - Text region detection (MSER)
    - Dominant color extraction
    - Layout analysis (horizontal/vertical/square)
    - Context inference from visual cues
    """
    try:
        import cv2
        import numpy as np

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"objects": [], "tags": [], "context": "", "text": ""}

        h, w = img.shape[:2]
        tags: List[str] = []
        objects: List[str] = []

        # ── Brightness & saturation ──────────────────────────────────────────
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        avg_saturation = float(hsv[:, :, 1].mean())
        avg_brightness = float(hsv[:, :, 2].mean())

        if avg_brightness < 50:
            tags.append("тёмное изображение")
        elif avg_brightness > 210:
            tags.append("яркое изображение")
        if avg_saturation > 120:
            tags.append("насыщенные цвета")
        elif avg_saturation < 20:
            tags.append("чёрно-белое изображение")

        # ── Dominant color ───────────────────────────────────────────────────
        dominant_color = _get_dominant_color(img)
        if dominant_color:
            tags.append(f"основной цвет: {dominant_color}")

        # ── Face detection ───────────────────────────────────────────────────
        try:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_eq = cv2.equalizeHist(gray)
            faces = face_cascade.detectMultiScale(
                gray_eq, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25)
            )
            if len(faces) > 0:
                tags.append("люди на фото")
                objects.append(f"лица: {len(faces)}")
        except Exception:
            pass

        # ── Text region detection (MSER) ─────────────────────────────────────
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            if len(regions) > 10:
                tags.append("текст на изображении")
                objects.append("текстовые области")
        except Exception:
            pass

        # ── Layout orientation ───────────────────────────────────────────────
        if w > h * 1.5:
            tags.append("горизонтальное фото")
        elif h > w * 1.5:
            tags.append("вертикальное фото")
        else:
            tags.append("квадратное фото")

        # ── Resolution ───────────────────────────────────────────────────────
        if w * h > 2_000_000:
            tags.append("высокое разрешение")
        elif w * h < 90_000:
            tags.append("низкое разрешение")

        # ── Real estate context: large interior/room detection ────────────────
        # Heuristic: bright, saturated, horizontal, many textures → could be interior
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var > 200 and avg_brightness > 100 and w > h:
                tags.append("интерьер/помещение")
        except Exception:
            pass

        context = _detect_context_from_labels(tags, objects)
        summary = _build_summary(tags, objects, context)

        return {"objects": objects, "tags": tags, "context": context, "text": "", "summary": summary}

    except Exception as e:
        logger.error(f"OpenCV анализ: {e}")
        return {"objects": [], "tags": [], "context": "", "text": ""}


def _get_dominant_color(img) -> Optional[str]:
    """Return name of the dominant color in the image."""
    try:
        import cv2
        import numpy as np

        img_small = cv2.resize(img, (50, 50))
        pixels = img_small.reshape(-1, 3).astype(float)
        avg_bgr = pixels.mean(axis=0)
        b, g, r = avg_bgr

        color_names = {
            "красный": (r > 150 and g < 100 and b < 100),
            "зелёный": (g > 150 and r < 100 and b < 100),
            "синий": (b > 150 and r < 100 and g < 100),
            "жёлтый": (r > 150 and g > 150 and b < 100),
            "белый": (r > 200 and g > 200 and b > 200),
            "чёрный": (r < 60 and g < 60 and b < 60),
        }
        for name, condition in color_names.items():
            if condition:
                return name
        return None
    except Exception:
        return None


def _build_summary(tags: List[str], objects: List[str], context: str) -> str:
    """Build a human-readable summary of analysis results."""
    parts = []
    if context:
        parts.append(f"Контекст: {context}")
    if objects:
        parts.append("Объекты: " + ", ".join(objects[:5]))
    if tags:
        parts.append("Теги: " + ", ".join(tags[:8]))
    return ". ".join(parts)


# Legacy alias for backward compatibility
def _build_context(tags: list, objects: list) -> str:
    return _detect_context_from_labels(tags, objects)
