"""
Base Model with common fields and utilities.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

