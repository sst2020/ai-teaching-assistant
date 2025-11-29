"""
Schemas for Code Static Analysis Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class IssueSeverity(str, Enum):
    """Severity levels for code issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONVENTION = "convention"
    REFACTOR = "refactor"


class CodeIssue(BaseModel):
    """Individual code issue found during analysis."""
    line: int = Field(..., description="Line number where issue occurs")
    column: int = Field(0, description="Column number where issue occurs")
    code: str = Field(..., description="Issue code (e.g., E501, W291)")
    message: str = Field(..., description="Description of the issue")
    severity: IssueSeverity = Field(..., description="Severity level")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class ComplexityMetrics(BaseModel):
    """Code complexity metrics."""
    cyclomatic_complexity: float = Field(..., description="McCabe cyclomatic complexity")
    cognitive_complexity: float = Field(0, description="Cognitive complexity score")
    maintainability_index: float = Field(..., ge=0, le=100, description="Maintainability index (0-100)")
    lines_of_code: int = Field(..., description="Total lines of code")
    logical_lines: int = Field(..., description="Logical lines of code")
    comment_lines: int = Field(..., description="Number of comment lines")
    blank_lines: int = Field(..., description="Number of blank lines")
    comment_ratio: float = Field(..., ge=0, le=100, description="Percentage of comments")


class FunctionAnalysis(BaseModel):
    """Analysis of individual function."""
    name: str = Field(..., description="Function name")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")
    complexity: int = Field(..., description="Cyclomatic complexity")
    parameters: int = Field(..., description="Number of parameters")
    is_too_complex: bool = Field(False, description="Whether function exceeds complexity threshold")
    issues: List[str] = Field(default_factory=list, description="Issues specific to this function")


class CodeSmell(BaseModel):
    """Detected code smell."""
    type: str = Field(..., description="Type of code smell")
    description: str = Field(..., description="Description of the smell")
    location: str = Field(..., description="Location in code")
    severity: IssueSeverity = Field(..., description="Severity level")
    refactoring_suggestion: str = Field("", description="Suggested refactoring")


class StyleAnalysisResult(BaseModel):
    """PEP 8 style analysis result."""
    is_compliant: bool = Field(..., description="Whether code is PEP 8 compliant")
    total_issues: int = Field(..., description="Total number of style issues")
    issues: List[CodeIssue] = Field(default_factory=list, description="List of style issues")
    score: float = Field(..., ge=0, le=100, description="Style compliance score")


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    include_complexity: bool = Field(True, description="Include complexity analysis")
    include_style: bool = Field(True, description="Include style analysis")
    include_smells: bool = Field(True, description="Include code smell detection")


class CodeAnalysisResult(BaseModel):
    """Complete code analysis result."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    language: str = Field(..., description="Programming language analyzed")
    analyzed_at: datetime = Field(..., description="Timestamp of analysis")
    
    # Style Analysis
    style_analysis: Optional[StyleAnalysisResult] = None
    
    # Complexity Metrics
    complexity_metrics: Optional[ComplexityMetrics] = None
    
    # Function-level Analysis
    functions: List[FunctionAnalysis] = Field(default_factory=list)
    
    # Code Smells
    code_smells: List[CodeSmell] = Field(default_factory=list)
    
    # Overall Scores
    overall_quality_score: float = Field(..., ge=0, le=100, description="Overall code quality score")
    
    # Summary
    summary: str = Field("", description="Human-readable summary of analysis")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

