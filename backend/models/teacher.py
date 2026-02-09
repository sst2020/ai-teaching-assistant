"""
Teacher Model - Represents teachers in the system.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.user import User


class Teacher(Base, TimestampMixin):
    """
    Teacher model representing teaching staff.

    Attributes:
        id: Primary key
        teacher_id: Unique teacher identifier
        name: Teacher's full name
        email: Teacher's email address
        department: Department name
        title: Job title
        hire_date: Date when teacher joined
        user_id: Optional linked user account
    """
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Linked user ID (optional)"
    )

    teacher_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    hire_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="teacher",
        uselist=False
    )

    __table_args__ = (
        Index("ix_teachers_department_teacher_id", "department", "teacher_id"),
    )

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, teacher_id='{self.teacher_id}', name='{self.name}')>"
