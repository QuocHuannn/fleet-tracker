# API Gateway Authentication
# JWT token validation và user context

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import httpx
from typing import Dict, Any, Optional
import logging

from .config import settings

security = HTTPBearer()
logger = logging.getLogger(__name__)

async def verify_token(request: Request) -> Dict[str, Any]:
    """Verify JWT token và return user context"""
    
    # Get authorization header
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "Missing authorization header"
            }
        )
    
    # Extract token
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized", 
                "message": "Invalid authorization header format"
            }
        )
    
    try:
        # Validate token with Auth Service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/validate-token",
                json={"token": token}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "unauthorized",
                        "message": "Invalid or expired token"
                    }
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "auth_service_error",
                        "message": "Authentication service unavailable"
                    }
                )
                
    except httpx.RequestError:
        logger.error("Auth service unavailable")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "auth_service_unavailable",
                "message": "Authentication service is temporarily unavailable"
            }
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Internal authentication error"
            }
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current user"""
    
    # Create fake request object to use verify_token
    class FakeRequest:
        def __init__(self, token: str):
            self.headers = {"authorization": f"Bearer {token}"}
    
    fake_request = FakeRequest(credentials.credentials)
    return await verify_token(fake_request)

def require_roles(allowed_roles: list):
    """Decorator to require specific roles"""
    
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "message": f"Required role: {allowed_roles}",
                    "user_role": user_role
                }
            )
        return user
    
    return role_checker

def require_permissions(required_permissions: list):
    """Decorator to require specific permissions"""
    
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get("permissions", [])
        
        missing_permissions = [
            perm for perm in required_permissions
            if perm not in user_permissions
        ]
        
        if missing_permissions:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": "Missing required permissions",
                    "required": required_permissions,
                    "missing": missing_permissions
                }
            )
        return user
    
    return permission_checker
