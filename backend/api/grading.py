"""
Grading Result Router - 评分结果管理 API

处理评分结果的 CRUD 操作，支持:
- 按学生/作业/提交获取成绩
- 手动覆盖 AI 评分
- 评分统计信息
- Redis 缓存集成
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import math
import logging

from core.database import get_db
from core.cache import cache_service, CacheKeys, CacheService
from schemas.grading import (
    GradingResultCreate,
    GradingResultUpdate,
    GradingResultOverride,
    GradingResultResponse,
    GradingResultWithSubmission,
    GradingResultListResponse,
    GradingResultWithSubmissionList,
    GradingStatistics,
)
from utils.crud import crud_grading_result, crud_submission, crud_student, crud_assignment
from models.grading_result import GradedBy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grading", tags=["Grading Results"])


@router.post("", response_model=GradingResultResponse, status_code=201)
async def create_grading_result(
    grading_in: GradingResultCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建评分结果。
    
    - 为指定的提交记录创建评分结果
    - 每个提交只能有一个评分结果
    - 自动设置评分时间（如未提供）
    """
    # 验证提交记录存在
    submission = await crud_submission.get(db, grading_in.submission_id)
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"Submission with ID '{grading_in.submission_id}' not found"
        )
    
    # 检查是否已存在评分结果
    existing = await crud_grading_result.get_by_submission_id(db, grading_in.submission_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Grading result already exists for submission '{grading_in.submission_id}'"
        )
    
    # 创建评分数据
    grading_data = {
        "submission_id": grading_in.submission_id,
        "overall_score": grading_in.overall_score,
        "max_score": grading_in.max_score,
        "feedback": grading_in.feedback,
        "graded_by": grading_in.graded_by,
        "graded_at": grading_in.graded_at or datetime.utcnow(),
    }
    
    grading_result = await crud_grading_result.create(db, grading_data)
    await db.commit()
    
    # 失效相关缓存
    await cache_service.delete(CacheKeys.grading_by_submission(grading_in.submission_id))
    await cache_service.delete(CacheKeys.grading_by_student(submission.student_id))
    await cache_service.delete(CacheKeys.grading_by_assignment(submission.assignment_id))
    
    logger.info(f"创建评分结果: ID={grading_result.id}, 提交={grading_in.submission_id}")
    
    return _to_response(grading_result)


