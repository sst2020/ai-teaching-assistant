"""
Test utilities for the AI Teaching Assistant.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import Base, get_db
from typing import AsyncGenerator
import asyncio


async def override_get_db():
    """Override for get_db dependency that uses in-memory database."""
    # Create a test-specific engine
    test_async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    test_async_sessionmaker = async_sessionmaker(
        bind=test_async_engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with test_async_sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    await test_async_engine.dispose()