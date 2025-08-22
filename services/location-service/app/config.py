from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Cấu hình cho Location Service
    """
    # Service info
    SERVICE_NAME: str = "location-service"
    VERSION: str = "0.1.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # Database settings
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # MQTT settings
    MQTT_BROKER_URL: str = "mqtt://mosquitto:1883"
    MQTT_CLIENT_ID: str = "location-service"
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_TOPIC_PREFIX: str = "fleet/vehicles/"
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Vehicle service URL
    VEHICLE_SERVICE_URL: str = "http://vehicle-service:8002"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Tạo và cache instance của Settings
    """
    return Settings()


settings = get_settings()
