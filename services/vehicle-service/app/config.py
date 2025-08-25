from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Union
from functools import lru_cache

class Settings(BaseSettings):
    """Cấu hình cho Vehicle Service"""

    # Application Settings
    APP_NAME: str = "Fleet Tracker Vehicle Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # Database Configuration
    VEHICLE_DB_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Service URLs
    AUTH_SERVICE_URL: str

    # JWT Configuration (must match Auth Service)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

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
