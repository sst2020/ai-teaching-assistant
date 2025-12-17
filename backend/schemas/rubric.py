"""
Schemas for Rubric Management API
评分标准管理 API 的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RubricBase(BaseModel):
    """Rubric 基础 schema"""
    name: str = Field(..., min_length=1, max_length=255, description="评分标准名称")
    description: Optional[str] = Field(None, description="评分标准描述")
    criteria: Optional[Dict[str, Any]] = Field(
        None, 
        description="评分标准详情（JSON 格式，键值对结构）",
        examples=[{
            "correctness": {
                "weight": 0.5,
                "description": "代码功能正确性",
                "max_points": 50
            },
            "quality": {
                "weight": 0.5,
                "description": "代码质量和风格",
                "max_points": 50
            }
        }]
    )
    max_score: float = Field(100.0, ge=0, description="最高分数")


class RubricCreate(RubricBase):
    """创建 Rubric 的 schema"""
    rubric_id: str = Field(..., min_length=1, max_length=50, description="唯一标识符")


class RubricUpdate(BaseModel):
    """更新 Rubric 的 schema（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="评分标准名称")
    description: Optional[str] = Field(None, description="评分标准描述")
    criteria: Optional[Dict[str, Any]] = Field(None, description="评分标准详情（JSON 格式）")
    max_score: Optional[float] = Field(None, ge=0, description="最高分数")


class RubricResponse(RubricBase):
    """Rubric 响应 schema"""
    id: int = Field(..., description="数据库 ID")
    rubric_id: str = Field(..., description="唯一标识符")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class RubricListResponse(BaseModel):
    """Rubric 分页列表响应 schema"""
    items: List[RubricResponse] = Field(default_factory=list, description="Rubric 列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")

