"""
认证日志模型 - 用于跟踪所有认证事件
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class AuthLog(Base):
    """认证日志模型 - 记录所有认证相关事件"""
    
    __tablename__ = "auth_logs"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 用户信息
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    student_id: Mapped[str] = mapped_column(String(10), nullable=False, index=True, comment="学号")
    
    # 事件类型: login, logout, register, token_refresh, password_change, token_revoke, login_failed
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # 事件状态: success, failure
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # IP 地址和用户代理
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 最长 45 字符
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 失败原因(仅在 status=failure 时记录)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 额外信息(JSON 格式)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # 索引优化
    __table_args__ = (
        # 复合索引用于查询特定用户的特定事件
        Index('idx_user_event', 'user_id', 'event_type'),
        # 复合索引用于查询特定时间段的事件
        Index('idx_event_time', 'event_type', 'created_at'),
        # 复合索引用于查询失败的登录尝试
        Index('idx_failed_login', 'student_id', 'event_type', 'status', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<AuthLog(id={self.id}, student_id={self.student_id}, event={self.event_type}, status={self.status})>"

