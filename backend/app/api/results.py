from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List
from .. import models, schemas, database
from ..services.export_service import ExportService

router = APIRouter()

def _build_query(db: Session, source_type: Optional[str] = None, content_type: Optional[str] = None,
                 keyword: Optional[str] = None, country: Optional[str] = None, city: Optional[str] = None,
                 date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    query = db.query(models.Mention)
    if source_type:
        query = query.filter(models.Mention.source_type == source_type)
    if content_type:
        query = query.filter(models.Mention.content_type == content_type)
    if keyword:
        query = query.filter(models.Mention.keyword.ilike(f"%{keyword}%"))
    if country:
        query = query.filter(models.Mention.geo_country == country)
    if city:
        query = query.filter(models.Mention.geo_city == city)
    if date_from:
        query = query.filter(models.Mention.date >= date_from)
    if date_to:
        query = query.filter(models.Mention.date <= date_to)
    return query

@router.get("/", response_model=List[schemas.MentionOut])
def list_mentions(
    db: Session = Depends(database.get_db),
    source_type: Optional[str] = None,
    content_type: Optional[str] = None,
    keyword: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
):
    query = _build_query(db, source_type, content_type, keyword, country, city, date_from, date_to)
    return query.order_by(desc(models.Mention.date)).offset(offset).limit(limit).all()

@router.get("/export")
def export_mentions(
    db: Session = Depends(database.get_db),
    format: str = Query("csv", pattern="^(csv|excel|json)$"),
    source_type: Optional[str] = None,
    content_type: Optional[str] = None,
    keyword: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    query = _build_query(db, source_type, content_type, keyword, country, city, date_from, date_to)
    mentions_orm = query.order_by(desc(models.Mention.date)).limit(10000).all()
    mentions = [
        {
            "id": m.id,
            "text": m.text,
            "source_type": m.source_type,
            "source_url": m.source_url,
            "author": m.author,
            "date": m.date.isoformat() if m.date else None,
            "geo_country": m.geo_country,
            "geo_city": m.geo_city,
            "keyword": m.keyword,
            "content_type": m.content_type,
            "ocr_text": m.ocr_text,
            "media_url": m.media_url,
        }
        for m in mentions_orm
    ]
    if format == "csv":
        return ExportService.export_to_csv(mentions)
    elif format == "excel":
        return ExportService.export_to_excel(mentions)
    elif format == "json":
        return ExportService.export_to_json(mentions)

@router.delete("/{mention_id}")
def delete_mention(mention_id: int, db: Session = Depends(database.get_db)):
    mention = db.query(models.Mention).filter(models.Mention.id == mention_id).first()
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    db.delete(mention)
    db.commit()
    return {"ok": True}