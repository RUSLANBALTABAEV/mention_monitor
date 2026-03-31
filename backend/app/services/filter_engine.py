import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FilterEngine:
    @staticmethod
    def filter_by_keywords(text: str, keywords: List[str], operator: str = "OR", exact_match: bool = False) -> bool:
        if not keywords:
            return True
        def _match(kw: str) -> bool:
            if exact_match:
                return bool(re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))
            return kw.lower() in text.lower()
        if operator == "AND":
            return all(_match(kw) for kw in keywords)
        else:
            return any(_match(kw) for kw in keywords)

    @staticmethod
    def filter_by_minus_words(text: str, minus_words: List[str]) -> bool:
        if not minus_words:
            return True
        return not any(mw.lower() in text.lower() for mw in minus_words)

    @staticmethod
    def filter_by_source(source_url: str, whitelist: List[str], blacklist: List[str]) -> bool:
        if whitelist:
            return any(source_url.startswith(allowed) for allowed in whitelist)
        if blacklist:
            return not any(source_url.startswith(blocked) for blocked in blacklist)
        return True

    @staticmethod
    def filter_by_user(author: str, blacklist_users: List[str]) -> bool:
        if not author or not blacklist_users:
            return True
        return author not in blacklist_users

    @staticmethod
    def filter_by_user_whitelist(author: str, whitelist_users: List[str]) -> bool:
        if not whitelist_users:
            return True
        return author in whitelist_users if author else False

    @staticmethod
    def filter_by_geo(mention_geo: Dict, required_country: Optional[str], required_city: Optional[str]) -> bool:
        if required_country and mention_geo.get("country") != required_country:
            return False
        if required_city and mention_geo.get("city") != required_city:
            return False
        return True

    @staticmethod
    def filter_by_time(mention_date: datetime, time_filter: str, custom_range: Optional[Tuple[datetime, datetime]] = None) -> bool:
        now = datetime.utcnow()
        if time_filter == "24h":
            return mention_date >= now - timedelta(hours=24)
        elif time_filter == "3d":
            return mention_date >= now - timedelta(days=3)
        elif time_filter == "week":
            return mention_date >= now - timedelta(days=7)
        elif time_filter == "custom" and custom_range:
            return custom_range[0] <= mention_date <= custom_range[1]
        return True

    @staticmethod
    def apply_all_filters(
        mention: Dict,
        keywords: List[str],
        minus_words: List[str],
        whitelist: List[str],
        blacklist: List[str],
        blacklist_users: List[str],
        required_country: Optional[str],
        required_city: Optional[str],
        time_filter: str,
        custom_time_range: Optional[Tuple[datetime, datetime]] = None,
        keyword_operator: str = "OR",
        exact_match: bool = False,
        whitelist_users: Optional[List[str]] = None,
    ) -> bool:
        text = mention.get("text", "") or mention.get("ocr_text", "") or ""
        if not text:
            return False
        if not FilterEngine.filter_by_keywords(text, keywords, keyword_operator, exact_match):
            return False
        if not FilterEngine.filter_by_minus_words(text, minus_words):
            return False
        source_url = mention.get("source_url", "")
        if not FilterEngine.filter_by_source(source_url, whitelist, blacklist):
            return False
        author = mention.get("author") or ""
        if not FilterEngine.filter_by_user(author, blacklist_users):
            return False
        if whitelist_users and not FilterEngine.filter_by_user_whitelist(author, whitelist_users):
            return False
        geo = {"country": mention.get("geo_country"), "city": mention.get("geo_city")}
        if not FilterEngine.filter_by_geo(geo, required_country, required_city):
            return False
        mention_date = mention.get("date")
        if mention_date and not FilterEngine.filter_by_time(mention_date, time_filter, custom_time_range):
            return False
        return True