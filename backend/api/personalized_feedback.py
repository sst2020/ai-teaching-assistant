"""
Personalized Feedback API - Endpoints for generating personalized feedback based on student history.
"""
import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.feedback import (
    PersonalizedFeedbackRequest, PersonalizedFeedbackResponse,
    FeedbackDetailLevel, FeedbackTone, StudentHistoryAnalysis
)
from services.feedback_service import feedback_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Personalized Feedback"])


@router.post("/personalized", response_model=PersonalizedFeedbackResponse)
async def generate_personalized_feedback(
    request: PersonalizedFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized feedback based on student history.

    This endpoint analyzes the student's historical submissions to provide:
    - Trend analysis (improving, declining, stable, fluctuating)
    - Level-appropriate feedback (beginner, intermediate, advanced)
    - Progressive improvement suggestions with difficulty levels
    - Personalized encouragement based on performance

    Args:
        request: PersonalizedFeedbackRequest with code and student_id

    Returns:
        PersonalizedFeedbackResponse with comprehensive personalized feedback
    """
    try:
        start_time = time.time()

        feedback = await feedback_service.generate_personalized_feedback(
            request=request,
            db_session=db
        )

        processing_time = (time.time() - start_time) * 1000

        return PersonalizedFeedbackResponse(
            success=True,
            feedback=feedback,
            message="个性化评语生成成功",
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Failed to generate personalized feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成个性化评语失败: {str(e)}"
        )


@router.get("/student-history/{student_id}", response_model=StudentHistoryAnalysis)
async def get_student_history(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get student's historical performance analysis.

    This endpoint provides:
    - Total submissions count
    - Average score
    - Performance trend
    - Skill level estimation
    - Identified strengths and weaknesses
    - Recurring issues

    Args:
        student_id: Student ID

    Returns:
        StudentHistoryAnalysis with comprehensive history data
    """
    try:
        history = await feedback_service._analyze_student_history(
            student_id=student_id,
            db_session=db
        )
        return history

    except Exception as e:
        logger.error(f"Failed to get student history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取学生历史记录失败: {str(e)}"
        )


@router.get("/detail-levels")
async def list_detail_levels():
    """
    List available feedback detail levels.

    Returns:
        List of detail levels with descriptions
    """
    return [
        {
            "value": FeedbackDetailLevel.BRIEF.value,
            "name": "简洁",
            "name_en": "Brief",
            "description": "只包含关键点，适合快速查看",
            "description_en": "Key points only, suitable for quick review"
        },
        {
            "value": FeedbackDetailLevel.STANDARD.value,
            "name": "标准",
            "name_en": "Standard",
            "description": "适中的详细程度，包含示例",
            "description_en": "Moderate detail with examples"
        },
        {
            "value": FeedbackDetailLevel.DETAILED.value,
            "name": "详细",
            "name_en": "Detailed",
            "description": "包含更多解释和学习资源",
            "description_en": "More explanations and learning resources"
        },
        {
            "value": FeedbackDetailLevel.COMPREHENSIVE.value,
            "name": "全面",
            "name_en": "Comprehensive",
            "description": "包含所有细节、示例和资源",
            "description_en": "All details, examples, and resources"
        }
    ]


@router.get("/tones")
async def list_feedback_tones():
    """
    List available feedback tones.

    Returns:
        List of tones with descriptions
    """
    return [
        {
            "value": FeedbackTone.ENCOURAGING.value,
            "name": "鼓励型",
            "name_en": "Encouraging",
            "description": "积极正面，强调进步"
        },
        {
            "value": FeedbackTone.PROFESSIONAL.value,
            "name": "专业型",
            "name_en": "Professional",
            "description": "客观中立，注重技术细节"
        },
        {
            "value": FeedbackTone.DETAILED.value,
            "name": "详尽型",
            "name_en": "Detailed",
            "description": "深入分析，提供详细解释"
        },
        {
            "value": FeedbackTone.CONCISE.value,
            "name": "简洁型",
            "name_en": "Concise",
            "description": "简明扼要，直击要点"
        },
        {
            "value": FeedbackTone.FRIENDLY.value,
            "name": "友好型",
            "name_en": "Friendly",
            "description": "亲切友好，像朋友交流"
        },
        {
            "value": FeedbackTone.STRICT.value,
            "name": "严格型",
            "name_en": "Strict",
            "description": "严格要求，强调规范"
        }
    ]

