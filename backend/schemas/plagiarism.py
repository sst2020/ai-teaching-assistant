"""
Schemas for Plagiarism Detection Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class SimilarityLevel(str, Enum):
    """Levels of similarity detection."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MatchType(str, Enum):
    """Types of code matching."""
    EXACT = "exact"
    STRUCTURAL = "structural"  # AST structure match
    TOKEN_SEQUENCE = "token_sequence"  # Token pattern match
    RENAMED = "renamed"  # Same structure, different variable names
    PARTIAL = "partial"


class CodeMatch(BaseModel):
    """A matched code segment between two submissions."""
    match_type: MatchType = Field(..., description="Type of match detected")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    code_snippet_1: str = Field("", description="Code snippet from first submission")
    code_snippet_2: str = Field("", description="Code snippet from second submission")
    line_range_1: tuple = Field((1, 1), description="Line range in first submission")
    line_range_2: tuple = Field((1, 1), description="Line range in second submission")
    explanation: str = Field("", description="Explanation of the match")


class SubmissionComparison(BaseModel):
    """Comparison result between two submissions."""
    submission_id_1: str = Field(..., description="First submission ID")
    submission_id_2: str = Field(..., description="Second submission ID")
    student_id_1: str = Field(..., description="First student ID")
    student_id_2: str = Field(..., description="Second student ID")
    similarity_score: float = Field(..., ge=0, le=1, description="Overall similarity (0-1)")
    matches: List[CodeMatch] = Field(default_factory=list, description="List of matching segments")
    analysis_notes: str = Field("", description="Analysis notes")


class PlagiarismCheckRequest(BaseModel):
    """Request for plagiarism check."""
    submission_id: str = Field(..., description="Submission ID")
    student_id: str = Field(..., description="Student ID of submission to check")
    course_id: str = Field(..., description="Course ID")
    code: str = Field(..., description="Code to check for plagiarism")
    compare_with_history: bool = Field(True, description="Compare with historical submissions")
    similarity_threshold: float = Field(0.7, ge=0, le=1, description="Threshold for flagging (0-1)")


class PlagiarismReport(BaseModel):
    """Comprehensive plagiarism detection report."""
    report_id: str = Field(..., description="Unique report identifier")
    submission_id: str = Field(..., description="Submission ID checked")
    checked_at: datetime = Field(..., description="Timestamp of check")

    # Overall Results
    overall_similarity: float = Field(..., ge=0, le=1, description="Highest similarity found (0-1)")
    similarity_level: SimilarityLevel = Field(..., description="Overall similarity level")
    is_flagged: bool = Field(..., description="Whether submission is flagged")

    # Detailed Comparisons
    comparisons: List[SubmissionComparison] = Field(default_factory=list)

    # Summary
    summary: str = Field("", description="Human-readable summary")


class SubmissionRecord(BaseModel):
    """Record of a submission for plagiarism database."""
    submission_id: str = Field(..., description="Unique submission ID")
    student_id: str = Field(..., description="Student ID")
    assignment_id: str = Field(..., description="Assignment ID")
    code: str = Field(..., description="Submitted code")
    code_hash: str = Field(..., description="Hash of normalized code")
    ast_fingerprint: str = Field(..., description="AST-based fingerprint")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    token_sequence: List[str] = Field(default_factory=list, description="Tokenized code sequence")


class BatchPlagiarismRequest(BaseModel):
    """Request for batch plagiarism check."""
    assignment_id: str = Field(..., description="Assignment ID")
    submissions: List[PlagiarismCheckRequest] = Field(..., description="List of submissions to check")
    cross_compare: bool = Field(True, description="Compare submissions against each other")


