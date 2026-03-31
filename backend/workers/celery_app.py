from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "mention_monitor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.parse_tasks", "workers.ocr_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,       # 30 min hard limit
    task_soft_time_limit=25 * 60,  # 25 min soft limit
    worker_max_tasks_per_child=50, # restart worker after 50 tasks to avoid memory leaks
)


def _get_parser_interval_seconds() -> int:
    """
    Read parser_interval from DB settings.
    Falls back to env variable if DB is unavailable.
    """
    try:
        from app.database import SessionLocal
        from app.models import AppSettings
        db = SessionLocal()
        try:
            setting = db.query(AppSettings).filter(AppSettings.key == "parser_interval").first()
            if setting:
                return int(setting.value) * 60
        finally:
            db.close()
    except Exception:
        pass
    return settings.PARSER_INTERVAL * 60


celery_app.conf.beat_schedule = {
    "run-all-parsers": {
        "task": "workers.parse_tasks.run_all_parsers",
        "schedule": _get_parser_interval_seconds(),
    },
}
