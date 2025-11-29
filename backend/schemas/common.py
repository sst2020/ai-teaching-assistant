"""
Common Schemas used across the application
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    version: str
    timestamp: datetime


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[list] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20
    
    
class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

