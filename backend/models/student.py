"""
Student Model - Represents students in the system.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.submission import Submission
    from models.question import Question


class Student(Base, TimestampMixin):
    """
    Student model representing enrolled students.
    
    Attributes:
        id: Primary key
        student_id: Unique student identifier (e.g., student number)
        name: Student's full name
        email: Student's email address
        enrollment_date: Date when student enrolled
        course_id: Course the student is enrolled in
    """
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    enrollment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    course_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    
    # Relationships
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_students_course_id_student_id", "course_id", "student_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}')>"

