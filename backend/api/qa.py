"""
Q&A Triage Router - Handles AI-powered Q&A endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    QAAnalyticsReport,
    EscalationRequest
)
from schemas.qa_log import QALogCreate, QALogResponse, QALogStats
from schemas.common import APIResponse
from services.qa_service import qa_service
from services.qa_engine_service import qa_engine_service

router = APIRouter(prefix="/qa", tags=["Q&A Triage"])


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Submit a question for AI-powered answering.
    
    - Automatically categorizes the question by complexity
    - Provides AI-generated answers for common questions
    - Escalates complex questions to teachers when needed
    """
    try:
        response = await qa_service.answer_question(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalate", response_model=QuestionResponse)
async def escalate_question(request: EscalationRequest):
    """
    Escalate a question to a teacher.
    
    Use this when the AI answer is insufficient or the student
    needs more detailed explanation.
    """
    try:
        response = await qa_service.escalate_question(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{course_id}", response_model=QAAnalyticsReport)
async def get_qa_analytics(
    course_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Q&A analytics report for a course.

    - Identifies knowledge gaps based on question patterns
    - Provides statistics on AI vs teacher resolution
    - Generates teaching recommendations
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        report = await qa_service.generate_analytics_report(
            db=db,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-ask", response_model=QALogResponse)
async def smart_ask_question(
    request: QALogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    智能问答接口 - 使用知识库匹配和分诊逻辑

    - 自动提取问题关键词
    - 匹配知识库条目
    - 根据匹配度和难度进行分诊
    - 持久化问答记录到数据库
    """
    try:
        response = await qa_engine_service.process_question(db, request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=QALogStats)
async def get_qa_stats(db: AsyncSession = Depends(get_db)):
    """
    获取问答统计信息

    - 总问题数
    - 按分诊结果统计
    - 平均响应时间
    - 有帮助率
    """
    try:
        stats = await qa_engine_service.get_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{student_id}", response_model=List[QALogResponse])
async def get_student_history(
    student_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学生的问答历史

    - 按时间倒序排列
    - 支持限制返回数量
    """
    try:
        history = await qa_service.get_student_question_history(db, student_id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weakness/{student_id}")
async def get_student_weakness(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取学生的知识薄弱点报告

    - 分析学生提问记录
    - 识别知识薄弱领域
    - 生成改进建议
    """
    try:
        report = await qa_service.get_weakness_report(db, student_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str):
    """
    Get details of a specific question.
    """
    if question_id not in qa_service._questions:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return qa_service._questions[question_id]


@router.get("/health")
async def qa_health():
    """Health check for Q&A service."""
    return {
        "service": "Q&A Triage",
        "status": "healthy",
        "questions_in_memory": len(qa_service._questions)
    }

