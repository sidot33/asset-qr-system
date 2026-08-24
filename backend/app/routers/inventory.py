from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uuid
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..crypto import decrypt_payload

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.post("/tasks", response_model=schemas.InventoryTaskResponse)
def create_task(task: schemas.InventoryTaskCreate, db: Session = Depends(get_db)):
    db_task = models.InventoryTask(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/tasks", response_model=List[schemas.InventoryTaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.InventoryTask).all()


@router.get("/scan-rfid/{rfid_tag}", response_model=schemas.AssetResponse)
def scan_asset_by_rfid(rfid_tag: str, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.rfid_tag == rfid_tag).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/scan/{token}", response_model=schemas.AssetResponse)
def scan_asset(token: str, db: Session = Depends(get_db)):
    try:
        payload = decrypt_payload(token)
        asset_code = payload.get("a")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid QR code: {str(e)}")

    asset = db.query(models.Asset).filter(models.Asset.asset_code == asset_code).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.post("/confirm", response_model=schemas.InventoryRecordResponse)
def confirm_inventory(confirm: schemas.InventoryConfirm, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.asset_code == confirm.asset_code).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check for duplicate within 5 minutes
    five_mins_ago = func.datetime("now", "-5 minutes")
    recent = db.query(models.InventoryRecord).filter(
        models.InventoryRecord.asset_code == confirm.asset_code,
        models.InventoryRecord.inventory_time >= five_mins_ago
    ).first()
    
    if recent:
        raise HTTPException(status_code=400, detail="请勿重复盘点（5分钟内）")
    
    # Determine status
    status = "正常"
    if asset.location != confirm.actual_location:
        status = "位置不符"
    
    record = models.InventoryRecord(
        asset_code=confirm.asset_code,
        inventory_person=confirm.inventory_person,
        original_location=asset.location,
        actual_location=confirm.actual_location,
        gps_location=confirm.gps_location,
        device_info=confirm.device_info,
        status=status,
        task_id=confirm.task_id or str(uuid.uuid4())
    )
    
    db.add(record)
    
    # Update asset inventory logs
    logs = asset.inventory_logs or []
    logs.append({
        "time": datetime.now().isoformat(),
        "person": confirm.inventory_person,
        "status": status,
        "actual_location": confirm.actual_location
    })
    asset.inventory_logs = logs
    
    db.commit()
    db.refresh(record)
    return record


@router.get("/records", response_model=List[schemas.InventoryRecordResponse])
def list_records(
    task_id: Optional[str] = None,
    asset_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.InventoryRecord)
    if task_id:
        query = query.filter(models.InventoryRecord.task_id == task_id)
    if asset_code:
        query = query.filter(models.InventoryRecord.asset_code == asset_code)
    return query.order_by(models.InventoryRecord.inventory_time.desc()).all()
