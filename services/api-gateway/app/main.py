# API Gateway - Main Entry Point
# Routes requests to appropriate microservices

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
from typing import Dict, Any
import logging

from .config import settings
from .middleware import RateLimitMiddleware, LoggingMiddleware
from .auth import verify_token
from .routes import health, proxy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fleet Tracker API Gateway",
    description="Central API Gateway for Fleet Tracker microservices",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    contact={
        "name": "Trương Quốc Huân",
        "email": "truonghuan0709@gmail.com",
        "url": "https://github.com/QuocHuannn"
    }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(proxy.router, prefix="/api/v1", tags=["Proxy"])

@app.get("/")
async def root():
    """API Gateway root endpoint"""
    return {
        "service": "Fleet Tracker API Gateway",
        "version": "1.0.0",
        "status": "healthy",
        "services": {
            "auth_service": settings.AUTH_SERVICE_URL,
            "vehicle_service": settings.VEHICLE_SERVICE_URL,
            "location_service": settings.LOCATION_SERVICE_URL,
            "notification_service": settings.NOTIFICATION_SERVICE_URL
        }
    }

@app.exception_handler(httpx.RequestError)
async def request_error_handler(request: Request, exc: httpx.RequestError):
    """Handle service communication errors"""
    logger.error(f"Service request failed: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "Upstream service is temporarily unavailable",
            "retry_after": 30
        }
    )

@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """Handle HTTP errors from services"""
    return JSONResponse(
        status_code=exc.response.status_code,
        content={
            "error": "upstream_error",
            "message": f"Service returned {exc.response.status_code}",
            "details": exc.response.text if exc.response.text else None
        }
    )

@app.on_event("startup")
async def startup_event():
    """Initialize gateway resources"""
    logger.info("🚀 API Gateway starting up...")
    
    # Health check tất cả services
    services = {
        "auth": settings.AUTH_SERVICE_URL,
        "vehicle": settings.VEHICLE_SERVICE_URL,
        "location": settings.LOCATION_SERVICE_URL,
        "notification": settings.NOTIFICATION_SERVICE_URL
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} service is healthy")
                else:
                    logger.warning(f"⚠️  {service_name} service returned {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {service_name} service is unreachable: {e}")

    logger.info("🎯 API Gateway ready to serve requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup gateway resources"""
    logger.info("🔄 API Gateway shutting down...")
    logger.info("✅ API Gateway shutdown completed")
