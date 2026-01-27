"""
Assignment Model - Represents course assignments.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, DateTime, Float, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.submission import Submission
    from models.rubric import Rubric


class AssignmentType(str, Enum):
    """Types of assignments."""
    CODE = "code"
    ESSAY = "essay"
    QUIZ = "quiz"
    PROJECT = "project"


class Assignment(Base, TimestampMixin):
    """
    Assignment model representing course assignments.
    
    Attributes:
        id: Primary key
        assignment_id: Unique assignment identifier
        title: Assignment title
        description: Assignment description
        assignment_type: Type of assignment (code/essay/quiz)
        course_id: Course this assignment belongs to
        due_date: Assignment due date
        max_score: Maximum possible score
        rubric_id: Foreign key to rubric
    """
    __tablename__ = "assignments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignment_type: Mapped[AssignmentType] = mapped_column(
        SQLEnum(AssignmentType),
        nullable=False,
        default=AssignmentType.CODE,
    )
    course_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    rubric_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rubrics.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Relationships
    rubric: Mapped[Optional["Rubric"]] = relationship(
        "Rubric",
        back_populates="assignments",
    )
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_assignments_course_id_due_date", "course_id", "due_date"),
    )
    
    def __repr__(self) -> str:
        return f"<Assignment(id={self.id}, assignment_id='{self.assignment_id}', title='{self.title}')>"

