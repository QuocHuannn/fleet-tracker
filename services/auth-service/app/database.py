# Auth Service Database Connection

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[Session, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db() -> None:
    """Initialize database"""
    try:
        # Import models để ensure tables are created
        from . import models  # noqa
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Auth Service database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_db() -> None:
    """Close database connections"""
    engine.dispose()
    logger.info("✅ Auth Service database connections closed")
