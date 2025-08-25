"""Location data models for GPS processing"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# SQLAlchemy imports
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class LocationData(BaseModel):
    """GPS location data from devices"""
    
    # Identifiers
    vehicle_id: str
    device_id: Optional[str] = None
    
    # GPS coordinates
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    
    # Motion data
    speed: Optional[float] = Field(None, ge=0)  # km/h
    heading: Optional[int] = Field(None, ge=0, le=360)  # degrees
    
    # GPS quality
    accuracy: Optional[float] = Field(None, ge=0)  # meters
    satellites: Optional[int] = Field(None, ge=0)
    hdop: Optional[float] = Field(None, ge=0)  # Horizontal dilution of precision
    
    # Vehicle data
    odometer: Optional[float] = Field(None, ge=0)  # kilometers
    fuel_level: Optional[float] = Field(None, ge=0, le=100)  # percentage
    battery_voltage: Optional[float] = None
    temperature: Optional[float] = None
    engine_status: Optional[str] = None  # on, off, idle
    
    # Timestamps
    recorded_at: datetime
    received_at: Optional[datetime] = None
    
    # Raw data from device
    raw_data: Optional[Dict[str, Any]] = None
    
    @validator('speed')
    def validate_speed(cls, v):
        if v is not None and v > 300:  # > 300 km/h seems unrealistic
            raise ValueError('Speed value seems unrealistic')
        return v
    
    @validator('vehicle_id', 'device_id')
    def validate_ids(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('ID cannot be empty')
        return v
    
    class Config:
        # Allow datetime objects
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ProcessedLocation(BaseModel):
    """Processed location data with additional computed fields"""
    
    # Original location data
    location_data: LocationData
    
    # Computed fields
    address: Optional[str] = None
    is_valid: bool = True
    validation_errors: list = []
    
    # Movement analysis
    distance_from_last: Optional[float] = None  # meters
    time_since_last: Optional[float] = None     # seconds
    is_moving: Optional[bool] = None
    is_speeding: Optional[bool] = None
    speed_limit: Optional[float] = None
    
    # Geofence analysis
    geofence_violations: list = []
    current_geofences: list = []
    
    # Trip analysis
    trip_id: Optional[str] = None
    is_trip_start: bool = False
    is_trip_end: bool = False
    
    # Alert triggers
    alerts_triggered: list = []
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processor_version: str = "1.0.0"

class GeofenceViolation(BaseModel):
    """Geofence violation data"""
    
    geofence_id: str
    geofence_name: str
    violation_type: str  # entry, exit, speed_violation
    vehicle_id: str
    location_data: LocationData
    violation_time: datetime
    severity: str = "medium"  # low, medium, high, critical

# SQLAlchemy Models

class Location(Base):
    """Location data database model"""
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(String(255), nullable=False, index=True)
    device_id = Column(String(255), index=True)
    
    # GPS coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    
    # Motion data
    speed = Column(Float)
    heading = Column(Integer)
    
    # GPS quality
    accuracy = Column(Float)
    satellites = Column(Integer)
    hdop = Column(Float)
    
    # Vehicle data
    odometer = Column(Float)
    fuel_level = Column(Float)
    battery_voltage = Column(Float)
    temperature = Column(Float)
    engine_status = Column(String(50))
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Raw data
    raw_data = Column(JSONB, default={})
    
    # Computed fields
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSONB, default=[])
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Location(vehicle_id='{self.vehicle_id}', lat={self.latitude}, lng={self.longitude})>"
