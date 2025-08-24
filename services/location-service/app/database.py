# Location Service Database Connection

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import os

logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv("LOCATION_DB_URL", "postgresql+psycopg2://location_user:location_password@location-db:5432/location_db")

# Database engine
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db() -> None:
    """Initialize database"""
    try:
        # Import models to ensure tables are created
        # TODO: Add actual models import when ready
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Location Service database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_db() -> None:
    """Close database connections"""
    engine.dispose()
    logger.info("✅ Location Service database connections closed")