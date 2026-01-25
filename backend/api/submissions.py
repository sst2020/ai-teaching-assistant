"""
Submission Management Router - Handles submission CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import math

from core.database import get_db
from schemas.submission import (
    SubmissionCreate, SubmissionUpdate, SubmissionResponse,
    SubmissionStatusUpdate, SubmissionListResponse, SubmissionDetailResponse
)
from schemas.common import APIResponse
from utils.crud import crud_submission, crud_student, crud_assignment, generate_unique_id
from models.submission import SubmissionStatus

router = APIRouter(prefix="/submissions", tags=["Submission Management"])


@router.post("", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    submission_in: SubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    提交作业。

    创建新的作业提交记录，验证学生和作业是否存在，
    如未提供 submission_id 则自动生成。

    Args:
        submission_in: 提交信息，包含学生ID、作业ID、提交内容等
        db: 数据库会话依赖

    Returns:
        SubmissionResponse: 创建的提交记录

    Raises:
        HTTPException 404: 学生或作业不存在
        HTTPException 400: 提交ID已存在
    """
    # Validate student exists
    student = await crud_student.get_by_student_id(db, submission_in.student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{submission_in.student_id}' not found"
        )
    
    # Validate assignment exists
    assignment = await crud_assignment.get_by_assignment_id(db, submission_in.assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{submission_in.assignment_id}' not found"
        )
    
    # Generate submission_id if not provided
    submission_id = submission_in.submission_id or generate_unique_id("SUB")
    
    # Check if submission_id already exists
    existing = await crud_submission.get_by_submission_id(db, submission_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Submission with ID '{submission_id}' already exists"
        )
    
    # Create submission data
    submission_data = {
        "submission_id": submission_id,
        "student_id": student.id,  # Use database ID
        "assignment_id": assignment.id,  # Use database ID
        "content": submission_in.content,
        "file_path": submission_in.file_path,
        "submitted_at": submission_in.submitted_at or datetime.utcnow(),
        "status": SubmissionStatus.PENDING,
    }
    
    submission = await crud_submission.create(db, submission_data)
    return submission


@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取提交详情。

    根据提交ID获取提交详细信息，包含关联的学生和作业信息。

    Args:
        submission_id: 提交的唯一标识符
        db: 数据库会话依赖

    Returns:
        SubmissionDetailResponse: 包含学生和作业信息的提交详情

    Raises:
        HTTPException 404: 提交记录不存在
    """
    submission = await crud_submission.get_by_submission_id(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"Submission with ID '{submission_id}' not found"
        )
    
    # Get related data
    student = await crud_student.get(db, submission.student_id)
    assignment = await crud_assignment.get(db, submission.assignment_id)
    
    return SubmissionDetailResponse(
        id=submission.id,
        submission_id=submission.submission_id,
        student_id=submission.student_id,
        assignment_id=submission.assignment_id,
        content=submission.content,
        file_path=submission.file_path,
        submitted_at=submission.submitted_at,
        status=submission.status,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        student_name=student.name if student else None,
        student_external_id=student.student_id if student else None,
        assignment_title=assignment.title if assignment else None,
        assignment_external_id=assignment.assignment_id if assignment else None,
    )


@router.get("/student/{student_id}", response_model=SubmissionListResponse)
async def get_student_submissions(
    student_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学生的所有提交记录。

    根据学生外部ID查询该学生的所有作业提交，支持分页。

    Args:
        student_id: 学生的外部唯一标识符
        page: 页码，从1开始
        page_size: 每页记录数，范围1-100
        db: 数据库会话依赖

    Returns:
        SubmissionListResponse: 分页的提交记录列表

    Raises:
        HTTPException 404: 学生不存在
    """
    # Get student by external ID
    student = await crud_student.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )
    
    skip = (page - 1) * page_size
    submissions = await crud_submission.get_by_student(db, student.id, skip=skip, limit=page_size)
    total = await crud_submission.count_by_student(db, student.id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return SubmissionListResponse(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/assignment/{assignment_id}", response_model=SubmissionListResponse)
async def get_assignment_submissions(
    assignment_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取作业的所有提交记录。

    根据作业外部ID查询该作业的所有学生提交，支持分页。

    Args:
        assignment_id: 作业的外部唯一标识符
        page: 页码，从1开始
        page_size: 每页记录数，范围1-100
        db: 数据库会话依赖

    Returns:
        SubmissionListResponse: 分页的提交记录列表

    Raises:
        HTTPException 404: 作业不存在
    """
    # Get assignment by external ID
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )

    skip = (page - 1) * page_size
    submissions = await crud_submission.get_by_assignment(db, assignment.id, skip=skip, limit=page_size)
    total = await crud_submission.count_by_assignment(db, assignment.id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return SubmissionListResponse(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/{submission_id}/status", response_model=SubmissionResponse)
async def update_submission_status(
    submission_id: str,
    status_update: SubmissionStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新提交状态。

    更新指定提交记录的状态，可选状态包括：待批改、已批改、已标记。

    Args:
        submission_id: 提交的唯一标识符
        status_update: 状态更新信息，包含新状态值
        db: 数据库会话依赖

    Returns:
        SubmissionResponse: 更新后的提交记录

    Raises:
        HTTPException 400: 无效的状态值
        HTTPException 404: 提交记录不存在
    """
    # Map string status to enum
    status_map = {
        "pending": SubmissionStatus.PENDING,
        "graded": SubmissionStatus.GRADED,
        "flagged": SubmissionStatus.FLAGGED,
    }

    status = status_map.get(status_update.status.value.lower())
    if not status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {status_update.status}"
        )

    submission = await crud_submission.update_status(db, submission_id, status)
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"Submission with ID '{submission_id}' not found"
        )

    return submission

