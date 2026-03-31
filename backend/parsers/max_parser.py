import requests
import logging
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from app.database import SessionLocal
from app.models import Mention
from app.utils.geo import extract_geo_from_text
from app.services.filter_engine import FilterEngine

logger = logging.getLogger(__name__)

MAX_SEARCH_URL = "https://max.ru/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

class MaxParser(BaseParser):
    def parse(self, keywords: List[str], minus_words: Optional[List[str]] = None,
              blacklist_users: Optional[List[str]] = None, whitelist_users: Optional[List[str]] = None):
        db = SessionLocal()
        try:
            for keyword in keywords:
                logger.info(f"Max: searching for '{keyword}'")
                results = self._search(keyword)
                saved = 0
                for item in results:
                    text = item.get("text", "")
                    if not text:
                        continue
                    if minus_words and not FilterEngine.filter_by_minus_words(text, minus_words):
                        continue
                    source_url = item.get("url", "")
                    exists = db.query(Mention).filter(Mention.source_url == source_url).first()
                    if exists:
                        continue
                    geo = extract_geo_from_text(text)
                    mention = Mention(
                        text=text,
                        source_type="max",
                        source_url=source_url,
                        author=item.get("author"),
                        date=item.get("date", datetime.utcnow()),
                        geo_country=geo.get("country"),
                        geo_city=geo.get("city"),
                        keyword=keyword,
                        content_type="text",
                    )
                    db.add(mention)
                    saved += 1
                db.commit()
                logger.info(f"Max: saved {saved} results for '{keyword}'")
        except Exception as e:
            logger.error(f"Max parser: {e}")
            db.rollback()
        finally:
            db.close()

    def _search(self, keyword: str) -> List[dict]:
        results = []
        try:
            resp = requests.get(MAX_SEARCH_URL, params={"q": keyword, "type": "posts"}, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                return results
            soup = BeautifulSoup(resp.text, "html.parser")
            post_blocks = soup.find_all(attrs={"data-testid": True}) or soup.find_all("article") or soup.find_all(class_=lambda c: c and "post" in c.lower())
            for block in post_blocks[:50]:
                text_el = block.find("p") or block.find(class_=lambda c: c and "text" in c.lower())
                text = text_el.get_text(strip=True) if text_el else ""
                if not text:
                    continue
                link_el = block.find("a", href=True)
                url = ""
                if link_el:
                    href = link_el["href"]
                    url = href if href.startswith("http") else f"https://max.ru{href}"
                author_el = block.find(class_=lambda c: c and "author" in c.lower() if c else False)
                author = author_el.get_text(strip=True) if author_el else None
                date_el = block.find("time")
                date = datetime.utcnow()
                if date_el and date_el.get("datetime"):
                    try:
                        date = datetime.fromisoformat(date_el["datetime"].replace("Z", "+00:00"))
                    except Exception:
                        pass
                results.append({"text": text, "url": url, "author": author, "date": date})
        except Exception as e:
            logger.error(f"Max _search: {e}")
        return results