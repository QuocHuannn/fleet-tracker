"""JWT Token Handler for Auth Service"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
import logging

from .config import settings
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class JWTHandler:
    """Handles JWT token creation and validation"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
    
    def create_access_token(self, user: Any) -> str:
        """Create access token for user"""
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'role': user.role,
            'firebase_uid': user.firebase_uid,
            'token_type': 'access',
            'iat': int(now.timestamp()),
            'exp': int(expires_at.timestamp())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: Any) -> str:
        """Create refresh token for user"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            'user_id': str(user.id),
            'token_type': 'refresh',
            'iat': int(now.timestamp()),
            'exp': int(expires_at.timestamp())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def hash_token(self, token: str) -> str:
        """Create hash of token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token payload without verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            return None
