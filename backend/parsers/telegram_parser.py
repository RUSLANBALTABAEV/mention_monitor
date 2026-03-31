"""
Telegram parser using Telethon.
Monitors Telegram channels and groups for keyword mentions.
"""
import asyncio
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


class TelegramParser(BaseParser):
    """
    Parser for Telegram channels and groups using Telethon API.
    Requires TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_PHONE in settings.
    """

    def parse(
        self,
        keywords: List[str],
        minus_words: Optional[List[str]] = None,
        blacklist_users: Optional[List[str]] = None,
        whitelist_users: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
    ):
        """Synchronous wrapper around the async parse logic."""
        if not self._check_credentials():
            logger.warning("Telegram parser skipped: credentials not configured")
            return

        try:
            asyncio.run(
                self._async_parse(
                    keywords,
                    minus_words or [],
                    blacklist_users or [],
                    whitelist_users or [],
                    channels or [],
                )
            )
        except Exception as e:
            logger.error(f"TelegramParser: {e}")

    def _check_credentials(self) -> bool:
        return bool(
            getattr(settings, "TELEGRAM_API_ID", None)
            and getattr(settings, "TELEGRAM_API_HASH", None)
            and getattr(settings, "TELEGRAM_PHONE", None)
        )

    async def _async_parse(
        self,
        keywords: List[str],
        minus_words: List[str],
        blacklist_users: List[str],
        whitelist_users: List[str],
        channels: List[str],
    ):
        from telethon import TelegramClient
        from telethon.tl.functions.messages import SearchRequest
        from telethon.tl.types import InputMessagesFilterEmpty

        session_name = "mention_monitor_session"
        api_id = int(settings.TELEGRAM_API_ID)
        api_hash = settings.TELEGRAM_API_HASH
        phone = settings.TELEGRAM_PHONE

        client = TelegramClient(session_name, api_id, api_hash)
        await client.start(phone=phone)

        db = SessionLocal()
        try:
            # Search across all dialogs if no specific channels provided
            if not channels:
                dialogs = await client.get_dialogs()
                channels = [
                    d.entity.username
                    for d in dialogs
                    if hasattr(d.entity, "username") and d.entity.username
                ]

            for keyword in keywords:
                logger.info(f"Telegram: searching for '{keyword}'")
                saved = 0

                for channel in channels[:50]:  # limit to 50 channels per run
                    try:
                        entity = await client.get_entity(channel)
                        result = await client(
                            SearchRequest(
                                peer=entity,
                                q=keyword,
                                filter=InputMessagesFilterEmpty(),
                                min_date=None,
                                max_date=None,
                                offset_id=0,
                                add_offset=0,
                                limit=100,
                                max_id=0,
                                min_id=0,
                                hash=0,
                            )
                        )

                        for msg in result.messages:
                            if not msg.message:
                                continue

                            text = msg.message
                            if minus_words and not FilterEngine.filter_by_minus_words(
                                text, minus_words
                            ):
                                continue

                            sender_id = msg.sender_id or 0
                            author = str(sender_id)
                            try:
                                sender = await client.get_entity(sender_id)
                                author = getattr(sender, "username", None) or getattr(
                                    sender, "first_name", str(sender_id)
                                )
                            except Exception:
                                pass

                            if blacklist_users and not FilterEngine.filter_by_user(
                                author, blacklist_users
                            ):
                                continue

                            source_url = (
                                f"https://t.me/{channel}/{msg.id}"
                                if channel
                                else f"tg://msg/{sender_id}/{msg.id}"
                            )

                            exists = (
                                db.query(Mention)
                                .filter(Mention.source_url == source_url)
                                .first()
                            )
                            if exists:
                                continue

                            geo = extract_geo_from_text(text)
                            mention = Mention(
                                text=text,
                                source_type="telegram",
                                source_url=source_url,
                                author=author,
                                date=msg.date.replace(tzinfo=None)
                                if msg.date
                                else datetime.utcnow(),
                                geo_country=geo.get("country"),
                                geo_city=geo.get("city"),
                                keyword=keyword,
                                content_type="text",
                                raw_data={
                                    "message_id": msg.id,
                                    "channel": channel,
                                    "views": getattr(msg, "views", None),
                                },
                            )
                            db.add(mention)
                            saved += 1

                    except Exception as e:
                        logger.warning(f"Telegram channel '{channel}' error: {e}")
                        continue

                db.commit()
                logger.info(f"Telegram: saved {saved} results for '{keyword}'")

        except Exception as e:
            logger.error(f"TelegramParser async: {e}")
            db.rollback()
        finally:
            db.close()
            await client.disconnect()

    def search_historical(
        self,
        keywords: List[str],
        date_from: datetime,
        date_to: datetime,
        channels: Optional[List[str]] = None,
        minus_words: Optional[List[str]] = None,
    ):
        """Search historical messages within a date range."""
        if not self._check_credentials():
            logger.warning("Telegram parser skipped: credentials not configured")
            return

        try:
            asyncio.run(
                self._async_historical_search(
                    keywords,
                    date_from,
                    date_to,
                    channels or [],
                    minus_words or [],
                )
            )
        except Exception as e:
            logger.error(f"TelegramParser historical: {e}")

    async def _async_historical_search(
        self,
        keywords: List[str],
        date_from: datetime,
        date_to: datetime,
        channels: List[str],
        minus_words: List[str],
    ):
        from telethon import TelegramClient
        from telethon.tl.types import InputMessagesFilterEmpty

        session_name = "mention_monitor_session"
        api_id = int(settings.TELEGRAM_API_ID)
        api_hash = settings.TELEGRAM_API_HASH
        phone = settings.TELEGRAM_PHONE

        client = TelegramClient(session_name, api_id, api_hash)
        await client.start(phone=phone)

        db = SessionLocal()
        try:
            for channel in channels:
                try:
                    entity = await client.get_entity(channel)
                    for keyword in keywords:
                        async for msg in client.iter_messages(
                            entity,
                            search=keyword,
                            offset_date=date_to,
                            reverse=False,
                            limit=500,
                        ):
                            if msg.date.replace(tzinfo=None) < date_from:
                                break
                            if not msg.message:
                                continue

                            text = msg.message
                            if minus_words and not FilterEngine.filter_by_minus_words(
                                text, minus_words
                            ):
                                continue

                            source_url = f"https://t.me/{channel}/{msg.id}"
                            exists = (
                                db.query(Mention)
                                .filter(Mention.source_url == source_url)
                                .first()
                            )
                            if exists:
                                continue

                            geo = extract_geo_from_text(text)
                            mention = Mention(
                                text=text,
                                source_type="telegram",
                                source_url=source_url,
                                author=str(msg.sender_id),
                                date=msg.date.replace(tzinfo=None),
                                geo_country=geo.get("country"),
                                geo_city=geo.get("city"),
                                keyword=keyword,
                                content_type="text",
                                raw_data={"message_id": msg.id, "channel": channel},
                            )
                            db.add(mention)

                    db.commit()
                except Exception as e:
                    logger.warning(f"Historical search error for '{channel}': {e}")
                    continue
        finally:
            db.close()
            await client.disconnect()
