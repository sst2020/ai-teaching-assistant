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
    PERFORMANCE = "performance"
    ERROR_HANDLING = "error_handling"
    TESTING = "testing"
    ALGORITHM = "algorithm"


class TemplateTone(str, Enum):
    """Tone variants for feedback templates."""
    NEUTRAL = "neutral"
    ENCOURAGING = "encouraging"
    STRICT = "strict"
    PROFESSIONAL = "professional"


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    DEEPSEEK = "deepseek"


class AIInteractionType(str, Enum):
    """Types of AI interactions."""
    GENERATE_FEEDBACK = "generate_feedback"
    EXPLAIN_CODE = "explain_code"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    ANSWER_QUESTION = "answer_question"


class FeedbackDetailLevel(str, Enum):
    """Detail level for feedback generation."""
    BRIEF = "brief"           # 简洁 - 只包含关键点
    STANDARD = "standard"     # 标准 - 适中的详细程度
    DETAILED = "detailed"     # 详细 - 包含更多解释
    COMPREHENSIVE = "comprehensive"  # 全面 - 包含所有细节和示例


class SuggestionDifficulty(str, Enum):
    """Difficulty level for improvement suggestions."""
    EASY = "easy"       # 立即可做 - 简单修改
    MEDIUM = "medium"   # 需要学习 - 需要一些学习
    HARD = "hard"       # 进阶挑战 - 需要深入学习


class StudentLevel(str, Enum):
    """Student skill level."""
    BEGINNER = "beginner"         # 初学者
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"          # 高级


class PerformanceTrend(str, Enum):
    """Student performance trend."""
    IMPROVING = "improving"     # 进步中
    DECLINING = "declining"     # 退步中
    STABLE = "stable"           # 稳定
    FLUCTUATING = "fluctuating" # 波动


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
# Personalized Feedback Schemas
# ============================================

class ProgressiveSuggestion(BaseModel):
    """A progressive improvement suggestion with difficulty and time estimate."""
    suggestion_id: str = Field(..., description="Unique suggestion ID")
    difficulty: SuggestionDifficulty = Field(..., description="Difficulty level")
    title: str = Field(..., description="Suggestion title")
    title_zh: str = Field(..., description="Suggestion title in Chinese")
    description: str = Field(..., description="Detailed description")
    description_zh: str = Field(..., description="Description in Chinese")
    estimated_time: str = Field(..., description="Estimated time to implement (e.g., '5 minutes', '1 hour')")
    estimated_time_zh: str = Field(..., description="Estimated time in Chinese")
    code_example: Optional[str] = Field(None, description="Example code if applicable")
    learning_resources: List[str] = Field(default_factory=list, description="Related learning resources")
    order: int = Field(1, description="Order in the learning path")


class LearningPath(BaseModel):
    """A structured learning path with progressive steps."""
    path_id: str = Field(..., description="Unique path ID")
    title: str = Field(..., description="Learning path title")
    title_zh: str = Field(..., description="Title in Chinese")
    description: str = Field(..., description="Path description")
    description_zh: str = Field(..., description="Description in Chinese")
    steps: List[ProgressiveSuggestion] = Field(default_factory=list)
    total_estimated_time: str = Field(..., description="Total estimated time")
    total_estimated_time_zh: str = Field(..., description="Total time in Chinese")


class StudentHistoryAnalysis(BaseModel):
    """Analysis of student's historical performance."""
    student_id: str = Field(..., description="Student ID")
    total_submissions: int = Field(0, description="Total number of submissions")
    average_score: float = Field(0.0, description="Average score across submissions")
    trend: PerformanceTrend = Field(PerformanceTrend.STABLE, description="Performance trend")
    trend_zh: str = Field("稳定", description="Trend in Chinese")
    level: StudentLevel = Field(StudentLevel.INTERMEDIATE, description="Estimated skill level")
    level_zh: str = Field("中级", description="Level in Chinese")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    strengths_zh: List[str] = Field(default_factory=list, description="Strengths in Chinese")
    weaknesses: List[str] = Field(default_factory=list, description="Areas needing improvement")
    weaknesses_zh: List[str] = Field(default_factory=list, description="Weaknesses in Chinese")
    recurring_issues: List[str] = Field(default_factory=list, description="Issues that appear repeatedly")
    recurring_issues_zh: List[str] = Field(default_factory=list, description="Recurring issues in Chinese")
    improvement_rate: float = Field(0.0, description="Rate of improvement (0-100)")
    recent_scores: List[float] = Field(default_factory=list, description="Recent submission scores")


