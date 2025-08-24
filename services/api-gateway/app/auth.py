"""Authentication utilities for API Gateway"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import logging
from typing import Optional, Dict

from .config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Verify JWT token with auth service"""
    if not credentials:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/auth/validate-token",
                json={"token": credentials.credentials},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return credentials.credentials
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

async def get_current_user(token: Optional[str] = Depends(verify_token)) -> Dict:
    """Get current user from token"""
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/users/profile",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")
    except Exception as e:
        logger.error(f"User lookup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")