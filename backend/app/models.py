from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from .database import Base

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True, nullable=False)
    operator = Column(String, default="OR")
    exact_match = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MinusWord(Base):
    __tablename__ = "minus_words"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    type = Column(String)
    is_whitelist = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserBlacklist(Base):
    __tablename__ = "user_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    source_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserWhitelist(Base):
    __tablename__ = "user_whitelist"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    source_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CRMIntegration(Base):
    __tablename__ = "crm_integrations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    webhook_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    send_on_types = Column(JSON, default=['text', 'story', 'image'])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Mention(Base):
    __tablename__ = "mentions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=True)
    source_type = Column(String, index=True)
    source_url = Column(String)
    author = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), index=True)
    geo_country = Column(String, nullable=True)
    geo_city = Column(String, nullable=True)
    keyword = Column(String, index=True)
    content_type = Column(String)
    ocr_text = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())