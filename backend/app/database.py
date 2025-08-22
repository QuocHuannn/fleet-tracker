# Database Connection và Session Management
# PostgreSQL với PostGIS connection setup

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

from .config import settings

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[Session, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db() -> None:
    """Initialize database and create tables"""
    # TODO: Import all models here
    # from .models import vehicle, location, user, alert
    
    # Enable PostGIS extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            print("✅ PostGIS extension enabled")
        except Exception as e:
            print(f"⚠️  PostGIS extension error: {e}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

async def close_db() -> None:
    """Close database connections"""
    engine.dispose()
    print("✅ Database connections closed")
