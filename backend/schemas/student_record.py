"""
Schemas for Student Record Management API
"""
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StudentRecordBase(BaseModel):
    """Base schema for student record data."""
    name: str = Field(..., min_length=1, max_length=100, description="学生姓名")
    student_id: str = Field(..., min_length=1, max_length=50, description="学号")
    assignment_number: str = Field(..., min_length=1, max_length=50, description="作业编号")


class StudentRecordCreate(StudentRecordBase):
    """Schema for creating a new student record."""
    password: str = Field(..., min_length=6, max_length=128, description="明文密码")


class StudentRecordUpdate(BaseModel):
    """Schema for updating student record information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="学生姓名")
    student_id: Optional[str] = Field(None, min_length=1, max_length=50, description="学号")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="明文密码")
    assignment_number: Optional[str] = Field(None, min_length=1, max_length=50, description="作业编号")


class StudentRecordResponse(BaseModel):
    """Schema for student record response (不含密码)."""
    id: int = Field(..., description="数据库 ID")
    name: str = Field(..., description="学生姓名")
    student_id: str = Field(..., description="学号")
    assignment_number: str = Field(..., description="作业编号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class StudentRecordListResponse(BaseModel):
    """Schema for paginated student record list."""
    items: List[StudentRecordResponse] = Field(default_factory=list, description="记录列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")
