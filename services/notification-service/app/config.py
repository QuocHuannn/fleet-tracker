# Notification Service Configuration

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Notification Service settings"""
    
    # Application Settings
    APP_NAME: str = "Fleet Tracker Notification Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("NOTIFICATION_DB_URL", "postgresql+psycopg2://notification_user:notification_password@notification-db:5432/notification_db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # WebSocket Configuration
    WS_MAX_CONNECTIONS: int = 1000
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Notification Settings
    MAX_NOTIFICATIONS_PER_USER: int = 100
    NOTIFICATION_BATCH_SIZE: int = 50
    
    # Email Configuration (for future use)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # SMS Configuration (for future use)  
    SMS_PROVIDER_API_KEY: str = os.getenv("SMS_PROVIDER_API_KEY", "")
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return self.CORS_ORIGINS.split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
