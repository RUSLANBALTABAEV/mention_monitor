"""
Historical search API endpoint.
Allows searching for mentions in a specified date range across all or specific sources.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()


class HistoricalSearchRequest(BaseModel):
    keywords: List[str]
    date_from: datetime
    date_to: datetime
    source_types: Optional[List[str]] = None  # ["vk", "telegram", "site", "all"]
    channels: Optional[List[str]] = None       # Telegram channels to search
    minus_words: Optional[List[str]] = None


class HistoricalSearchResponse(BaseModel):
    task_id: Optional[str]
    message: str
    keywords: List[str]
    date_from: datetime
    date_to: datetime


@router.post("/search", response_model=HistoricalSearchResponse)
def start_historical_search(
    request: HistoricalSearchRequest,
    background_tasks: BackgroundTasks,
):
    """
    Launch historical search in the background.
    Results will be stored in the mentions table and retrievable via /api/results.
    """
    if request.date_from >= request.date_to:
        raise HTTPException(status_code=400, detail="date_from must be before date_to")
    if not request.keywords:
        raise HTTPException(status_code=400, detail="At least one keyword is required")

    try:
        from workers.parse_tasks import run_historical_search
        task = run_historical_search.delay(
            keywords=request.keywords,
            date_from=request.date_from.isoformat(),
            date_to=request.date_to.isoformat(),
            source_types=request.source_types,
            channels=request.channels,
            minus_words=request.minus_words,
        )
        return HistoricalSearchResponse(
            task_id=str(task.id),
            message="Historical search started. Results will appear in /api/results as they are collected.",
            keywords=request.keywords,
            date_from=request.date_from,
            date_to=request.date_to,
        )
    except Exception as e:
        # Run synchronously if Celery is unavailable
        background_tasks.add_task(
            _run_historical_sync,
            request.keywords,
            request.date_from,
            request.date_to,
            request.source_types,
            request.channels,
            request.minus_words,
        )
        return HistoricalSearchResponse(
            task_id=None,
            message="Historical search started (sync mode). Results will appear shortly.",
            keywords=request.keywords,
            date_from=request.date_from,
            date_to=request.date_to,
        )


def _run_historical_sync(
    keywords, date_from, date_to, source_types, channels, minus_words
):
    from app.services.parser_manager import ParserManager
    ParserManager.run_historical_search(
        keywords=keywords,
        date_from=date_from,
        date_to=date_to,
        source_types=source_types,
        channels=channels,
        minus_words=minus_words,
    )
