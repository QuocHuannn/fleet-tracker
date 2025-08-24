"""WebSocket routes for real-time notifications"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import json
import logging

from ..websocket_manager import websocket_manager
from ..auth_utils import verify_websocket_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    client_info: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time notifications"""
    
    # Verify authentication token
    user_data = await verify_websocket_token(token)
    if not user_data:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    user_id = user_data['user_id']
    
    # Parse client info
    client_info_dict = {}
    if client_info:
        try:
            client_info_dict = json.loads(client_info)
        except json.JSONDecodeError:
            logger.warning(f"Invalid client_info format: {client_info}")
    
    connection_id = None
    
    try:
        # Connect to WebSocket manager
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            user_id=user_id,
            client_info=client_info_dict
        )
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message
                await websocket_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {user_id}")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {user_id}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": "Internal server error"
                }))
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        # Clean up connection
        if connection_id:
            await websocket_manager.disconnect(connection_id)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_stats()

@router.post("/ws/broadcast")
async def broadcast_message(message_data: dict):
    """Broadcast message to all connected clients (admin only)"""
    # TODO: Add admin authentication
    
    if message_data.get('type') == 'alert':
        await websocket_manager.broadcast_alert(message_data.get('data', {}))
    elif message_data.get('type') == 'location_update':
        await websocket_manager.broadcast_location_update(message_data.get('data', {}))
    else:
        raise HTTPException(status_code=400, detail="Invalid message type")
    
    return {"message": "Broadcast sent successfully"}
