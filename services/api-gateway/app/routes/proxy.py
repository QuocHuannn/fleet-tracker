"""Proxy routes for API Gateway"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
import httpx
import logging
from typing import Optional
import asyncio
import json

from ..config import settings
from ..auth import verify_token, get_current_user
from ..middleware import add_correlation_id

logger = logging.getLogger(__name__)
router = APIRouter()

# HTTP client for service communication
http_client = httpx.AsyncClient(timeout=30.0)

async def proxy_request(
    request: Request,
    target_url: str,
    user_data: Optional[dict] = None
):
    """Proxy request to target service"""
    try:
        # Get request data
        body = await request.body()
        headers = dict(request.headers)
        
        # Remove hop-by-hop headers
        headers_to_remove = ['host', 'content-length', 'connection', 'upgrade']
        for header in headers_to_remove:
            headers.pop(header, None)
        
        # Add user context if authenticated
        if user_data:
            headers['X-User-ID'] = user_data.get('user_id', '')
            headers['X-User-Role'] = user_data.get('role', '')
        
        # Add correlation ID
        correlation_id = getattr(request.state, 'correlation_id', None)
        if correlation_id:
            headers['X-Correlation-ID'] = correlation_id
        
        # Make request to target service
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params)
        )
        
        # Stream response back
        def generate():
            yield response.content
            
        return StreamingResponse(
            generate(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get('content-type')
        )
        
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to {target_url}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except httpx.ConnectError:
        logger.error(f"Connection error to {target_url}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

# Auth Service Proxy
@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    """Proxy to Auth Service"""
    target_url = f"{settings.AUTH_SERVICE_URL}/auth/{path}"
    return await proxy_request(request, target_url)

# Vehicle Service Proxy  
@router.api_route("/vehicles/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def vehicles_proxy(
    request: Request, 
    path: str, 
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Vehicle Service (requires authentication)"""
    target_url = f"{settings.VEHICLE_SERVICE_URL}/vehicles/{path}"
    return await proxy_request(request, target_url, current_user)

@router.api_route("/vehicles", methods=["GET", "POST"])
async def vehicles_root_proxy(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Vehicle Service root (requires authentication)"""
    target_url = f"{settings.VEHICLE_SERVICE_URL}/vehicles"
    return await proxy_request(request, target_url, current_user)

# Location Service Proxy
@router.api_route("/locations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def locations_proxy(
    request: Request, 
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Location Service (requires authentication)"""
    target_url = f"{settings.LOCATION_SERVICE_URL}/locations/{path}"
    return await proxy_request(request, target_url, current_user)

@router.api_route("/geofences/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def geofences_proxy(
    request: Request, 
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Location Service - Geofences (requires authentication)"""
    target_url = f"{settings.LOCATION_SERVICE_URL}/geofences/{path}"
    return await proxy_request(request, target_url, current_user)

# Notification Service Proxy
@router.api_route("/alerts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def alerts_proxy(
    request: Request, 
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Notification Service - Alerts (requires authentication)"""
    target_url = f"{settings.NOTIFICATION_SERVICE_URL}/alerts/{path}"
    return await proxy_request(request, target_url, current_user)

@router.api_route("/alerts", methods=["GET", "POST"])
async def alerts_root_proxy(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Proxy to Notification Service - Alerts root (requires authentication)"""  
    target_url = f"{settings.NOTIFICATION_SERVICE_URL}/alerts"
    return await proxy_request(request, target_url, current_user)

# Health check aggregator
@router.get("/health/services")
async def health_check_all_services():
    """Check health of all services"""
    services = {
        "auth": f"{settings.AUTH_SERVICE_URL}/health",
        "vehicle": f"{settings.VEHICLE_SERVICE_URL}/health", 
        "location": f"{settings.LOCATION_SERVICE_URL}/health",
        "notification": f"{settings.NOTIFICATION_SERVICE_URL}/health"
    }
    
    results = {}
    
    # Check all services concurrently
    async def check_service(name: str, url: str):
        try:
            response = await http_client.get(url, timeout=5.0)
            return name, {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "details": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return name, {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None
            }
    
    # Run health checks concurrently
    tasks = [check_service(name, url) for name, url in services.items()]
    health_results = await asyncio.gather(*tasks)
    
    for name, result in health_results:
        results[name] = result
    
    # Determine overall status
    overall_status = "healthy"
    unhealthy_count = sum(1 for result in results.values() if result["status"] != "healthy")
    
    if unhealthy_count > 0:
        if unhealthy_count == len(services):
            overall_status = "critical"
        else:
            overall_status = "degraded"
    
    return {
        "status": overall_status,
        "services": results,
        "total_services": len(services),
        "healthy_services": len(services) - unhealthy_count,
        "unhealthy_services": unhealthy_count
    }