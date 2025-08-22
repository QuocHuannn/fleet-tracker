from sqlalchemy import Column, String, Enum, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.database import Base


class DeviceStatus(str, enum.Enum):
    """
    Trạng thái của thiết bị GPS
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DISCONNECTED = "disconnected"


class Device(Base):
    """
    Model cho thiết bị GPS
    """
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    imei = Column(String(50), unique=True, nullable=False)
    sim_card = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.ACTIVE)
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

    # Relationship
    # vehicle = relationship("Vehicle", back_populates="devices")

    def __repr__(self):
        return f"<Device {self.imei}>"
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary
        """
        return {
            "id": str(self.id),
            "vehicle_id": str(self.vehicle_id),
            "imei": self.imei,
            "sim_card": self.sim_card,
            "model": self.model,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
