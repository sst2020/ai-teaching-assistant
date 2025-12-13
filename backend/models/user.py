"""
用户模型

用于认证和授权的核心用户模型。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampMixin
from core.database import Base


class User(Base, TimestampMixin):
    """
    用户模型 - 用于认证和授权。
    
    一个 User 可以关联一个 Student (学生业务数据)。
    未来可以扩展 Teacher、Admin 等角色。
    """
    __tablename__ = "users"

    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 认证信息
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="用户邮箱 (登录凭证)"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 哈希后的密码"
    )
    
    # 用户信息
    role: Mapped[str] = mapped_column(
        String(50),
        default="student",
        nullable=False,
        comment="用户角色: student, teacher, admin"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="账户是否激活"
    )
    
    # 登录追踪
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    
    # 关系
    # 一对一: User -> Student
    student: Mapped[Optional["Student"]] = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # 一对多: User -> RefreshToken
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 一对多: User -> TokenBlacklist
    blacklisted_tokens: Mapped[list["TokenBlacklist"]] = relationship(
        "TokenBlacklist",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

