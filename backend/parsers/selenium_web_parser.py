"""
Selenium-based web parser for dynamic JavaScript-rendered websites.
Used when a site requires browser emulation (React, Vue, Angular SPAs).
"""
import logging
import os
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from .base_parser import BaseParser
from app.database import SessionLocal
from app.models import Mention
from app.utils.geo import extract_geo_from_text
from app.services.filter_engine import FilterEngine

logger = logging.getLogger(__name__)

SELENIUM_URL = os.getenv("SELENIUM_URL", "http://localhost:4444/wd/hub")


def _get_driver():
    """Create a remote Selenium WebDriver instance."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    # Try remote Selenium grid first; fall back to local ChromeDriver
    try:
        driver = webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=options,
        )
        return driver
    except Exception:
        # Local fallback
        from selenium.webdriver.chrome.service import Service
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Could not create WebDriver: {e}")
            return None


class SeleniumWebParser(BaseParser):
    """
    Parser for dynamic websites that require JavaScript rendering.
    Complements the static BeautifulSoup-based WebParser.
    """

    def parse(
        self,
        keywords: List[str],
        minus_words: Optional[List[str]] = None,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
        blacklist_users: Optional[List[str]] = None,
        whitelist_users: Optional[List[str]] = None,
    ):
        if not whitelist:
            logger.info("SeleniumWebParser: no whitelist URLs, skipping")
            return

        driver = _get_driver()
        if not driver:
            logger.warning("SeleniumWebParser: WebDriver unavailable, skipping")
            return

        db = SessionLocal()
        try:
            for url in whitelist:
                try:
                    self._parse_url(driver, db, url, keywords, minus_words or [], blacklist or [])
                except Exception as e:
                    logger.error(f"SeleniumWebParser error on {url}: {e}")
        finally:
            db.close()
            try:
                driver.quit()
            except Exception:
                pass

    def _parse_url(self, driver, db, url: str, keywords: List[str], minus_words: List[str], blacklist: List[str]):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        from bs4 import BeautifulSoup

        if blacklist and any(url.startswith(b) for b in blacklist):
            return

        logger.info(f"SeleniumWebParser: loading {url}")
        driver.get(url)

        # Wait for page to load (body present and no spinner)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Extra wait for JS frameworks to render
            import time
            time.sleep(2)
        except Exception:
            pass

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Remove script/style noise
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        full_text = soup.get_text(separator=" ", strip=True)

        for kw in keywords:
            if FilterEngine.filter_by_keywords(full_text, [kw], "OR", False):
                if minus_words and not FilterEngine.filter_by_minus_words(full_text, minus_words):
                    continue

                exists = db.query(Mention).filter(Mention.source_url == url).first()
                if exists:
                    continue

                geo = extract_geo_from_text(full_text)
                mention = Mention(
                    text=full_text[:1000],
                    source_type="site",
                    source_url=url,
                    author=None,
                    date=datetime.utcnow(),
                    geo_country=geo.get("country"),
                    geo_city=geo.get("city"),
                    keyword=kw,
                    content_type="text",
                    raw_data={"parser": "selenium", "url": url},
                )
                db.add(mention)

        db.commit()

    def scroll_and_parse(self, url: str, keywords: List[str], max_scrolls: int = 5) -> List[dict]:
        """
        Scroll through an infinite-scroll page and collect all posts matching keywords.
        Returns a list of raw result dicts.
        """
        driver = _get_driver()
        if not driver:
            return []

        results = []
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from bs4 import BeautifulSoup
            import time

            driver.get(url)
            time.sleep(3)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(max_scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()

            articles = soup.find_all(["article", "div"], class_=lambda c: c and "post" in c.lower() if c else False)
            for article in articles:
                text = article.get_text(strip=True)
                for kw in keywords:
                    if kw.lower() in text.lower():
                        link = article.find("a", href=True)
                        href = link["href"] if link else url
                        full_url = href if href.startswith("http") else urljoin(url, href)
                        results.append({"text": text[:500], "url": full_url, "keyword": kw})
                        break

        except Exception as e:
            logger.error(f"scroll_and_parse error: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        return results
