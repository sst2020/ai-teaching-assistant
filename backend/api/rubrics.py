"""
Rubric Management Router - 评分标准管理 API
处理评分标准的 CRUD 操作和关联查询
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from core.database import get_db
from schemas.rubric import (
    RubricCreate, RubricUpdate, RubricResponse, RubricListResponse
)
from schemas.assignment_crud import AssignmentResponse
from utils.crud import crud_rubric

router = APIRouter(prefix="/rubrics", tags=["Rubric Management"])


@router.post("", response_model=RubricResponse, status_code=201)
async def create_rubric(
    rubric_in: RubricCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的评分标准。

    - 创建一个新的评分标准记录
    - rubric_id 必须唯一
    - criteria 字段为可选的 JSON 对象，使用键值对结构

    **请求示例**：
    ```json
    {
        "rubric_id": "RUB001",
        "name": "Python 作业评分标准",
        "description": "用于评估 Python 编程作业的标准",
        "max_score": 100.0,
        "criteria": {
            "correctness": {
                "weight": 0.5,
                "description": "代码功能正确性",
                "max_points": 50
            },
            "quality": {
                "weight": 0.3,
                "description": "代码质量和风格",
                "max_points": 30
            },
            "documentation": {
                "weight": 0.2,
                "description": "文档和注释",
                "max_points": 20
            }
        }
    }
    ```

    **响应示例**：
    ```json
    {
        "id": 1,
        "rubric_id": "RUB001",
        "name": "Python 作业评分标准",
        "description": "用于评估 Python 编程作业的标准",
        "max_score": 100.0,
        "criteria": {...},
        "created_at": "2024-12-17T10:00:00Z",
        "updated_at": null
    }
    ```
    """
    # 检查 rubric_id 是否已存在
    existing = await crud_rubric.get_by_rubric_id(db, rubric_in.rubric_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Rubric with ID '{rubric_in.rubric_id}' already exists"
        )

    # 创建 Rubric
    rubric_data = rubric_in.model_dump()
    rubric = await crud_rubric.create(db, rubric_data)
    await db.commit()
    return rubric


@router.get("", response_model=RubricListResponse)
async def list_rubrics(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取评分标准列表（分页）。

    - 支持分页查询
    - 默认每页 20 条记录
    - 返回总数和分页信息

    **查询参数**：
    - `page`: 页码（默认 1）
    - `page_size`: 每页数量（默认 20，最大 100）

    **响应示例**：
    ```json
    {
        "items": [
            {
                "id": 1,
                "rubric_id": "RUB001",
                "name": "Python 作业评分标准",
                "max_score": 100.0,
                ...
            }
        ],
        "total": 50,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
    }
    ```
    """
    skip = (page - 1) * page_size
    rubrics = await crud_rubric.get_multi(db, skip=skip, limit=page_size)
    total = await crud_rubric.count(db)
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return RubricListResponse(
        items=rubrics,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )



@router.get("/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个评分标准。

    - 通过 rubric_id 获取评分标准详情
    - 如果不存在返回 404 错误

    **路径参数**：
    - `rubric_id`: 评分标准唯一标识符

    **响应示例**：
    ```json
    {
        "id": 1,
        "rubric_id": "RUB001",
        "name": "Python 作业评分标准",
        "description": "用于评估 Python 编程作业的标准",
        "max_score": 100.0,
        "criteria": {...},
        "created_at": "2024-12-17T10:00:00Z",
        "updated_at": null
    }
    ```
    """
    rubric = await crud_rubric.get_by_rubric_id(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=404,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )
    return rubric


@router.put("/{rubric_id}", response_model=RubricResponse)
async def update_rubric(
    rubric_id: str,
    rubric_in: RubricUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新评分标准。

    - 支持部分字段更新
    - 只更新提供的字段
    - 如果不存在返回 404 错误

    **路径参数**：
    - `rubric_id`: 评分标准唯一标识符

    **请求示例**（部分更新）：
    ```json
    {
        "name": "更新后的评分标准名称",
        "max_score": 120.0
    }
    ```

    **响应示例**：
    ```json
    {
        "id": 1,
        "rubric_id": "RUB001",
        "name": "更新后的评分标准名称",
        "max_score": 120.0,
        ...
    }
    ```
    """
    rubric = await crud_rubric.get_by_rubric_id(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=404,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )

    # 更新 Rubric
    update_data = rubric_in.model_dump(exclude_unset=True)
    updated_rubric = await crud_rubric.update(db, rubric, update_data)
    await db.commit()
    return updated_rubric


@router.delete("/{rubric_id}", status_code=204)
async def delete_rubric(
    rubric_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除评分标准。

    - 删除指定的评分标准
    - 关联的 Assignment 的 rubric_id 会被设置为 NULL（数据库级联）
    - 如果不存在返回 404 错误

    **路径参数**：
    - `rubric_id`: 评分标准唯一标识符

    **响应**：
    - 成功：204 No Content
    - 失败：404 Not Found
    """
    rubric = await crud_rubric.get_by_rubric_id(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=404,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )

    await crud_rubric.delete(db, rubric.id)
    await db.commit()


@router.get("/{rubric_id}/assignments", response_model=list[AssignmentResponse])
async def get_rubric_assignments(
    rubric_id: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的最大记录数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取使用指定评分标准的所有作业。

    - 返回关联到此评分标准的所有作业列表
    - 支持分页
    - 如果评分标准不存在返回 404 错误

    **路径参数**：
    - `rubric_id`: 评分标准唯一标识符

    **查询参数**：
    - `skip`: 跳过的记录数（默认 0）
    - `limit`: 返回的最大记录数（默认 100）

    **响应示例**：
    ```json
    [
        {
            "id": 1,
            "assignment_id": "HW001",
            "title": "Python 基础作业",
            "rubric_id": 1,
            ...
        }
    ]
    ```
    """
    # 检查 Rubric 是否存在
    rubric = await crud_rubric.get_by_rubric_id(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=404,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )

    # 获取关联的 Assignments
    assignments = await crud_rubric.get_assignments_by_rubric(
        db, rubric_id, skip=skip, limit=limit
    )
    return assignments
