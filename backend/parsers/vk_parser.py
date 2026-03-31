import requests
import logging
from datetime import datetime
from typing import List, Optional
from .base_parser import BaseParser
from app.config import settings
from app.database import SessionLocal
from app.models import Mention
from app.utils.geo import extract_geo_from_text
from app.services.filter_engine import FilterEngine

logger = logging.getLogger(__name__)

VK_API_VERSION = "5.131"
VK_API_BASE = "https://api.vk.com/method"

class VkParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.token = settings.VK_ACCESS_TOKEN

    def _api(self, method: str, **params) -> Optional[dict]:
        if not self.token:
            return None
        params["access_token"] = self.token
        params["v"] = VK_API_VERSION
        try:
            resp = requests.get(f"{VK_API_BASE}/{method}", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                logger.error(f"VK API error: {data['error']}")
                return None
            return data.get("response")
        except Exception as e:
            logger.error(f"VK API request failed: {e}")
            return None

    def parse(self, keywords: List[str], minus_words: Optional[List[str]] = None,
              blacklist_users: Optional[List[str]] = None, whitelist_users: Optional[List[str]] = None):
        if not self.token:
            logger.warning("VK parser skipped: token not set")
            return
        db = SessionLocal()
        try:
            for keyword in keywords:
                logger.info(f"VK: searching for '{keyword}'")
                response = self._api("newsfeed.search", q=keyword, count=100, extended=1)
                if not response:
                    continue
                items = response.get("items", [])
                profiles = {p["id"]: p for p in response.get("profiles", [])}
                groups = {g["id"]: g for g in response.get("groups", [])}
                saved = 0
                for item in items:
                    text = item.get("text", "")
                    if not text:
                        continue
                    if minus_words and not FilterEngine.filter_by_minus_words(text, minus_words):
                        continue
                    owner_id = item.get("owner_id", item.get("from_id", 0))
                    if owner_id > 0:
                        profile = profiles.get(owner_id, {})
                        author = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
                    else:
                        group = groups.get(abs(owner_id), {})
                        author = group.get("name", f"group{abs(owner_id)}")
                    post_id = item.get("id", "")
                    source_url = f"https://vk.com/wall{owner_id}_{post_id}"
                    date_ts = item.get("date")
                    mention_date = datetime.utcfromtimestamp(date_ts) if date_ts else datetime.utcnow()
                    geo = extract_geo_from_text(text)
                    exists = db.query(Mention).filter(Mention.source_url == source_url).first()
                    if exists:
                        continue
                    mention = Mention(
                        text=text,
                        source_type="vk",
                        source_url=source_url,
                        author=author,
                        date=mention_date,
                        geo_country=geo.get("country"),
                        geo_city=geo.get("city"),
                        keyword=keyword,
                        content_type="text",
                        raw_data=item,
                    )
                    db.add(mention)
                    saved += 1
                db.commit()
                logger.info(f"VK: saved {saved} results for '{keyword}'")
        except Exception as e:
            logger.error(f"VK parser: {e}")
            db.rollback()
        finally:
            db.close()

    def get_stories(self, keywords: List[str]) -> List[dict]:
        stories = []
        if not self.token:
            return stories
        response = self._api("stories.get", extended=1)
        if not response:
            return stories
        for story_group in response.get("items", []):
            for story in story_group:
                text = story.get("text", "") or ""
                photo = story.get("photo") or {}
                sizes = photo.get("sizes", [])
                media_url = sizes[-1]["url"] if sizes else None
                stories.append({
                    "text": text,
                    "media_url": media_url,
                    "owner_id": story.get("owner_id"),
                    "story_id": story.get("id"),
                    "date": story.get("date"),
                    "matched_keyword": next((kw for kw in keywords if kw.lower() in text.lower()), None),
                    "raw": story,
                })
        return stories

    def parse_historical(
        self,
        keywords: List[str],
        date_from: "datetime",
        date_to: "datetime",
        minus_words: Optional[List[str]] = None,
    ):
        """Search VK posts within a historical date range using start_time/end_time."""
        if not self.token:
            logger.warning("VK historical parser skipped: token not set")
            return
        import calendar
        db = SessionLocal()
        try:
            start_ts = int(calendar.timegm(date_from.timetuple()))
            end_ts = int(calendar.timegm(date_to.timetuple()))
            for keyword in keywords:
                logger.info(f"VK historical: searching '{keyword}' from {date_from} to {date_to}")
                response = self._api(
                    "newsfeed.search",
                    q=keyword,
                    count=200,
                    extended=1,
                    start_time=start_ts,
                    end_time=end_ts,
                )
                if not response:
                    continue
                items = response.get("items", [])
                profiles = {p["id"]: p for p in response.get("profiles", [])}
                groups = {g["id"]: g for g in response.get("groups", [])}
                saved = 0
                for item in items:
                    text = item.get("text", "")
                    if not text:
                        continue
                    if minus_words and not FilterEngine.filter_by_minus_words(text, minus_words):
                        continue
                    owner_id = item.get("owner_id", item.get("from_id", 0))
                    if owner_id > 0:
                        profile = profiles.get(owner_id, {})
                        author = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
                    else:
                        group = groups.get(abs(owner_id), {})
                        author = group.get("name", f"group{abs(owner_id)}")
                    post_id = item.get("id", "")
                    source_url = f"https://vk.com/wall{owner_id}_{post_id}"
                    date_ts = item.get("date")
                    mention_date = datetime.utcfromtimestamp(date_ts) if date_ts else datetime.utcnow()
                    geo = extract_geo_from_text(text)
                    exists = db.query(Mention).filter(Mention.source_url == source_url).first()
                    if exists:
                        continue
                    mention = Mention(
                        text=text,
                        source_type="vk",
                        source_url=source_url,
                        author=author,
                        date=mention_date,
                        geo_country=geo.get("country"),
                        geo_city=geo.get("city"),
                        keyword=keyword,
                        content_type="text",
                        raw_data=item,
                    )
                    db.add(mention)
                    saved += 1
                db.commit()
                logger.info(f"VK historical: saved {saved} results for '{keyword}'")
        except Exception as e:
            logger.error(f"VK historical parser: {e}")
            db.rollback()
        finally:
            db.close()
