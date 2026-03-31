from celery import shared_task
from app.services.parser_manager import ParserManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@shared_task
def run_all_parsers():
    logger.info("Running all parsers...")
    ParserManager.run_all_parsers()
    logger.info("All parsers finished.")


@shared_task
def run_historical_search(
    keywords,
    date_from,
    date_to,
    source_types=None,
    channels=None,
    minus_words=None,
):
    """Celery task for historical search across sources."""
    logger.info(f"Historical search task started: keywords={keywords}")
    try:
        df = datetime.fromisoformat(date_from) if isinstance(date_from, str) else date_from
        dt = datetime.fromisoformat(date_to) if isinstance(date_to, str) else date_to
        ParserManager.run_historical_search(
            keywords=keywords,
            date_from=df,
            date_to=dt,
            source_types=source_types,
            channels=channels,
            minus_words=minus_words,
        )
    except Exception as e:
        logger.error(f"Historical search task error: {e}")
    logger.info("Historical search task finished.")
