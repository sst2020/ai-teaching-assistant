"""
Q&A Service - Handles AI-powered question answering and triage
"""
from typing import List, Optional
from datetime import datetime
import uuid

from schemas.qa import (
    QuestionRequest, QuestionResponse, QuestionCategory, QuestionStatus,
    AIAnswer, QAAnalyticsReport, KnowledgeGap, EscalationRequest
)
from services.ai_service import ai_service


class QAService:
    """Service for AI-powered Q&A triage."""

    def __init__(self):
        self._questions: dict = {}
        self.ai = ai_service

    async def answer_question(self, request: QuestionRequest) -> QuestionResponse:
        """Process and answer a student question using AI."""
        question_id = str(uuid.uuid4())

        # AI-powered categorization
        category_str = await self.ai.categorize_question(request.question)
        category = self._map_category(category_str)

        # Generate AI answer
        ai_answer = await self._generate_answer(request)

        # Determine status based on AI confidence
        status = QuestionStatus.AI_ANSWERED
        if ai_answer.needs_teacher_review or ai_answer.confidence < 0.6:
            status = QuestionStatus.ESCALATED

        response = QuestionResponse(
            question_id=question_id, student_id=request.student_id,
            course_id=request.course_id, question=request.question,
            category=category, status=status, ai_answer=ai_answer,
            created_at=datetime.utcnow(), answered_at=datetime.utcnow()
        )

        self._questions[question_id] = response
        return response

    def _map_category(self, category_str: str) -> QuestionCategory:
        """Map string category to enum."""
        mapping = {
            "basic": QuestionCategory.BASIC,
            "intermediate": QuestionCategory.INTERMEDIATE,
            "advanced": QuestionCategory.ADVANCED,
            "administrative": QuestionCategory.ADMINISTRATIVE
        }
        return mapping.get(category_str, QuestionCategory.INTERMEDIATE)

    async def _generate_answer(self, request: QuestionRequest) -> AIAnswer:
        """Generate an AI answer for the question."""
        context = f"Course: {request.course_id}" if request.course_id else ""
        result = await self.ai.answer_question(request.question, context)

        return AIAnswer(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            needs_teacher_review=result["needs_teacher_review"]
        )
    
    async def escalate_question(self, request: EscalationRequest) -> QuestionResponse:
        """Escalate a question to a teacher."""
        if request.question_id not in self._questions:
            raise ValueError(f"Question {request.question_id} not found")
        
        question = self._questions[request.question_id]
        question.status = QuestionStatus.ESCALATED
        return question
    
    async def generate_analytics_report(
        self, 
        course_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> QAAnalyticsReport:
        """Generate analytics report for Q&A records."""
        # TODO: Implement actual analytics
        return QAAnalyticsReport(
            course_id=course_id,
            period_start=start_date,
            period_end=end_date,
            total_questions=150,
            ai_resolved_count=120,
            teacher_resolved_count=30,
            average_response_time_seconds=2.5,
            knowledge_gaps=[
                KnowledgeGap(
                    topic="Recursion",
                    frequency=25,
                    difficulty_level="intermediate",
                    sample_questions=["How does recursion work?", "When to use recursion?"]
                ),
                KnowledgeGap(
                    topic="Pointers",
                    frequency=18,
                    difficulty_level="advanced",
                    sample_questions=["What are pointers?", "Pointer arithmetic explained"]
                )
            ],
            common_topics=[
                {"topic": "Variables", "count": 45},
                {"topic": "Functions", "count": 38},
                {"topic": "Loops", "count": 32}
            ],
            recommendations=[
                "Consider additional lecture time on recursion concepts",
                "Provide more practice exercises for pointer manipulation"
            ]
        )


# Singleton instance
qa_service = QAService()

