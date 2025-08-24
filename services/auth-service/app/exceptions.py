"""Custom exceptions for Auth Service"""

class AuthServiceException(Exception):
    """Base exception for Auth Service"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(AuthServiceException):
    """Authentication related errors"""
    pass

class AuthorizationError(AuthServiceException):
    """Authorization related errors"""
    pass

class ValidationError(AuthServiceException):
    """Data validation errors"""
    pass

class UserNotFoundError(AuthServiceException):
    """User not found errors"""
    pass

class UserAlreadyExistsError(AuthServiceException):
    """User already exists errors"""
    pass

class SessionExpiredError(AuthServiceException):
    """Session expired errors"""
    pass

class InvalidTokenError(AuthServiceException):
    """Invalid token errors"""
    pass
