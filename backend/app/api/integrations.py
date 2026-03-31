import requests
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import models, schemas, database

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.CRMIntegrationOut)
def create_integration(body: schemas.CRMIntegrationCreate, db: Session = Depends(database.get_db)):
    crm = models.CRMIntegration(
        name=body.name,
        webhook_url=body.webhook_url,
        is_active=body.is_active,
        send_on_types=body.send_on_types,
    )
    db.add(crm)
    db.commit()
    db.refresh(crm)
    return crm

@router.get("/", response_model=List[schemas.CRMIntegrationOut])
def list_integrations(db: Session = Depends(database.get_db)):
    return db.query(models.CRMIntegration).all()

@router.put("/{integration_id}", response_model=schemas.CRMIntegrationOut)
def update_integration(integration_id: int, body: schemas.CRMIntegrationCreate, db: Session = Depends(database.get_db)):
    crm = db.query(models.CRMIntegration).filter(models.CRMIntegration.id == integration_id).first()
    if not crm:
        raise HTTPException(status_code=404, detail="Integration not found")
    crm.name = body.name
    crm.webhook_url = body.webhook_url
    crm.is_active = body.is_active
    crm.send_on_types = body.send_on_types
    db.commit()
    db.refresh(crm)
    return crm

@router.delete("/{integration_id}")
def delete_integration(integration_id: int, db: Session = Depends(database.get_db)):
    crm = db.query(models.CRMIntegration).filter(models.CRMIntegration.id == integration_id).first()
    if not crm:
        raise HTTPException(status_code=404, detail="Integration not found")
    db.delete(crm)
    db.commit()
    return {"ok": True}

@router.post("/{integration_id}/test")
def test_integration(integration_id: int, db: Session = Depends(database.get_db)):
    crm = db.query(models.CRMIntegration).filter(models.CRMIntegration.id == integration_id).first()
    if not crm:
        raise HTTPException(status_code=404, detail="Integration not found")
    payload = _build_payload({
        "id": 0,
        "text": "Тестовое упоминание от Mention Monitor",
        "source_type": "test",
        "source_url": "https://example.com",
        "author": "test_user",
        "date": "2026-01-01T00:00:00",
        "keyword": "тест",
        "content_type": "text",
        "geo_country": "Россия",
        "geo_city": "Москва",
        "ocr_text": "",
        "media_url": "",
    }, crm.name)
    try:
        resp = requests.post(crm.webhook_url, json=payload, timeout=10)
        return {"status": resp.status_code, "ok": resp.ok, "response": resp.text[:500]}
    except Exception as e:
        return {"status": 0, "ok": False, "error": str(e)}

def _build_payload(mention: Dict[str, Any], crm_name: str) -> Dict:
    base = {
        "mention_id": mention.get("id"),
        "text": mention.get("text"),
        "source": mention.get("source_url"),
        "source_type": mention.get("source_type"),
        "author": mention.get("author"),
        "date": str(mention.get("date")),
        "keyword": mention.get("keyword"),
        "content_type": mention.get("content_type"),
        "geo_country": mention.get("geo_country"),
        "geo_city": mention.get("geo_city"),
        "ocr_text": mention.get("ocr_text"),
        "media_url": mention.get("media_url"),
    }
    if crm_name.lower() == "amocrm":
        return {
            "leads[add][0][name]": f"Упоминание: {mention.get('keyword')}",
            "leads[add][0][tags]": mention.get("source_type", ""),
            "leads[add][0][custom_fields][0][id]": "mention_text",
            "leads[add][0][custom_fields][0][values][0][value]": mention.get("text", ""),
            **base,
        }
    elif crm_name.lower() == "bitrix24":
        return {
            "FIELDS[TITLE]": f"Упоминание: {mention.get('keyword')}",
            "FIELDS[COMMENTS]": mention.get("text", ""),
            "FIELDS[SOURCE_ID]": "WEBFORM",
            "FIELDS[SOURCE_DESCRIPTION]": mention.get("source_url", ""),
            **base,
        }
    return base

def send_to_crm_webhooks(mention: Dict[str, Any], db: Session):
    integrations = db.query(models.CRMIntegration).filter(models.CRMIntegration.is_active == True).all()
    for crm in integrations:
        content_type = mention.get("content_type", "text")
        if crm.send_on_types and content_type not in crm.send_on_types:
            continue
        payload = _build_payload(mention, crm.name)
        try:
            resp = requests.post(crm.webhook_url, json=payload, timeout=10)
            if not resp.ok:
                logger.warning(f"CRM {crm.name} returned {resp.status_code}: {resp.text[:200]}")
            else:
                logger.info(f"Mention #{mention.get('id')} sent to {crm.name}")
        except Exception as e:
            logger.error(f"Error sending to {crm.name}: {e}")