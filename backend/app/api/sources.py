"""
Sources API — whitelist/blacklist management with priority support.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter()


@router.get("/", response_model=List[schemas.SourceOut])
def list_sources(db: Session = Depends(database.get_db)):
    return db.query(models.Source).order_by(models.Source.priority.desc()).all()


@router.post("/", response_model=schemas.SourceOut)
def create_source(body: schemas.SourceCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.Source).filter(models.Source.url == body.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source URL already exists")
    source = models.Source(
        url=body.url,
        type=body.type,
        is_whitelist=body.is_whitelist,
        priority=body.priority,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/{source_id}", response_model=schemas.SourceOut)
def update_source(source_id: int, body: schemas.SourceCreate, db: Session = Depends(database.get_db)):
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.url = body.url
    source.type = body.type
    source.is_whitelist = body.is_whitelist
    source.priority = body.priority
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}/priority", response_model=schemas.SourceOut)
def update_priority(source_id: int, body: schemas.SourcePriorityUpdate, db: Session = Depends(database.get_db)):
    """Update only the priority of a source (1=low … 10=high)."""
    if not (1 <= body.priority <= 10):
        raise HTTPException(status_code=400, detail="priority must be between 1 and 10")
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.priority = body.priority
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(database.get_db)):
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()
    return {"ok": True}