@router.get("/{grading_id}", response_model=GradingResultWithSubmission)
async def get_grading_result(
    grading_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个评分结果（包含提交详情）。
    """
    # 尝试从缓存获取
    cache_key = CacheKeys.grading_result(grading_id)
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    grading_result = await crud_grading_result.get_with_submission(db, grading_id)
    if not grading_result:
        raise HTTPException(
            status_code=404,
            detail=f"Grading result with ID '{grading_id}' not found"
        )
    
    response = _to_response_with_submission(grading_result)
    
    # 缓存结果
    await cache_service.set(cache_key, response.model_dump(), CacheService.TTL_MEDIUM)
    
    return response


@router.get("/submission/{submission_id}", response_model=GradingResultResponse)
async def get_grading_by_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    按提交记录 ID 获取评分结果。
    """
    # 尝试从缓存获取
    cache_key = CacheKeys.grading_by_submission(submission_id)
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    grading_result = await crud_grading_result.get_by_submission_id(db, submission_id)
    if not grading_result:
        raise HTTPException(
            status_code=404,
            detail=f"No grading result found for submission '{submission_id}'"
        )
    
    response = _to_response(grading_result)
    
    # 缓存结果
    await cache_service.set(cache_key, response.model_dump(), CacheService.TTL_MEDIUM)
    
    return response


def _to_response(grading_result) -> GradingResultResponse:
    """转换为响应模型"""
    return GradingResultResponse(
        id=grading_result.id,
        submission_id=grading_result.submission_id,
        overall_score=grading_result.overall_score,
        max_score=grading_result.max_score,
        feedback=grading_result.feedback,
        graded_at=grading_result.graded_at,
        graded_by=grading_result.graded_by,
        percentage_score=grading_result.percentage_score,
        created_at=grading_result.created_at,
        updated_at=grading_result.updated_at,
    )


def _to_response_with_submission(grading_result) -> GradingResultWithSubmission:
    """转换为包含提交详情的响应模型"""
    submission = grading_result.submission
    student = submission.student if submission else None
    assignment = submission.assignment if submission else None

    return GradingResultWithSubmission(
        id=grading_result.id,
        submission_id=grading_result.submission_id,
        overall_score=grading_result.overall_score,
        max_score=grading_result.max_score,
        feedback=grading_result.feedback,
        graded_at=grading_result.graded_at,
        graded_by=grading_result.graded_by,
        percentage_score=grading_result.percentage_score,
        created_at=grading_result.created_at,
        updated_at=grading_result.updated_at,
        submission_external_id=submission.submission_id if submission else None,
        student_id=student.id if student else None,
        student_external_id=student.student_id if student else None,
        student_name=student.name if student else None,
        assignment_id=assignment.id if assignment else None,
        assignment_external_id=assignment.assignment_id if assignment else None,
        assignment_title=assignment.title if assignment else None,
        submitted_at=submission.submitted_at if submission else None,
    )


@router.get("/student/{student_id}", response_model=GradingResultListResponse)
async def get_grading_by_student(
    student_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    按学生 ID 获取所有评分结果。

    - 支持分页
    - 按评分时间倒序排列
    """
    # 验证学生存在并获取数据库 ID
    student = await crud_student.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )

    # 获取评分结果
    skip = (page - 1) * page_size
    grading_results = await crud_grading_result.get_by_student_id(
        db, student.id, skip=skip, limit=page_size
    )
    total = await crud_grading_result.count_by_student_id(db, student.id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return GradingResultListResponse(
        items=[_to_response(g) for g in grading_results],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/assignment/{assignment_id}", response_model=GradingResultListResponse)
async def get_grading_by_assignment(
    assignment_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    按作业 ID 获取所有评分结果。

    - 支持分页
    - 按评分时间倒序排列
    """
    # 验证作业存在并获取数据库 ID
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )

    # 获取评分结果
    skip = (page - 1) * page_size
    grading_results = await crud_grading_result.get_by_assignment_id(
        db, assignment.id, skip=skip, limit=page_size
    )
    total = await crud_grading_result.count_by_assignment_id(db, assignment.id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return GradingResultListResponse(
        items=[_to_response(g) for g in grading_results],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/assignment/{assignment_id}/statistics", response_model=GradingStatistics)
async def get_grading_statistics(
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取作业的评分统计信息。

    包括:
    - 已评分数量
    - 平均分、最高分、最低分
    - AI 评分 vs 教师评分数量
    - 分数分布
    """
    # 验证作业存在
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )

    stats = await crud_grading_result.get_statistics_by_assignment(db, assignment.id)

    # 计算分数分布
    grading_results = await crud_grading_result.get_by_assignment_id(
        db, assignment.id, skip=0, limit=1000
    )
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for g in grading_results:
        pct = g.percentage_score
        if pct >= 90:
            distribution["A"] += 1
        elif pct >= 80:
            distribution["B"] += 1
        elif pct >= 70:
            distribution["C"] += 1
        elif pct >= 60:
            distribution["D"] += 1
        else:
            distribution["F"] += 1

    return GradingStatistics(
        total_graded=stats["total_graded"],
        average_score=stats["average_score"],
        highest_score=stats["highest_score"],
        lowest_score=stats["lowest_score"],
        ai_graded_count=stats["ai_graded_count"],
        teacher_graded_count=stats["teacher_graded_count"],
        score_distribution=distribution,
    )


@router.put("/{grading_id}/override", response_model=GradingResultResponse)
async def override_grading_result(
    grading_id: int,
    override_in: GradingResultOverride,
    db: AsyncSession = Depends(get_db)
):
    """
    教师覆盖 AI 评分。

    - 更新评分分数
    - 将评分者改为教师
    - 记录覆盖原因（如提供）
    """
    grading_result = await crud_grading_result.get(db, grading_id)
    if not grading_result:
        raise HTTPException(
            status_code=404,
            detail=f"Grading result with ID '{grading_id}' not found"
        )

    # 构建更新数据
    update_data = {
        "overall_score": override_in.overall_score,
        "graded_by": GradedBy.TEACHER,
        "graded_at": datetime.utcnow(),
    }

    # 更新反馈（保留原有反馈，添加覆盖信息）
    feedback = grading_result.feedback or {}
    if override_in.feedback:
        feedback.update(override_in.feedback)
    if override_in.override_reason:
        feedback["override_reason"] = override_in.override_reason
        feedback["original_score"] = grading_result.overall_score
    update_data["feedback"] = feedback

    updated = await crud_grading_result.update(db, grading_result, update_data)
    await db.commit()

    # 失效相关缓存
    await cache_service.delete(CacheKeys.grading_result(grading_id))
    await cache_service.delete(CacheKeys.grading_by_submission(grading_result.submission_id))

    logger.info(f"教师覆盖评分: ID={grading_id}, 原分数={grading_result.overall_score}, 新分数={override_in.overall_score}")

    return _to_response(updated)


@router.delete("/{grading_id}", status_code=204)
async def delete_grading_result(
    grading_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除评分结果。

    - 删除指定的评分结果
    - 如果不存在返回 404 错误
    """
    grading_result = await crud_grading_result.get(db, grading_id)
    if not grading_result:
        raise HTTPException(
            status_code=404,
            detail=f"Grading result with ID '{grading_id}' not found"
        )

    submission_id = grading_result.submission_id
    await crud_grading_result.delete(db, grading_id)
    await db.commit()

    # 失效相关缓存
    await cache_service.delete(CacheKeys.grading_result(grading_id))
    await cache_service.delete(CacheKeys.grading_by_submission(submission_id))

    logger.info(f"删除评分结果: ID={grading_id}")

