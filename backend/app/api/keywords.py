from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.KeywordOut)
def create_keyword(keyword: schemas.KeywordCreate, db: Session = Depends(database.get_db)):
    db_keyword = models.Keyword(
        text=keyword.text,
        operator=keyword.operator,
        exact_match=keyword.exact_match
    )
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

@router.get("/", response_model=list[schemas.KeywordOut])
def list_keywords(db: Session = Depends(database.get_db)):
    return db.query(models.Keyword).all()

@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(database.get_db)):
    keyword = db.query(models.Keyword).filter(models.Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(keyword)
    db.commit()
    return {"ok": True}