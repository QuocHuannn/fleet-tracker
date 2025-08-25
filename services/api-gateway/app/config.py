# API Gateway Configuration
# Environment settings và service URLs

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
    AUTH_SERVICE_URL: str
    VEHICLE_SERVICE_URL: str
    LOCATION_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"

    @model_validator(mode='before')
    @classmethod
    def parse_cors_origins(cls, values):
        if isinstance(values, dict) and 'CORS_ORIGINS' in values:
            cors_origins = values.get('CORS_ORIGINS')
            if isinstance(cors_origins, str):
                values['CORS_ORIGINS'] = [origin.strip() for origin in cors_origins.split(",")]
        return values

    # JWT Configuration (for token validation)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Redis for rate limiting and caching
    REDIS_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
