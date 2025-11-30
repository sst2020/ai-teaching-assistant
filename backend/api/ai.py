"""
AI API Endpoints - Provides AI-powered features for code analysis and feedback.
"""
import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.feedback import (
    GenerateFeedbackRequest, FeedbackResponse, GeneratedFeedback,
    ExplainCodeRequest, ExplainCodeResponse,
    SuggestImprovementsRequest, SuggestImprovementsResponse,
    AnswerQuestionRequest, AnswerQuestionResponse,
    AIConfigResponse, AIProvider
)
from services.ai_service import ai_service
from services.feedback_service import feedback_service
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-feedback", response_model=FeedbackResponse)
async def generate_feedback(
    request: GenerateFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered feedback for code.

    This endpoint analyzes the provided code and generates personalized,
    constructive feedback based on:
    - Code analysis results (complexity, style, security)
    - Assignment requirements (if provided)
    - Student's historical performance (if student_id provided)
    - Selected feedback tone

    Args:
        request: GenerateFeedbackRequest with code and options

    Returns:
        FeedbackResponse with comprehensive feedback
    """
    start_time = time.time()

    try:
        # Generate feedback using the feedback service
        feedback = await feedback_service.generate_feedback(request)

        # If AI enhancement is requested and API key is available
        if request.use_ai and settings.OPENAI_API_KEY:
            try:
                ai_result = await ai_service.generate_code_feedback(
                    code=request.code,
                    analysis_results={
                        "overall_score": feedback.overall_score,
                        "grade": feedback.overall_grade,
                        "issues": [item.message for cat in feedback.categories for item in cat.items]
                    }
                )
                # Append AI feedback to summary
                if ai_result and not ai_result.startswith("AI service"):
                    feedback.summary += f"\n\nAI Insights: {ai_result[:500]}"
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")

        processing_time = (time.time() - start_time) * 1000

        return FeedbackResponse(
            success=True,
            feedback=feedback,
            message="Feedback generated successfully",
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate feedback: {str(e)}"
        )


@router.post("/explain-code", response_model=ExplainCodeResponse)
async def explain_code(request: ExplainCodeRequest):
    """
    Explain code to a student.

    Provides a clear explanation of what the code does, key concepts used,
    and learning resources. The explanation is tailored to the student's level.

    Args:
        request: ExplainCodeRequest with code and options

    Returns:
        ExplainCodeResponse with explanation and concepts
    """
    try:
        result = await ai_service.explain_code(
            code=request.code,
            language=request.language,
            detail_level=request.detail_level,
            student_level=request.student_level
        )

        return ExplainCodeResponse(
            success=result.get("success", True),
            explanation=result.get("explanation", ""),
            key_concepts=result.get("key_concepts", []),
            complexity_notes=result.get("complexity_notes"),
            learning_resources=result.get("learning_resources", [])
        )

    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain code: {str(e)}"
        )


@router.post("/suggest-improvements", response_model=SuggestImprovementsResponse)
async def suggest_improvements(request: SuggestImprovementsRequest):
    """
    Suggest improvements for code.

    Analyzes the code and provides actionable suggestions for improvement,
    optionally including refactored code examples.

    Args:
        request: SuggestImprovementsRequest with code and options

    Returns:
        SuggestImprovementsResponse with suggestions
    """
    try:
        result = await ai_service.suggest_improvements(
            code=request.code,
            language=request.language,
            focus_areas=request.focus_areas,
            max_suggestions=request.max_suggestions,
            include_refactored_code=request.include_refactored_code
        )

        return SuggestImprovementsResponse(
            success=result.get("success", True),
            suggestions=result.get("suggestions", []),
            refactored_code=result.get("refactored_code"),
            improvement_summary=result.get("improvement_summary", "")
        )

    except Exception as e:
        logger.error(f"Improvement suggestions failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest improvements: {str(e)}"
        )


@router.post("/answer-question", response_model=AnswerQuestionResponse)
async def answer_question(request: AnswerQuestionRequest):
    """
    Answer a student's question about code or programming.

    Provides educational answers with related concepts and follow-up questions
    to encourage further learning.

    Args:
        request: AnswerQuestionRequest with question and optional code context

    Returns:
        AnswerQuestionResponse with answer and related information
    """
    try:
        result = await ai_service.answer_student_question(
            question=request.question,
            code=request.code,
            language=request.language,
            context=request.context
        )

        return AnswerQuestionResponse(
            success=result.get("success", True),
            answer=result.get("answer", ""),
            related_concepts=result.get("related_concepts", []),
            code_examples=result.get("code_examples", []),
            follow_up_questions=result.get("follow_up_questions", [])
        )

    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.get("/config", response_model=AIConfigResponse)
async def get_ai_config():
    """
    Get current AI configuration.

    Returns information about the configured AI provider, model, and settings.
    """
    return AIConfigResponse(
        provider=AIProvider.OPENAI if settings.OPENAI_API_KEY else AIProvider.LOCAL,
        model=settings.AI_MODEL,
        temperature=settings.AI_TEMPERATURE,
        max_tokens=settings.AI_MAX_TOKENS,
        available_models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    )


@router.get("/stats")
async def get_ai_stats():
    """
    Get AI service statistics.

    Returns statistics about AI interactions including total count,
    average latency, and breakdown by interaction type.
    """
    return ai_service.get_interaction_stats()


@router.get("/health")
async def ai_health_check():
    """
    Check AI service health.

    Verifies that the AI service is properly configured and operational.
    """
    has_api_key = bool(settings.OPENAI_API_KEY)

    return {
        "status": "healthy" if has_api_key else "degraded",
        "provider": "openai" if has_api_key else "local",
        "model": settings.AI_MODEL,
        "api_configured": has_api_key,
        "message": "AI service is operational" if has_api_key else "Using local fallback (no API key configured)"
    }
