"""
Schemas for Assignment Review Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AssignmentType(str, Enum):
    """Types of assignments."""
    CODE = "code"
    ESSAY = "essay"
    QUIZ = "quiz"
    PROJECT = "project"


class GradingStatus(str, Enum):
    """Status of grading process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgrammingLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class AssignmentSubmission(BaseModel):
    """Schema for submitting an assignment for review."""
    student_id: str = Field(..., description="Unique identifier for the student")
    assignment_id: str = Field(..., description="Unique identifier for the assignment")
    assignment_type: AssignmentType = Field(..., description="Type of assignment")
    content: Optional[str] = Field(None, description="Text content of the assignment")
    file_name: Optional[str] = Field(None, description="Name of uploaded file")
    language: ProgrammingLanguage = Field(ProgrammingLanguage.PYTHON, description="Programming language")
    expected_output: Optional[str] = Field(None, description="Expected output for correctness testing")
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="Test cases for validation")


class CodeQualityMetrics(BaseModel):
    """Detailed code quality metrics from static analysis."""
    cyclomatic_complexity: float = Field(0, description="Code complexity score")
    maintainability_index: float = Field(0, ge=0, le=100, description="Maintainability score")
    lines_of_code: int = Field(0, description="Total lines of code")
    comment_ratio: float = Field(0, ge=0, le=100, description="Percentage of comments")
    pep8_issues: int = Field(0, description="Number of PEP8 style violations")
    code_smells_count: int = Field(0, description="Number of code smells detected")


class CodeFeedback(BaseModel):
    """Feedback for code assignments."""
    correctness_score: float = Field(..., ge=0, le=100, description="Score for code correctness")
    style_score: float = Field(..., ge=0, le=100, description="Score for code style")
    efficiency_score: float = Field(..., ge=0, le=100, description="Score for code efficiency")
    readability_score: float = Field(0, ge=0, le=100, description="Score for code readability")
    comments: List[str] = Field(default_factory=list, description="Detailed feedback comments")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    quality_metrics: Optional[CodeQualityMetrics] = Field(None, description="Detailed quality metrics")
    line_comments: Dict[int, List[str]] = Field(default_factory=dict, description="Comments for specific lines")
    ai_feedback: Optional[str] = Field(None, description="AI-generated personalized feedback")


class ReportFeedback(BaseModel):
    """Feedback for report/project assignments."""
    completeness_score: float = Field(..., ge=0, le=100, description="Score for completeness")
    innovation_score: float = Field(..., ge=0, le=100, description="Score for innovation")
    clarity_score: float = Field(..., ge=0, le=100, description="Score for clarity")
    comments: List[str] = Field(default_factory=list, description="Detailed feedback comments")
    revision_suggestions: List[str] = Field(default_factory=list, description="Revision suggestions")


class PlagiarismResult(BaseModel):
    """Result of plagiarism detection."""
    similarity_score: float = Field(..., ge=0, le=100, description="Overall similarity percentage")
    is_plagiarized: bool = Field(..., description="Whether plagiarism is detected")
    similar_sources: List[dict] = Field(default_factory=list, description="List of similar sources found")
    analysis_details: str = Field("", description="Detailed analysis explanation")


class GradingResult(BaseModel):
    """Complete grading result for an assignment."""
    submission_id: str
    student_id: str
    assignment_id: str
    assignment_type: AssignmentType
    overall_score: float = Field(..., ge=0, le=100)
    status: GradingStatus
    code_feedback: Optional[CodeFeedback] = None
    report_feedback: Optional[ReportFeedback] = None
    plagiarism_result: Optional[PlagiarismResult] = None
    graded_at: datetime
    feedback_summary: str = Field("", description="AI-generated summary of feedback")


class BatchGradingRequest(BaseModel):
    """Request for batch grading multiple assignments."""
    assignment_id: str = Field(..., description="Assignment identifier")
    submissions: List[AssignmentSubmission] = Field(..., description="List of submissions to grade")


class BatchGradingResponse(BaseModel):
    """Response for batch grading request."""
    batch_id: str
    total_submissions: int
    status: GradingStatus
    results: List[GradingResult] = Field(default_factory=list)

