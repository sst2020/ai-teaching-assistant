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
    注册新学生账户。

    创建新的学生记录，包含学号、姓名、邮箱等基本信息。
    系统会自动检查学号和邮箱的唯一性。

    Args:
        student_in: 学生注册信息，包含：
            - student_id: 学号（必填，唯一）
            - name: 姓名（必填）
            - email: 邮箱地址（必填，唯一）
            - course_id: 课程ID（可选）
        db: 异步数据库会话（自动注入）

    Returns:
        StudentResponse: 创建成功的学生信息

    Raises:
        HTTPException 400: 学号或邮箱已存在
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
    学生登录认证。

    通过学号验证学生身份，可选择性验证邮箱。
    登录成功返回学生完整信息。

    Args:
        login_data: 登录凭据，包含：
            - student_id: 学号（必填）
            - email: 邮箱地址（可选，用于二次验证）
        db: 异步数据库会话（自动注入）

    Returns:
        StudentLoginResponse: 登录结果，包含：
            - success: 是否成功
            - message: 结果消息
            - student: 学生信息（成功时返回）
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
    获取学生列表（分页）。

    支持按课程ID筛选，返回分页结果。

    Args:
        page: 页码（默认1，最小1）
        page_size: 每页数量（默认20，范围1-100）
        course_id: 课程ID筛选条件（可选）
        db: 异步数据库会话（自动注入）

    Returns:
        StudentListResponse: 分页学生列表，包含：
            - items: 学生列表
            - total: 总数量
            - page: 当前页码
            - page_size: 每页数量
            - total_pages: 总页数
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
    根据学号获取学生信息。

    Args:
        student_id: 学号
        db: 异步数据库会话（自动注入）

    Returns:
        StudentResponse: 学生详细信息

    Raises:
        HTTPException 404: 学生不存在
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
    更新学生信息。

    仅更新请求中提供的字段，未提供的字段保持不变。
    更新邮箱时会检查唯一性。

    Args:
        student_id: 学号
        student_in: 更新数据，可包含：
            - name: 姓名
            - email: 邮箱地址
            - course_id: 课程ID
        db: 异步数据库会话（自动注入）

    Returns:
        StudentResponse: 更新后的学生信息

    Raises:
        HTTPException 404: 学生不存在
        HTTPException 400: 邮箱已被使用
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
    删除学生账户。

    删除指定学号的学生及其所有关联数据。

    Args:
        student_id: 学号
        db: 异步数据库会话（自动注入）

    Returns:
        APIResponse: 操作结果，包含：
            - success: 是否成功
            - message: 结果消息

    Raises:
        HTTPException 404: 学生不存在
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

