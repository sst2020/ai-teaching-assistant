"""
QA Log Model

问答日志模型，用于记录用户问答交互历史。
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.sql import func

from models.base import Base


class TriageResult(str, Enum):
    """分诊结果枚举"""
    AUTO_REPLY = "auto_reply"           # 自动回复
    TO_ASSISTANT = "to_assistant"       # 转助教
    TO_TEACHER = "to_teacher"           # 转教师
    PENDING = "pending"                 # 待处理


class QALogStatus(str, Enum):
    """问答日志状态枚举"""
    ANSWERED = "answered"               # 已回答
    PENDING = "pending"                 # 待处理
    ESCALATED = "escalated"             # 已升级
    CLOSED = "closed"                   # 已关闭


class QALog(Base):
    """问答日志模型"""
    __tablename__ = "qa_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 用户信息
    user_id = Column(String(36), nullable=True, index=True)
    user_name = Column(String(100), nullable=True)
    session_id = Column(String(36), nullable=True, index=True)
    
    # 问题信息
    question = Column(Text, nullable=False)
    question_keywords = Column(JSON, nullable=True)  # 提取的关键词
    detected_category = Column(String(50), nullable=True)  # 检测到的分类
    detected_difficulty = Column(Integer, nullable=True)  # 检测到的难度
    
    # 匹配信息
    matched_entry_id = Column(String(36), nullable=True, index=True)  # 匹配的知识库条目ID
    match_score = Column(Float, nullable=True)  # 匹配分数 0-1
    match_method = Column(String(50), nullable=True)  # 匹配方法
    
    # 回复信息
    answer = Column(Text, nullable=True)
    answer_source = Column(String(50), nullable=True)  # 回复来源: knowledge_base, assistant, teacher
    
    # 分诊信息
    triage_result = Column(SQLEnum(TriageResult), default=TriageResult.PENDING)
    assigned_to = Column(String(36), nullable=True)  # 分配给谁处理
    priority = Column(Integer, default=0)  # 优先级 0-5
    is_urgent = Column(Boolean, default=False)  # 是否紧急
    
    # 状态信息
    status = Column(SQLEnum(QALogStatus), default=QALogStatus.PENDING)
    
    # 反馈信息
    is_helpful = Column(Boolean, nullable=True)  # 用户反馈是否有帮助
    feedback_text = Column(Text, nullable=True)  # 用户反馈文本
    
    # 处理信息
    handled_by = Column(String(36), nullable=True)  # 处理人ID
    handled_at = Column(DateTime, nullable=True)  # 处理时间
    response_time_seconds = Column(Float, nullable=True)  # 响应时间（秒）
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<QALog(log_id={self.log_id}, status={self.status})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "log_id": self.log_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "session_id": self.session_id,
            "question": self.question,
            "question_keywords": self.question_keywords,
            "detected_category": self.detected_category,
            "detected_difficulty": self.detected_difficulty,
            "matched_entry_id": self.matched_entry_id,
            "match_score": self.match_score,
            "match_method": self.match_method,
            "answer": self.answer,
            "answer_source": self.answer_source,
            "triage_result": self.triage_result.value if self.triage_result else None,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "is_urgent": self.is_urgent,
            "status": self.status.value if self.status else None,
            "is_helpful": self.is_helpful,
            "feedback_text": self.feedback_text,
            "handled_by": self.handled_by,
            "handled_at": self.handled_at.isoformat() if self.handled_at else None,
            "response_time_seconds": self.response_time_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

