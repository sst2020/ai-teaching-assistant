"""
Refresh Token 模型

用于存储和管理刷新令牌。
"""
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class RefreshToken(Base):
    """
    Refresh Token 模型 - 用于刷新 Access Token。
    
    Refresh Token 是长期有效的令牌,用于获取新的 Access Token。
    """
    __tablename__ = "refresh_tokens"

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
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        nullable=False,
        comment="Refresh token 字符串"
    )
    
    # 状态
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="过期时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已撤销"
    )
    
    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens"
    )

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"

