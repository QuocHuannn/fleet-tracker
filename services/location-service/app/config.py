# Location Service Configuration

from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Union
from functools import lru_cache

class Settings(BaseSettings):
    """Location Service settings"""

    # Application Settings
    APP_NAME: str = "Fleet Tracker Location Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # Database Configuration (PostgreSQL + PostGIS)
    LOCATION_DB_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Configuration
    REDIS_URL: str

    # MQTT Configuration
    MQTT_BROKER_URL: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_CLIENT_ID: str = "location-service"

    # Service URLs
    VEHICLE_SERVICE_URL: str

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

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()