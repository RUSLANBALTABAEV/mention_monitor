"""
Scrapy-based spider for crawling static websites at scale.
Complements the requests+BeautifulSoup WebParser with proper crawling,
robots.txt respect, rate limiting and link following.
"""
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MentionSpider:
    """
    Scrapy spider runner that crawls whitelisted sites for keyword mentions.
    Integrates with the existing parser pipeline.
    """

    name = "mention_spider"

    def run(
        self,
        keywords: List[str],
        start_urls: List[str],
        minus_words: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        db=None,
    ) -> List[dict]:
        """
        Run a Scrapy crawl in-process and return collected items.
        Falls back to requests+BS4 if Scrapy is not available.
        """
        minus_words = minus_words or []

        try:
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            import scrapy

            collected = []

            class KeywordSpider(scrapy.Spider):
                name = "keyword_spider"
                custom_settings = {
                    "ROBOTSTXT_OBEY": True,
                    "DOWNLOAD_DELAY": 1,
                    "CONCURRENT_REQUESTS": 8,
                    "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
                    "USER_AGENT": (
                        "Mozilla/5.0 (compatible; MentionMonitorBot/1.0; "
                        "+https://github.com/mention-monitor)"
                    ),
                    "LOG_LEVEL": "WARNING",
                    "CLOSESPIDER_ITEMCOUNT": 500,
                    "DEPTH_LIMIT": 3,
                }

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.start_urls = start_urls
                    self.allowed_domains = allowed_domains or [
                        urlparse(u).netloc for u in start_urls
                    ]
                    self._keywords = keywords
                    self._minus_words = minus_words

                def parse(self, response):
                    from scrapy import Selector

                    text = " ".join(response.css("body *::text").getall())
                    text = " ".join(text.split())  # normalize whitespace

                    for kw in self._keywords:
                        if kw.lower() in text.lower():
                            if self._minus_words and any(
                                mw.lower() in text.lower() for mw in self._minus_words
                            ):
                                break

                            collected.append(
                                {
                                    "text": text[:1000],
                                    "url": response.url,
                                    "keyword": kw,
                                    "date": datetime.utcnow(),
                                    "source_type": "site",
                                }
                            )
                            break  # one match per page per run

                    # Follow links within allowed domains
                    for href in response.css("a::attr(href)").getall():
                        yield response.follow(href, self.parse)

            process = CrawlerProcess(get_project_settings())
            process.crawl(KeywordSpider)
            process.start()

            logger.info(f"Scrapy crawl completed: {len(collected)} items")
            return collected

        except ImportError:
            logger.warning("Scrapy not available, falling back to requests")
            return self._fallback_parse(keywords, start_urls, minus_words)
        except Exception as e:
            logger.error(f"Scrapy error: {e}")
            return self._fallback_parse(keywords, start_urls, minus_words)

    @staticmethod
    def _fallback_parse(
        keywords: List[str], start_urls: List[str], minus_words: List[str]
    ) -> List[dict]:
        """Simple requests+BS4 fallback when Scrapy is unavailable."""
        import requests
        from bs4 import BeautifulSoup

        results = []
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }

        for url in start_urls:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                text = soup.get_text(separator=" ", strip=True)

                for kw in keywords:
                    if kw.lower() in text.lower():
                        if minus_words and any(
                            mw.lower() in text.lower() for mw in minus_words
                        ):
                            break
                        results.append(
                            {
                                "text": text[:1000],
                                "url": url,
                                "keyword": kw,
                                "date": datetime.utcnow(),
                                "source_type": "site",
                            }
                        )
                        break
            except Exception as e:
                logger.warning(f"Fallback parse error for {url}: {e}")

        return results
