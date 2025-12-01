"""
AIInteraction Model - Stores AI interaction history for auditing.
"""
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Integer, Float, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.base import TimestampMixin


class AIProvider(str, PyEnum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class AIInteractionType(str, PyEnum):
    """Types of AI interactions."""
    GENERATE_FEEDBACK = "generate_feedback"
    EXPLAIN_CODE = "explain_code"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    ANSWER_QUESTION = "answer_question"


class AIInteraction(Base, TimestampMixin):
    """
    AIInteraction model for storing AI interaction history.
    
    Attributes:
        id: Primary key
        interaction_type: Type of AI interaction
        provider: AI provider used
        model: Model name/version
        prompt: Input prompt sent to AI
        response: AI response
        tokens_used: Number of tokens consumed
        latency_ms: Response latency in milliseconds
        student_id: Associated student ID
        submission_id: Associated submission ID
        file_id: Associated file ID
        extra_metadata: Additional metadata as JSON
        success: Whether the interaction was successful
        error_message: Error message if failed
    """
    __tablename__ = "ai_interactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    interaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AIProvider.OPENAI.value
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="gpt-4")
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    student_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    submission_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    extra_metadata: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, default=dict)
    success: Mapped[bool] = mapped_column(nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_ai_interactions_type_provider", "interaction_type", "provider"),
        Index("ix_ai_interactions_student_type", "student_id", "interaction_type"),
    )
    
    def __repr__(self) -> str:
        return f"<AIInteraction(id={self.id}, type='{self.interaction_type}', provider='{self.provider}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "interaction_type": self.interaction_type,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "student_id": self.student_id,
            "submission_id": self.submission_id,
            "file_id": self.file_id,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

