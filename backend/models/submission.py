"""
Submission Model - Represents student assignment submissions.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.student import Student
    from models.assignment import Assignment
    from models.grading_result import GradingResult
    from models.plagiarism_check import PlagiarismCheck


class SubmissionStatus(str, Enum):
    """Status of a submission."""
    PENDING = "pending"
    GRADED = "graded"
    FLAGGED = "flagged"


class Submission(Base, TimestampMixin):
    """
    Submission model representing student assignment submissions.
    
    Attributes:
        id: Primary key
        submission_id: Unique submission identifier
        student_id: Foreign key to student
        assignment_id: Foreign key to assignment
        content: Submitted content (text/code)
        submitted_at: Submission timestamp
        status: Submission status (pending/graded/flagged)
        file_path: Path to uploaded file if any
    """
    __tablename__ = "submissions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus),
        nullable=False,
        default=SubmissionStatus.PENDING,
    )
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="submissions",
    )
    assignment: Mapped["Assignment"] = relationship(
        "Assignment",
        back_populates="submissions",
    )
    grading_result: Mapped[Optional["GradingResult"]] = relationship(
        "GradingResult",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )
    plagiarism_check: Mapped[Optional["PlagiarismCheck"]] = relationship(
        "PlagiarismCheck",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_submissions_student_assignment", "student_id", "assignment_id"),
        Index("ix_submissions_status_submitted_at", "status", "submitted_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, submission_id='{self.submission_id}', status='{self.status}')>"

