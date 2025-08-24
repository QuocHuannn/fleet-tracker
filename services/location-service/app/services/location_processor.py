"""Location data processing service"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import SessionLocal
from ..models.location_data import LocationData, ProcessedLocation, GeofenceViolation
from ..config import settings

logger = logging.getLogger(__name__)

class LocationProcessor:
    """Processes GPS location data from devices"""
    
    def __init__(self):
        self.last_locations: Dict[str, LocationData] = {}  # Cache last location per vehicle
        self.processing_queue = asyncio.Queue()
        
    async def process_location(self, location_data: LocationData) -> ProcessedLocation:
        """Process incoming GPS location data"""
        try:
            # Validate location data
            if not self._is_valid_location(location_data):
                logger.warning(f"Invalid location data for vehicle {location_data.vehicle_id}")
                return ProcessedLocation(
                    location_data=location_data,
                    is_valid=False,
                    validation_errors=["Invalid GPS coordinates"]
                )
            
            # Get database session
            db = SessionLocal()
            
            try:
                # Create processed location object
                processed = ProcessedLocation(location_data=location_data)
                
                # Analyze movement
                await self._analyze_movement(processed, db)
                
                # Check geofences
                await self._check_geofences(processed, db)
                
                # Analyze trip patterns
                await self._analyze_trips(processed, db)
                
                # Store location data
                await self._store_location(processed, db)
                
                # Update current location cache
                await self._update_current_location(processed, db)
                
                # Generate alerts if needed
                await self._generate_alerts(processed, db)
                
                # Cache for next processing
                self.last_locations[location_data.vehicle_id] = location_data
                
                logger.debug(f"✅ Processed location for vehicle {location_data.vehicle_id}")
                return processed
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing location: {str(e)}")
            return ProcessedLocation(
                location_data=location_data,
                is_valid=False,
                validation_errors=[f"Processing error: {str(e)}"]
            )
    
    def _is_valid_location(self, location: LocationData) -> bool:
        """Validate GPS coordinates"""
        # Check coordinate ranges
        if not (-90 <= location.latitude <= 90):
            return False
        if not (-180 <= location.longitude <= 180):
            return False
        
        # Check for obvious invalid coordinates (0,0) unless actually there
        if location.latitude == 0 and location.longitude == 0:
            return False
        
        # Check timestamp is reasonable (not too far in future/past)
        now = datetime.utcnow()
        if location.recorded_at > now + timedelta(minutes=5):
            return False
        if location.recorded_at < now - timedelta(days=7):
            return False
        
        return True
    
    async def _analyze_movement(self, processed: ProcessedLocation, db: Session):
        """Analyze movement patterns and speed"""
        location = processed.location_data
        vehicle_id = location.vehicle_id
        
        # Get last location from cache
        last_location = self.last_locations.get(vehicle_id)
        
        if last_location:
            # Calculate distance and time difference
            processed.distance_from_last = self._calculate_distance(
                last_location.latitude, last_location.longitude,
                location.latitude, location.longitude
            )
            
            time_diff = (location.recorded_at - last_location.recorded_at).total_seconds()
            processed.time_since_last = time_diff
            
            # Determine if moving (speed > 5 km/h or distance > 50m in last update)
            if location.speed and location.speed > 5:
                processed.is_moving = True
            elif processed.distance_from_last and processed.distance_from_last > 50:
                processed.is_moving = True
            else:
                processed.is_moving = False
            
            # Check for speeding (TODO: get speed limits from geofences/roads)
            default_speed_limit = 80  # km/h
            if location.speed and location.speed > default_speed_limit:
                processed.is_speeding = True
                processed.speed_limit = default_speed_limit
    
    async def _check_geofences(self, processed: ProcessedLocation, db: Session):
        """Check for geofence violations"""
        location = processed.location_data
        
        try:
            # Query active geofences (using PostGIS spatial queries)
            query = text("""
                SELECT id, name, type, boundary, max_speed
                FROM geofences 
                WHERE is_active = true
                AND ST_Contains(boundary, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            """)
            
            result = db.execute(query, {
                'lat': location.latitude, 
                'lng': location.longitude
            })
            
            current_geofences = result.fetchall()
            processed.current_geofences = [row[0] for row in current_geofences]
            
            # Check speed violations within geofences
            for row in current_geofences:
                geofence_id, name, geofence_type, boundary, max_speed = row
                
                if max_speed and location.speed and location.speed > max_speed:
                    violation = GeofenceViolation(
                        geofence_id=str(geofence_id),
                        geofence_name=name,
                        violation_type="speed_violation",
                        vehicle_id=location.vehicle_id,
                        location=location,
                        severity="high",
                        description=f"Speed {location.speed} km/h exceeds limit {max_speed} km/h in {name}"
                    )
                    processed.geofence_violations.append(violation)
            
            # TODO: Check for entry/exit violations by comparing with last location
            
        except Exception as e:
            logger.error(f"Error checking geofences: {str(e)}")
    
    async def _analyze_trips(self, processed: ProcessedLocation, db: Session):
        """Analyze trip patterns"""
        location = processed.location_data
        
        # Simple trip detection logic
        # TODO: Implement more sophisticated trip detection
        
        if processed.is_moving:
            # Check if this starts a new trip
            last_location = self.last_locations.get(location.vehicle_id)
            if not last_location or not getattr(processed, 'was_moving', True):
                processed.is_trip_start = True
                # TODO: Create new trip in database
        else:
            # Check if this ends a trip
            if location.vehicle_id in self.last_locations:
                processed.is_trip_end = True
                # TODO: Close active trip in database
    
    async def _store_location(self, processed: ProcessedLocation, db: Session):
        """Store location data in database"""
        location = processed.location_data
        
        try:
            # Insert into locations table (using raw SQL for PostGIS)
            query = text("""
                INSERT INTO locations (
                    id, vehicle_id, device_id, position, altitude, speed, heading,
                    accuracy, satellites, hdop, odometer, fuel_level, battery_voltage,
                    temperature, engine_status, address, raw_data, recorded_at, received_at
                ) VALUES (
                    :id, :vehicle_id, :device_id, 
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :altitude, :speed, :heading, :accuracy, :satellites, :hdop,
                    :odometer, :fuel_level, :battery_voltage, :temperature, :engine_status,
                    :address, :raw_data, :recorded_at, :received_at
                )
            """)
            
            db.execute(query, {
                'id': str(uuid.uuid4()),
                'vehicle_id': location.vehicle_id,
                'device_id': location.device_id,
                'lat': location.latitude,
                'lng': location.longitude,
                'altitude': location.altitude,
                'speed': location.speed,
                'heading': location.heading,
                'accuracy': location.accuracy,
                'satellites': location.satellites,
                'hdop': location.hdop,
                'odometer': location.odometer,
                'fuel_level': location.fuel_level,
                'battery_voltage': location.battery_voltage,
                'temperature': location.temperature,
                'engine_status': location.engine_status,
                'address': processed.address,
                'raw_data': location.raw_data,
                'recorded_at': location.recorded_at,
                'received_at': datetime.utcnow()
            })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing location: {str(e)}")
            db.rollback()
    
    async def _update_current_location(self, processed: ProcessedLocation, db: Session):
        """Update current location cache table"""
        location = processed.location_data
        
        try:
            # Upsert current location
            query = text("""
                INSERT INTO current_locations (
                    vehicle_id, position, speed, heading, address, last_update, is_online, signal_quality
                ) VALUES (
                    :vehicle_id, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :speed, :heading, :address, :last_update, true, :signal_quality
                ) ON CONFLICT (vehicle_id) DO UPDATE SET
                    position = EXCLUDED.position,
                    speed = EXCLUDED.speed,
                    heading = EXCLUDED.heading,
                    address = EXCLUDED.address,
                    last_update = EXCLUDED.last_update,
                    is_online = EXCLUDED.is_online,
                    signal_quality = EXCLUDED.signal_quality,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            signal_quality = 95 if location.satellites and location.satellites >= 8 else 70
            
            db.execute(query, {
                'vehicle_id': location.vehicle_id,
                'lat': location.latitude,
                'lng': location.longitude,
                'speed': location.speed,
                'heading': location.heading,
                'address': processed.address,
                'last_update': location.recorded_at,
                'signal_quality': signal_quality
            })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating current location: {str(e)}")
            db.rollback()
    
    async def _generate_alerts(self, processed: ProcessedLocation, db: Session):
        """Generate alerts based on processed location data"""
        alerts = []
        
        # Speed violation alerts
        if processed.is_speeding:
            alerts.append({
                'type': 'speed_violation',
                'severity': 'high',
                'message': f'Vehicle exceeded speed limit: {processed.location_data.speed} km/h'
            })
        
        # Geofence violation alerts
        for violation in processed.geofence_violations:
            alerts.append({
                'type': 'geofence_violation',
                'severity': violation.severity,
                'message': violation.description
            })
        
        # TODO: Send alerts to notification service via event system
        
        processed.alerts_triggered = alerts
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two GPS coordinates in meters"""
        import math
        
        # Haversine formula
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) * math.sin(delta_lng / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
