"""
Schemas for Q&A Triage Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionCategory(str, Enum):
    """Categories of questions."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ADMINISTRATIVE = "administrative"


class QuestionStatus(str, Enum):
    """Status of a question."""
    PENDING = "pending"
    AI_ANSWERED = "ai_answered"
    ESCALATED = "escalated"
    TEACHER_ANSWERED = "teacher_answered"
    RESOLVED = "resolved"


class QuestionRequest(BaseModel):
    """Schema for submitting a question."""
    student_id: str = Field(..., description="Unique identifier for the student")
    course_id: str = Field(..., description="Course identifier")
    question: str = Field(..., min_length=1, description="The question text")
    context: Optional[str] = Field(None, description="Additional context for the question")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class AIAnswer(BaseModel):
    """AI-generated answer."""
    answer: str = Field(..., description="The AI-generated answer")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the answer")
    sources: List[str] = Field(default_factory=list, description="Reference sources used")
    needs_teacher_review: bool = Field(False, description="Whether teacher review is recommended")


class QuestionResponse(BaseModel):
    """Response for a submitted question."""
    question_id: str
    student_id: str
    course_id: str
    question: str
    category: QuestionCategory
    status: QuestionStatus
    ai_answer: Optional[AIAnswer] = None
    teacher_answer: Optional[str] = None
    created_at: datetime
    answered_at: Optional[datetime] = None


class KnowledgeGap(BaseModel):
    """Identified knowledge gap from Q&A analysis."""
    topic: str = Field(..., description="Topic with knowledge gap")
    frequency: int = Field(..., description="Number of related questions")
    difficulty_level: str = Field(..., description="Difficulty level of the topic")
    sample_questions: List[str] = Field(default_factory=list, description="Sample questions on this topic")


class QAAnalyticsReport(BaseModel):
    """Analytics report from Q&A records."""
    course_id: str
    period_start: datetime
    period_end: datetime
    total_questions: int
    ai_resolved_count: int
    teacher_resolved_count: int
    average_response_time_seconds: float
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list)
    common_topics: List[dict] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list, description="Teaching recommendations")


class EscalationRequest(BaseModel):
    """Request to escalate a question to a teacher."""
    question_id: str = Field(..., description="Question to escalate")
    reason: str = Field(..., description="Reason for escalation")
    priority: str = Field("normal", description="Priority level: low, normal, high")

