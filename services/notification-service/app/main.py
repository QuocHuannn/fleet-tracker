# Notification Service - Main Application

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from .database import init_db, close_db
from .config import settings
from .routes import health, alerts, websocket

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fleet Tracker Notification Service",
    description="Notification & Alert Management microservice",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    contact={
        "name": "Trương Quốc Huân",
        "email": "truonghuan0709@gmail.com"
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"]) 
app.include_router(websocket.router, prefix="", tags=["WebSocket"])

@app.get("/")
async def root():
    """Notification service root endpoint"""
    return {
        "service": "Fleet Tracker Notification Service",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "alerts": "/alerts",
            "websocket": "/ws",
            "websocket_stats": "/ws/stats"
        },
        "websocket": {
            "url": "ws://localhost:8004/ws",
            "authentication": "token_query_parameter"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize service resources"""
    logger.info("📢 Notification Service starting up...")
    await init_db()
    logger.info("✅ Notification Service ready")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup service resources"""
    logger.info("🔄 Notification Service shutting down...")
    await close_db()
    logger.info("✅ Notification Service shutdown completed")