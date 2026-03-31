from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Keyword
class KeywordCreate(BaseModel):
    text: str
    operator: str = "OR"
    exact_match: bool = False

class KeywordOut(BaseModel):
    id: int
    text: str
    operator: str
    exact_match: bool
    created_at: datetime
    class Config:
        from_attributes = True

# MinusWord
class MinusWordCreate(BaseModel):
    text: str

class MinusWordOut(BaseModel):
    id: int
    text: str
    class Config:
        from_attributes = True

# Source
class SourceCreate(BaseModel):
    url: str
    type: str
    is_whitelist: bool = True
    priority: int = 5

class SourceOut(BaseModel):
    id: int
    url: str
    type: str
    is_whitelist: bool
    priority: int
    class Config:
        from_attributes = True

# UserBlacklist
class UserBlacklistCreate(BaseModel):
    username: str
    source_type: str

class UserBlacklistOut(BaseModel):
    id: int
    username: str
    source_type: str
    class Config:
        from_attributes = True

# UserWhitelist
class UserWhitelistCreate(BaseModel):
    username: str
    source_type: str

class UserWhitelistOut(BaseModel):
    id: int
    username: str
    source_type: str
    class Config:
        from_attributes = True

# AppSettings
class AppSettingOut(BaseModel):
    id: int
    key: str
    value: str
    class Config:
        from_attributes = True

class AppSettingUpdate(BaseModel):
    value: str

# CRMIntegration
class CRMIntegrationCreate(BaseModel):
    name: str
    webhook_url: str
    is_active: bool = True
    send_on_types: List[str] = ['text', 'story', 'image']

class CRMIntegrationOut(BaseModel):
    id: int
    name: str
    webhook_url: str
    is_active: bool
    send_on_types: List[str]
    class Config:
        from_attributes = True

# Mention
class MentionOut(BaseModel):
    id: int
    text: Optional[str]
    source_type: str
    source_url: str
    author: Optional[str]
    date: datetime
    geo_country: Optional[str]
    geo_city: Optional[str]
    keyword: str
    content_type: str
    ocr_text: Optional[str]
    media_url: Optional[str]
    class Config:
        from_attributes = True

# Source priority update
class SourcePriorityUpdate(BaseModel):
    priority: int
