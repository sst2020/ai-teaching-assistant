"""
Teacher Management Router - Handles teacher CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from core.database import get_db
from core.dependencies import require_roles
from schemas.teacher import (
    TeacherCreate, TeacherUpdate, TeacherResponse,
    TeacherLogin, TeacherLoginResponse, TeacherListResponse
)
from schemas.common import APIResponse
from utils.crud import crud_teacher

router = APIRouter(prefix="/teachers", tags=["Teacher Management"])


@router.post("/register", response_model=TeacherResponse, status_code=201)
async def register_teacher(
    teacher_in: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(["admin"]))
):
    """
    Register a new teacher account.
    """
    existing = await crud_teacher.get_by_teacher_id(db, teacher_in.teacher_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Teacher with ID '{teacher_in.teacher_id}' already exists"
        )

    existing_email = await crud_teacher.get_by_email(db, teacher_in.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail=f"Teacher with email '{teacher_in.email}' already exists"
        )

    teacher_data = teacher_in.model_dump()
    teacher = await crud_teacher.create(db, teacher_data)
    return teacher


@router.post("/login", response_model=TeacherLoginResponse)
async def login_teacher(
    login_data: TeacherLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Teacher login validation (basic).
    """
    teacher = await crud_teacher.get_by_teacher_id(db, login_data.teacher_id)

    if not teacher:
        return TeacherLoginResponse(
            success=False,
            message=f"Teacher with ID '{login_data.teacher_id}' not found",
            teacher=None
        )

    if login_data.email and teacher.email != login_data.email:
        return TeacherLoginResponse(
            success=False,
            message="Email verification failed",
            teacher=None
        )

    return TeacherLoginResponse(
        success=True,
        message="Login successful",
        teacher=TeacherResponse.model_validate(teacher)
    )


@router.get("", response_model=TeacherListResponse)
async def list_teachers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(["admin"]))
):
    """
    Get paginated teacher list.
    """
    skip = (page - 1) * page_size
    filters = {"department": department} if department else None

    teachers = await crud_teacher.get_multi(db, skip=skip, limit=page_size, filters=filters)
    total = await crud_teacher.count(db, filters=filters)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return TeacherListResponse(
        items=[TeacherResponse.model_validate(t) for t in teachers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(["admin"]))
):
    """
    Get a teacher by teacher_id.
    """
    teacher = await crud_teacher.get_by_teacher_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail=f"Teacher with ID '{teacher_id}' not found"
        )
    return teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: str,
    teacher_in: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(["admin"]))
):
    """
    Update teacher information.
    """
    teacher = await crud_teacher.get_by_teacher_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail=f"Teacher with ID '{teacher_id}' not found"
        )

    update_data = teacher_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        existing = await crud_teacher.get_by_email(db, update_data["email"])
        if existing and existing.id != teacher.id:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{update_data['email']}' is already in use"
            )

    updated_teacher = await crud_teacher.update(db, teacher, update_data)
    return updated_teacher


@router.delete("/{teacher_id}", response_model=APIResponse)
async def delete_teacher(
    teacher_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(["admin"]))
):
    """
    Delete a teacher account.
    """
    teacher = await crud_teacher.get_by_teacher_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail=f"Teacher with ID '{teacher_id}' not found"
        )

    await crud_teacher.delete(db, teacher.id)
    return APIResponse(
        success=True,
        message=f"Teacher '{teacher_id}' deleted successfully"
    )
