"""
CRUD Utility Functions for Database Operations

This module provides reusable CRUD operations for all database models.
"""
from typing import Optional, List, Type, TypeVar, Generic, Any, Dict
from datetime import datetime
import uuid

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import Base
from models import (
    Student, Assignment, Submission, GradingResult,
    Question, Answer, PlagiarismCheck, Rubric
)
from models.submission import SubmissionStatus

# Generic type for models
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional filters."""
        query = select(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        query = select(func.count()).select_from(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False


# Student CRUD
class CRUDStudent(CRUDBase[Student]):
    """CRUD operations for Student model."""
    
    async def get_by_student_id(self, db: AsyncSession, student_id: str) -> Optional[Student]:
        """Get student by unique student_id."""
        result = await db.execute(
            select(Student).where(Student.student_id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Student]:
        """Get student by email."""
        result = await db.execute(
            select(Student).where(Student.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_course(
        self, db: AsyncSession, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """Get students by course ID."""
        result = await db.execute(
            select(Student)
            .where(Student.course_id == course_id)
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())


# Assignment CRUD
class CRUDAssignment(CRUDBase[Assignment]):
    """CRUD operations for Assignment model."""
    
    async def get_by_assignment_id(self, db: AsyncSession, assignment_id: str) -> Optional[Assignment]:
        """Get assignment by unique assignment_id."""
        result = await db.execute(
            select(Assignment).where(Assignment.assignment_id == assignment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_course(
        self, db: AsyncSession, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Get assignments by course ID."""
        result = await db.execute(
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.due_date.desc().nullslast())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_course(self, db: AsyncSession, course_id: str) -> int:
        """Count assignments by course ID."""
        result = await db.execute(
            select(func.count()).select_from(Assignment).where(Assignment.course_id == course_id)
        )
        return result.scalar() or 0


# Submission CRUD
class CRUDSubmission(CRUDBase[Submission]):
    """CRUD operations for Submission model."""

    async def get_by_submission_id(self, db: AsyncSession, submission_id: str) -> Optional[Submission]:
        """Get submission by unique submission_id."""
        result = await db.execute(
            select(Submission).where(Submission.submission_id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student(
        self, db: AsyncSession, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get submissions by student database ID."""
        result = await db.execute(
            select(Submission)
            .where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assignment(
        self, db: AsyncSession, assignment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get submissions by assignment database ID."""
        result = await db.execute(
            select(Submission)
            .where(Submission.assignment_id == assignment_id)
            .order_by(Submission.submitted_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_student(self, db: AsyncSession, student_id: int) -> int:
        """Count submissions by student."""
        result = await db.execute(
            select(func.count()).select_from(Submission).where(Submission.student_id == student_id)
        )
        return result.scalar() or 0

    async def count_by_assignment(self, db: AsyncSession, assignment_id: int) -> int:
        """Count submissions by assignment."""
        result = await db.execute(
            select(func.count()).select_from(Submission).where(Submission.assignment_id == assignment_id)
        )
        return result.scalar() or 0

    async def update_status(
        self, db: AsyncSession, submission_id: str, status: SubmissionStatus
    ) -> Optional[Submission]:
        """Update submission status."""
        submission = await self.get_by_submission_id(db, submission_id)
        if submission:
            submission.status = status
            await db.flush()
            await db.refresh(submission)
        return submission


def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_part = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}_{unique_part}"
    return f"{timestamp}_{unique_part}"


# Create singleton instances
crud_student = CRUDStudent(Student)
crud_assignment = CRUDAssignment(Assignment)
crud_submission = CRUDSubmission(Submission)

