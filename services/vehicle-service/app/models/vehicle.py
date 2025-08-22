from sqlalchemy import Column, String, Enum, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.database import Base


class VehicleStatus(str, enum.Enum):
    """
    Trạng thái của xe
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class VehicleType(str, enum.Enum):
    """
    Loại xe
    """
    CAR = "car"
    TRUCK = "truck"
    VAN = "van"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    OTHER = "other"


class Vehicle(Base):
    """
    Model cho thông tin xe
    """
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    type = Column(Enum(VehicleType), nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.ACTIVE)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

    def __repr__(self):
        return f"<Vehicle {self.license_plate}>"
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "license_plate": self.license_plate,
            "type": self.type.value,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
