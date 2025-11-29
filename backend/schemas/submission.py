"""
Schemas for Submission Management API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubmissionStatusEnum(str, Enum):
    """Status of a submission (matching database model)."""
    PENDING = "pending"
    GRADED = "graded"
    FLAGGED = "flagged"


class SubmissionBase(BaseModel):
    """Base schema for submission data."""
    content: Optional[str] = Field(None, description="Submitted content (text/code)")
    file_path: Optional[str] = Field(None, max_length=500, description="Path to uploaded file")


class SubmissionCreate(SubmissionBase):
    """Schema for creating a new submission."""
    submission_id: Optional[str] = Field(None, max_length=50, description="Unique submission identifier (auto-generated if not provided)")
    student_id: str = Field(..., description="Student ID (unique identifier)")
    assignment_id: str = Field(..., description="Assignment ID (unique identifier)")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp (defaults to now)")


class SubmissionUpdate(BaseModel):
    """Schema for updating submission information."""
    content: Optional[str] = Field(None, description="Submitted content")
    file_path: Optional[str] = Field(None, max_length=500, description="Path to uploaded file")


class SubmissionStatusUpdate(BaseModel):
    """Schema for updating submission status."""
    status: SubmissionStatusEnum = Field(..., description="New submission status")


class SubmissionResponse(SubmissionBase):
    """Schema for submission response."""
    id: int = Field(..., description="Database ID")
    submission_id: str = Field(..., description="Unique submission identifier")
    student_id: int = Field(..., description="Student database ID")
    assignment_id: int = Field(..., description="Assignment database ID")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    status: SubmissionStatusEnum = Field(..., description="Submission status")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record update timestamp")

    class Config:
        from_attributes = True


class SubmissionDetailResponse(SubmissionResponse):
    """Schema for detailed submission response with related data."""
    student_name: Optional[str] = Field(None, description="Student name")
    student_external_id: Optional[str] = Field(None, description="Student external ID")
    assignment_title: Optional[str] = Field(None, description="Assignment title")
    assignment_external_id: Optional[str] = Field(None, description="Assignment external ID")


class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list response."""
    items: List[SubmissionResponse] = Field(default_factory=list, description="List of submissions")
    total: int = Field(..., description="Total number of submissions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

