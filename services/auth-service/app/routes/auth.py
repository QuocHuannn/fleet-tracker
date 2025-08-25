"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime
import uuid
import logging

from ..database import get_db
from ..firebase_auth import firebase_auth_manager
from ..models import User, UserSession
from ..jwt_handler import JWTHandler
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
jwt_handler = JWTHandler()

class LoginRequest(BaseModel):
    firebase_token: str
    device_info: Optional[dict] = None
    
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    role: str
    display_name: Optional[str]
    expires_at: datetime.datetime

class TokenValidationRequest(BaseModel):
    token: str

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Login with Firebase token"""
    try:
        # Verify Firebase token
        firebase_user = await firebase_auth_manager.verify_id_token(request.firebase_token)
        
        # Get or create user in database
        user = db.query(User).filter(User.firebase_uid == firebase_user['uid']).first()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=firebase_user['uid'],
                email=firebase_user['email'],
                display_name=firebase_user['name'],
                role='viewer',  # Default role
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.email}")
        else:
            # Update user info
            user.display_name = firebase_user['name']
            user.last_login = datetime.datetime.utcnow()
            db.commit()
        
        # Generate JWT tokens
        access_token = jwt_handler.create_access_token(user)
        refresh_token = jwt_handler.create_refresh_token(user)
        
        # Store session
        session = UserSession(
            user_id=user.id,
            token_hash=jwt_handler.hash_token(refresh_token),
            device_info=request.device_info or {},
            ip_address=req.client.host if req.client else None,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(session)
        db.commit()
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            email=user.email,
            role=user.role,
            display_name=user.display_name,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/dev-login", response_model=LoginResponse)
async def dev_login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Development login endpoint - bypass Firebase for testing"""
    try:
        # For development, accept any token and create mock user
        mock_firebase_user = {
            'uid': 'dev_user_123',
            'email': 'admin@fleettracker.com',
            'name': 'Admin User'
        }
        
        # Get or create user in database
        user = db.query(User).filter(User.firebase_uid == mock_firebase_user['uid']).first()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=mock_firebase_user['uid'],
                email=mock_firebase_user['email'],
                display_name=mock_firebase_user['name'],
                role='admin',  # Admin role for development
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created development user: {user.email}")
        else:
            # Update user info
            user.display_name = mock_firebase_user['name']
            user.last_login = datetime.datetime.utcnow()
            db.commit()
        
        # Generate JWT tokens
        access_token = jwt_handler.create_access_token(user)
        refresh_token = jwt_handler.create_refresh_token(user)
        
        # Store session
        session = UserSession(
            user_id=user.id,
            token_hash=jwt_handler.hash_token(refresh_token),
            device_info=request.device_info or {},
            ip_address=req.client.host if req.client else None,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(session)
        db.commit()
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            email=user.email,
            role=user.role,
            display_name=user.display_name,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
    except Exception as e:
        logger.error(f"Dev login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Development authentication failed")

@router.post("/simple-login")
async def simple_login():
    """Simple development login - no database required"""
    try:
        # Return mock user data
        return {
            "access_token": "dev_access_token_123",
            "refresh_token": "dev_refresh_token_123",
            "user_id": "dev_user_123",
            "email": "admin@fleettracker.com",
            "role": "admin",
            "display_name": "Admin User",
            "expires_at": "2025-12-31T23:59:59Z"
        }
        
    except Exception as e:
        logger.error(f"Simple login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Simple login failed")

@router.post("/simple-validate")
async def simple_validate(request: TokenValidationRequest):
    """Simple token validation for development"""
    try:
        # For development, accept any token
        if request.token:
            return {
                "valid": True,
                "user": {
                    "id": "dev_user_123",
                    "email": "admin@fleettracker.com",
                    "display_name": "Admin User",
                    "role": "admin"
                }
            }
        else:
            return {"valid": False, "error": "No token provided"}
        
    except Exception as e:
        logger.error(f"Simple validation error: {str(e)}")
        return {"valid": False, "error": str(e)}

@router.post("/refresh")
async def refresh_token():
    """Refresh JWT token"""
    # TODO: Implement token refresh
    return {"message": "Token refresh not implemented yet"}

@router.post("/logout")
async def logout():
    """Logout user"""
    # TODO: Implement logout logic
    return {"message": "Logout successful"}
