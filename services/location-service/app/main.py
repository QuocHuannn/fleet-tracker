from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
from typing import Dict, Any

from app.database import init_db, close_db, get_db
from app.config import settings
from app.routes import location_router, geofence_router
from app.mqtt import mqtt_client
from app.models import InvalidCoordinatesError, GeofenceNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await mqtt_client.connect()
    yield
    # Shutdown
    await mqtt_client.disconnect()
    await close_db()

# Khởi tạo FastAPI app
app = FastAPI(
    title="Location Service",
    description="Xử lý dữ liệu vị trí và địa lý",
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
@app.exception_handler(InvalidCoordinatesError)
async def invalid_coordinates_handler(request: Request, exc: InvalidCoordinatesError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_coordinates",
            "message": "Invalid GPS coordinates provided",
            "details": exc.details,
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(GeofenceNotFoundError)
async def geofence_not_found_handler(request: Request, exc: GeofenceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "geofence_not_found",
            "message": f"Geofence with ID {exc.geofence_id} not found",
            "request_id": request.state.request_id
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    health_status = {
        "status": "healthy",
        "service": "location-service",
        "version": app.version,
        "mqtt": "connected" if mqtt_client.is_connected else "disconnected"
    }
    
    # Nếu MQTT không kết nối được, trả về trạng thái degraded
    if not mqtt_client.is_connected:
        health_status["status"] = "degraded"
        return JSONResponse(content=health_status, status_code=503)
    
    return health_status

# Đăng ký routers
app.include_router(location_router.router, prefix="/api/v1", tags=["Locations"])
app.include_router(geofence_router.router, prefix="/api/v1", tags=["Geofences"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Location Service",
        "version": app.version,
        "docs_url": "/docs"
    }
