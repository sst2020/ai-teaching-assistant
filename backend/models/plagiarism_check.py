"""
PlagiarismCheck Model - Represents plagiarism check results.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.submission import Submission


class PlagiarismCheck(Base, TimestampMixin):
    """
    PlagiarismCheck model representing plagiarism detection results.
    
    Attributes:
        id: Primary key
        submission_id: Foreign key to submission
        similarity_score: Overall similarity score (0-1)
        is_flagged: Whether the submission is flagged for review
        matches: JSON containing match details
        checked_at: Timestamp when check was performed
    """
    __tablename__ = "plagiarism_checks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    matches: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Relationships
    submission: Mapped["Submission"] = relationship(
        "Submission",
        back_populates="plagiarism_check",
    )
    
    def __repr__(self) -> str:
        return f"<PlagiarismCheck(id={self.id}, submission_id={self.submission_id}, similarity={self.similarity_score}, flagged={self.is_flagged})>"
    
    @property
    def similarity_percentage(self) -> float:
        """Get similarity as percentage."""
        return self.similarity_score * 100

