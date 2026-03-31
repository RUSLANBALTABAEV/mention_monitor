import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

CITY_MAP = {
    "москва": ("Россия", "Москва"),
    "moscow": ("Россия", "Москва"),
    "санкт-петербург": ("Россия", "Санкт-Петербург"),
    "питер": ("Россия", "Санкт-Петербург"),
    "спб": ("Россия", "Санкт-Петербург"),
    "saint petersburg": ("Россия", "Санкт-Петербург"),
    "новосибирск": ("Россия", "Новосибирск"),
    "екатеринбург": ("Россия", "Екатеринбург"),
    "казань": ("Россия", "Казань"),
    "нижний новгород": ("Россия", "Нижний Новгород"),
    "ростов-на-дону": ("Россия", "Ростов-на-Дону"),
    "краснодар": ("Россия", "Краснодар"),
    "сочи": ("Россия", "Сочи"),
    "минск": ("Беларусь", "Минск"),
    "киев": ("Украина", "Киев"),
    "алматы": ("Казахстан", "Алматы"),
    "ташкент": ("Узбекистан", "Ташкент"),
    "london": ("Великобритания", "Лондон"),
    "paris": ("Франция", "Париж"),
    "berlin": ("Германия", "Берлин"),
    "new york": ("США", "Нью-Йорк"),
    "dubai": ("ОАЭ", "Дубай"),
    "istanbul": ("Турция", "Стамбул"),
}
COUNTRY_KEYWORDS = {
    "россия": "Россия", "рф": "Россия", "russia": "Россия",
    "беларусь": "Беларусь", "belarus": "Беларусь",
    "украина": "Украина", "ukraine": "Украина",
    "казахстан": "Казахстан", "kazakhstan": "Казахстан",
    "узбекистан": "Узбекистан", "uzbekistan": "Узбекистан",
    "германия": "Германия", "germany": "Германия",
    "франция": "Франция", "france": "Франция",
    "сша": "США", "usa": "США",
    "китай": "Китай", "china": "Китай",
    "турция": "Турция", "turkey": "Турция",
}
_GEO_PATTERNS = [
    r"(?:в|из|по|для|г\.?|город|города|городе)\s+([А-ЯЁа-яёA-Za-z\-]+(?:\s+[А-ЯЁа-яёA-Za-z\-]+)?)",
    r"(?:живу|нахожусь|работаю|приехал|переехал)\s+(?:в|из)\s+([А-ЯЁа-яёA-Za-z\-]+(?:\s+[А-ЯЁа-яёA-Za-z\-]+)?)",
    r"#([А-ЯЁа-яё]{4,})",
]

def extract_geo_from_text(text: str) -> Dict[str, Optional[str]]:
    if not text:
        return {"country": None, "city": None}
    try:
        from geotext import GeoText
        places = GeoText(text)
        if places.cities or places.countries:
            city = places.cities[0] if places.cities else None
            country = places.countries[0] if places.countries else None
            return {"country": country, "city": city}
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"geotext error: {e}")

    text_lower = text.lower()
    found_city = None
    found_country = None
    for key, (country, city) in CITY_MAP.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            found_city = city
            found_country = country
            break
    if not found_country:
        for key, country in COUNTRY_KEYWORDS.items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                found_country = country
                break
    if not found_city:
        for pattern in _GEO_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                candidate = match.strip().lower()
                if candidate in CITY_MAP:
                    found_country, found_city = CITY_MAP[candidate]
                    break
            if found_city:
                break
    return {"country": found_country, "city": found_city}