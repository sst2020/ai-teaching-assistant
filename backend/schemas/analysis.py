"""
Schemas for advanced code analysis results.

This module defines Pydantic models for:
- Code quality analysis (cyclomatic/cognitive complexity, maintainability index)
- Linting results (Pylint integration)
- Security analysis (Bandit integration)
- Performance analysis
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class ComplexityGrade(str, Enum):
    """Complexity grade based on cyclomatic complexity."""
    A = "A"  # 1-5: Simple, low risk
    B = "B"  # 6-10: More complex, moderate risk
    C = "C"  # 11-20: Complex, high risk
    D = "D"  # 21-30: Very complex, very high risk
    E = "E"  # 31-40: Untestable, extremely high risk
    F = "F"  # 41+: Error-prone, unmaintainable


class MaintainabilityRating(str, Enum):
    """Maintainability rating based on MI score."""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"           # 60-79
    MODERATE = "moderate"   # 40-59
    POOR = "poor"           # 20-39
    VERY_POOR = "very_poor" # 0-19


class IssueSeverity(str, Enum):
    """Severity level for issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONVENTION = "convention"
    REFACTOR = "refactor"


class SecuritySeverity(str, Enum):
    """Security issue severity."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PerformanceIssueType(str, Enum):
    """Types of performance issues."""
    INFINITE_LOOP = "infinite_loop"
    INEFFICIENT_ALGORITHM = "inefficient_algorithm"
    GLOBAL_VARIABLE = "global_variable"
    LARGE_FILE_READ = "large_file_read"
    BLOCKING_OPERATION = "blocking_operation"
    MEMORY_LEAK = "memory_leak"
    REPEATED_COMPUTATION = "repeated_computation"
    NESTED_LOOP_LOOKUP = "nested_loop_lookup"


# ============================================
# Code Quality Analysis Schemas
# ============================================

class FunctionComplexity(BaseModel):
    """Complexity metrics for a single function."""
    name: str = Field(..., description="Function name")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")
    cyclomatic_complexity: int = Field(..., description="Cyclomatic complexity score")
    cognitive_complexity: int = Field(0, description="Cognitive complexity score")
    grade: ComplexityGrade = Field(..., description="Complexity grade (A-F)")
    is_complex: bool = Field(False, description="Whether function exceeds complexity threshold")
    nesting_depth: int = Field(0, description="Maximum nesting depth")
    parameters: int = Field(0, description="Number of parameters")
    lines_of_code: int = Field(0, description="Lines of code in function")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class DuplicateCodeBlock(BaseModel):
    """Information about a duplicate code block."""
    block_id: int = Field(..., description="Unique identifier for this duplicate group")
    lines: List[int] = Field(..., description="Line numbers where duplicates occur")
    code_snippet: str = Field(..., description="The duplicated code snippet")
    similarity: float = Field(..., ge=0, le=100, description="Similarity percentage")
    suggestion: str = Field("", description="Refactoring suggestion")


class CodeQualityMetrics(BaseModel):
    """Overall code quality metrics."""
    # Cyclomatic Complexity
    avg_cyclomatic_complexity: float = Field(0, description="Average cyclomatic complexity")
    max_cyclomatic_complexity: int = Field(0, description="Maximum cyclomatic complexity")
    total_functions: int = Field(0, description="Total number of functions")
    complex_functions: int = Field(0, description="Functions with complexity > 10")
    
    # Cognitive Complexity
    avg_cognitive_complexity: float = Field(0, description="Average cognitive complexity")
    max_cognitive_complexity: int = Field(0, description="Maximum cognitive complexity")
    deep_nesting_count: int = Field(0, description="Functions with nesting > 4")
    
    # Maintainability Index
    maintainability_index: float = Field(0, ge=0, le=100, description="Maintainability index (0-100)")
    maintainability_rating: MaintainabilityRating = Field(
        MaintainabilityRating.MODERATE, description="Maintainability rating"
    )
    
    # Code Duplication
    duplicate_blocks: int = Field(0, description="Number of duplicate code blocks")
    duplication_percentage: float = Field(0, ge=0, le=100, description="Percentage of duplicated code")
    
    # Lines Metrics
    total_lines: int = Field(0, description="Total lines of code")
    code_lines: int = Field(0, description="Lines of actual code")
    comment_lines: int = Field(0, description="Lines of comments")
    blank_lines: int = Field(0, description="Blank lines")
    comment_ratio: float = Field(0, description="Comment to code ratio percentage")


class CodeQualityResult(BaseModel):
    """Complete code quality analysis result."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    language: str = Field("python", description="Programming language")
    
    # Overall Score
    score: float = Field(..., ge=0, le=100, description="Overall quality score")
    grade: str = Field(..., description="Letter grade (A-F)")
    
    # Metrics
    metrics: CodeQualityMetrics = Field(..., description="Quality metrics")
    
    # Function-level Analysis
    functions: List[FunctionComplexity] = Field(default_factory=list, description="Per-function analysis")
    
    # Duplicate Code
    duplicates: List[DuplicateCodeBlock] = Field(default_factory=list, description="Duplicate code blocks")
    
    # Issues
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Quality issues found")
    
    # Summary and Recommendations
    summary: str = Field("", description="Analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


# ============================================
# Linter Analysis Schemas
# ============================================

class LintIssue(BaseModel):
    """A single linting issue."""
    rule_id: str = Field(..., description="Rule identifier (e.g., C0301)")
    rule_name: str = Field("", description="Human-readable rule name")
    category: str = Field(..., description="Issue category (convention, refactor, warning, error)")
    severity: IssueSeverity = Field(..., description="Issue severity")
    line: int = Field(..., description="Line number")
    column: int = Field(0, description="Column number")
    message: str = Field(..., description="Issue message")
    message_zh: str = Field("", description="Issue message in Chinese")
    suggestion: str = Field("", description="Fix suggestion")
    code_snippet: str = Field("", description="Relevant code snippet")


class LintRuleConfig(BaseModel):
    """Configuration for a linting rule."""
    rule_id: str = Field(..., description="Rule identifier")
    enabled: bool = Field(True, description="Whether rule is enabled")
    severity: IssueSeverity = Field(IssueSeverity.WARNING, description="Rule severity")
    options: Dict[str, Any] = Field(default_factory=dict, description="Rule-specific options")


class LintResult(BaseModel):
    """Complete linting analysis result."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    language: str = Field("python", description="Programming language")
    linter: str = Field("pylint", description="Linter used")

    # Overall Score
    score: float = Field(..., ge=0, le=100, description="Linting score")

    # Issues by Category
    total_issues: int = Field(0, description="Total issues found")
    errors: int = Field(0, description="Error count")
    warnings: int = Field(0, description="Warning count")
    conventions: int = Field(0, description="Convention violation count")
    refactors: int = Field(0, description="Refactor suggestion count")

    # Detailed Issues
    issues: List[LintIssue] = Field(default_factory=list, description="All linting issues")

    # Summary
    summary: str = Field("", description="Analysis summary")


# ============================================
# Security Analysis Schemas
# ============================================

class SecurityIssue(BaseModel):
    """A security vulnerability or issue."""
    issue_id: str = Field(..., description="Issue identifier")
    test_id: str = Field(..., description="Bandit test ID (e.g., B101)")
    test_name: str = Field(..., description="Test name")
    severity: SecuritySeverity = Field(..., description="Issue severity")
    confidence: str = Field(..., description="Confidence level (HIGH, MEDIUM, LOW)")
    line: int = Field(..., description="Line number")
    column: int = Field(0, description="Column number")
    code_snippet: str = Field("", description="Vulnerable code snippet")
    issue_text: str = Field(..., description="Issue description")
    issue_text_zh: str = Field("", description="Issue description in Chinese")
    more_info: str = Field("", description="Link to more information")
    recommendation: str = Field("", description="How to fix the issue")


class SecurityResult(BaseModel):
    """Complete security analysis result."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    language: str = Field("python", description="Programming language")

    # Overall Score
    score: float = Field(..., ge=0, le=100, description="Security score")

    # Issue Counts
    total_issues: int = Field(0, description="Total security issues")
    high_severity: int = Field(0, description="High severity issues")
    medium_severity: int = Field(0, description="Medium severity issues")
    low_severity: int = Field(0, description="Low severity issues")

    # Detailed Issues
    issues: List[SecurityIssue] = Field(default_factory=list, description="All security issues")

    # Summary
    summary: str = Field("", description="Security analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")


# ============================================
# Performance Analysis Schemas
# ============================================

class PerformanceIssue(BaseModel):
    """A performance issue or anti-pattern."""
    issue_type: PerformanceIssueType = Field(..., description="Type of performance issue")
    severity: IssueSeverity = Field(..., description="Issue severity")
    line: int = Field(..., description="Line number")
    column: int = Field(0, description="Column number")
    code_snippet: str = Field("", description="Problematic code snippet")
    description: str = Field(..., description="Issue description")
    description_zh: str = Field("", description="Issue description in Chinese")
    impact: str = Field("", description="Performance impact")
    suggestion: str = Field("", description="How to fix the issue")


class BestPracticeViolation(BaseModel):
    """A best practice violation."""
    category: str = Field(..., description="Violation category")
    rule: str = Field(..., description="Best practice rule")
    severity: IssueSeverity = Field(..., description="Violation severity")
    line: int = Field(..., description="Line number")
    description: str = Field(..., description="Violation description")
    description_zh: str = Field("", description="Description in Chinese")
    suggestion: str = Field("", description="How to fix")


class PerformanceResult(BaseModel):
    """Complete performance analysis result."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    language: str = Field("python", description="Programming language")

    # Overall Score
    score: float = Field(..., ge=0, le=100, description="Performance score")

    # Issue Counts
    total_issues: int = Field(0, description="Total performance issues")

    # Detailed Issues
    performance_issues: List[PerformanceIssue] = Field(
        default_factory=list, description="Performance issues"
    )
    best_practice_violations: List[BestPracticeViolation] = Field(
        default_factory=list, description="Best practice violations"
    )

    # Summary
    summary: str = Field("", description="Performance analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="Performance recommendations")


# ============================================
# Comprehensive Analysis Schema
# ============================================

class ComprehensiveAnalysisResult(BaseModel):
    """Complete comprehensive analysis combining all analysis types."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    language: str = Field("python", description="Programming language")

    # Overall Score
    overall_score: float = Field(..., ge=0, le=100, description="Overall score")
    grade: str = Field(..., description="Letter grade (A-F)")

    # Individual Results
    quality: Optional[CodeQualityResult] = Field(None, description="Code quality analysis")
    lint: Optional[LintResult] = Field(None, description="Linting analysis")
    security: Optional[SecurityResult] = Field(None, description="Security analysis")
    performance: Optional[PerformanceResult] = Field(None, description="Performance analysis")

    # Summary
    summary: str = Field("", description="Comprehensive analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="All recommendations")

    # Metrics Summary
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Combined metrics")


# ============================================
# Request Schemas
# ============================================

class AnalysisCodeRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    filename: Optional[str] = Field(None, description="Optional filename for context")
    timeout: int = Field(30, ge=5, le=120, description="Analysis timeout in seconds")


class LintRequest(BaseModel):
    """Request for linting analysis."""
    code: str = Field(..., description="Source code to lint")
    language: str = Field("python", description="Programming language")
    rules: List[LintRuleConfig] = Field(default_factory=list, description="Rule configurations")
    config_file: Optional[str] = Field(None, description="Path to linter config file")


class SecurityRequest(BaseModel):
    """Request for security analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    severity_threshold: SecuritySeverity = Field(
        SecuritySeverity.LOW, description="Minimum severity to report"
    )


class PerformanceRequest(BaseModel):
    """Request for performance analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    check_best_practices: bool = Field(True, description="Include best practices check")


class ComprehensiveRequest(BaseModel):
    """Request for comprehensive analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    include_quality: bool = Field(True, description="Include quality analysis")
    include_lint: bool = Field(True, description="Include linting")
    include_security: bool = Field(True, description="Include security analysis")
    include_performance: bool = Field(True, description="Include performance analysis")
    timeout: int = Field(30, ge=5, le=120, description="Analysis timeout in seconds")

