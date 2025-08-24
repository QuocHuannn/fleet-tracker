"""Alert management routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime
import uuid

from ..database import get_db
from ..models import Alert

router = APIRouter()

class AlertResponse(BaseModel):
    id: str
    vehicle_id: str
    type: str
    category: str
    title: str
    message: str
    severity: str
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    created_at: datetime.datetime
    acknowledged_at: Optional[datetime.datetime]
    resolved_at: Optional[datetime.datetime]

class AlertCreateRequest(BaseModel):
    vehicle_id: str
    type: str
    category: str
    title: str
    message: str
    severity: str = "medium"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    vehicle_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List alerts with filtering and pagination"""
    query = db.query(Alert)
    
    if vehicle_id:
        query = query.filter(Alert.vehicle_id == vehicle_id)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.offset(skip).limit(limit).all()
    
    return [
        AlertResponse(
            id=str(alert.id),
            vehicle_id=str(alert.vehicle_id),
            type=alert.type,
            category=alert.category,
            title=alert.title,
            message=alert.message,
            severity=alert.severity,
            status=alert.status,
            latitude=float(alert.latitude) if alert.latitude else None,
            longitude=float(alert.longitude) if alert.longitude else None,
            address=alert.address,
            created_at=alert.created_at,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at
        )
        for alert in alerts
    ]

@router.post("/", response_model=AlertResponse)
async def create_alert(request: AlertCreateRequest, db: Session = Depends(get_db)):
    """Create new alert"""
    alert = Alert(
        vehicle_id=uuid.UUID(request.vehicle_id),
        type=request.type,
        category=request.category,
        title=request.title,
        message=request.message,
        severity=request.severity,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return AlertResponse(
        id=str(alert.id),
        vehicle_id=str(alert.vehicle_id),
        type=alert.type,
        category=alert.category,
        title=alert.title,
        message=alert.message,
        severity=alert.severity,
        status=alert.status,
        latitude=float(alert.latitude) if alert.latitude else None,
        longitude=float(alert.longitude) if alert.longitude else None,
        address=alert.address,
        created_at=alert.created_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at
    )

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get alert by ID"""
    alert = db.query(Alert).filter(Alert.id == uuid.UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse(
        id=str(alert.id),
        vehicle_id=str(alert.vehicle_id),
        type=alert.type,
        category=alert.category,
        title=alert.title,
        message=alert.message,
        severity=alert.severity,
        status=alert.status,
        latitude=float(alert.latitude) if alert.latitude else None,
        longitude=float(alert.longitude) if alert.longitude else None,
        address=alert.address,
        created_at=alert.created_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at
    )

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Acknowledge alert"""
    alert = db.query(Alert).filter(Alert.id == uuid.UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged_at = datetime.datetime.utcnow()
    alert.status = "acknowledged"
    
    db.commit()
    
    return {"message": "Alert acknowledged successfully"}

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolution_notes: Optional[str] = None, db: Session = Depends(get_db)):
    """Resolve alert"""
    alert = db.query(Alert).filter(Alert.id == uuid.UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved_at = datetime.datetime.utcnow()
    alert.status = "resolved"
    if resolution_notes:
        alert.resolution_notes = resolution_notes
    
    db.commit()
    
    return {"message": "Alert resolved successfully"}
