"""
Triage Schemas

分诊相关的 Pydantic 模型。
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class DifficultyLevelEnum(str, Enum):
    """难度级别枚举"""
    L1 = "L1"  # 入门级
    L2 = "L2"  # 基础级
    L3 = "L3"  # 中级
    L4 = "L4"  # 高级
    L5 = "L5"  # 专家级


class TriageDecision(str, Enum):
    """分诊决策枚举"""
    AUTO_REPLY = "auto_reply"           # 自动回复
    AUTO_REPLY_CONFIRM = "auto_reply_confirm"  # 自动回复需确认
    TO_ASSISTANT = "to_assistant"       # 转助教
    TO_TEACHER = "to_teacher"           # 转教师
    TO_TEACHER_URGENT = "to_teacher_urgent"  # 紧急转教师


class HandlerRole(str, Enum):
    """处理人角色枚举"""
    SYSTEM = "system"       # 系统自动
    ASSISTANT = "assistant" # 助教
    TEACHER = "teacher"     # 教师


# 难度级别描述
DIFFICULTY_DESCRIPTIONS = {
    "L1": {"name": "入门级", "description": "基础语法、简单概念", "examples": ["变量声明", "数据类型", "print语句"]},
    "L2": {"name": "基础级", "description": "常用语法、基本操作", "examples": ["循环", "条件判断", "函数定义"]},
    "L3": {"name": "中级", "description": "进阶概念、常见算法", "examples": ["递归", "排序算法", "数据结构"]},
    "L4": {"name": "高级", "description": "复杂问题、设计模式", "examples": ["并发编程", "架构设计", "性能优化"]},
    "L5": {"name": "专家级", "description": "系统级问题、深度优化", "examples": ["分布式系统", "底层原理", "高级调优"]},
}


class TriageRequest(BaseModel):
    """分诊请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None
    is_urgent: bool = Field(False, description="是否紧急")
    context: Optional[str] = Field(None, description="上下文信息")


class TriageResponse(BaseModel):
    """分诊响应"""
    log_id: str
    question: str
    detected_category: Optional[str] = None
    detected_difficulty: int
    difficulty_label: str
    match_score: float
    matched_entry_id: Optional[str] = None
    decision: TriageDecision
    answer: Optional[str] = None
    answer_source: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: int
    is_urgent: bool
    confidence_message: str
    created_at: datetime


class PendingQuestion(BaseModel):
    """待处理问题"""
    log_id: str
    question: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    detected_category: Optional[str] = None
    detected_difficulty: int
    difficulty_label: str
    match_score: Optional[float] = None
    priority: int
    is_urgent: bool
    triage_result: str
    created_at: datetime
    waiting_time_seconds: float


class PendingQueueResponse(BaseModel):
    """待处理队列响应"""
    total: int
    urgent_count: int
    questions: List[PendingQuestion]


class TeacherTakeoverRequest(BaseModel):
    """教师接管请求"""
    log_id: str
    teacher_id: str
    teacher_name: Optional[str] = None


class TeacherAnswerRequest(BaseModel):
    """教师回答请求"""
    log_id: str
    teacher_id: str
    answer: str = Field(..., min_length=1)
    update_knowledge_base: bool = Field(False, description="是否更新知识库")
    new_keywords: Optional[List[str]] = None


class TeacherAnswerResponse(BaseModel):
    """教师回答响应"""
    log_id: str
    answer: str
    answered_by: str
    answered_at: datetime
    knowledge_base_updated: bool
    new_entry_id: Optional[str] = None


class TriageStats(BaseModel):
    """分诊统计"""
    total_questions: int
    auto_replied: int
    to_assistant: int
    to_teacher: int
    pending: int
    urgent_pending: int
    avg_response_time: Optional[float] = None
    avg_waiting_time: Optional[float] = None
    resolution_rate: float
    questions_by_difficulty: dict
    questions_by_decision: dict


class DifficultyInfo(BaseModel):
    """难度级别信息"""
    level: str
    name: str
    description: str
    examples: List[str]


class DifficultyLevelsResponse(BaseModel):
    """难度级别列表响应"""
    levels: List[DifficultyInfo]

