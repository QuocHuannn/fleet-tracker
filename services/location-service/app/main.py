from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .database import init_db, close_db, get_db
from .config import settings
from .routes import location_router, geofence_router, health
from .mqtt_handler import mqtt_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🌍 Location Service starting up...")
    await init_db()
    
    # Connect to MQTT broker
    try:
        await mqtt_handler.connect()
        logger.info("✅ MQTT handler connected")
    except Exception as e:
        logger.error(f"❌ MQTT connection failed: {str(e)}")
        # Continue without MQTT for development
    
    logger.info("✅ Location Service ready")
    yield
    
    # Shutdown
    logger.info("🔄 Location Service shutting down...")
    await mqtt_handler.disconnect()
    await close_db()
    logger.info("✅ Location Service shutdown completed")

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

# Error handlers will be added later

# Đăng ký routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(location_router.router, prefix="/locations", tags=["Locations"])
app.include_router(geofence_router.router, prefix="/geofences", tags=["Geofences"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Fleet Tracker Location Service",
        "version": "1.0.0",
        "status": "healthy",
        "mqtt_connected": mqtt_handler.is_connected(),
        "endpoints": {
            "health": "/health",
            "locations": "/locations/*",
            "geofences": "/geofences/*",
            "docs": "/docs"
        }
    }
