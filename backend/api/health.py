"""
Health Check Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional

from schemas.common import HealthResponse
from core.config import settings
from core.database import get_db

router = APIRouter(tags=["Health"])


async def check_database_health(db: AsyncSession) -> tuple[bool, Optional[str]]:
    """Check if database connection is healthy."""
    try:
        await db.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify the API and database are running.

    Returns:
        HealthResponse with status, version, timestamp, and database status
    """
    db_healthy, db_error = await check_database_health(db)

    # Determine overall status
    if db_healthy:
        status = "healthy"
    else:
        status = "degraded"

    return HealthResponse(
        status=status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database_status="connected" if db_healthy else f"error: {db_error}"
    )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/docs",
        "health_check": "/health"
    }

