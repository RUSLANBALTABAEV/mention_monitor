import logging
import requests
from datetime import datetime
from typing import List, Optional

from app.utils.ocr import extract_text_from_image
from app.utils.ai_vision import analyze_image
from app.utils.geo import extract_geo_from_text
from app.services.filter_engine import FilterEngine
from app.database import SessionLocal
from app.models import Mention

logger = logging.getLogger(__name__)

class StoryProcessor:
    def process(self, keywords: Optional[List[str]] = None, minus_words: Optional[List[str]] = None,
                blacklist_users: Optional[List[str]] = None, whitelist_users: Optional[List[str]] = None):
        keywords = keywords or []
        minus_words = minus_words or []
        logger.info("StoryProcessor: starting story collection")
        all_stories = []
        try:
            from parsers.vk_parser import VkParser
            vk = VkParser()
            vk_stories = vk.get_stories(keywords)
            for s in vk_stories:
                s["source_type"] = "vk"
            all_stories.extend(vk_stories)
            logger.info(f"VK Stories: {len(vk_stories)}")
        except Exception as e:
            logger.error(f"VK Stories error: {e}")
        try:
            from parsers.tenchat_parser import TenChatParser
            tc = TenChatParser()
            tc_stories = tc.get_stories(keywords)
            for s in tc_stories:
                s["source_type"] = "tenchat"
            all_stories.extend(tc_stories)
            logger.info(f"TenChat Stories: {len(tc_stories)}")
        except Exception as e:
            logger.error(f"TenChat Stories error: {e}")
        self._save_stories(all_stories, keywords, minus_words, blacklist_users, whitelist_users)

    def _save_stories(self, stories: List[dict], keywords: List[str], minus_words: List[str],
                      blacklist_users: List[str], whitelist_users: List[str]):
        db = SessionLocal()
        saved = 0
        try:
            for story in stories:
                media_url = story.get("media_url")
                raw_text = story.get("text", "") or ""
                source_type = story.get("source_type", "story")
                owner_id = story.get("owner_id")
                story_id = story.get("story_id")
                if source_type == "vk" and owner_id and story_id:
                    source_url = f"https://vk.com/stories{owner_id}_{story_id}"
                elif media_url:
                    source_url = media_url
                else:
                    source_url = f"story://{source_type}/{datetime.utcnow().timestamp()}"
                exists = db.query(Mention).filter(Mention.source_url == source_url).first()
                if exists:
                    continue
                ocr_text = ""
                ai_tags = []
                ai_context = ""
                if media_url:
                    try:
                        img_bytes = self._download_media(media_url)
                        if img_bytes:
                            ocr_text = extract_text_from_image(img_bytes) or ""
                            ai_result = analyze_image(img_bytes)
                            ai_tags = ai_result.get("tags", [])
                            ai_context = ai_result.get("context", "")
                    except Exception as e:
                        logger.warning(f"Error processing media {media_url}: {e}")
                full_text = " ".join(filter(None, [raw_text, ocr_text, ai_context]))
                matched_keyword = story.get("matched_keyword") or next((kw for kw in keywords if kw.lower() in full_text.lower()), None)
                if not matched_keyword and keywords:
                    continue
                if minus_words and full_text and not FilterEngine.filter_by_minus_words(full_text, minus_words):
                    continue
                geo = extract_geo_from_text(full_text)
                date_ts = story.get("date")
                mention_date = datetime.utcfromtimestamp(date_ts) if date_ts else datetime.utcnow()
                mention = Mention(
                    text=raw_text or ocr_text or ai_context,
                    source_type=source_type,
                    source_url=source_url,
                    author=str(owner_id) if owner_id else None,
                    date=mention_date,
                    geo_country=geo.get("country"),
                    geo_city=geo.get("city"),
                    keyword=matched_keyword or "",
                    content_type="story",
                    ocr_text=ocr_text,
                    media_url=media_url,
                    raw_data={"ai_tags": ai_tags, "ai_context": ai_context, "original": story.get("raw")},
                )
                db.add(mention)
                saved += 1
            db.commit()
            logger.info(f"StoryProcessor: saved {saved} stories")
        except Exception as e:
            logger.error(f"StoryProcessor _save_stories: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def _download_media(url: str) -> Optional[bytes]:
        try:
            resp = requests.get(url, timeout=15, stream=True)
            resp.raise_for_status()
            content = resp.content
            if len(content) > 20 * 1024 * 1024:
                logger.warning(f"Media too large: {url}")
                return None
            return content
        except Exception as e:
            logger.error(f"Error downloading media {url}: {e}")
            return None