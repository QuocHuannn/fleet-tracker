from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
from typing import Dict, Any

from app.database import init_db, close_db, get_db
from app.config import settings
from app.routes import vehicle_router, device_router
from app.models import VehicleNotFoundError, DuplicateLicensePlateError
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

# Khởi tạo FastAPI app
app = FastAPI(
    title="Vehicle Service",
    description="Quản lý thông tin xe và thiết bị GPS",
    version="0.1.0",
    lifespan=lifespan
)

# Instrument the app for Prometheus
Instrumentator().instrument(app).expose(app)

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
@app.exception_handler(VehicleNotFoundError)
async def vehicle_not_found_handler(request: Request, exc: VehicleNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "vehicle_not_found",
            "message": f"Vehicle with ID {exc.vehicle_id} not found",
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(DuplicateLicensePlateError)
async def duplicate_license_plate_handler(request: Request, exc: DuplicateLicensePlateError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "duplicate_license_plate",
            "message": f"Vehicle with license plate {exc.license_plate} already exists",
            "request_id": request.state.request_id
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "vehicle-service",
        "version": app.version
    }

# Đăng ký routers
app.include_router(vehicle_router.router, prefix="/api/v1", tags=["Vehicles"])
app.include_router(device_router.router, prefix="/api/v1", tags=["Devices"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Vehicle Service",
        "version": app.version,
        "docs_url": "/docs"
    }
