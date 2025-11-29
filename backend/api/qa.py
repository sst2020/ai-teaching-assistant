"""
Q&A Triage Router - Handles AI-powered Q&A endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    QAAnalyticsReport,
    EscalationRequest
)
from schemas.common import APIResponse
from services.qa_service import qa_service

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
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze")
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
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
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

