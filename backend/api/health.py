"""
Health Check Router
"""
from fastapi import APIRouter
from datetime import datetime

from schemas.common import HealthResponse
from core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        HealthResponse with status, version, and timestamp
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
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

