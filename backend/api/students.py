"""
Student Management Router - Handles student CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from core.database import get_db
from schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse,
    StudentLogin, StudentLoginResponse, StudentListResponse
)
from schemas.common import APIResponse
from utils.crud import crud_student

router = APIRouter(prefix="/students", tags=["Student Management"])


@router.post("/register", response_model=StudentResponse, status_code=201)
async def register_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new student.
    
    - Creates a new student record with the provided information
    - Returns the created student data
    """
    # Check if student_id already exists
    existing = await crud_student.get_by_student_id(db, student_in.student_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Student with ID '{student_in.student_id}' already exists"
        )
    
    # Check if email already exists
    existing_email = await crud_student.get_by_email(db, student_in.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail=f"Student with email '{student_in.email}' already exists"
        )
    
    # Create student
    student_data = student_in.model_dump()
    student = await crud_student.create(db, student_data)
    return student


@router.post("/login", response_model=StudentLoginResponse)
async def login_student(
    login_data: StudentLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Student login/authentication.
    
    - Verifies student exists by student_id
    - Optionally verifies email if provided
    - Returns student information on success
    """
    student = await crud_student.get_by_student_id(db, login_data.student_id)
    
    if not student:
        return StudentLoginResponse(
            success=False,
            message=f"Student with ID '{login_data.student_id}' not found",
            student=None
        )
    
    # Verify email if provided
    if login_data.email and student.email != login_data.email:
        return StudentLoginResponse(
            success=False,
            message="Email verification failed",
            student=None
        )
    
    return StudentLoginResponse(
        success=True,
        message="Login successful",
        student=StudentResponse.model_validate(student)
    )


@router.get("", response_model=StudentListResponse)
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all students with pagination.
    
    - Supports filtering by course_id
    - Returns paginated results
    """
    skip = (page - 1) * page_size
    filters = {"course_id": course_id} if course_id else None
    
    students = await crud_student.get_multi(db, skip=skip, limit=page_size, filters=filters)
    total = await crud_student.count(db, filters=filters)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return StudentListResponse(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get student information by student_id.
    
    - Returns student details if found
    - Returns 404 if student not found
    """
    student = await crud_student.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )
    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update student information.
    
    - Updates only the provided fields
    - Returns the updated student data
    """
    student = await crud_student.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )
    
    # Check email uniqueness if being updated
    update_data = student_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        existing = await crud_student.get_by_email(db, update_data["email"])
        if existing and existing.id != student.id:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{update_data['email']}' is already in use"
            )

    updated_student = await crud_student.update(db, student, update_data)
    return updated_student


@router.delete("/{student_id}", response_model=APIResponse)
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a student.

    - Removes the student and all associated data
    - Returns success message on deletion
    """
    student = await crud_student.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )

    await crud_student.delete(db, student.id)
    return APIResponse(
        success=True,
        message=f"Student '{student_id}' deleted successfully"
    )

