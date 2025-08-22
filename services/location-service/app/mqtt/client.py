import asyncio
import json
from typing import Dict, Any, Optional, Callable
import logging
from urllib.parse import urlparse
import uuid
import ssl

import aiomqtt
from aiomqtt import Client, Message

from app.config import settings

logger = logging.getLogger(__name__)

class MQTTClient:
    """
    MQTT Client để nhận dữ liệu từ thiết bị GPS
    """
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected: bool = False
        self.handlers: Dict[str, Callable] = {}
        self.task: Optional[asyncio.Task] = None
        
        # Parse MQTT URL
        url = urlparse(settings.MQTT_BROKER_URL)
        self.host = url.hostname or "localhost"
        self.port = url.port or 1883
        self.use_ssl = url.scheme == "mqtts"
        
    async def connect(self):
        """
        Kết nối đến MQTT broker
        """
        try:
            # Tạo SSL context nếu cần
            ssl_context = None
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
            
            # Kết nối đến MQTT broker
            self.client = Client(
                hostname=self.host,
                port=self.port,
                username=settings.MQTT_USERNAME,
                password=settings.MQTT_PASSWORD,
                client_id=f"{settings.MQTT_CLIENT_ID}-{uuid.uuid4()}",
                ssl_context=ssl_context
            )
            
            await self.client.__aenter__()
            self.is_connected = True
            
            # Subscribe các topics
            await self.client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}+/location")
            
            # Bắt đầu task xử lý messages
            self.task = asyncio.create_task(self.message_loop())
            
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
        except Exception as e:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
    
    async def disconnect(self):
        """
        Ngắt kết nối từ MQTT broker
        """
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.is_connected = False
            logger.info("Disconnected from MQTT broker")
    
    async def message_loop(self):
        """
        Vòng lặp xử lý MQTT messages
        """
        try:
            async for message in self.client.messages:
                try:
                    # Parse topic để lấy vehicle_id
                    topic_parts = message.topic.value.decode().split('/')
                    if len(topic_parts) >= 3:
                        vehicle_id = topic_parts[1]
                        message_type = topic_parts[2]
                        
                        # Xử lý message dựa vào loại
                        if message_type == "location":
                            await self.handle_location_message(vehicle_id, message)
                except Exception as e:
                    logger.error(f"Error processing MQTT message: {str(e)}")
        except asyncio.CancelledError:
            # Task bị hủy, không làm gì
            pass
        except Exception as e:
            logger.error(f"MQTT message loop error: {str(e)}")
            self.is_connected = False
    
    async def handle_location_message(self, vehicle_id: str, message: Message):
        """
        Xử lý message vị trí từ thiết bị GPS
        """
        try:
            # Parse payload
            payload = json.loads(message.payload)
            
            # Log message
            logger.debug(f"Received location from vehicle {vehicle_id}: {payload}")
            
            # Gọi handler nếu có
            if "location" in self.handlers:
                await self.handlers["location"](vehicle_id, payload)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in location message from vehicle {vehicle_id}")
        except Exception as e:
            logger.error(f"Error handling location message: {str(e)}")
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Đăng ký handler cho loại message
        """
        self.handlers[message_type] = handler


# Singleton instance
mqtt_client = MQTTClient()
