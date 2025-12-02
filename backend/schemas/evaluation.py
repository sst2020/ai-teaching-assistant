"""
Pydantic schemas for multi-dimensional evaluation system.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class EvaluationDimension(str, Enum):
    """Dimensions for code evaluation."""
    TECHNICAL_ABILITY = "technical_ability"       # 技术能力
    CODE_QUALITY = "code_quality"                 # 代码质量
    INNOVATION = "innovation"                     # 创新性
    BEST_PRACTICES = "best_practices"             # 最佳实践
    EFFICIENCY = "efficiency"                     # 效率
    DOCUMENTATION = "documentation"               # 文档


# Dimension metadata with Chinese translations
DIMENSION_METADATA = {
    EvaluationDimension.TECHNICAL_ABILITY: {
        "name": "Technical Ability",
        "name_zh": "技术能力",
        "description": "Demonstrates understanding of programming concepts and language features",
        "description_zh": "展示对编程概念和语言特性的理解",
        "weight": 0.20,
    },
    EvaluationDimension.CODE_QUALITY: {
        "name": "Code Quality",
        "name_zh": "代码质量",
        "description": "Code structure, readability, and maintainability",
        "description_zh": "代码结构、可读性和可维护性",
        "weight": 0.25,
    },
    EvaluationDimension.INNOVATION: {
        "name": "Innovation",
        "name_zh": "创新性",
        "description": "Creative problem-solving and unique approaches",
        "description_zh": "创造性解决问题和独特方法",
        "weight": 0.10,
    },
    EvaluationDimension.BEST_PRACTICES: {
        "name": "Best Practices",
        "name_zh": "最佳实践",
        "description": "Following industry standards and conventions",
        "description_zh": "遵循行业标准和规范",
        "weight": 0.20,
    },
    EvaluationDimension.EFFICIENCY: {
        "name": "Efficiency",
        "name_zh": "效率",
        "description": "Algorithm efficiency and resource usage",
        "description_zh": "算法效率和资源使用",
        "weight": 0.15,
    },
    EvaluationDimension.DOCUMENTATION: {
        "name": "Documentation",
        "name_zh": "文档",
        "description": "Code comments, docstrings, and documentation quality",
        "description_zh": "代码注释、文档字符串和文档质量",
        "weight": 0.10,
    },
}


class DimensionScore(BaseModel):
    """Score for a single evaluation dimension."""
    dimension: EvaluationDimension = Field(..., description="Evaluation dimension")
    score: float = Field(..., ge=0, le=100, description="Score 0-100")
    weight: float = Field(..., ge=0, le=1, description="Weight in overall score")
    name: str = Field(..., description="Dimension name")
    name_zh: str = Field(..., description="Dimension name in Chinese")
    description: str = Field("", description="Score explanation")
    description_zh: str = Field("", description="Explanation in Chinese")
    strengths: List[str] = Field(default_factory=list, description="Strengths in this dimension")
    strengths_zh: List[str] = Field(default_factory=list, description="Strengths in Chinese")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    improvements_zh: List[str] = Field(default_factory=list, description="Improvements in Chinese")


class RadarChartData(BaseModel):
    """Data for radar chart visualization."""
    labels: List[str] = Field(..., description="Dimension labels")
    labels_zh: List[str] = Field(..., description="Labels in Chinese")
    student_scores: List[float] = Field(..., description="Student's scores")
    class_average: Optional[List[float]] = Field(None, description="Class average scores")
    max_scores: List[float] = Field(default_factory=lambda: [100] * 6, description="Maximum scores")


class ClassComparison(BaseModel):
    """Comparison with class statistics."""
    student_id: str = Field(..., description="Student ID")
    student_overall: float = Field(..., description="Student's overall score")
    class_average: float = Field(..., description="Class average score")
    class_median: float = Field(..., description="Class median score")
    class_max: float = Field(..., description="Class maximum score")
    class_min: float = Field(..., description="Class minimum score")
    percentile: float = Field(..., description="Student's percentile rank")
    rank: int = Field(..., description="Student's rank in class")
    total_students: int = Field(..., description="Total students in class")
    dimension_comparisons: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Per-dimension comparison with class"
    )


class AbilityAnalysisReport(BaseModel):
    """Comprehensive ability analysis report."""
    report_id: str = Field(..., description="Unique report ID")
    student_id: str = Field(..., description="Student ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Overall assessment
    overall_score: float = Field(..., ge=0, le=100)
    overall_grade: str = Field(..., description="Letter grade A-F")
    overall_summary: str = Field(..., description="Overall summary")
    overall_summary_zh: str = Field(..., description="Summary in Chinese")
    
    # Dimension scores
    dimension_scores: List[DimensionScore] = Field(default_factory=list)
    
    # Radar chart data
    radar_chart: RadarChartData = Field(...)
    
    # Class comparison (optional)
    class_comparison: Optional[ClassComparison] = Field(None)
    
    # Recommendations
    top_strengths: List[str] = Field(default_factory=list)
    top_strengths_zh: List[str] = Field(default_factory=list)
    priority_improvements: List[str] = Field(default_factory=list)
    priority_improvements_zh: List[str] = Field(default_factory=list)
    
    # Learning recommendations
    recommended_focus_areas: List[str] = Field(default_factory=list)
    recommended_focus_areas_zh: List[str] = Field(default_factory=list)


class MultiDimensionalEvaluationRequest(BaseModel):
    """Request for multi-dimensional evaluation."""
    code: str = Field(..., description="Source code to evaluate")
    language: str = Field("python", description="Programming language")
    student_id: str = Field(..., description="Student ID")
    assignment_id: Optional[str] = Field(None, description="Assignment ID")
    include_class_comparison: bool = Field(False, description="Include class comparison")
    class_id: Optional[str] = Field(None, description="Class ID for comparison")


class MultiDimensionalEvaluationResponse(BaseModel):
    """Response for multi-dimensional evaluation."""
    success: bool = Field(True)
    report: AbilityAnalysisReport
    message: str = Field("多维度评估完成")
    processing_time_ms: Optional[float] = Field(None)

