# API Gateway Configuration
# Environment settings và service URLs

import os
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Union
from functools import lru_cache

class Settings(BaseSettings):
    """API Gateway settings"""
    
    # Application Settings
    APP_NAME: str = "Fleet Tracker API Gateway"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    VEHICLE_SERVICE_URL: str = "http://vehicle-service:8002"
    LOCATION_SERVICE_URL: str = "http://location-service:8003"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"
    
    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    @model_validator(mode='before')
    @classmethod
    def parse_cors_origins(cls, values):
        if isinstance(values, dict) and 'CORS_ORIGINS' in values:
            cors_origins = values['CORS_ORIGINS']
            if isinstance(cors_origins, str):
                values['CORS_ORIGINS'] = cors_origins.split(",")
        return values
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 1000
    RATE_LIMIT_BURST_SIZE: int = 100
    
    # JWT Configuration (for token validation) - MUST match auth service
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or "INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    
    # Redis for rate limiting và caching
    REDIS_URL: str = "redis://redis:6379"
    
    # Timeouts
    SERVICE_TIMEOUT: float = 10.0
    SERVICE_CONNECT_TIMEOUT: float = 5.0
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
