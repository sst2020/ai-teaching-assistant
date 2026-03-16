"""
Test utilities for the AI Teaching Assistant.
"""
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from core.database import Base


# Global variable to store the test engine and session maker
_test_engine = None
_test_sessionmaker = None
_test_database_url = None


def get_test_database_url() -> str:
    """Get the test database URL."""
    return os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


def is_sqlite_test_database() -> bool:
    """Whether the current test database is SQLite."""
    return get_test_database_url().startswith("sqlite")


def reset_test_db_sync() -> None:
    """
    Reset the MySQL test database outside the app event loop.

    This avoids cross-loop issues with aiomysql on Windows when tests use TestClient.
    """
    if is_sqlite_test_database():
        return

    sync_url = make_url(get_test_database_url()).set(drivername="mysql+pymysql")
    sync_engine = create_engine(sync_url, future=True)
    try:
        with sync_engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(text(f"TRUNCATE TABLE `{table.name}`"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    finally:
        sync_engine.dispose()


def clear_test_db_state() -> None:
    """Clear cached async test engine state between sync TestClient runs."""
    global _test_engine, _test_sessionmaker, _test_database_url
    _test_engine = None
    _test_sessionmaker = None
    _test_database_url = None


async def init_test_db():
    """
    Initialize the test database with all required tables.

    Default strategy:
    - Unit tests: SQLite in-memory (fast, isolated)
    - Optional integration mode: set TEST_DATABASE_URL to a MySQL URL
    """
    global _test_engine, _test_sessionmaker, _test_database_url

    # Import all models at the start to ensure they are registered with Base.metadata
    # This is critical to ensure all tables (including code_files) are created
    import models

    # Create a test-specific engine
    test_database_url = get_test_database_url()
    is_sqlite = test_database_url.startswith("sqlite")

    if (
        _test_engine is not None
        and _test_sessionmaker is not None
        and _test_database_url == test_database_url
    ):
        return

    engine_kwargs = {"echo": False}
    if is_sqlite:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Close MySQL test connections aggressively to avoid cross-loop cleanup warnings on Windows.
        engine_kwargs["poolclass"] = NullPool

    _test_engine = create_async_engine(test_database_url, **engine_kwargs)
    _test_database_url = test_database_url

    if is_sqlite:
        # In-memory SQLite needs schema creation on the test engine itself.
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

    if is_sqlite_test_database():
        # SQLite in-memory databases are connection-local, so schema must exist here.
        async with _test_engine.begin() as conn:
            import models  # Re-import to ensure models are registered
            await conn.run_sync(Base.metadata.create_all)

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
    global _test_engine, _test_sessionmaker, _test_database_url
    if _test_engine:
        await _test_engine.dispose()
        _test_engine = None
        _test_sessionmaker = None
        _test_database_url = None
