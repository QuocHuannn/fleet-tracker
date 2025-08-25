# Auth Service - Main Application
# Handles user authentication và authorization

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import logging

from .config import settings
from .database import init_db, close_db
from .routes import auth, users, health
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fleet Tracker Auth Service",
    description="Authentication & Authorization microservice",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    contact={
        "name": "Trương Quốc Huân",
        "email": "truonghuan0709@gmail.com"
    }
)

# Instrument the app for Prometheus
Instrumentator().instrument(app).expose(app)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
async def root():
    """Auth service root endpoint"""
    return {
        "service": "Fleet Tracker Auth Service",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "login": "/auth/login",
            "token_validation": "/auth/validate-token",
            "users": "/users"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize service resources"""
    logger.info("🔐 Auth Service starting up...")
    await init_db()
    logger.info("✅ Auth Service ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup service resources"""
    logger.info("🔄 Auth Service shutting down...")
    await close_db()
    logger.info("✅ Auth Service shutdown completed")
