"""
GradingResult Model - Represents grading results for submissions.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.submission import Submission


class GradedBy(str, Enum):
    """Who graded the submission."""
    AI = "AI"
    TEACHER = "teacher"


class GradingResult(Base, TimestampMixin):
    """
    GradingResult model representing grading results for submissions.
    
    Attributes:
        id: Primary key
        submission_id: Foreign key to submission
        overall_score: Score achieved
        max_score: Maximum possible score
        feedback: JSON containing detailed feedback
        graded_at: Timestamp when graded
        graded_by: Who graded (AI/teacher)
    """
    __tablename__ = "grading_results"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    graded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    graded_by: Mapped[GradedBy] = mapped_column(
        SQLEnum(GradedBy),
        nullable=False,
        default=GradedBy.AI,
    )
    
    # Relationships
    submission: Mapped["Submission"] = relationship(
        "Submission",
        back_populates="grading_result",
    )
    
    def __repr__(self) -> str:
        return f"<GradingResult(id={self.id}, submission_id={self.submission_id}, score={self.overall_score}/{self.max_score})>"
    
    @property
    def percentage_score(self) -> float:
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.overall_score / self.max_score) * 100

