"""
Token 黑名单模型

用于存储已撤销的 JWT Token,实现登出功能。
"""
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class TokenBlacklist(Base):
    """
    Token 黑名单模型 - 用于撤销 JWT Token。
    
    当用户登出或需要撤销 token 时,将 token 的 JTI 加入黑名单。
    """
    __tablename__ = "token_blacklist"

    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 外键
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的用户 ID"
    )
    
    # Token 信息
    jti: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="JWT ID (唯一标识符)"
    )
    token_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Token 类型: access 或 refresh"
    )
    
    # 时间信息
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="加入黑名单的时间"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Token 原始过期时间 (用于定期清理)"
    )
    
    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="blacklisted_tokens"
    )

    def __repr__(self) -> str:
        return f"<TokenBlacklist(id={self.id}, jti='{self.jti}', type='{self.token_type}')>"

