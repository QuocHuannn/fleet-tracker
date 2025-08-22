from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from geoalchemy2 import Geometry

from app.config import settings

# Tạo SQLAlchemy engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT
)

# Tạo session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Base class cho models
Base = declarative_base()

async def init_db():
    """
    Khởi tạo database connection và tạo tables nếu cần
    """
    async with engine.begin() as conn:
        # Tạo tables nếu chưa tồn tại
        # await conn.run_sync(Base.metadata.create_all)
        pass

async def close_db():
    """
    Đóng database connection
    """
    await engine.dispose()

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency để lấy database session
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
