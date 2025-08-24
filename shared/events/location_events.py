"""Location-related events for Fleet Tracker"""
from typing import Optional, Dict, Any, List
from .base_event import BaseEvent

class LocationUpdatedEvent(BaseEvent):
    """Event emitted when vehicle location is updated"""
    
    def __init__(self, vehicle_id: str, location_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="location.updated",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "location": location_data
            },
            **kwargs
        )

class GeofenceViolatedEvent(BaseEvent):
    """Event emitted when vehicle violates geofence"""
    
    def __init__(self, vehicle_id: str, geofence_id: str, violation_type: str, location_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="geofence.violated",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "geofence_id": geofence_id,
                "violation_type": violation_type,  # "entry", "exit"
                "location": location_data
            },
            **kwargs
        )

class SpeedViolationEvent(BaseEvent):
    """Event emitted when vehicle exceeds speed limit"""
    
    def __init__(self, vehicle_id: str, current_speed: float, speed_limit: float, location_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="speed.violated",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "current_speed": current_speed,
                "speed_limit": speed_limit,
                "location": location_data
            },
            **kwargs
        )

class TripStartedEvent(BaseEvent):
    """Event emitted when a trip starts"""
    
    def __init__(self, vehicle_id: str, trip_id: str, start_location: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="trip.started",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "trip_id": trip_id,
                "start_location": start_location
            },
            **kwargs
        )

class TripCompletedEvent(BaseEvent):
    """Event emitted when a trip is completed"""
    
    def __init__(self, vehicle_id: str, trip_id: str, trip_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="trip.completed",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "trip_id": trip_id,
                "trip": trip_data
            },
            **kwargs
        )

class VehicleOfflineEvent(BaseEvent):
    """Event emitted when vehicle goes offline"""
    
    def __init__(self, vehicle_id: str, last_seen: str, **kwargs):
        super().__init__(
            event_type="vehicle.offline",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "last_seen": last_seen
            },
            **kwargs
        )

class VehicleOnlineEvent(BaseEvent):
    """Event emitted when vehicle comes back online"""
    
    def __init__(self, vehicle_id: str, location_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="vehicle.online",
            source_service="location-service",
            data={
                "vehicle_id": vehicle_id,
                "location": location_data
            },
            **kwargs
        )
