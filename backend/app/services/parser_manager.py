"""
ParserManager orchestrates all parsers, respects source priorities,
and supports historical search.
"""
import logging
from datetime import datetime
from typing import List, Optional

from app.database import SessionLocal
from app.models import Keyword, MinusWord, Source, UserBlacklist, UserWhitelist

logger = logging.getLogger(__name__)


class ParserManager:

    # ─── Data helpers ────────────────────────────────────────────────────────

    @staticmethod
    def get_active_keywords() -> List[str]:
        db = SessionLocal()
        try:
            return [kw.text for kw in db.query(Keyword).all()]
        finally:
            db.close()

    @staticmethod
    def get_minus_words() -> List[str]:
        db = SessionLocal()
        try:
            return [mw.text for mw in db.query(MinusWord).all()]
        finally:
            db.close()

    @staticmethod
    def get_whitelist() -> List[str]:
        """Return whitelist URLs ordered by priority descending."""
        db = SessionLocal()
        try:
            sources = (
                db.query(Source)
                .filter(Source.is_whitelist == True)
                .order_by(Source.priority.desc())
                .all()
            )
            return [s.url for s in sources]
        finally:
            db.close()

    @staticmethod
    def get_blacklist() -> List[str]:
        db = SessionLocal()
        try:
            return [s.url for s in db.query(Source).filter(Source.is_whitelist == False).all()]
        finally:
            db.close()

    @staticmethod
    def get_blacklist_users() -> List[str]:
        db = SessionLocal()
        try:
            return [u.username for u in db.query(UserBlacklist).all()]
        finally:
            db.close()

    @staticmethod
    def get_whitelist_users() -> List[str]:
        db = SessionLocal()
        try:
            return [u.username for u in db.query(UserWhitelist).all()]
        finally:
            db.close()

    @staticmethod
    def get_sources_by_priority() -> List[dict]:
        """Return all sources with their priority metadata."""
        db = SessionLocal()
        try:
            sources = (
                db.query(Source)
                .order_by(Source.priority.desc())
                .all()
            )
            return [
                {
                    "url": s.url,
                    "type": s.type,
                    "is_whitelist": s.is_whitelist,
                    "priority": s.priority,
                }
                for s in sources
            ]
        finally:
            db.close()

    # ─── Main parse run ──────────────────────────────────────────────────────

    @staticmethod
    def run_all_parsers():
        keywords = ParserManager.get_active_keywords()
        minus_words = ParserManager.get_minus_words()
        whitelist = ParserManager.get_whitelist()
        blacklist = ParserManager.get_blacklist()
        blacklist_users = ParserManager.get_blacklist_users()
        whitelist_users = ParserManager.get_whitelist_users()

        if not keywords:
            logger.warning("No keywords found, skipping parsing.")
            return

        logger.info(f"Starting parsers with {len(keywords)} keyword(s), "
                    f"{len(whitelist)} whitelist URL(s), priority-ordered.")

        # ── 1. Static web parser (BeautifulSoup) ────────────────────────────
        try:
            from parsers.web_parser import WebParser
            web = WebParser()
            web.parse(keywords, minus_words, whitelist, blacklist, blacklist_users, whitelist_users)
            logger.info("WebParser finished.")
        except Exception as e:
            logger.error(f"WebParser: {e}")

        # ── 2. Dynamic web parser (Selenium) — for JS-heavy sites ────────────
        try:
            from parsers.selenium_web_parser import SeleniumWebParser
            # Only parse sites flagged as 'dynamic' (type == 'dynamic') from whitelist
            db = SessionLocal()
            dynamic_urls = [
                s.url for s in db.query(Source)
                .filter(Source.is_whitelist == True, Source.type == "dynamic")
                .order_by(Source.priority.desc())
                .all()
            ]
            db.close()

            if dynamic_urls:
                sel_parser = SeleniumWebParser()
                sel_parser.parse(
                    keywords, minus_words, dynamic_urls, blacklist,
                    blacklist_users, whitelist_users
                )
                logger.info(f"SeleniumWebParser finished ({len(dynamic_urls)} dynamic URLs).")
        except Exception as e:
            logger.error(f"SeleniumWebParser: {e}")

        # ── 3. Scrapy crawler ────────────────────────────────────────────────
        try:
            from parsers.scrapy_spider import MentionSpider
            from app.database import SessionLocal as SL
            from app.models import Mention
            from app.utils.geo import extract_geo_from_text

            spider = MentionSpider()
            items = spider.run(keywords, whitelist, minus_words)
            db = SL()
            try:
                saved = 0
                for item in items:
                    exists = db.query(Mention).filter(Mention.source_url == item["url"]).first()
                    if exists:
                        continue
                    geo = extract_geo_from_text(item.get("text", ""))
                    mention = Mention(
                        text=item.get("text", "")[:1000],
                        source_type="site",
                        source_url=item["url"],
                        author=None,
                        date=item.get("date", datetime.utcnow()),
                        geo_country=geo.get("country"),
                        geo_city=geo.get("city"),
                        keyword=item.get("keyword", ""),
                        content_type="text",
                        raw_data={"parser": "scrapy"},
                    )
                    db.add(mention)
                    saved += 1
                db.commit()
                logger.info(f"Scrapy spider saved {saved} new mentions.")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"ScrapySpider: {e}")

        # ── 4. VK ────────────────────────────────────────────────────────────
        try:
            from parsers.vk_parser import VkParser
            vk = VkParser()
            vk.parse(keywords, minus_words, blacklist_users, whitelist_users)
            logger.info("VkParser finished.")
        except Exception as e:
            logger.error(f"VkParser: {e}")

        # ── 5. TenChat ───────────────────────────────────────────────────────
        try:
            from parsers.tenchat_parser import TenChatParser
            tenchat = TenChatParser()
            tenchat.parse(keywords, minus_words, blacklist_users, whitelist_users)
            logger.info("TenChatParser finished.")
        except Exception as e:
            logger.error(f"TenChatParser: {e}")

        # ── 6. Max ───────────────────────────────────────────────────────────
        try:
            from parsers.max_parser import MaxParser
            max_parser = MaxParser()
            max_parser.parse(keywords, minus_words, blacklist_users, whitelist_users)
            logger.info("MaxParser finished.")
        except Exception as e:
            logger.error(f"MaxParser: {e}")

        # ── 7. Telegram (Telethon) ───────────────────────────────────────────
        try:
            from parsers.telegram_parser import TelegramParser
            tg = TelegramParser()
            tg.parse(keywords, minus_words, blacklist_users, whitelist_users)
            logger.info("TelegramParser finished.")
        except Exception as e:
            logger.error(f"TelegramParser: {e}")

        # ── 8. Stories ───────────────────────────────────────────────────────
        try:
            from parsers.story_processor import StoryProcessor
            story = StoryProcessor()
            story.process(keywords, minus_words, blacklist_users, whitelist_users)
            logger.info("StoryProcessor finished.")
        except Exception as e:
            logger.error(f"StoryProcessor: {e}")

        logger.info("All parsers finished.")

    # ─── Historical search ───────────────────────────────────────────────────

    @staticmethod
    def run_historical_search(
        keywords: List[str],
        date_from: datetime,
        date_to: datetime,
        source_types: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        minus_words: Optional[List[str]] = None,
    ):
        """
        Search historical data across available sources.
        Currently supports: database (already stored), Telegram.
        Web/VK historical search uses existing stored data filtered by date.
        """
        source_types = source_types or ["all"]
        minus_words = minus_words or ParserManager.get_minus_words()

        logger.info(
            f"Historical search: keywords={keywords}, "
            f"from={date_from}, to={date_to}, sources={source_types}"
        )

        results = []

        # ── Telegram historical ──────────────────────────────────────────────
        if "all" in source_types or "telegram" in source_types:
            try:
                from parsers.telegram_parser import TelegramParser
                tg = TelegramParser()
                tg.search_historical(
                    keywords=keywords,
                    date_from=date_from,
                    date_to=date_to,
                    channels=channels,
                    minus_words=minus_words,
                )
                logger.info("Telegram historical search completed.")
            except Exception as e:
                logger.error(f"Telegram historical: {e}")

        # ── VK historical via API ────────────────────────────────────────────
        if "all" in source_types or "vk" in source_types:
            try:
                from parsers.vk_parser import VkParser
                vk = VkParser()
                # VK newsfeed.search supports date range via start_time/end_time
                vk.parse_historical(
                    keywords=keywords,
                    date_from=date_from,
                    date_to=date_to,
                    minus_words=minus_words,
                )
                logger.info("VK historical search completed.")
            except Exception as e:
                logger.error(f"VK historical: {e}")

        return results
