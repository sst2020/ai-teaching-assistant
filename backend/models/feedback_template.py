"""
FeedbackTemplate Model - Stores reusable feedback templates.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.base import TimestampMixin


class TemplateCategory(str, PyEnum):
    """Categories for feedback templates."""
    COMMON_ISSUES = "common_issues"
    LANGUAGE_SPECIFIC = "language_specific"
    ASSIGNMENT_SPECIFIC = "assignment_specific"
    ENCOURAGEMENT = "encouragement"
    SECURITY = "security"
    STYLE = "style"
    COMPLEXITY = "complexity"
    NAMING = "naming"
    PERFORMANCE = "performance"
    ERROR_HANDLING = "error_handling"
    TESTING = "testing"
    ALGORITHM = "algorithm"


class TemplateTone(str, PyEnum):
    """Tone variants for feedback templates."""
    NEUTRAL = "neutral"
    ENCOURAGING = "encouraging"
    STRICT = "strict"
    PROFESSIONAL = "professional"


class FeedbackTemplate(Base, TimestampMixin):
    """
    FeedbackTemplate model for storing reusable feedback templates.
    
    Attributes:
        id: Primary key
        name: Template name
        category: Template category
        language: Specific programming language or None for all
        title: Feedback title template
        message: Feedback message template with placeholders
        severity: Default severity (info, warning, error)
        tags: JSON array of searchable tags
        variables: JSON array of available placeholder variables
        is_active: Whether template is active
        usage_count: Number of times template was used
    """
    __tablename__ = "feedback_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TemplateCategory.COMMON_ISSUES.value,
        index=True
    )
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    tags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, default=list)
    variables: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # New fields for enhanced template system
    tone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=TemplateTone.NEUTRAL.value,
        index=True
    )
    locale: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="en", index=True)
    
    def __repr__(self) -> str:
        return f"<FeedbackTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def render(self, **kwargs) -> tuple[str, str]:
        """
        Render the template with provided variables.
        
        Args:
            **kwargs: Variable values to substitute
            
        Returns:
            Tuple of (rendered_title, rendered_message)
        """
        title = self.title
        message = self.message
        
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        return title, message
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "language": self.language,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "tags": self.tags or [],
            "variables": self.variables or [],
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "tone": self.tone,
            "locale": self.locale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

