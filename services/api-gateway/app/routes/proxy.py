# API Gateway Proxy Routes
# Request routing to microservices

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
import httpx
import json
from typing import Any, Dict
import logging

from ..config import settings
from ..auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)

async def proxy_request(
    request: Request,
    target_url: str,
    path: str,
    require_auth: bool = True
) -> Response:
    """Generic request proxying function"""
    
    # Authentication check
    if require_auth:
        try:
            user = await verify_token(request)
        except HTTPException as e:
            raise e
    
    # Prepare headers
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Build full URL
    full_url = f"{target_url}/{path.lstrip('/')}"
    
    # Prepare request data
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=settings.SERVICE_CONNECT_TIMEOUT,
                read=settings.SERVICE_TIMEOUT
            )
        ) as client:
            
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            # Create response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError as e:
        logger.error(f"Service request failed: {full_url} - {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "Service is temporarily unavailable",
                "service": target_url
            }
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Service HTTP error: {full_url} - {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "service_error",
                "message": f"Service returned error: {e.response.status_code}"
            }
        )

# Auth Service Routes
@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(request: Request, path: str):
    """Proxy requests to Auth Service"""
    # Auth endpoints don't require pre-authentication
    return await proxy_request(
        request, 
        settings.AUTH_SERVICE_URL, 
        path, 
        require_auth=False
    )

# Vehicle Service Routes  
@router.api_route("/vehicles/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_vehicles(request: Request, path: str):
    """Proxy requests to Vehicle Service"""
    return await proxy_request(request, settings.VEHICLE_SERVICE_URL, f"vehicles/{path}")

@router.api_route("/vehicles", methods=["GET", "POST"])
async def proxy_vehicles_root(request: Request):
    """Proxy root vehicles requests"""
    return await proxy_request(request, settings.VEHICLE_SERVICE_URL, "vehicles")

# Location Service Routes
@router.api_route("/locations/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_locations(request: Request, path: str):
    """Proxy requests to Location Service"""
    return await proxy_request(request, settings.LOCATION_SERVICE_URL, f"locations/{path}")

@router.api_route("/locations", methods=["GET", "POST"])
async def proxy_locations_root(request: Request):
    """Proxy root locations requests"""
    return await proxy_request(request, settings.LOCATION_SERVICE_URL, "locations")

@router.api_route("/geofences/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_geofences(request: Request, path: str):
    """Proxy geofence requests to Location Service"""
    return await proxy_request(request, settings.LOCATION_SERVICE_URL, f"geofences/{path}")

@router.api_route("/geofences", methods=["GET", "POST"])
async def proxy_geofences_root(request: Request):
    """Proxy root geofences requests"""
    return await proxy_request(request, settings.LOCATION_SERVICE_URL, "geofences")

# Notification Service Routes
@router.api_route("/alerts/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_alerts(request: Request, path: str):
    """Proxy requests to Notification Service"""
    return await proxy_request(request, settings.NOTIFICATION_SERVICE_URL, f"alerts/{path}")

@router.api_route("/alerts", methods=["GET", "POST"])
async def proxy_alerts_root(request: Request):
    """Proxy root alerts requests"""
    return await proxy_request(request, settings.NOTIFICATION_SERVICE_URL, "alerts")

@router.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_notifications(request: Request, path: str):
    """Proxy notification requests"""
    return await proxy_request(request, settings.NOTIFICATION_SERVICE_URL, f"notifications/{path}")

# Aggregated Endpoints (combine data from multiple services)
@router.get("/dashboard/summary")
async def dashboard_summary(request: Request, user: Dict[Any, Any] = Depends(verify_token)):
    """Get dashboard summary from multiple services"""
    
    async with httpx.AsyncClient() as client:
        try:
            # Get data from multiple services concurrently
            auth_header = {"Authorization": request.headers.get("authorization")}
            
            tasks = [
                client.get(f"{settings.VEHICLE_SERVICE_URL}/vehicles/summary", headers=auth_header),
                client.get(f"{settings.LOCATION_SERVICE_URL}/locations/summary", headers=auth_header),
                client.get(f"{settings.NOTIFICATION_SERVICE_URL}/alerts/summary", headers=auth_header)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            summary = {
                "user": user,
                "vehicles": {},
                "locations": {},
                "alerts": {},
                "timestamp": int(time.time())
            }
            
            # Parse responses
            if not isinstance(responses[0], Exception) and responses[0].status_code == 200:
                summary["vehicles"] = responses[0].json()
            
            if not isinstance(responses[1], Exception) and responses[1].status_code == 200:
                summary["locations"] = responses[1].json()
                
            if not isinstance(responses[2], Exception) and responses[2].status_code == 200:
                summary["alerts"] = responses[2].json()
            
            return summary
            
        except Exception as e:
            logger.error(f"Dashboard summary error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch dashboard summary"
            )