class BatchPlagiarismReport(BaseModel):
    """Batch plagiarism check report."""
    report_id: str = Field(..., description="Unique report ID")
    course_id: str = Field(..., description="Course ID")
    checked_at: datetime = Field(..., description="Timestamp of check")
    total_submissions: int = Field(..., description="Total submissions checked")
    flagged_pairs: int = Field(..., description="Number of flagged pairs")
    comparisons: List[SubmissionComparison] = Field(default_factory=list)
    summary: str = Field("", description="Summary of batch check")


# ============================================
# 新增：增强的查重与原创性分析类型
# ============================================

class SimilarityAlgorithm(str, Enum):
    """相似度计算算法类型"""
    AST = "ast"                    # AST结构相似度
    LEVENSHTEIN = "levenshtein"    # 编辑距离算法
    COSINE = "cosine"              # 余弦相似度（TF-IDF）
    TOKEN = "token"                # Token序列相似度
    COMBINED = "combined"          # 综合算法


class CodeTransformationType(str, Enum):
    """代码变换类型"""
    VARIABLE_RENAME = "variable_rename"      # 变量重命名
    FUNCTION_RENAME = "function_rename"      # 函数重命名
    EXTRACT_FUNCTION = "extract_function"    # 提取函数
    INLINE_VARIABLE = "inline_variable"      # 内联变量
    REORDER_STATEMENTS = "reorder_statements"  # 语句重排序
    COMMENT_MODIFICATION = "comment_modification"  # 注释修改
    WHITESPACE_CHANGE = "whitespace_change"  # 空白符修改


class DetailedCodeMatch(BaseModel):
    """详细的代码匹配信息，包含精确位置"""
    source_student_id: str = Field(..., description="源学生ID")
    target_student_id: str = Field(..., description="目标学生ID")
    source_start_line: int = Field(..., ge=1, description="源代码起始行")
    source_end_line: int = Field(..., ge=1, description="源代码结束行")
    source_start_col: int = Field(0, ge=0, description="源代码起始列")
    source_end_col: int = Field(0, ge=0, description="源代码结束列")
    target_start_line: int = Field(..., ge=1, description="目标代码起始行")
    target_end_line: int = Field(..., ge=1, description="目标代码结束行")
    target_start_col: int = Field(0, ge=0, description="目标代码起始列")
    target_end_col: int = Field(0, ge=0, description="目标代码结束列")
    source_snippet: str = Field(..., description="源代码片段")
    target_snippet: str = Field(..., description="目标代码片段")
    similarity: float = Field(..., ge=0, le=1, description="相似度分数")
    algorithm: SimilarityAlgorithm = Field(..., description="检测算法")
    transformation_type: Optional[CodeTransformationType] = Field(
        None, description="检测到的代码变换类型"
    )
    explanation: str = Field("", description="匹配说明")


class SimilarityMatrixEntry(BaseModel):
    """相似度矩阵单元格数据"""
    student_id_1: str = Field(..., description="学生1 ID")
    student_id_2: str = Field(..., description="学生2 ID")
    student_name_1: str = Field("", description="学生1姓名")
    student_name_2: str = Field("", description="学生2姓名")
    similarity_score: float = Field(..., ge=0, le=1, description="综合相似度")
    algorithm_scores: Dict[str, float] = Field(
        default_factory=dict, description="各算法的相似度分数"
    )
    is_flagged: bool = Field(False, description="是否标记为可疑")


class SimilarityMatrix(BaseModel):
    """完整的相似度矩阵"""
    report_id: str = Field(..., description="报告ID")
    assignment_id: str = Field(..., description="作业ID")
    created_at: datetime = Field(..., description="创建时间")
    student_ids: List[str] = Field(..., description="学生ID列表")
    student_names: List[str] = Field(default_factory=list, description="学生姓名列表")
    matrix: List[List[float]] = Field(..., description="相似度矩阵数据")
    entries: List[SimilarityMatrixEntry] = Field(
        default_factory=list, description="详细的矩阵条目"
    )
    threshold: float = Field(0.7, description="相似度阈值")
    flagged_count: int = Field(0, description="标记的可疑对数量")


