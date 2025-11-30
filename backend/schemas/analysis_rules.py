"""
Schemas for Code Analysis Rules and Results
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RuleSeverity(str, Enum):
    """Severity levels for analysis rules."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RuleCategory(str, Enum):
    """Categories for analysis rules."""
    STYLE = "style"
    COMPLEXITY = "complexity"
    BEST_PRACTICES = "best_practices"
    SECURITY = "security"
    NAMING = "naming"
    STRUCTURE = "structure"


class SupportedLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    JSX = "jsx"
    TSX = "tsx"
    ALL = "all"


# ============================================
# Rule Configuration Schemas
# ============================================

class RuleThreshold(BaseModel):
    """Configurable threshold for a rule."""
    name: str = Field(..., description="Threshold name")
    value: Any = Field(..., description="Threshold value")
    description: Optional[str] = Field(None, description="Threshold description")


class AnalysisRule(BaseModel):
    """Definition of a single analysis rule."""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    description: str = Field(..., description="Rule description")
    category: RuleCategory = Field(..., description="Rule category")
    severity: RuleSeverity = Field(RuleSeverity.WARNING, description="Default severity")
    enabled: bool = Field(True, description="Whether rule is enabled")
    languages: List[SupportedLanguage] = Field(
        default_factory=lambda: [SupportedLanguage.ALL],
        description="Languages this rule applies to"
    )
    thresholds: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configurable thresholds"
    )
    weight: float = Field(1.0, ge=0, le=10, description="Weight for scoring")


class RuleSet(BaseModel):
    """Collection of analysis rules."""
    name: str = Field(..., description="Rule set name")
    description: Optional[str] = Field(None, description="Rule set description")
    version: str = Field("1.0.0", description="Rule set version")
    rules: List[AnalysisRule] = Field(default_factory=list, description="List of rules")


class RuleConfiguration(BaseModel):
    """User-configurable rule settings."""
    rule_id: str = Field(..., description="Rule ID to configure")
    enabled: Optional[bool] = Field(None, description="Override enabled state")
    severity: Optional[RuleSeverity] = Field(None, description="Override severity")
    thresholds: Optional[Dict[str, Any]] = Field(None, description="Override thresholds")


# ============================================
# Violation Schemas
# ============================================

class RuleViolation(BaseModel):
    """A single rule violation found during analysis."""
    rule_id: str = Field(..., description="ID of violated rule")
    rule_name: str = Field(..., description="Name of violated rule")
    category: RuleCategory = Field(..., description="Rule category")
    severity: RuleSeverity = Field(..., description="Violation severity")
    line: int = Field(..., description="Line number")
    column: int = Field(0, description="Column number")
    end_line: Optional[int] = Field(None, description="End line number")
    end_column: Optional[int] = Field(None, description="End column number")
    message: str = Field(..., description="Violation message")
    suggestion: Optional[str] = Field(None, description="Fix suggestion")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")


# ============================================
# Metrics Schemas
# ============================================

class NamingConventionResult(BaseModel):
    """Results of naming convention checks."""
    total_identifiers: int = Field(0, description="Total identifiers checked")
    violations: int = Field(0, description="Number of violations")
    details: List[RuleViolation] = Field(default_factory=list)


class ComplexityResult(BaseModel):
    """Detailed complexity analysis results."""
    cyclomatic_complexity: float = Field(0, description="Average cyclomatic complexity")
    max_cyclomatic_complexity: int = Field(0, description="Maximum cyclomatic complexity")
    cognitive_complexity: float = Field(0, description="Average cognitive complexity")
    max_nesting_depth: int = Field(0, description="Maximum nesting depth")
    avg_nesting_depth: float = Field(0, description="Average nesting depth")
    total_functions: int = Field(0, description="Total number of functions")
    complex_functions: int = Field(0, description="Functions exceeding complexity threshold")
    avg_function_length: float = Field(0, description="Average function length in lines")
    max_function_length: int = Field(0, description="Maximum function length")
    avg_parameters: float = Field(0, description="Average parameters per function")
    max_parameters: int = Field(0, description="Maximum parameters in a function")


class LineMetrics(BaseModel):
    """Line-based code metrics."""
    total_lines: int = Field(0, description="Total lines")
    code_lines: int = Field(0, description="Lines of code")
    comment_lines: int = Field(0, description="Comment lines")
    blank_lines: int = Field(0, description="Blank lines")
    docstring_lines: int = Field(0, description="Docstring lines")
    comment_ratio: float = Field(0, description="Comment to code ratio percentage")



# ============================================
# Category Scores
# ============================================

class CategoryScore(BaseModel):
    """Score for a specific category."""
    category: RuleCategory = Field(..., description="Category name")
    score: float = Field(..., ge=0, le=100, description="Category score")
    violations: int = Field(0, description="Number of violations")
    weight: float = Field(1.0, description="Category weight in overall score")


# ============================================
# Analysis Result Schemas
# ============================================

class AnalysisResultSummary(BaseModel):
    """Summary of analysis results."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall quality score")
    grade: str = Field(..., description="Letter grade (A-F)")
    category_scores: List[CategoryScore] = Field(default_factory=list)
    total_violations: int = Field(0, description="Total violations found")
    critical_violations: int = Field(0, description="Critical/error violations")
    warnings: int = Field(0, description="Warning violations")
    info_violations: int = Field(0, description="Info violations")


class FullAnalysisResult(BaseModel):
    """Complete analysis result with all details."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    file_id: Optional[str] = Field(None, description="Associated file ID")
    language: str = Field(..., description="Programming language")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")

    # Summary
    summary: AnalysisResultSummary = Field(..., description="Analysis summary")

    # Detailed Metrics
    line_metrics: LineMetrics = Field(default_factory=LineMetrics)
    complexity: ComplexityResult = Field(default_factory=ComplexityResult)
    structure: StructureResult = Field(default_factory=StructureResult)
    naming: NamingConventionResult = Field(default_factory=NamingConventionResult)

    # All Violations
    violations: List[RuleViolation] = Field(default_factory=list)

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)

    # Comparison data (for multiple submissions)
    comparison_metrics: Optional[Dict[str, Any]] = Field(None)


class AnalysisRequest(BaseModel):
    """Request to analyze code."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language")
    file_id: Optional[str] = Field(None, description="Associated file ID")
    rule_overrides: List[RuleConfiguration] = Field(
        default_factory=list,
        description="Rule configuration overrides"
    )
    include_suggestions: bool = Field(True, description="Include fix suggestions")


class BatchAnalysisRequest(BaseModel):
    """Request to analyze multiple files."""
    file_ids: List[str] = Field(..., description="List of file IDs to analyze")
    rule_overrides: List[RuleConfiguration] = Field(default_factory=list)
    generate_comparison: bool = Field(False, description="Generate comparison metrics")


class AnalysisResultResponse(BaseModel):
    """API response for analysis result."""
    success: bool = Field(True)
    result: FullAnalysisResult
    message: str = Field("Analysis completed successfully")


class BatchAnalysisResponse(BaseModel):
    """API response for batch analysis."""
    success: bool = Field(True)
    results: List[FullAnalysisResult] = Field(default_factory=list)
    summary: Optional[Dict[str, Any]] = Field(None, description="Aggregate summary")
    message: str = Field("Batch analysis completed")
