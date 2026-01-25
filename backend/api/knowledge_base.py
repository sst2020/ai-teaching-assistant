"""
Knowledge Base API Router - Handles knowledge base CRUD operations.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseSearchRequest,
    KnowledgeBaseSearchResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseBulkCreate,
    KnowledgeBaseStats,
    CategoriesResponse,
    CategoryInfo,
    KnowledgeBaseCategory,
)
from services.knowledge_base_service import knowledge_base_service

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


# ============ Category Descriptions ============
CATEGORY_DESCRIPTIONS = {
    "syntax_error": "语法错误相关问题",
    "logic_error": "逻辑错误和Bug相关问题",
    "environment": "环境配置和安装问题",
    "algorithm": "算法和数据结构问题",
    "concept": "编程概念理解问题",
    "debugging": "调试技巧和方法",
    "best_practice": "最佳实践和代码规范",
    "data_structure": "数据结构相关问题",
    "other": "其他问题",
}

CATEGORY_LABELS = {
    "syntax_error": "语法错误",
    "logic_error": "逻辑错误",
    "environment": "环境配置",
    "algorithm": "算法问题",
    "concept": "概念理解",
    "debugging": "调试技巧",
    "best_practice": "最佳实践",
    "data_structure": "数据结构",
    "other": "其他",
}


@router.post("", response_model=KnowledgeBaseResponse)
async def create_entry(
    data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的知识库条目。

    在知识库中创建一个新的问答条目，用于存储常见问题及其解答。

    Args:
        data: 知识库条目创建数据，包含问题、答案、分类等信息
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseResponse: 创建成功的知识库条目信息

    Raises:
        HTTPException: 500 - 创建条目时发生内部错误
    """
    try:
        entry = await knowledge_base_service.create_entry(db, data)
        return KnowledgeBaseResponse(
            entry_id=entry.entry_id,
            category=entry.category,
            question=entry.question,
            answer=entry.answer,
            keywords=entry.keywords,
            difficulty_level=entry.difficulty_level,
            language=entry.language,
            view_count=entry.view_count,
            helpful_count=entry.helpful_count,
            is_active=entry.is_active,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=KnowledgeBaseResponse)
