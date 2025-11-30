"""
Pydantic schemas for feedback generation, AI interactions, and templates.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class FeedbackTone(str, Enum):
    """Tone options for generated feedback."""
    ENCOURAGING = "encouraging"
    PROFESSIONAL = "professional"
    DETAILED = "detailed"
    CONCISE = "concise"
    FRIENDLY = "friendly"
    STRICT = "strict"


class FeedbackCategory(str, Enum):
    """Categories of feedback."""
    CODE_QUALITY = "code_quality"
    LOGIC_EFFICIENCY = "logic_efficiency"
    STYLE_READABILITY = "style_readability"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"
    SUGGESTIONS = "suggestions"
    ENCOURAGEMENT = "encouragement"


class TemplateCategory(str, Enum):
    """Categories for feedback templates."""
    COMMON_ISSUES = "common_issues"
    LANGUAGE_SPECIFIC = "language_specific"
    ASSIGNMENT_SPECIFIC = "assignment_specific"
    ENCOURAGEMENT = "encouragement"
    SECURITY = "security"
    STYLE = "style"
    COMPLEXITY = "complexity"
    NAMING = "naming"


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class AIInteractionType(str, Enum):
    """Types of AI interactions."""
    GENERATE_FEEDBACK = "generate_feedback"
    EXPLAIN_CODE = "explain_code"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    ANSWER_QUESTION = "answer_question"


# ============================================
# Feedback Item Schemas
# ============================================

class FeedbackItem(BaseModel):
    """Individual feedback item."""
    category: FeedbackCategory = Field(..., description="Feedback category")
    title: str = Field(..., description="Short title for the feedback")
    message: str = Field(..., description="Detailed feedback message")
    severity: str = Field("info", description="Severity: info, warning, error")
    line_number: Optional[int] = Field(None, description="Related line number")
    code_snippet: Optional[str] = Field(None, description="Related code snippet")
    suggestion: Optional[str] = Field(None, description="Suggested fix or improvement")


class CategoryFeedback(BaseModel):
    """Feedback grouped by category."""
    category: FeedbackCategory
    score: float = Field(..., ge=0, le=100, description="Category score 0-100")
    items: List[FeedbackItem] = Field(default_factory=list)
    summary: str = Field("", description="Category summary")


class GeneratedFeedback(BaseModel):
    """Complete generated feedback for a submission."""
    submission_id: Optional[str] = Field(None)
    file_id: Optional[str] = Field(None)
    overall_score: float = Field(..., ge=0, le=100)
    overall_grade: str = Field(..., description="Letter grade A-F")
    summary: str = Field(..., description="Overall feedback summary")
    categories: List[CategoryFeedback] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list, description="Code strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    tone: FeedbackTone = Field(FeedbackTone.PROFESSIONAL)
    language: str = Field("python")


# ============================================
# Request Schemas
# ============================================

class GenerateFeedbackRequest(BaseModel):
    """Request to generate feedback for code."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    submission_id: Optional[str] = Field(None, description="Associated submission ID")
    file_id: Optional[str] = Field(None, description="Associated file ID")
    assignment_id: Optional[str] = Field(None, description="Assignment for context")
    student_id: Optional[str] = Field(None, description="Student for historical context")
    rubric: Optional[Dict[str, Any]] = Field(None, description="Grading rubric")
    tone: FeedbackTone = Field(FeedbackTone.PROFESSIONAL, description="Feedback tone")
    include_suggestions: bool = Field(True, description="Include improvement suggestions")
    max_items_per_category: int = Field(5, ge=1, le=20)
    use_ai: bool = Field(True, description="Use AI for enhanced feedback")


class ExplainCodeRequest(BaseModel):
    """Request to explain code to a student."""
    code: str = Field(..., description="Code to explain")
    language: str = Field("python", description="Programming language")
    detail_level: str = Field("medium", description="Detail level: basic, medium, detailed")
    focus_areas: List[str] = Field(default_factory=list, description="Specific areas to focus on")
    student_level: str = Field("intermediate", description="Student level: beginner, intermediate, advanced")


