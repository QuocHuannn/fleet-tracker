"""Authentication utilities for Notification Service"""
import httpx
import logging
from typing import Optional, Dict

from .config import settings

logger = logging.getLogger(__name__)

async def verify_websocket_token(token: Optional[str]) -> Optional[Dict]:
    """Verify JWT token for WebSocket connections"""
    if not token:
        return None
    
    try:
        # Call auth service to validate token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://auth-service:8001/auth/validate-token",
                json={"token": token},
                timeout=5.0
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if token_data.get('valid'):
                    return {
                        'user_id': token_data.get('user_id'),
                        'role': token_data.get('role'),
                        'email': token_data.get('email')
                    }
            
            logger.warning(f"Token validation failed: {response.status_code}")
            return None
            
    except httpx.TimeoutException:
        logger.error("Auth service timeout during token validation")
        return None
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return None