async def get_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定的知识库条目。

    根据条目ID获取知识库中的特定条目详情，同时增加浏览计数。

    Args:
        entry_id: 知识库条目的唯一标识符
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseResponse: 知识库条目的完整信息

    Raises:
        HTTPException: 404 - 指定的条目不存在
    """
    entry = await knowledge_base_service.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="条目不存在")
    
    # Increment view count
    await knowledge_base_service.increment_view(db, entry_id)
    
    return KnowledgeBaseResponse(
        entry_id=entry.entry_id,
        category=entry.category,
        question=entry.question,
        answer=entry.answer,
        keywords=entry.keywords,
        difficulty_level=entry.difficulty_level,
        language=entry.language,
        view_count=entry.view_count + 1,
        helpful_count=entry.helpful_count,
        is_active=entry.is_active,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.put("/{entry_id}", response_model=KnowledgeBaseResponse)
async def update_entry(
    entry_id: str,
    data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新知识库条目。

    根据条目ID更新知识库条目的内容，支持部分更新。

    Args:
        entry_id: 要更新的知识库条目ID
        data: 更新数据，包含需要修改的字段
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseResponse: 更新后的知识库条目信息

    Raises:
        HTTPException: 404 - 指定的条目不存在
    """
    entry = await knowledge_base_service.update_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="条目不存在")
    
    return KnowledgeBaseResponse(
        entry_id=entry.entry_id,
        category=entry.category,
        question=entry.question,
        answer=entry.answer,
        keywords=entry.keywords,
        difficulty_level=entry.difficulty_level,
        language=entry.language,
        view_count=entry.view_count,
        helpful_count=entry.helpful_count,
        is_active=entry.is_active,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除知识库条目（软删除）。

    将指定的知识库条目标记为已删除状态，不会物理删除数据。

    Args:
        entry_id: 要删除的知识库条目ID
        db: 数据库会话依赖

    Returns:
        dict: 包含删除成功消息和条目ID

    Raises:
        HTTPException: 404 - 指定的条目不存在
    """
    success = await knowledge_base_service.delete_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="条目不存在")
    
    return {"message": "条目已删除", "entry_id": entry_id}


@router.get("", response_model=KnowledgeBaseListResponse)
async def list_entries(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(default=None, description="分类过滤"),
    language: Optional[str] = Query(default=None, description="语言过滤"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取知识库条目列表。

    分页获取知识库中的条目列表，支持按分类和语言过滤。

    Args:
        page: 页码，从1开始
        page_size: 每页显示的条目数量，范围1-100
        category: 可选的分类过滤条件
        language: 可选的语言过滤条件
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseListResponse: 包含条目列表和分页信息
    """
    entries, total = await knowledge_base_service.list_entries(
        db, page=page, page_size=page_size, category=category, language=language
    )
    
    return KnowledgeBaseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        entries=[
            KnowledgeBaseResponse(
                entry_id=e.entry_id,
                category=e.category,
                question=e.question,
                answer=e.answer,
                keywords=e.keywords,
                difficulty_level=e.difficulty_level,
                language=e.language,
                view_count=e.view_count,
                helpful_count=e.helpful_count,
                is_active=e.is_active,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in entries
        ],
    )


@router.post("/search", response_model=KnowledgeBaseSearchResponse)
async def search_entries(
    request: KnowledgeBaseSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    搜索知识库条目。

    基于关键词、分类、难度等条件搜索知识库中的条目，
    支持全文搜索和多条件组合查询。

    Args:
        request: 搜索请求参数，包含查询关键词、过滤条件等
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseSearchResponse: 搜索结果，包含匹配的条目列表和总数
    """
    results = await knowledge_base_service.search(db, request)

    return KnowledgeBaseSearchResponse(
        query=request.query,
        total_results=len(results),
        results=results,
    )


@router.get("/categories/list", response_model=CategoriesResponse)
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有分类信息。

    返回知识库中所有可用的分类，包括每个分类的名称、
    描述和该分类下的条目数量统计。

    Args:
        db: 数据库会话依赖

    Returns:
        CategoriesResponse: 分类列表，包含各分类的详细信息和统计
    """
    stats = await knowledge_base_service.get_stats(db)

    categories = []
    for cat in KnowledgeBaseCategory:
        categories.append(CategoryInfo(
            value=cat.value,
            label=CATEGORY_LABELS.get(cat.value, cat.value),
            description=CATEGORY_DESCRIPTIONS.get(cat.value, ""),
            count=stats.entries_by_category.get(cat.value, 0),
        ))

    return CategoriesResponse(categories=categories)


@router.post("/bulk", response_model=List[KnowledgeBaseResponse])
async def bulk_create_entries(
    data: KnowledgeBaseBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    批量创建知识库条目。

    一次性创建多个知识库条目，适用于初始化数据导入
    或批量添加相关知识点的场景。

    Args:
        data: 批量创建数据，包含多个条目的创建信息
        db: 数据库会话依赖

    Returns:
        List[KnowledgeBaseResponse]: 创建成功的条目列表

    Raises:
        HTTPException: 500 - 批量创建过程中发生错误
    """
    try:
        entries = await knowledge_base_service.bulk_create(db, data.entries)
        return [
            KnowledgeBaseResponse(
                entry_id=e.entry_id,
                category=e.category,
                question=e.question,
                answer=e.answer,
                keywords=e.keywords,
                difficulty_level=e.difficulty_level,
                language=e.language,
                view_count=e.view_count,
                helpful_count=e.helpful_count,
                is_active=e.is_active,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in entries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{entry_id}/helpful")
async def mark_helpful(
    entry_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    标记条目为有帮助。

    用户反馈机制，将指定条目标记为有帮助，
    用于统计条目的实用性和优化推荐算法。

    Args:
        entry_id: 知识库条目的唯一标识符
        db: 数据库会话依赖

    Returns:
        dict: 操作结果消息，包含 message 和 entry_id

    Raises:
        HTTPException: 404 - 指定的条目不存在
    """
    entry = await knowledge_base_service.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="条目不存在")

    await knowledge_base_service.increment_helpful(db, entry_id)

    return {"message": "已标记为有帮助", "entry_id": entry_id}


@router.get("/stats/overview", response_model=KnowledgeBaseStats)
async def get_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取知识库统计信息。

    返回知识库的整体统计数据，包括总条目数、
    各分类条目数、活跃条目数等汇总信息。

    Args:
        db: 数据库会话依赖

    Returns:
        KnowledgeBaseStats: 统计信息，包含各维度的数据汇总
    """
    return await knowledge_base_service.get_stats(db)

