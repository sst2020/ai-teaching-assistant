"""
Answer Model - Represents answers to student questions.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.question import Question


class Answer(Base, TimestampMixin):
    """
    Answer model representing answers to student questions.
    
    Attributes:
        id: Primary key
        question_id: Foreign key to question
        ai_answer: AI-generated answer
        confidence: AI confidence score (0-1)
        needs_teacher_review: Whether teacher review is needed
        teacher_answer: Teacher's answer if provided
        answered_at: Timestamp when answered
    """
    __tablename__ = "answers"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    ai_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    needs_teacher_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    teacher_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Relationships
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answer",
    )

    # Indexes
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}  # 明确指定MySQL存储引擎
    )

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question_id={self.question_id}, confidence={self.confidence})>"
    
    @property
    def has_teacher_response(self) -> bool:
        """Check if teacher has provided a response."""
        return self.teacher_answer is not None and len(self.teacher_answer.strip()) > 0
    
    @property
    def final_answer(self) -> Optional[str]:
        """Get the final answer (teacher's if available, otherwise AI's)."""
        if self.has_teacher_response:
            return self.teacher_answer
        return self.ai_answer

