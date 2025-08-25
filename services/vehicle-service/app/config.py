from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Optional, Union
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Cấu hình cho Vehicle Service
    """
    # Service info
    SERVICE_NAME: str = "vehicle-service"
    VERSION: str = "0.1.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Database settings
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "*"
    
    @model_validator(mode='before')
    @classmethod
    def parse_cors_origins(cls, values):
        if isinstance(values, dict) and 'CORS_ORIGINS' in values:
            cors_origins = values['CORS_ORIGINS']
            if isinstance(cors_origins, str):
                if cors_origins == "*":
                    values['CORS_ORIGINS'] = ["*"]
                else:
                    values['CORS_ORIGINS'] = cors_origins.split(",")
        return values
    
    # Auth service URL
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    
    # JWT settings - MUST match auth service
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or "INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    
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
