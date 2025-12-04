"""
Knowledge Base Model - Stores common programming questions and answers.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, JSON, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.base import TimestampMixin


class KnowledgeBaseCategory(str, Enum):
    """Categories for knowledge base entries."""
    SYNTAX_ERROR = "syntax_error"           # 语法错误
    LOGIC_ERROR = "logic_error"             # 逻辑错误
    ENVIRONMENT = "environment"             # 环境配置
    ALGORITHM = "algorithm"                 # 算法问题
    CONCEPT = "concept"                     # 概念理解
    DEBUGGING = "debugging"                 # 调试技巧
    BEST_PRACTICE = "best_practice"         # 最佳实践
    DATA_STRUCTURE = "data_structure"       # 数据结构
    OTHER = "other"                         # 其他


class DifficultyLevel(int, Enum):
    """Difficulty levels for questions."""
    L1_BEGINNER = 1      # 入门级：基础语法、简单概念
    L2_BASIC = 2         # 基础级：常用语法、基本操作
    L3_INTERMEDIATE = 3  # 中级：进阶概念、常见算法
    L4_ADVANCED = 4      # 高级：复杂问题、设计模式
    L5_EXPERT = 5        # 专家级：系统级问题、优化


class KnowledgeBaseEntry(Base, TimestampMixin):
    """
    Knowledge Base Entry model for storing common Q&A pairs.
    
    Attributes:
        id: Primary key
        entry_id: Unique identifier (UUID)
        category: Question category
        question: Question description
        answer: Standard answer
        keywords: Keyword tags (JSON array)
        difficulty_level: Difficulty level (1-5)
        language: Programming language (optional)
        view_count: Number of views
        helpful_count: Number of helpful votes
        is_active: Whether the entry is active
    """
    __tablename__ = "knowledge_base_entries"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entry_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    category: Mapped[KnowledgeBaseCategory] = mapped_column(
        SQLEnum(KnowledgeBaseCategory),
        nullable=False,
        default=KnowledgeBaseCategory.OTHER,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    difficulty_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=DifficultyLevel.L2_BASIC.value,
    )
    language: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    helpful_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("ix_kb_category_difficulty", "category", "difficulty_level"),
        Index("ix_kb_language_category", "language", "category"),
        Index("ix_kb_active_category", "is_active", "category"),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeBaseEntry(id={self.id}, entry_id='{self.entry_id}', category='{self.category}')>"
    
    @property
    def helpfulness_ratio(self) -> float:
        """Calculate the helpfulness ratio."""
        if self.view_count == 0:
            return 0.0
        return self.helpful_count / self.view_count
    
    def increment_view(self) -> None:
        """Increment the view count."""
        self.view_count += 1
    
    def increment_helpful(self) -> None:
        """Increment the helpful count."""
        self.helpful_count += 1

