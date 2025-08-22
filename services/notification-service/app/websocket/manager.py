from fastapi import WebSocket
from typing import Dict, List, Set, Any
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Quản lý WebSocket connections và subscriptions
    """
    def __init__(self):
        # Lưu trữ active connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Lưu trữ subscriptions
        self.vehicle_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of vehicle_ids
        self.alert_subscribers: Set[str] = set()  # set of client_ids
        
        # Số lượng kết nối
        self.active_connections_count = 0
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """
        Kết nối WebSocket client
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.active_connections_count += 1
        logger.info(f"WebSocket client {client_id} connected. Total connections: {self.active_connections_count}")
    
    def disconnect(self, client_id: str):
        """
        Ngắt kết nối WebSocket client
        """
        if client_id in self.active_connections:
            self.active_connections.pop(client_id)
            self.active_connections_count -= 1
            
            # Xóa subscriptions
            if client_id in self.vehicle_subscriptions:
                self.vehicle_subscriptions.pop(client_id)
            if client_id in self.alert_subscribers:
                self.alert_subscribers.remove(client_id)
            
            logger.info(f"WebSocket client {client_id} disconnected. Total connections: {self.active_connections_count}")
    
    def subscribe_to_vehicles(self, client_id: str, vehicle_ids: List[str]):
        """
        Subscribe client vào updates của các xe
        """
        if client_id not in self.vehicle_subscriptions:
            self.vehicle_subscriptions[client_id] = set()
        
        self.vehicle_subscriptions[client_id].update(vehicle_ids)
        logger.debug(f"Client {client_id} subscribed to vehicles: {vehicle_ids}")
    
    def subscribe_to_alerts(self, client_id: str):
        """
        Subscribe client vào tất cả alerts
        """
        self.alert_subscribers.add(client_id)
        logger.debug(f"Client {client_id} subscribed to all alerts")
    
    async def broadcast_vehicle_update(self, vehicle_id: str, data: Dict[str, Any]):
        """
        Broadcast update về xe đến các clients đã subscribe
        """
        # Tìm các clients đã subscribe vào xe này
        subscribed_clients = [
            client_id for client_id, vehicle_ids in self.vehicle_subscriptions.items()
            if vehicle_id in vehicle_ids
        ]
        
        # Broadcast message
        message = {
            "type": "vehicle_update",
            "vehicle_id": vehicle_id,
            "data": data
        }
        
        await self._broadcast_to_clients(subscribed_clients, message)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """
        Broadcast alert đến tất cả clients đã subscribe vào alerts
        """
        message = {
            "type": "alert",
            "data": alert_data
        }
        
        # Broadcast đến tất cả alert subscribers
        await self._broadcast_to_clients(list(self.alert_subscribers), message)
        
        # Nếu alert liên quan đến xe cụ thể, broadcast đến các subscribers của xe đó
        if "vehicle_id" in alert_data:
            vehicle_id = alert_data["vehicle_id"]
            vehicle_subscribers = [
                client_id for client_id, vehicle_ids in self.vehicle_subscriptions.items()
                if vehicle_id in vehicle_ids
            ]
            
            # Loại bỏ các clients đã nhận alert qua alert subscription
            vehicle_subscribers = [c for c in vehicle_subscribers if c not in self.alert_subscribers]
            
            if vehicle_subscribers:
                await self._broadcast_to_clients(vehicle_subscribers, message)
    
    async def _broadcast_to_clients(self, client_ids: List[str], message: Dict[str, Any]):
        """
        Gửi message đến danh sách clients
        """
        if not client_ids:
            return
        
        # Chuyển đổi message thành JSON
        json_message = json.dumps(message)
        
        # Gửi message đến từng client
        for client_id in client_ids:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_text(json_message)
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {str(e)}")
                    # Ngắt kết nối client nếu gửi thất bại
                    self.disconnect(client_id)


# Singleton instance
websocket_manager = WebSocketManager()
