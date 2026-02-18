"""
Schemas for Teacher Management API
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class TeacherBase(BaseModel):
    """Base schema for teacher data."""
    name: str = Field(..., min_length=1, max_length=255, description="Teacher's full name")
    email: str = Field(..., description="Teacher's email address")
    department: Optional[str] = Field(None, max_length=100, description="Department name")
    title: Optional[str] = Field(None, max_length=100, description="Job title")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class TeacherCreate(TeacherBase):
    """Schema for creating a new teacher."""
    teacher_id: str = Field(..., min_length=1, max_length=50, description="Unique teacher identifier")
    hire_date: Optional[datetime] = Field(None, description="Date when teacher joined")


class TeacherUpdate(BaseModel):
    """Schema for updating teacher information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Teacher's full name")
    email: Optional[str] = Field(None, description="Teacher's email address")
    department: Optional[str] = Field(None, max_length=100, description="Department name")
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    hire_date: Optional[datetime] = Field(None, description="Date when teacher joined")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is None:
            return v
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class TeacherResponse(TeacherBase):
    """Schema for teacher response."""
    id: int = Field(..., description="Database ID")
    teacher_id: str = Field(..., description="Unique teacher identifier")
    hire_date: Optional[datetime] = Field(None, description="Date when teacher joined")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record update timestamp")

    class Config:
        from_attributes = True


class TeacherLogin(BaseModel):
    """Schema for teacher login."""
    teacher_id: str = Field(..., description="Teacher ID for login")
    email: Optional[str] = Field(None, description="Email for verification (optional)")


class TeacherLoginResponse(BaseModel):
    """Schema for teacher login response."""
    success: bool = Field(..., description="Whether login was successful")
    message: str = Field(..., description="Login result message")
    teacher: Optional[TeacherResponse] = Field(None, description="Teacher information if login successful")


class TeacherListResponse(BaseModel):
    """Schema for paginated teacher list response."""
    items: List[TeacherResponse] = Field(default_factory=list, description="List of teachers")
    total: int = Field(..., description="Total number of teachers")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

