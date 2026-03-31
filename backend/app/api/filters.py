from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()

# ─── Минус-слова ─────────────────────────────────────────────────────────────
@router.post("/minus-words", response_model=schemas.MinusWordOut)
def create_minus_word(word: schemas.MinusWordCreate, db: Session = Depends(database.get_db)):
    db_word = models.MinusWord(text=word.text)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

@router.get("/minus-words", response_model=list[schemas.MinusWordOut])
def list_minus_words(db: Session = Depends(database.get_db)):
    return db.query(models.MinusWord).all()

@router.delete("/minus-words/{word_id}")
def delete_minus_word(word_id: int, db: Session = Depends(database.get_db)):
    word = db.query(models.MinusWord).filter(models.MinusWord.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    db.delete(word)
    db.commit()
    return {"ok": True}

# ─── Чёрный список пользователей ─────────────────────────────────────────────
@router.post("/user-blacklist", response_model=schemas.UserBlacklistOut)
def add_blacklist_user(user: schemas.UserBlacklistCreate, db: Session = Depends(database.get_db)):
    db_user = models.UserBlacklist(username=user.username, source_type=user.source_type)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/user-blacklist", response_model=list[schemas.UserBlacklistOut])
def list_blacklist_users(db: Session = Depends(database.get_db)):
    return db.query(models.UserBlacklist).all()

@router.delete("/user-blacklist/{user_id}")
def delete_blacklist_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.UserBlacklist).filter(models.UserBlacklist.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}

# ─── Белый список пользователей ─────────────────────────────────────────────
@router.post("/user-whitelist", response_model=schemas.UserWhitelistOut)
def add_whitelist_user(user: schemas.UserWhitelistCreate, db: Session = Depends(database.get_db)):
    db_user = models.UserWhitelist(username=user.username, source_type=user.source_type)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/user-whitelist", response_model=list[schemas.UserWhitelistOut])
def list_whitelist_users(db: Session = Depends(database.get_db)):
    return db.query(models.UserWhitelist).all()

@router.delete("/user-whitelist/{user_id}")
def delete_whitelist_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.UserWhitelist).filter(models.UserWhitelist.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}