class PersonalizedFeedbackRequest(BaseModel):
    """Request for personalized feedback generation."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    student_id: str = Field(..., description="Student ID for historical context")
    submission_id: Optional[str] = Field(None, description="Current submission ID")
    assignment_id: Optional[str] = Field(None, description="Assignment ID")
    detail_level: FeedbackDetailLevel = Field(FeedbackDetailLevel.STANDARD, description="Detail level")
    tone: FeedbackTone = Field(FeedbackTone.PROFESSIONAL, description="Feedback tone")
    include_learning_path: bool = Field(True, description="Include progressive learning path")
    include_history_analysis: bool = Field(True, description="Include historical analysis")
    max_suggestions: int = Field(5, ge=1, le=20, description="Maximum suggestions")


class PersonalizedFeedback(BaseModel):
    """Complete personalized feedback with history context."""
    feedback_id: str = Field(..., description="Unique feedback ID")
    student_id: str = Field(..., description="Student ID")
    submission_id: Optional[str] = Field(None)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Core feedback
    overall_score: float = Field(..., ge=0, le=100)
    overall_grade: str = Field(..., description="Letter grade A-F")
    summary: str = Field(..., description="Overall feedback summary")
    summary_zh: str = Field(..., description="Summary in Chinese")

    # Personalization
    personalized_message: str = Field(..., description="Personalized message based on history")
    personalized_message_zh: str = Field(..., description="Personalized message in Chinese")

    # History analysis
    history_analysis: Optional[StudentHistoryAnalysis] = Field(None)

    # Categorized feedback
    categories: List[CategoryFeedback] = Field(default_factory=list)

    # Progressive suggestions
    suggestions: List[ProgressiveSuggestion] = Field(default_factory=list)
    learning_path: Optional[LearningPath] = Field(None)

    # Encouragement
    encouragement: str = Field("", description="Encouraging message")
    encouragement_zh: str = Field("", description="Encouragement in Chinese")

    # Metadata
    tone: FeedbackTone = Field(FeedbackTone.PROFESSIONAL)
    detail_level: FeedbackDetailLevel = Field(FeedbackDetailLevel.STANDARD)
    language: str = Field("python")


class PersonalizedFeedbackResponse(BaseModel):
    """Response for personalized feedback generation."""
    success: bool = Field(True)
    feedback: PersonalizedFeedback
    message: str = Field("个性化评语生成成功")
    processing_time_ms: Optional[float] = Field(None)


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
    tone: Optional[TemplateTone] = Field(TemplateTone.NEUTRAL, description="Template tone variant")
    locale: Optional[str] = Field("en", description="Template locale (e.g., 'en', 'zh-CN')")


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
    tone: Optional[TemplateTone] = None
    locale: Optional[str] = None


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


class TemplateSearchRequest(BaseModel):
    """Request for advanced template search."""
    query: Optional[str] = Field(None, description="Search query for name, title, message, tags")
    categories: Optional[List[TemplateCategory]] = Field(None, description="Filter by categories")
    languages: Optional[List[str]] = Field(None, description="Filter by languages")
    tones: Optional[List[TemplateTone]] = Field(None, description="Filter by tones")
    locales: Optional[List[str]] = Field(None, description="Filter by locales")
    severities: Optional[List[str]] = Field(None, description="Filter by severities")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (any match)")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    min_usage_count: Optional[int] = Field(None, ge=0, description="Minimum usage count")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field("name", description="Sort field: name, usage_count, created_at")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc, desc")


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


