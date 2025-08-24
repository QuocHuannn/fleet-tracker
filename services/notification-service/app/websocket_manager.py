"""WebSocket Manager for Real-time Notifications"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from .database import SessionLocal
from .models import WebSocketConnection, Alert
from .config import settings

logger = logging.getLogger(__name__)

class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # subscribe, unsubscribe, ping, alert, location_update
    data: Dict[str, Any] = {}
    timestamp: datetime = datetime.utcnow()
    message_id: str = ""
    
    def __init__(self, **data):
        if not data.get('message_id'):
            data['message_id'] = str(uuid.uuid4())
        super().__init__(**data)

class ConnectionInfo(BaseModel):
    """WebSocket connection information"""
    user_id: str
    connection_id: str
    websocket: WebSocket
    subscriptions: Set[str] = set()
    last_activity: datetime = datetime.utcnow()
    client_info: Dict[str, Any] = {}

class WebSocketManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Active connections: {connection_id: ConnectionInfo}
        self.connections: Dict[str, ConnectionInfo] = {}
        
        # User connections: {user_id: Set[connection_id]}
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Subscription groups: {subscription_type: Set[connection_id]}
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # Message queue for offline users
        self.message_queue: Dict[str, List[WebSocketMessage]] = {}
        
        self.cleanup_task = None
    
    async def connect(self, websocket: WebSocket, user_id: str, client_info: Dict = None) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        connection_info = ConnectionInfo(
            user_id=user_id,
            connection_id=connection_id,
            websocket=websocket,
            client_info=client_info or {}
        )
        
        # Store connection
        self.connections[connection_id] = connection_info
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Store in database
        await self._store_connection_db(connection_info)
        
        # Send welcome message
        welcome_msg = WebSocketMessage(
            type="connection_established",
            data={
                "connection_id": connection_id,
                "user_id": user_id,
                "server_time": datetime.utcnow().isoformat()
            }
        )
        await self._send_to_connection(connection_id, welcome_msg)
        
        # Send queued messages
        await self._send_queued_messages(user_id, connection_id)
        
        logger.info(f"🔗 WebSocket connected: {user_id} ({connection_id})")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        user_id = connection_info.user_id
        
        # Remove from subscriptions
        for subscription_type in list(connection_info.subscriptions):
            await self._unsubscribe_connection(connection_id, subscription_type)
        
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove connection
        del self.connections[connection_id]
        
        # Update database
        await self._remove_connection_db(connection_id)
        
        logger.info(f"❌ WebSocket disconnected: {user_id} ({connection_id})")
    
    async def handle_message(self, connection_id: str, message: dict):
        """Handle incoming WebSocket message"""
        if connection_id not in self.connections:
            return
        
        try:
            ws_message = WebSocketMessage(**message)
            connection_info = self.connections[connection_id]
            connection_info.last_activity = datetime.utcnow()
            
            logger.debug(f"📨 Received message from {connection_info.user_id}: {ws_message.type}")
            
            # Handle different message types
            if ws_message.type == "subscribe":
                await self._handle_subscribe(connection_id, ws_message)
            elif ws_message.type == "unsubscribe":
                await self._handle_unsubscribe(connection_id, ws_message)
            elif ws_message.type == "ping":
                await self._handle_ping(connection_id, ws_message)
            elif ws_message.type == "get_alerts":
                await self._handle_get_alerts(connection_id, ws_message)
            else:
                logger.warning(f"Unknown message type: {ws_message.type}")
        
        except ValidationError as e:
            logger.error(f"Invalid WebSocket message format: {str(e)}")
            await self._send_error(connection_id, "Invalid message format")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self._send_error(connection_id, "Internal server error")
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert to subscribed users"""
        alert_message = WebSocketMessage(
            type="alert",
            data=alert_data
        )
        
        # Send to all users subscribed to alerts
        subscription_key = "alerts"
        if subscription_key in self.subscriptions:
            for connection_id in list(self.subscriptions[subscription_key]):
                await self._send_to_connection(connection_id, alert_message)
        
        # Send to users subscribed to specific vehicle
        vehicle_id = alert_data.get('vehicle_id')
        if vehicle_id:
            vehicle_subscription = f"vehicle_{vehicle_id}"
            if vehicle_subscription in self.subscriptions:
                for connection_id in list(self.subscriptions[vehicle_subscription]):
                    await self._send_to_connection(connection_id, alert_message)
    
    async def broadcast_location_update(self, location_data: Dict[str, Any]):
        """Broadcast location update to subscribed users"""
        location_message = WebSocketMessage(
            type="location_update",
            data=location_data
        )
        
        vehicle_id = location_data.get('vehicle_id')
        if not vehicle_id:
            return
        
        # Send to users subscribed to this vehicle
        subscription_key = f"vehicle_{vehicle_id}"
        if subscription_key in self.subscriptions:
            for connection_id in list(self.subscriptions[subscription_key]):
                await self._send_to_connection(connection_id, location_message)
        
        # Send to users subscribed to all vehicles
        all_vehicles_key = "all_vehicles"
        if all_vehicles_key in self.subscriptions:
            for connection_id in list(self.subscriptions[all_vehicles_key]):
                await self._send_to_connection(connection_id, location_message)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to specific user (all their connections)"""
        if user_id not in self.user_connections:
            # Queue message for offline user
            if user_id not in self.message_queue:
                self.message_queue[user_id] = []
            self.message_queue[user_id].append(message)
            return
        
        # Send to all user's connections
        for connection_id in list(self.user_connections[user_id]):
            await self._send_to_connection(connection_id, message)
    
    async def _handle_subscribe(self, connection_id: str, message: WebSocketMessage):
        """Handle subscription request"""
        subscription_type = message.data.get('subscription_type')
        
        if not subscription_type:
            await self._send_error(connection_id, "Missing subscription_type")
            return
        
        # Add to subscription group
        if subscription_type not in self.subscriptions:
            self.subscriptions[subscription_type] = set()
        self.subscriptions[subscription_type].add(connection_id)
        
        # Add to connection subscriptions
        connection_info = self.connections[connection_id]
        connection_info.subscriptions.add(subscription_type)
        
        # Update database
        await self._update_connection_subscriptions_db(connection_id, list(connection_info.subscriptions))
        
        # Send confirmation
        response = WebSocketMessage(
            type="subscription_confirmed",
            data={
                "subscription_type": subscription_type,
                "message": f"Subscribed to {subscription_type}"
            }
        )
        await self._send_to_connection(connection_id, response)
        
        logger.info(f"📋 User subscribed to {subscription_type} ({connection_id})")
    
    async def _handle_unsubscribe(self, connection_id: str, message: WebSocketMessage):
        """Handle unsubscription request"""
        subscription_type = message.data.get('subscription_type')
        
        if subscription_type:
            await self._unsubscribe_connection(connection_id, subscription_type)
        
        response = WebSocketMessage(
            type="unsubscription_confirmed",
            data={
                "subscription_type": subscription_type,
                "message": f"Unsubscribed from {subscription_type}"
            }
        )
        await self._send_to_connection(connection_id, response)
    
    async def _handle_ping(self, connection_id: str, message: WebSocketMessage):
        """Handle ping message"""
        pong = WebSocketMessage(
            type="pong",
            data={
                "server_time": datetime.utcnow().isoformat(),
                "original_message_id": message.message_id
            }
        )
        await self._send_to_connection(connection_id, pong)
    
    async def _handle_get_alerts(self, connection_id: str, message: WebSocketMessage):
        """Handle get alerts request"""
        connection_info = self.connections[connection_id]
        user_id = connection_info.user_id
        
        # Get recent alerts from database
        db = SessionLocal()
        try:
            alerts = db.query(Alert).filter(
                Alert.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).order_by(Alert.created_at.desc()).limit(50).all()
            
            alerts_data = [
                {
                    "id": str(alert.id),
                    "vehicle_id": str(alert.vehicle_id),
                    "type": alert.type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ]
            
            response = WebSocketMessage(
                type="alerts_list",
                data={"alerts": alerts_data}
            )
            await self._send_to_connection(connection_id, response)
            
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            await self._send_error(connection_id, "Failed to get alerts")
        finally:
            db.close()
    
    async def _send_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        try:
            await connection_info.websocket.send_text(message.json())
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {str(e)}")
            # Remove broken connection
            await self.disconnect(connection_id)
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to connection"""
        error_msg = WebSocketMessage(
            type="error",
            data={"message": error_message}
        )
        await self._send_to_connection(connection_id, error_msg)
    
    async def _unsubscribe_connection(self, connection_id: str, subscription_type: str):
        """Remove connection from subscription"""
        if subscription_type in self.subscriptions:
            self.subscriptions[subscription_type].discard(connection_id)
            if not self.subscriptions[subscription_type]:
                del self.subscriptions[subscription_type]
        
        if connection_id in self.connections:
            self.connections[connection_id].subscriptions.discard(subscription_type)
    
    async def _send_queued_messages(self, user_id: str, connection_id: str):
        """Send queued messages to newly connected user"""
        if user_id not in self.message_queue:
            return
        
        messages = self.message_queue[user_id]
        for message in messages[-10:]:  # Send last 10 messages
            await self._send_to_connection(connection_id, message)
        
        # Clear queue
        del self.message_queue[user_id]
    
    async def _store_connection_db(self, connection_info: ConnectionInfo):
        """Store connection in database"""
        db = SessionLocal()
        try:
            db_connection = WebSocketConnection(
                user_id=uuid.UUID(connection_info.user_id),
                connection_id=connection_info.connection_id,
                client_info=connection_info.client_info
            )
            db.add(db_connection)
            db.commit()
        except Exception as e:
            logger.error(f"Error storing connection in DB: {str(e)}")
        finally:
            db.close()
    
    async def _remove_connection_db(self, connection_id: str):
        """Remove connection from database"""
        db = SessionLocal()
        try:
            db.query(WebSocketConnection).filter(
                WebSocketConnection.connection_id == connection_id
            ).delete()
            db.commit()
        except Exception as e:
            logger.error(f"Error removing connection from DB: {str(e)}")
        finally:
            db.close()
    
    async def _update_connection_subscriptions_db(self, connection_id: str, subscriptions: List[str]):
        """Update connection subscriptions in database"""
        # TODO: Update subscriptions in database if needed
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "total_connections": len(self.connections),
            "total_users": len(self.user_connections),
            "subscriptions": {k: len(v) for k, v in self.subscriptions.items()},
            "queued_messages": sum(len(msgs) for msgs in self.message_queue.values())
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
