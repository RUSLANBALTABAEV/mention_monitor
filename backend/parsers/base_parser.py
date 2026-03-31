from abc import ABC, abstractmethod
import logging

class BaseParser(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse(self, keywords, minus_words=None, whitelist=None, blacklist=None,
              blacklist_users=None, whitelist_users=None):
        pass

    def save_mention(self, mention_data):
        from app.database import SessionLocal
        from app.models import Mention
        db = SessionLocal()
        try:
            mention = Mention(**mention_data)
            db.add(mention)
            db.commit()
            self.logger.info(f"Saved mention: {mention_data.get('source_url')}")
        except Exception as e:
            self.logger.error(f"Error saving mention: {e}")
            db.rollback()
        finally:
            db.close()