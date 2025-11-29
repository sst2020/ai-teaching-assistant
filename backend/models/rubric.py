"""
Rubric Model - Represents grading rubrics for assignments.
"""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.assignment import Assignment


class Rubric(Base, TimestampMixin):
    """
    Rubric model for defining grading criteria.
    
    Attributes:
        id: Primary key
        rubric_id: Unique rubric identifier
        name: Rubric name
        description: Rubric description
        criteria: JSON containing grading criteria and weights
        max_score: Maximum possible score
    """
    __tablename__ = "rubrics"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rubric_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    # Relationships
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment",
        back_populates="rubric",
    )
    
    def __repr__(self) -> str:
        return f"<Rubric(id={self.id}, rubric_id='{self.rubric_id}', name='{self.name}')>"

