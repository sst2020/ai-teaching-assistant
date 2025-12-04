"""
Triage API Routes

分诊相关的 API 路由。
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.triage import (
    TriageRequest, TriageResponse,
    PendingQueueResponse,
    TeacherTakeoverRequest, TeacherAnswerRequest, TeacherAnswerResponse,
    TriageStats, DifficultyLevelsResponse
)
from services.triage_service import triage_service


router = APIRouter(prefix="/triage", tags=["分诊管理"])


@router.post("/ask", response_model=TriageResponse)
async def ask_question(
    request: TriageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    提交问题并获取分诊结果。
    
    系统会自动：
    1. 提取问题关键词
    2. 检测问题分类和难度
    3. 在知识库中查找匹配答案
    4. 根据匹配度和难度决定分诊路由
    """
    return await triage_service.triage_question(db, request)


@router.get("/queue", response_model=PendingQueueResponse)
async def get_pending_queue(
    role: Optional[str] = Query(None, description="处理人角色: assistant/teacher"),
    handler_id: Optional[str] = Query(None, description="处理人ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取待处理问题队列。
    
    - role=assistant: 只显示转助教的问题
    - role=teacher: 显示转助教和转教师的问题
    - handler_id: 筛选分配给特定处理人的问题
    """
    return await triage_service.get_pending_queue(
        db, 
        handler_role=role,
        handler_id=handler_id,
        page=page,
        page_size=page_size
    )


@router.post("/takeover")
async def teacher_takeover(
    request: TeacherTakeoverRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    教师接管问题。
    
    教师可以主动接管任何待处理的问题。
    """
    success = await triage_service.teacher_takeover(db, request)
    if not success:
        raise HTTPException(status_code=404, detail="问题不存在")
    return {"message": "接管成功", "log_id": request.log_id}


@router.post("/answer", response_model=TeacherAnswerResponse)
async def teacher_answer(
    request: TeacherAnswerRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    教师回答问题。
    
    教师可以：
    1. 直接回答问题
    2. 选择是否将问答对添加到知识库
    3. 指定新的关键词标签
    """
    response = await triage_service.teacher_answer(db, request)
    if not response:
        raise HTTPException(status_code=404, detail="问题不存在")
    return response


@router.get("/stats", response_model=TriageStats)
async def get_triage_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取分诊统计信息。"""
    return await triage_service.get_stats(db)


@router.get("/difficulty-levels", response_model=DifficultyLevelsResponse)
async def get_difficulty_levels():
    """获取难度级别定义。"""
    return triage_service.get_difficulty_levels()

