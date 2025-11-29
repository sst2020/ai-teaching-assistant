"""
Question Model - Represents student questions for Q&A triage.
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
    from models.answer import Answer


class QuestionCategory(str, Enum):
    """Categories of questions."""
    CONCEPT = "concept"
    ASSIGNMENT = "assignment"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class QuestionStatus(str, Enum):
    """Status of a question."""
    PENDING = "pending"
    ANSWERED = "answered"
    ESCALATED = "escalated"
    CLOSED = "closed"


class Question(Base, TimestampMixin):
    """
    Question model representing student questions.
    
    Attributes:
        id: Primary key
        question_id: Unique question identifier
        student_id: Foreign key to student
        course_id: Course the question relates to
        question_text: The question content
        context: Additional context for the question
        category: Question category
        status: Question status
    """
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[str] = mapped_column(
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
    course_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[QuestionCategory] = mapped_column(
        SQLEnum(QuestionCategory),
        nullable=False,
        default=QuestionCategory.OTHER,
    )
    status: Mapped[QuestionStatus] = mapped_column(
        SQLEnum(QuestionStatus),
        nullable=False,
        default=QuestionStatus.PENDING,
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="questions",
    )
    answer: Mapped[Optional["Answer"]] = relationship(
        "Answer",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_questions_course_status", "course_id", "status"),
        Index("ix_questions_student_created", "student_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, question_id='{self.question_id}', status='{self.status}')>"

