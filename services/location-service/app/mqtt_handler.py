"""MQTT Handler for Location Service - GPS Device Communication"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

import aiomqtt
from pydantic import BaseModel, ValidationError

from .config import settings
from .models import LocationData
from .services.location_processor import LocationProcessor

logger = logging.getLogger(__name__)

class GPSMessage(BaseModel):
    """GPS message format from devices"""
    device_id: str
    vehicle_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None  # km/h
    heading: Optional[int] = None  # degrees 0-360
    satellites: Optional[int] = None
    hdop: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[int] = None
    ignition: Optional[bool] = None
    odometer: Optional[float] = None
    fuel_level: Optional[float] = None

class MQTTHandler:
    """Handles MQTT communication for GPS devices"""
    
    def __init__(self):
        self.client: Optional[aiomqtt.Client] = None
        self.connected = False
        self.location_processor = LocationProcessor()
        self.message_handlers: Dict[str, Callable] = {}
        self.reconnect_interval = 5  # seconds
        self.max_reconnect_attempts = 10
        
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            # Extract connection details from URL
            broker_url = settings.MQTT_BROKER_URL.replace("mqtt://", "")
            host, port = broker_url.split(':') if ':' in broker_url else (broker_url, 1883)
            
            self.client = aiomqtt.Client(
                hostname=host,
                port=int(port),
                username=settings.MQTT_USERNAME,
                password=settings.MQTT_PASSWORD,
                client_id=f"{settings.MQTT_CLIENT_ID}-{uuid.uuid4().hex[:8]}",
                keepalive=60,
                clean_session=True
            )
            
            await self.client.__aenter__()
            self.connected = True
            
            # Subscribe to GPS data topics
            await self._subscribe_to_topics()
            
            logger.info(f"✅ MQTT connected to {host}:{port}")
            
            # Start message processing task
            asyncio.create_task(self._process_messages())
            
        except Exception as e:
            logger.error(f"❌ MQTT connection failed: {str(e)}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
                self.connected = False
                logger.info("✅ MQTT disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting MQTT: {str(e)}")
    
    async def _subscribe_to_topics(self):
        """Subscribe to MQTT topics for GPS data"""
        topics = [
            "fleet/vehicles/+/location",  # Individual vehicle locations
            "fleet/vehicles/+/status",    # Vehicle status updates
            "fleet/devices/+/heartbeat",  # Device heartbeats
            "fleet/system/broadcast"      # System broadcasts
        ]
        
        for topic in topics:
            await self.client.subscribe(topic)
            logger.info(f"📡 Subscribed to MQTT topic: {topic}")
    
    async def _process_messages(self):
        """Process incoming MQTT messages"""
        try:
            async for message in self.client.messages:
                await self._handle_message(message)
        except Exception as e:
            logger.error(f"Error processing MQTT messages: {str(e)}")
            if self.connected:
                await self._reconnect()
    
    async def _handle_message(self, message: aiomqtt.Message):
        """Handle individual MQTT message"""
        try:
            topic = str(message.topic)
            payload = message.payload.decode('utf-8')
            
            logger.debug(f"📥 MQTT message: {topic} -> {payload[:100]}...")
            
            # Route message based on topic
            if "/location" in topic:
                await self._handle_location_message(topic, payload)
            elif "/status" in topic:
                await self._handle_status_message(topic, payload)  
            elif "/heartbeat" in topic:
                await self._handle_heartbeat_message(topic, payload)
            elif "/broadcast" in topic:
                await self._handle_broadcast_message(topic, payload)
            else:
                logger.warning(f"Unknown MQTT topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error handling MQTT message: {str(e)}")
    
    async def _handle_location_message(self, topic: str, payload: str):
        """Handle GPS location messages"""
        try:
            # Parse JSON payload
            data = json.loads(payload)
            
            # Validate GPS message
            gps_message = GPSMessage(**data)
            
            # Convert to LocationData for processing
            location_data = LocationData(
                vehicle_id=gps_message.vehicle_id,
                device_id=gps_message.device_id,
                latitude=gps_message.latitude,
                longitude=gps_message.longitude,
                altitude=gps_message.altitude,
                speed=gps_message.speed,
                heading=gps_message.heading,
                accuracy=gps_message.accuracy,
                satellites=gps_message.satellites,
                hdop=gps_message.hdop,
                recorded_at=gps_message.timestamp,
                raw_data=data
            )
            
            # Process location data
            await self.location_processor.process_location(location_data)
            
            logger.info(f"📍 Processed GPS location for vehicle {gps_message.vehicle_id}")
            
        except ValidationError as e:
            logger.error(f"Invalid GPS message format: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GPS message: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing location message: {str(e)}")
    
    async def _handle_status_message(self, topic: str, payload: str):
        """Handle vehicle status messages"""
        try:
            data = json.loads(payload)
            vehicle_id = data.get('vehicle_id')
            status = data.get('status')
            
            logger.info(f"🚗 Vehicle {vehicle_id} status: {status}")
            
            # TODO: Update vehicle status in database
            # TODO: Generate status change events
            
        except Exception as e:
            logger.error(f"Error processing status message: {str(e)}")
    
    async def _handle_heartbeat_message(self, topic: str, payload: str):
        """Handle device heartbeat messages"""
        try:
            data = json.loads(payload)
            device_id = data.get('device_id')
            timestamp = data.get('timestamp')
            battery_level = data.get('battery_level')
            signal_strength = data.get('signal_strength')
            
            logger.debug(f"💓 Device {device_id} heartbeat - Battery: {battery_level}%")
            
            # TODO: Update device last heartbeat in database
            # TODO: Check for offline devices
            
        except Exception as e:
            logger.error(f"Error processing heartbeat message: {str(e)}")
    
    async def _handle_broadcast_message(self, topic: str, payload: str):
        """Handle system broadcast messages"""
        try:
            data = json.loads(payload)
            message_type = data.get('type')
            content = data.get('message')
            
            logger.info(f"📢 System broadcast [{message_type}]: {content}")
            
            # TODO: Handle different broadcast types
            # - System maintenance notifications  
            # - Emergency alerts
            # - Configuration updates
            
        except Exception as e:
            logger.error(f"Error processing broadcast message: {str(e)}")
    
    async def _reconnect(self):
        """Reconnect to MQTT broker with exponential backoff"""
        attempt = 0
        while attempt < self.max_reconnect_attempts and not self.connected:
            try:
                await asyncio.sleep(self.reconnect_interval * (2 ** attempt))
                await self.connect()
                logger.info("✅ MQTT reconnected successfully")
                break
            except Exception as e:
                attempt += 1
                logger.warning(f"MQTT reconnect attempt {attempt} failed: {str(e)}")
        
        if not self.connected:
            logger.error("❌ MQTT reconnection failed after maximum attempts")
    
    async def publish_command(self, vehicle_id: str, command: str, data: Dict[str, Any]):
        """Send command to vehicle device"""
        if not self.connected or not self.client:
            logger.error("MQTT not connected - cannot send command")
            return False
        
        try:
            topic = f"fleet/vehicles/{vehicle_id}/commands"
            payload = json.dumps({
                'command': command,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'sender': 'location-service'
            })
            
            await self.client.publish(topic, payload)
            logger.info(f"📤 Sent command to {vehicle_id}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending MQTT command: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected

# Global MQTT handler instance
mqtt_handler = MQTTHandler()
