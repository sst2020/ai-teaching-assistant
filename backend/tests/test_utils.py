"""
Test utilities for the AI Teaching Assistant.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import Base, get_db
from typing import AsyncGenerator
import asyncio


# Global variable to store the test engine and session maker
_test_engine = None
_test_sessionmaker = None


async def init_test_db():
    """Initialize the test database with all required tables."""
    global _test_engine, _test_sessionmaker

    # Create a test-specific engine
    _test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

    # Import all models to ensure they are registered with Base.metadata
    from models import (
        Student, Assignment, Submission, GradingResult,
        Question, Answer, PlagiarismCheck, Rubric, CodeFile,
        AnalysisResult, FeedbackTemplate, AIInteraction,
        KnowledgeBaseEntry, QALog
    )

    # Create all tables
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    _test_sessionmaker = async_sessionmaker(
        bind=_test_engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def override_get_db():
    """Override for get_db dependency that uses in-memory database."""
    global _test_engine, _test_sessionmaker

    # Ensure test database is initialized
    if _test_engine is None or _test_sessionmaker is None:
        await init_test_db()

    async with _test_sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_test_db():
    """Dispose of the test database resources."""
    global _test_engine
    if _test_engine:
        await _test_engine.dispose()
        _test_engine = None