class SuggestImprovementsRequest(BaseModel):
    """Request to suggest code improvements."""
    code: str = Field(..., description="Code to improve")
    language: str = Field("python", description="Programming language")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    max_suggestions: int = Field(5, ge=1, le=20)
    include_refactored_code: bool = Field(True, description="Include refactored code examples")


class AnswerQuestionRequest(BaseModel):
    """Request to answer a student question about code."""
    question: str = Field(..., description="Student's question")
    code: Optional[str] = Field(None, description="Related code context")
    language: str = Field("python", description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")


# ============================================
# Response Schemas
# ============================================

class FeedbackResponse(BaseModel):
    """Response for feedback generation."""
    success: bool = Field(True)
    feedback: GeneratedFeedback
    message: str = Field("Feedback generated successfully")
    processing_time_ms: Optional[float] = Field(None)


class ExplainCodeResponse(BaseModel):
    """Response for code explanation."""
    success: bool = Field(True)
    explanation: str = Field(..., description="Code explanation")
    key_concepts: List[str] = Field(default_factory=list)
    complexity_notes: Optional[str] = Field(None)
    learning_resources: List[str] = Field(default_factory=list)


class SuggestImprovementsResponse(BaseModel):
    """Response for improvement suggestions."""
    success: bool = Field(True)
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    refactored_code: Optional[str] = Field(None)
    improvement_summary: str = Field("")


class AnswerQuestionResponse(BaseModel):
    """Response for answering student questions."""
    success: bool = Field(True)
    answer: str = Field(..., description="Answer to the question")
    related_concepts: List[str] = Field(default_factory=list)
    code_examples: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)


# ============================================
# Template Schemas
# ============================================

class FeedbackTemplateBase(BaseModel):
    """Base schema for feedback templates."""
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    category: TemplateCategory = Field(..., description="Template category")
    language: Optional[str] = Field(None, description="Specific language or None for all")
    title: str = Field(..., description="Feedback title template")
    message: str = Field(..., description="Feedback message template with placeholders")
    severity: str = Field("info", description="Default severity")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    variables: List[str] = Field(default_factory=list, description="Available placeholder variables")
    is_active: bool = Field(True, description="Whether template is active")


class FeedbackTemplateCreate(FeedbackTemplateBase):
    """Schema for creating a feedback template."""
    pass


class FeedbackTemplateUpdate(BaseModel):
    """Schema for updating a feedback template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[TemplateCategory] = None
    language: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    tags: Optional[List[str]] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class FeedbackTemplateResponse(FeedbackTemplateBase):
    """Schema for feedback template response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    usage_count: int = Field(0, description="Number of times template was used")

    class Config:
        from_attributes = True


class FeedbackTemplateListResponse(BaseModel):
    """Response for listing feedback templates."""
    templates: List[FeedbackTemplateResponse]
    total: int
    page: int
    page_size: int


# ============================================
# AI Interaction Schemas
# ============================================

class AIInteractionCreate(BaseModel):
    """Schema for creating an AI interaction record."""
    interaction_type: AIInteractionType
    provider: AIProvider = Field(AIProvider.OPENAI)
    model: str = Field("gpt-4")
    prompt: str = Field(..., description="Input prompt")
    response: str = Field(..., description="AI response")
    tokens_used: int = Field(0)
    latency_ms: float = Field(0)
    student_id: Optional[str] = None
    submission_id: Optional[str] = None
    file_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIInteractionResponse(BaseModel):
    """Schema for AI interaction response."""
    id: int
    interaction_type: AIInteractionType
    provider: AIProvider
    model: str
    tokens_used: int
    latency_ms: float
    created_at: datetime
    student_id: Optional[str] = None
    submission_id: Optional[str] = None

    class Config:
        from_attributes = True


class AIConfigResponse(BaseModel):
    """Response for AI configuration."""
    provider: AIProvider
    model: str
    temperature: float
    max_tokens: int
    available_models: List[str]


