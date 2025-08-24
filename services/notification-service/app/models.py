# Notification Service Models

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from .database import Base

class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    device_id = Column(UUID(as_uuid=True), nullable=True)
    type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default='medium')
    status = Column(String(20), default='active')
    source_service = Column(String(50), nullable=True)
    source_event_id = Column(UUID(as_uuid=True), nullable=True)
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    address = Column(Text, nullable=True)
    metadata = Column(JSONB, default={})
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    auto_resolve = Column(Boolean, default=False)
    auto_resolve_timeout = Column(Integer, nullable=True)
    escalation_level = Column(Integer, default=0)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class NotificationRule(Base):
    """Notification rule model"""
    __tablename__ = "notification_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    alert_types = Column(ARRAY(String), nullable=True)
    alert_categories = Column(ARRAY(String), nullable=True)
    severity_levels = Column(ARRAY(String), nullable=True)
    vehicle_ids = Column(ARRAY(UUID), nullable=True)
    user_ids = Column(ARRAY(UUID), nullable=True)
    geofence_ids = Column(ARRAY(UUID), nullable=True)
    active_hours = Column(JSONB, nullable=True)
    active_days = Column(ARRAY(Integer), nullable=True)
    timezone = Column(String(50), default='UTC')
    channels = Column(ARRAY(String), nullable=False)
    delay_minutes = Column(Integer, default=0)
    repeat_interval_minutes = Column(Integer, nullable=True)
    max_repeats = Column(Integer, default=0)
    escalate_after_minutes = Column(Integer, nullable=True)
    escalation_user_ids = Column(ARRAY(UUID), nullable=True)
    escalation_channels = Column(ARRAY(String), nullable=True)
    priority = Column(Integer, default=1)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WebSocketConnection(Base):
    """WebSocket connection model"""
    __tablename__ = "websocket_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    connection_id = Column(String(255), nullable=False)
    client_info = Column(JSONB, default={})
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    subscribed_vehicles = Column(ARRAY(UUID), nullable=True)
    subscribed_alert_types = Column(ARRAY(String), nullable=True)
    subscribed_severities = Column(ARRAY(String), nullable=True)
