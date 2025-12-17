"""
Database Configuration and Session Management

This module provides SQLAlchemy engine configuration, session management,
and base model class for the AI Teaching Assistant backend.
"""
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_database_url(async_mode: bool = True) -> str:
    """
    Get the database URL, converting to async/sync driver as needed.

    Args:
        async_mode: If True, convert to async driver URL; if False, convert to sync driver URL

    Returns:
        Database URL string
    """
    url = settings.DATABASE_URL

    if async_mode:
        # Convert to async drivers
        # sqlite:/// to sqlite+aiosqlite:///
        if url.startswith("sqlite:///"):
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
        # postgresql:// to postgresql+asyncpg://
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        # mysql:// to mysql+aiomysql://
        elif url.startswith("mysql://") and "+aiomysql" not in url:
            url = url.replace("mysql://", "mysql+aiomysql://")
    else:
        # Convert to sync drivers (for Alembic migrations)
        # sqlite+aiosqlite:/// to sqlite:///
        if "+aiosqlite" in url:
            url = url.replace("sqlite+aiosqlite:///", "sqlite:///")
        # postgresql+asyncpg:// to postgresql://
        elif "+asyncpg" in url:
            url = url.replace("postgresql+asyncpg://", "postgresql://")
        # mysql+aiomysql:// to mysql://
        elif "+aiomysql" in url:
            url = url.replace("mysql+aiomysql://", "mysql://")

    return url


# Async engine for production use
async_engine = create_async_engine(
    get_database_url(async_mode=True),
    echo=settings.DATABASE_ECHO,
    # Use StaticPool for SQLite to avoid threading issues
    poolclass=StaticPool if settings.DATABASE_URL.startswith("sqlite") else None,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync engine for migrations and scripts
sync_engine = create_engine(
    get_database_url(async_mode=False),
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

# Sync session factory
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Get a synchronous database session for scripts and migrations.
    
    Returns:
        Session: Synchronous database session
    """
    return SyncSessionLocal()


async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called on application startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    This should be called on application shutdown.
    """
    await async_engine.dispose()


async def check_db_connection() -> tuple[bool, Optional[str]]:
    """
    Check if the database connection is healthy.
    
    Returns:
        Tuple of (is_healthy, error_message)
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)

