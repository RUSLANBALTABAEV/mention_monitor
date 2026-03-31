import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_parser import BaseParser
from app.services.filter_engine import FilterEngine
from app.utils.geo import extract_geo_from_text

class WebParser(BaseParser):
    def parse(self, keywords, minus_words=None, whitelist=None, blacklist=None,
              blacklist_users=None, whitelist_users=None):
        self.logger.info(f"WebParser started with keywords: {keywords}")
        for url in whitelist:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                for kw in keywords:
                    if FilterEngine.filter_by_keywords(text, [kw], "OR", False):
                        if minus_words and not FilterEngine.filter_by_minus_words(text, minus_words):
                            continue
                        self.save_mention({
                            'text': text[:500],
                            'source_type': 'site',
                            'source_url': url,
                            'author': None,
                            'date': None,
                            'geo_country': None,
                            'geo_city': None,
                            'keyword': kw,
                            'content_type': 'text',
                        })
            except Exception as e:
                self.logger.error(f"Error parsing {url}: {e}")