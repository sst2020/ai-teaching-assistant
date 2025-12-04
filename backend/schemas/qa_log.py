"""
QA Log Schemas

问答日志相关的 Pydantic 模型。
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class TriageResultEnum(str, Enum):
    """分诊结果枚举"""
    AUTO_REPLY = "auto_reply"
    TO_ASSISTANT = "to_assistant"
    TO_TEACHER = "to_teacher"
    PENDING = "pending"


class QALogStatusEnum(str, Enum):
    """问答日志状态枚举"""
    ANSWERED = "answered"
    PENDING = "pending"
    ESCALATED = "escalated"
    CLOSED = "closed"


class QALogCreate(BaseModel):
    """创建问答日志请求"""
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None
    question: str = Field(..., min_length=1, description="用户问题")


class QALogUpdate(BaseModel):
    """更新问答日志请求"""
    answer: Optional[str] = None
    answer_source: Optional[str] = None
    triage_result: Optional[TriageResultEnum] = None
    assigned_to: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=5)
    is_urgent: Optional[bool] = None
    status: Optional[QALogStatusEnum] = None
    handled_by: Optional[str] = None


class QALogFeedback(BaseModel):
    """用户反馈请求"""
    is_helpful: bool
    feedback_text: Optional[str] = None


class QALogResponse(BaseModel):
    """问答日志响应"""
    log_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None
    question: str
    question_keywords: Optional[List[str]] = None
    detected_category: Optional[str] = None
    detected_difficulty: Optional[int] = None
    matched_entry_id: Optional[str] = None
    match_score: Optional[float] = None
    match_method: Optional[str] = None
    answer: Optional[str] = None
    answer_source: Optional[str] = None
    triage_result: Optional[TriageResultEnum] = None
    assigned_to: Optional[str] = None
    priority: int = 0
    is_urgent: bool = False
    status: QALogStatusEnum
    is_helpful: Optional[bool] = None
    feedback_text: Optional[str] = None
    handled_by: Optional[str] = None
    handled_at: Optional[datetime] = None
    response_time_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QALogListResponse(BaseModel):
    """问答日志列表响应"""
    total: int
    page: int
    page_size: int
    logs: List[QALogResponse]


class QALogStats(BaseModel):
    """问答日志统计"""
    total_questions: int
    auto_replied: int
    to_assistant: int
    to_teacher: int
    pending: int
    avg_response_time: Optional[float] = None
    helpful_rate: Optional[float] = None
    questions_by_category: dict
    questions_by_difficulty: dict


class QALogQuery(BaseModel):
    """问答日志查询请求"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    status: Optional[QALogStatusEnum] = None
    triage_result: Optional[TriageResultEnum] = None
    assigned_to: Optional[str] = None
    is_urgent: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

