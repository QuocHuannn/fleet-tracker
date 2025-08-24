"""Vehicle-related events for Fleet Tracker"""
from typing import Optional, Dict, Any
from .base_event import BaseEvent

class VehicleCreatedEvent(BaseEvent):
    """Event emitted when a new vehicle is created"""
    
    def __init__(self, vehicle_id: str, vehicle_data: Dict[str, Any], user_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="vehicle.created",
            source_service="vehicle-service",
            user_id=user_id,
            data={
                "vehicle_id": vehicle_id,
                "vehicle": vehicle_data
            },
            **kwargs
        )

class VehicleUpdatedEvent(BaseEvent):
    """Event emitted when a vehicle is updated"""
    
    def __init__(self, vehicle_id: str, updated_fields: Dict[str, Any], user_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="vehicle.updated",
            source_service="vehicle-service",
            user_id=user_id,
            data={
                "vehicle_id": vehicle_id,
                "updated_fields": updated_fields
            },
            **kwargs
        )

class VehicleDeletedEvent(BaseEvent):
    """Event emitted when a vehicle is deleted"""
    
    def __init__(self, vehicle_id: str, user_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="vehicle.deleted",
            source_service="vehicle-service",
            user_id=user_id,
            data={
                "vehicle_id": vehicle_id
            },
            **kwargs
        )

class VehicleStatusChangedEvent(BaseEvent):
    """Event emitted when vehicle status changes"""
    
    def __init__(self, vehicle_id: str, old_status: str, new_status: str, user_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="vehicle.status.changed",
            source_service="vehicle-service",
            user_id=user_id,
            data={
                "vehicle_id": vehicle_id,
                "old_status": old_status,
                "new_status": new_status
            },
            **kwargs
        )

class DeviceRegisteredEvent(BaseEvent):
    """Event emitted when a device is registered to a vehicle"""
    
    def __init__(self, vehicle_id: str, device_id: str, device_data: Dict[str, Any], user_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="device.registered",
            source_service="vehicle-service",
            user_id=user_id,
            data={
                "vehicle_id": vehicle_id,
                "device_id": device_id,
                "device": device_data
            },
            **kwargs
        )
