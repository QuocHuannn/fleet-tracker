"""Common exceptions for Fleet Tracker microservices"""

class FleetTrackerException(Exception):
    """Base exception for Fleet Tracker"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(FleetTrackerException):
    """Authentication related errors"""
    pass

class AuthorizationError(FleetTrackerException):
    """Authorization related errors"""
    pass

class ValidationError(FleetTrackerException):
    """Data validation errors"""
    pass

class ServiceUnavailableError(FleetTrackerException):
    """Service unavailable errors"""
    pass

class ResourceNotFoundError(FleetTrackerException):
    """Resource not found errors"""
    pass

class DatabaseError(FleetTrackerException):
    """Database related errors"""
    pass

class ExternalServiceError(FleetTrackerException):
    """External service communication errors"""
    pass
