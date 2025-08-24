"""Health check endpoints for API Gateway"""
from fastapi import APIRouter
import datetime

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check():
    """API Gateway health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": "api-gateway",
        "version": "1.0.0",
        "message": "API Gateway is running"
    }