# API Gateway - Main Application

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from .config import settings
from .routes import health, proxy
from .middleware import add_correlation_id
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fleet Tracker API Gateway",
    description="API Gateway for Fleet Tracker microservices",
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

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    
    # Add correlation ID
    correlation_id = add_correlation_id(request)
    
    response = await call_next(request)
    
    # Add response headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = str(time.time() - start_time)
    response.headers["X-Gateway"] = "fleet-tracker-gateway"
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - "
        f"{time.time() - start_time:.3f}s - {correlation_id}"
    )
    
    return response

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(proxy.router, prefix="", tags=["Proxy"])

@app.get("/")
async def root():
    """API Gateway root endpoint"""
    return {
        "service": "Fleet Tracker API Gateway",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "vehicles": "/vehicles/*",
            "locations": "/locations/*",
            "geofences": "/geofences/*",
            "alerts": "/alerts/*",
            "services_health": "/health/services"
        },
        "services": {
            "auth": settings.AUTH_SERVICE_URL,
            "vehicle": settings.VEHICLE_SERVICE_URL,
            "location": settings.LOCATION_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(f"Unhandled exception: {str(exc)} - Correlation ID: {correlation_id}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "correlation_id": correlation_id
        }
    )

@app.on_event("startup")
async def startup_event():
    """Initialize gateway resources"""
    logger.info("🚀 API Gateway starting up...")
    logger.info("✅ API Gateway ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup gateway resources"""
    logger.info("🔄 API Gateway shutting down...")
    logger.info("✅ API Gateway shutdown completed")