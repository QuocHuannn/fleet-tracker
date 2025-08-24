"""Common authentication utilities for Fleet Tracker services"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from .exceptions import AuthenticationError, AuthorizationError

class UserClaims(BaseModel):
    """User claims structure for JWT tokens"""
    user_id: str
    email: str
    role: str
    permissions: List[str] = []
    exp: Optional[int] = None
    iat: Optional[int] = None

class TokenValidator:
    """JWT token validation utility"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def decode_token(self, token: str) -> UserClaims:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return UserClaims(**payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def create_token(self, user_claims: UserClaims, expires_in_hours: int = 24) -> str:
        """Create JWT token from user claims"""
        now = datetime.utcnow()
        claims = user_claims.dict()
        claims.update({
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=expires_in_hours)).timestamp())
        })
        
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

class PermissionChecker:
    """Permission checking utility"""
    
    ROLE_PERMISSIONS = {
        'admin': [
            'vehicle:create', 'vehicle:read', 'vehicle:update', 'vehicle:delete',
            'location:read', 'alert:read', 'alert:resolve', 'user:manage'
        ],
        'manager': [
            'vehicle:create', 'vehicle:read', 'vehicle:update',
            'location:read', 'alert:read', 'alert:resolve'
        ],
        'operator': [
            'vehicle:read', 'location:read', 'alert:read'
        ],
        'viewer': [
            'vehicle:read', 'location:read'
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_permission: str, user_permissions: List[str] = None) -> bool:
        """Check if user has required permission"""
        # Check explicit permissions first
        if user_permissions and required_permission in user_permissions:
            return True
        
        # Check role-based permissions
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role.lower(), [])
        return required_permission in role_permissions
    
    @classmethod
    def require_permission(cls, user_claims: UserClaims, required_permission: str):
        """Raise exception if user doesn't have required permission"""
        if not cls.has_permission(user_claims.role, required_permission, user_claims.permissions):
            raise AuthorizationError(
                f"Insufficient permissions. Required: {required_permission}",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "user_role": user_claims.role,
                    "required_permission": required_permission
                }
            )

def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """Extract bearer token from Authorization header"""
    if not authorization_header:
        return None
    
    if not authorization_header.startswith('Bearer '):
        return None
    
    return authorization_header[7:]  # Remove 'Bearer ' prefix
