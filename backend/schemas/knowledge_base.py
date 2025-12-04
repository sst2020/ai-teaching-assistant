"""
Schemas for Knowledge Base Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class KnowledgeBaseCategory(str, Enum):
    """Categories for knowledge base entries."""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    ENVIRONMENT = "environment"
    ALGORITHM = "algorithm"
    CONCEPT = "concept"
    DEBUGGING = "debugging"
    BEST_PRACTICE = "best_practice"
    DATA_STRUCTURE = "data_structure"
    OTHER = "other"


class DifficultyLevel(int, Enum):
    """Difficulty levels for questions."""
    L1_BEGINNER = 1
    L2_BASIC = 2
    L3_INTERMEDIATE = 3
    L4_ADVANCED = 4
    L5_EXPERT = 5


# ============ Request Schemas ============

class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base entry."""
    category: KnowledgeBaseCategory = Field(..., description="问题分类")
    question: str = Field(..., min_length=5, description="问题描述")
    answer: str = Field(..., min_length=10, description="标准答案")
    keywords: List[str] = Field(default_factory=list, description="关键词标签")
    difficulty_level: int = Field(default=2, ge=1, le=5, description="难度级别(1-5)")
    language: Optional[str] = Field(None, description="编程语言")


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base entry."""
    category: Optional[KnowledgeBaseCategory] = None
    question: Optional[str] = Field(None, min_length=5)
    answer: Optional[str] = Field(None, min_length=10)
    keywords: Optional[List[str]] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    language: Optional[str] = None
    is_active: Optional[bool] = None


class KnowledgeBaseSearchRequest(BaseModel):
    """Schema for searching knowledge base."""
    query: str = Field(..., min_length=2, description="搜索关键词")
    category: Optional[KnowledgeBaseCategory] = Field(None, description="分类过滤")
    difficulty_min: Optional[int] = Field(None, ge=1, le=5, description="最低难度")
    difficulty_max: Optional[int] = Field(None, ge=1, le=5, description="最高难度")
    language: Optional[str] = Field(None, description="编程语言过滤")
    limit: int = Field(default=10, ge=1, le=50, description="返回数量限制")


class KnowledgeBaseBulkCreate(BaseModel):
    """Schema for bulk creating knowledge base entries."""
    entries: List[KnowledgeBaseCreate] = Field(..., description="批量创建的条目列表")


# ============ Response Schemas ============

class KnowledgeBaseResponse(BaseModel):
    """Response schema for a knowledge base entry."""
    entry_id: str
    category: KnowledgeBaseCategory
    question: str
    answer: str
    keywords: List[str]
    difficulty_level: int
    language: Optional[str]
    view_count: int
    helpful_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class KnowledgeBaseSearchResult(BaseModel):
    """Search result with relevance score."""
    entry: KnowledgeBaseResponse
    relevance_score: float = Field(..., ge=0, le=1, description="相关度分数")
    matched_keywords: List[str] = Field(default_factory=list, description="匹配的关键词")


class KnowledgeBaseSearchResponse(BaseModel):
    """Response for knowledge base search."""
    query: str
    total_results: int
    results: List[KnowledgeBaseSearchResult]


class KnowledgeBaseListResponse(BaseModel):
    """Response for listing knowledge base entries."""
    total: int
    page: int
    page_size: int
    entries: List[KnowledgeBaseResponse]


class KnowledgeBaseStats(BaseModel):
    """Statistics for knowledge base."""
    total_entries: int
    active_entries: int
    entries_by_category: dict
    entries_by_difficulty: dict
    entries_by_language: dict
    total_views: int
    total_helpful: int
    average_helpfulness: float


class CategoryInfo(BaseModel):
    """Information about a category."""
    value: str
    label: str
    description: str
    count: int = 0


class CategoriesResponse(BaseModel):
    """Response for getting all categories."""
    categories: List[CategoryInfo]

