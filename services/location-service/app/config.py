# Location Service Configuration

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Location Service settings"""
    
    # Application Settings
    APP_NAME: str = "Fleet Tracker Location Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Database Configuration (PostgreSQL + PostGIS)
    DATABASE_URL: str = os.getenv("LOCATION_DB_URL", "postgresql+psycopg2://location_user:location_password@location-db:5432/location_db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # MQTT Configuration
    MQTT_BROKER_URL: str = os.getenv("MQTT_BROKER_URL", "mqtt://mosquitto:1883")
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "mqtt_user")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "mqtt_password")
    MQTT_CLIENT_ID: str = "location-service"
    
    # Vehicle Service URL (for validation)
    VEHICLE_SERVICE_URL: str = os.getenv("VEHICLE_SERVICE_URL", "http://vehicle-service:8002")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # Spatial Configuration
    DEFAULT_SRID: int = 4326  # WGS84
    DEFAULT_BUFFER_DISTANCE: float = 100.0  # meters
    MAX_LOCATION_AGE_MINUTES: int = 30
    
    # Trip Detection Settings
    MIN_TRIP_DISTANCE_METERS: float = 500.0
    MIN_TRIP_DURATION_MINUTES: int = 5
    IDLE_TIMEOUT_MINUTES: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()