"""
Schemas for Assignment CRUD API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssignmentTypeEnum(str, Enum):
    """Types of assignments (matching database model)."""
    CODE = "code"
    ESSAY = "essay"
    QUIZ = "quiz"


class AssignmentBase(BaseModel):
    """Base schema for assignment data."""
    title: str = Field(..., min_length=1, max_length=255, description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    assignment_type: AssignmentTypeEnum = Field(..., description="Type of assignment")
    course_id: str = Field(..., min_length=1, max_length=50, description="Course ID")
    due_date: Optional[datetime] = Field(None, description="Assignment due date")
    max_score: float = Field(100.0, ge=0, description="Maximum possible score")


class AssignmentCreate(AssignmentBase):
    """Schema for creating a new assignment."""
    assignment_id: str = Field(..., min_length=1, max_length=50, description="Unique assignment identifier")
    rubric_id: Optional[int] = Field(None, description="Associated rubric ID")


class AssignmentUpdate(BaseModel):
    """Schema for updating assignment information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    assignment_type: Optional[AssignmentTypeEnum] = Field(None, description="Type of assignment")
    course_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Course ID")
    due_date: Optional[datetime] = Field(None, description="Assignment due date")
    max_score: Optional[float] = Field(None, ge=0, description="Maximum possible score")
    rubric_id: Optional[int] = Field(None, description="Associated rubric ID")


class AssignmentResponse(AssignmentBase):
    """Schema for assignment response."""
    id: int = Field(..., description="Database ID")
    assignment_id: str = Field(..., description="Unique assignment identifier")
    rubric_id: Optional[int] = Field(None, description="Associated rubric ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record update timestamp")

    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    """Schema for paginated assignment list response."""
    items: List[AssignmentResponse] = Field(default_factory=list, description="List of assignments")
    total: int = Field(..., description="Total number of assignments")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

