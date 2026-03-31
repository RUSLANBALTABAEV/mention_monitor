from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter()

DEFAULT_SETTINGS = {
    "parser_interval": "15",
    "parser_enabled": "true",
}

def _get_or_create(db, key):
    setting = db.query(models.AppSettings).filter(models.AppSettings.key == key).first()
    if not setting:
        setting = models.AppSettings(key=key, value=DEFAULT_SETTINGS.get(key, ""))
        db.add(setting)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            setting = db.query(models.AppSettings).filter(models.AppSettings.key == key).first()
    return setting

@router.get("/", response_model=List[schemas.AppSettingOut])
def get_all_settings(db: Session = Depends(database.get_db)):
    for key in DEFAULT_SETTINGS:
        _get_or_create(db, key)
    return db.query(models.AppSettings).all()

@router.get("/{key}", response_model=schemas.AppSettingOut)
def get_setting(key: str, db: Session = Depends(database.get_db)):
    return _get_or_create(db, key)

@router.put("/{key}", response_model=schemas.AppSettingOut)
def update_setting(key: str, body: schemas.AppSettingUpdate, db: Session = Depends(database.get_db)):
    if key == "parser_interval":
        try:
            val = int(body.value)
            if not (5 <= val <= 60):
                raise HTTPException(status_code=400, detail="parser_interval must be between 5 and 60 minutes")
        except ValueError:
            raise HTTPException(status_code=400, detail="parser_interval must be an integer")
    setting = _get_or_create(db, key)
    setting.value = body.value
    db.commit()
    db.refresh(setting)
    if key == "parser_interval":
        # обновить интервал в Celery Beat (опционально)
        pass
    return setting

@router.post("/run_now")
def run_parsers_now():
    try:
        from workers.parse_tasks import run_all_parsers
        task = run_all_parsers.delay()
        return {"ok": True, "task_id": str(task.id)}
    except Exception as e:
        return {"ok": False, "error": str(e)}