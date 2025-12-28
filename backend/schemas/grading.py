"""
Schemas for Grading Result API
评分结果 API 的数据模型

与 models/grading_result.py 中的 GradingResult 模型兼容
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GradedByEnum(str, Enum):
    """评分者类型（与数据库模型一致）"""
    AI = "AI"
    TEACHER = "teacher"


class FeedbackDetail(BaseModel):
    """反馈详情结构"""
    category: str = Field(..., description="反馈类别")
    message: str = Field(..., description="反馈内容")
    severity: Optional[str] = Field(None, description="严重程度: info, warning, error")
    line_number: Optional[int] = Field(None, description="相关代码行号")
    suggestion: Optional[str] = Field(None, description="改进建议")


class GradingResultBase(BaseModel):
    """评分结果基础 schema"""
    overall_score: float = Field(..., ge=0, le=100, description="总分（0-100）")
    max_score: float = Field(100.0, ge=0, description="满分")
    feedback: Optional[Dict[str, Any]] = Field(
        None, 
        description="详细反馈（JSON 格式）",
        examples=[{
            "summary": "代码质量良好，但存在一些小问题",
            "strengths": ["逻辑清晰", "命名规范"],
            "improvements": ["可以添加更多注释", "建议使用类型提示"],
            "details": []
        }]
    )


class GradingResultCreate(GradingResultBase):
    """创建评分结果的 schema"""
    submission_id: int = Field(..., description="提交记录的数据库 ID")
    graded_by: GradedByEnum = Field(GradedByEnum.AI, description="评分者类型")
    graded_at: Optional[datetime] = Field(None, description="评分时间（默认为当前时间）")


class GradingResultUpdate(BaseModel):
    """更新评分结果的 schema（所有字段可选）"""
    overall_score: Optional[float] = Field(None, ge=0, le=100, description="总分")
    max_score: Optional[float] = Field(None, ge=0, description="满分")
    feedback: Optional[Dict[str, Any]] = Field(None, description="详细反馈")
    graded_by: Optional[GradedByEnum] = Field(None, description="评分者类型")
    graded_at: Optional[datetime] = Field(None, description="评分时间")


class GradingResultOverride(BaseModel):
    """教师覆盖评分的 schema"""
    overall_score: float = Field(..., ge=0, le=100, description="新的总分")
    feedback: Optional[Dict[str, Any]] = Field(None, description="教师反馈")
    override_reason: Optional[str] = Field(None, max_length=500, description="覆盖原因")


class GradingResultResponse(GradingResultBase):
    """评分结果响应 schema"""
    id: int = Field(..., description="评分结果 ID")
    submission_id: int = Field(..., description="提交记录 ID")
    graded_at: datetime = Field(..., description="评分时间")
    graded_by: GradedByEnum = Field(..., description="评分者类型")
    percentage_score: float = Field(..., description="百分比得分")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
    
    @field_validator('percentage_score', mode='before')
    @classmethod
    def calculate_percentage(cls, v, info):
        """如果未提供百分比得分，则计算"""
        if v is not None:
            return v
        # 从 values 中获取 overall_score 和 max_score
        data = info.data
        overall = data.get('overall_score', 0)
        max_score = data.get('max_score', 100)
        if max_score == 0:
            return 0.0
        return (overall / max_score) * 100


class GradingResultWithSubmission(GradingResultResponse):
    """包含提交详情的评分结果响应"""
    submission_external_id: Optional[str] = Field(None, description="提交记录外部 ID")
    student_id: Optional[int] = Field(None, description="学生数据库 ID")
    student_external_id: Optional[str] = Field(None, description="学生外部 ID")
    student_name: Optional[str] = Field(None, description="学生姓名")
    assignment_id: Optional[int] = Field(None, description="作业数据库 ID")
    assignment_external_id: Optional[str] = Field(None, description="作业外部 ID")
    assignment_title: Optional[str] = Field(None, description="作业标题")
    submitted_at: Optional[datetime] = Field(None, description="提交时间")


class GradingResultListResponse(BaseModel):
    """评分结果列表响应 schema"""
    items: List[GradingResultResponse] = Field(default_factory=list, description="评分结果列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class GradingResultWithSubmissionList(BaseModel):
    """包含提交详情的评分结果列表响应"""
    items: List[GradingResultWithSubmission] = Field(default_factory=list, description="评分结果列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class GradingStatistics(BaseModel):
    """评分统计信息"""
    total_graded: int = Field(..., description="已评分数量")
    average_score: float = Field(..., description="平均分")
    highest_score: float = Field(..., description="最高分")
    lowest_score: float = Field(..., description="最低分")
    ai_graded_count: int = Field(..., description="AI 评分数量")
    teacher_graded_count: int = Field(..., description="教师评分数量")
    score_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="分数分布（A: 90-100, B: 80-89, C: 70-79, D: 60-69, F: <60）"
    )


class BatchGradingRequest(BaseModel):
    """批量评分请求"""
    submission_ids: List[int] = Field(..., min_length=1, max_length=100, description="提交记录 ID 列表")
    use_ai: bool = Field(True, description="是否使用 AI 评分")


class BatchGradingResponse(BaseModel):
    """批量评分响应"""
    success_count: int = Field(..., description="成功评分数量")
    failed_count: int = Field(..., description="失败数量")
    results: List[GradingResultResponse] = Field(default_factory=list, description="评分结果列表")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误信息列表")

