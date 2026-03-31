import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ── Database & Queue ─────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost/mention_monitor")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")

    # ── VK ───────────────────────────────────────────────────────────────────
    VK_ACCESS_TOKEN: str = os.getenv("VK_ACCESS_TOKEN", "")
    VK_GROUP_ID: str = os.getenv("VK_GROUP_ID", "")

    # ── TenChat ──────────────────────────────────────────────────────────────
    TENCHAT_TOKEN: str = os.getenv("TENCHAT_TOKEN", "")

    # ── Max ──────────────────────────────────────────────────────────────────
    MAX_API_KEY: str = os.getenv("MAX_API_KEY", "")

    # ── Telegram (Telethon) ──────────────────────────────────────────────────
    TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_PHONE: str = os.getenv("TELEGRAM_PHONE", "")

    # ── AI / Vision ──────────────────────────────────────────────────────────
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    ENABLE_AI_VISION: bool = os.getenv("ENABLE_AI_VISION", "False").lower() in ("true", "1", "yes")

    # ── Selenium ─────────────────────────────────────────────────────────────
    SELENIUM_URL: str = os.getenv("SELENIUM_URL", "http://localhost:4444/wd/hub")

    # ── Parser ───────────────────────────────────────────────────────────────
    PARSER_INTERVAL: int = int(os.getenv("PARSER_INTERVAL", "15"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