class OriginalityReport(BaseModel):
    """原创性分析报告"""
    report_id: str = Field(..., description="报告ID")
    submission_id: str = Field(..., description="提交ID")
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field("", description="学生姓名")
    assignment_id: str = Field(..., description="作业ID")
    created_at: datetime = Field(..., description="创建时间")

    # 原创性评分
    originality_score: float = Field(..., ge=0, le=100, description="原创性评分(0-100)")

    # 各算法的相似度分解
    similarity_breakdown: Dict[str, float] = Field(
        default_factory=dict, description="各算法相似度分解"
    )

    # 详细匹配信息
    detailed_matches: List[DetailedCodeMatch] = Field(
        default_factory=list, description="详细的代码匹配列表"
    )

    # 相似的提交
    similar_submissions: List[str] = Field(
        default_factory=list, description="相似的提交ID列表"
    )

    # 检测到的代码变换
    detected_transformations: List[CodeTransformationType] = Field(
        default_factory=list, description="检测到的代码变换类型"
    )

    # 改进建议
    improvement_suggestions: List[str] = Field(
        default_factory=list, description="改进建议列表"
    )

    # 总结
    summary: str = Field("", description="分析总结")
    risk_level: SimilarityLevel = Field(
        SimilarityLevel.NONE, description="风险等级"
    )


class SubmissionData(BaseModel):
    """提交数据（用于批量分析）"""
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field("", description="学生姓名")
    code: str = Field(..., description="代码内容")
    submission_id: Optional[str] = Field(None, description="提交ID")


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field("", description="课程ID")
    submissions: List[SubmissionData] = Field(..., description="提交列表")
    similarity_threshold: float = Field(
        0.7, ge=0, le=1, description="相似度阈值"
    )
    algorithms: List[SimilarityAlgorithm] = Field(
        default_factory=lambda: [SimilarityAlgorithm.COMBINED],
        description="使用的算法列表"
    )
    generate_reports: bool = Field(
        True, description="是否生成详细报告"
    )


class BatchAnalysisResponse(BaseModel):
    """批量分析响应"""
    report_id: str = Field(..., description="报告ID")
    assignment_id: str = Field(..., description="作业ID")
    created_at: datetime = Field(..., description="创建时间")
    total_submissions: int = Field(..., description="总提交数")
    total_comparisons: int = Field(..., description="总比较次数")
    flagged_count: int = Field(..., description="标记的可疑对数量")

    # 相似度矩阵
    similarity_matrix: SimilarityMatrix = Field(..., description="相似度矩阵")

    # 可疑对列表
    suspicious_pairs: List[SubmissionComparison] = Field(
        default_factory=list, description="可疑的提交对"
    )

    # 各学生的原创性报告
    originality_reports: List[OriginalityReport] = Field(
        default_factory=list, description="原创性报告列表"
    )

    # 总结
    summary: str = Field("", description="分析总结")


class PlagiarismSettings(BaseModel):
    """查重设置"""
    similarity_threshold: float = Field(
        0.7, ge=0, le=1, description="相似度阈值"
    )
    algorithms: List[SimilarityAlgorithm] = Field(
        default_factory=lambda: [SimilarityAlgorithm.COMBINED],
        description="启用的算法"
    )
    ast_weight: float = Field(0.3, ge=0, le=1, description="AST算法权重")
    token_weight: float = Field(0.25, ge=0, le=1, description="Token算法权重")
    text_weight: float = Field(0.2, ge=0, le=1, description="文本算法权重")
    semantic_weight: float = Field(0.15, ge=0, le=1, description="语义算法权重")
    order_invariant_weight: float = Field(0.1, ge=0, le=1, description="顺序不变算法权重")
    detect_renaming: bool = Field(True, description="检测变量/函数重命名")
    detect_refactoring: bool = Field(True, description="检测代码重构")

