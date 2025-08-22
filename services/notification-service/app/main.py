from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
from typing import Dict, Any

from app.database import init_db, close_db, get_db
from app.config import settings
from app.routes import alert_router, notification_rule_router
from app.websocket import websocket_manager
from app.models import AlertNotFoundError, NotificationRuleNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

# Khởi tạo FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Xử lý thông báo và cảnh báo",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    start_time = time.time()
    
    # Tạo request ID nếu chưa có
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    # Thêm request ID và processing time vào response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    
    return response

# Error handlers
@app.exception_handler(AlertNotFoundError)
async def alert_not_found_handler(request: Request, exc: AlertNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "alert_not_found",
            "message": f"Alert with ID {exc.alert_id} not found",
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(NotificationRuleNotFoundError)
async def rule_not_found_handler(request: Request, exc: NotificationRuleNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "notification_rule_not_found",
            "message": f"Notification rule with ID {exc.rule_id} not found",
            "request_id": request.state.request_id
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": app.version,
        "websocket_clients": websocket_manager.active_connections
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Kết nối client
    client_id = str(uuid.uuid4())
    await websocket_manager.connect(client_id, websocket)
    
    try:
        # Xử lý messages từ client
        while True:
            data = await websocket.receive_json()
            
            # Xử lý message dựa vào type
            if data.get("type") == "subscribe":
                # Subscribe vào các topics
                if "vehicle_ids" in data:
                    websocket_manager.subscribe_to_vehicles(client_id, data["vehicle_ids"])
                if data.get("subscribe_to_alerts", False):
                    websocket_manager.subscribe_to_alerts(client_id)
                
                # Gửi xác nhận
                await websocket.send_json({
                    "type": "subscribe_ack",
                    "message": "Subscribed successfully"
                })
    except WebSocketDisconnect:
        # Ngắt kết nối client
        websocket_manager.disconnect(client_id)
    except Exception as e:
        # Xử lý lỗi
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        websocket_manager.disconnect(client_id)

# Đăng ký routers
app.include_router(alert_router.router, prefix="/api/v1", tags=["Alerts"])
app.include_router(notification_rule_router.router, prefix="/api/v1", tags=["Notification Rules"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Notification Service",
        "version": app.version,
        "docs_url": "/docs"
    }
