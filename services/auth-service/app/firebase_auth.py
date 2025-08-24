"""Firebase Authentication Integration for Auth Service"""
import firebase_admin
from firebase_admin import credentials, auth
import logging
from typing import Optional, Dict, Any
import os
import json

from .config import settings
from .exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

class FirebaseAuthManager:
    """Manages Firebase authentication operations"""
    
    def __init__(self):
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if settings.FIREBASE_SERVICE_ACCOUNT_KEY:
                # Use service account key
                service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
                cred = credentials.Certificate(service_account_info)
            else:
                # Use default credentials or development mode
                logger.warning("No Firebase service account key provided. Using development mode.")
                return
            
            # Initialize Firebase app if not already done
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
            else:
                self.app = firebase_admin.get_app()
            
            logger.info("✅ Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {str(e)}")
            self.app = None
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return user data"""
        if not self.app:
            # Development mode - return mock user
            logger.warning("Firebase not initialized. Using development mode.")
            return {
                'uid': 'dev_user_' + id_token[:8],
                'email': 'dev@fleettracker.local',
                'email_verified': True,
                'name': 'Development User',
                'picture': None,
                'firebase': {
                    'identities': {'email': ['dev@fleettracker.local']},
                    'sign_in_provider': 'password'
                }
            }
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            
            # Get additional user info
            user_record = auth.get_user(decoded_token['uid'])
            
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name') or user_record.display_name,
                'picture': decoded_token.get('picture') or user_record.photo_url,
                'firebase': decoded_token.get('firebase', {}),
                'custom_claims': decoded_token.get('custom_claims', {})
            }
            
        except auth.ExpiredIdTokenError:
            raise AuthenticationError("Firebase token has expired")
        except auth.RevokedIdTokenError:
            raise AuthenticationError("Firebase token has been revoked")
        except auth.InvalidIdTokenError:
            raise AuthenticationError("Invalid Firebase token")
        except Exception as e:
            logger.error(f"Firebase token verification error: {str(e)}")
            raise AuthenticationError("Firebase authentication failed")
    
    async def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> str:
        """Create custom Firebase token"""
        if not self.app:
            raise AuthenticationError("Firebase not available")
        
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"Error creating custom token: {str(e)}")
            raise AuthenticationError("Failed to create custom token")
    
    async def get_user_by_uid(self, uid: str) -> Dict[str, Any]:
        """Get user information by UID"""
        if not self.app:
            return {
                'uid': uid,
                'email': f'{uid}@fleettracker.local',
                'display_name': 'Development User',
                'disabled': False
            }
        
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'photo_url': user_record.photo_url,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'provider_data': [
                    {
                        'provider_id': provider.provider_id,
                        'uid': provider.uid,
                        'email': provider.email
                    } for provider in user_record.provider_data
                ],
                'custom_claims': user_record.custom_claims or {}
            }
        except auth.UserNotFoundError:
            raise AuthenticationError(f"User {uid} not found")
        except Exception as e:
            logger.error(f"Error getting user by UID: {str(e)}")
            raise AuthenticationError("Failed to get user information")
    
    async def set_custom_claims(self, uid: str, claims: Dict[str, Any]):
        """Set custom claims for user"""
        if not self.app:
            logger.warning("Firebase not available - cannot set custom claims")
            return
        
        try:
            auth.set_custom_user_claims(uid, claims)
            logger.info(f"Custom claims set for user {uid}: {claims}")
        except Exception as e:
            logger.error(f"Error setting custom claims: {str(e)}")
            raise AuthenticationError("Failed to set custom claims")
    
    async def delete_user(self, uid: str):
        """Delete user from Firebase"""
        if not self.app:
            logger.warning("Firebase not available - cannot delete user")
            return
        
        try:
            auth.delete_user(uid)
            logger.info(f"User {uid} deleted from Firebase")
        except auth.UserNotFoundError:
            logger.warning(f"User {uid} not found in Firebase")
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise AuthenticationError("Failed to delete user")

# Global Firebase auth manager instance
firebase_auth_manager = FirebaseAuthManager()
