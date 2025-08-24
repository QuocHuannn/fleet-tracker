"""Health check endpoints for location service"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
import datetime

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection with PostGIS
        db.execute(text("SELECT 1"))
        # Test PostGIS extension
        result = db.execute(text("SELECT PostGIS_Version()")).fetchone()
        db_status = "healthy"
        postgis_version = result[0] if result else "unknown"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        postgis_version = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": "location-service",
        "database": db_status,
        "postgis_version": postgis_version,
        "version": "1.0.0"
    }
