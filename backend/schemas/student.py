"""
Schemas for Student Management API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class StudentBase(BaseModel):
    """Base schema for student data."""
    name: str = Field(..., min_length=1, max_length=255, description="Student's full name")
    email: EmailStr = Field(..., description="Student's email address")
    course_id: Optional[str] = Field(None, max_length=50, description="Course ID the student is enrolled in")


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    student_id: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    enrollment_date: Optional[datetime] = Field(None, description="Date of enrollment")


class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Student's full name")
    email: Optional[EmailStr] = Field(None, description="Student's email address")
    course_id: Optional[str] = Field(None, max_length=50, description="Course ID")
    enrollment_date: Optional[datetime] = Field(None, description="Date of enrollment")


class StudentResponse(StudentBase):
    """Schema for student response."""
    id: int = Field(..., description="Database ID")
    student_id: str = Field(..., description="Unique student identifier")
    enrollment_date: Optional[datetime] = Field(None, description="Date of enrollment")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record update timestamp")

    class Config:
        from_attributes = True


class StudentLogin(BaseModel):
    """Schema for student login."""
    student_id: str = Field(..., description="Student ID for login")
    email: Optional[EmailStr] = Field(None, description="Email for verification (optional)")


class StudentLoginResponse(BaseModel):
    """Schema for student login response."""
    success: bool = Field(..., description="Whether login was successful")
    message: str = Field(..., description="Login result message")
    student: Optional[StudentResponse] = Field(None, description="Student information if login successful")


class StudentListResponse(BaseModel):
    """Schema for paginated student list response."""
    items: List[StudentResponse] = Field(default_factory=list, description="List of students")
    total: int = Field(..., description="Total number of students")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

