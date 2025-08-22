# API Gateway Health Check Routes
# System health monitoring

from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from typing import Dict, Any
import time

from ..config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": int(time.time()),
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including all services"""
    
    services = {
        "auth_service": settings.AUTH_SERVICE_URL,
        "vehicle_service": settings.VEHICLE_SERVICE_URL,
        "location_service": settings.LOCATION_SERVICE_URL,
        "notification_service": settings.NOTIFICATION_SERVICE_URL
    }
    
    health_status = {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": int(time.time()),
        "services": {}
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
        # Check each service health
        for service_name, service_url in services.items():
            try:
                start_time = time.time()
                response = await client.get(f"{service_url}/health")
                response_time = time.time() - start_time
                
                health_status["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": round(response_time * 1000, 2),  # ms
                    "status_code": response.status_code
                }
                
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unreachable",
                    "error": str(e),
                    "response_time": None
                }
    
    # Determine overall status
    unhealthy_services = [
        name for name, status in health_status["services"].items()
        if status["status"] != "healthy"
    ]
    
    if unhealthy_services:
        health_status["status"] = "degraded"
        health_status["unhealthy_services"] = unhealthy_services
    
    return health_status

@router.get("/services")
async def services_info():
    """Get information about all connected services"""
    return {
        "api_gateway": {
            "version": "1.0.0",
            "status": "active"
        },
        "services": {
            "auth_service": {
                "url": settings.AUTH_SERVICE_URL,
                "description": "Authentication & Authorization"
            },
            "vehicle_service": {
                "url": settings.VEHICLE_SERVICE_URL,
                "description": "Vehicle Management"
            },
            "location_service": {
                "url": settings.LOCATION_SERVICE_URL,
                "description": "GPS & Location Processing"
            },
            "notification_service": {
                "url": settings.NOTIFICATION_SERVICE_URL,
                "description": "Alerts & Notifications"
            }
        }
    }
