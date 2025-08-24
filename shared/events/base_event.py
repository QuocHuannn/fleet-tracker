"""Base event class for Fleet Tracker event system"""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class BaseEvent(BaseModel):
    """Base event class for all Fleet Tracker events"""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    source_service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        """Create event from dictionary"""
        return cls(**data)

class EventMetadata(BaseModel):
    """Event metadata for routing and processing"""
    
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None
    priority: int = 1  # 1 (highest) to 5 (lowest)
    routing_key: Optional[str] = None
