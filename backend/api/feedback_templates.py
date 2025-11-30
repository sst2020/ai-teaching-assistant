"""
Feedback Templates API - CRUD operations for feedback templates.
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from core.database import get_db
from models.feedback_template import FeedbackTemplate, TemplateCategory
from schemas.feedback import (
    FeedbackTemplateCreate, FeedbackTemplateUpdate,
    FeedbackTemplateResponse, FeedbackTemplateListResponse,
    TemplateCategory as SchemaCat
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback-templates", tags=["Feedback Templates"])


@router.post("", response_model=FeedbackTemplateResponse, status_code=201)
async def create_template(
    template: FeedbackTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new feedback template.

    Args:
        template: FeedbackTemplateCreate with template data

    Returns:
        Created FeedbackTemplateResponse
    """
    try:
        db_template = FeedbackTemplate(
            name=template.name,
            category=template.category.value,
            language=template.language,
            title=template.title,
            message=template.message,
            severity=template.severity,
            tags=template.tags,
            variables=template.variables,
            is_active=template.is_active
        )
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)

        return FeedbackTemplateResponse(
            id=db_template.id,
            name=db_template.name,
            category=SchemaCat(db_template.category),
            language=db_template.language,
            title=db_template.title,
            message=db_template.message,
            severity=db_template.severity,
            tags=db_template.tags or [],
            variables=db_template.variables or [],
            is_active=db_template.is_active,
            usage_count=db_template.usage_count,
            created_at=db_template.created_at,
            updated_at=db_template.updated_at
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("", response_model=FeedbackTemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    search: Optional[str] = Query(None, description="Search in name and tags"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    List feedback templates with filtering and pagination.

    Args:
        category: Optional category filter
        language: Optional language filter
        search: Optional search term
        is_active: Optional active status filter
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        FeedbackTemplateListResponse with templates and pagination info
    """
    try:
        # Build query
        query = select(FeedbackTemplate)
        count_query = select(func.count(FeedbackTemplate.id))

        # Apply filters
        if category:
            query = query.where(FeedbackTemplate.category == category)
            count_query = count_query.where(FeedbackTemplate.category == category)

        if language:
            query = query.where(
                or_(FeedbackTemplate.language == language, FeedbackTemplate.language.is_(None))
            )
            count_query = count_query.where(
                or_(FeedbackTemplate.language == language, FeedbackTemplate.language.is_(None))
            )

        if is_active is not None:
            query = query.where(FeedbackTemplate.is_active == is_active)
            count_query = count_query.where(FeedbackTemplate.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(FeedbackTemplate.name.ilike(search_pattern))
            count_query = count_query.where(FeedbackTemplate.name.ilike(search_pattern))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(FeedbackTemplate.name)

        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()

        return FeedbackTemplateListResponse(
            templates=[
                FeedbackTemplateResponse(
                    id=t.id,
                    name=t.name,
                    category=SchemaCat(t.category),
                    language=t.language,
                    title=t.title,
                    message=t.message,
                    severity=t.severity,
                    tags=t.tags or [],
                    variables=t.variables or [],
                    is_active=t.is_active,
                    usage_count=t.usage_count,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                ) for t in templates
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/{template_id}", response_model=FeedbackTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific feedback template by ID.

    Args:
        template_id: Template ID

    Returns:
        FeedbackTemplateResponse
    """
    result = await db.execute(
        select(FeedbackTemplate).where(FeedbackTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return FeedbackTemplateResponse(
        id=template.id,
        name=template.name,
        category=SchemaCat(template.category),
        language=template.language,
        title=template.title,
        message=template.message,
        severity=template.severity,
        tags=template.tags or [],
        variables=template.variables or [],
        is_active=template.is_active,
        usage_count=template.usage_count,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.put("/{template_id}", response_model=FeedbackTemplateResponse)
async def update_template(
    template_id: int,
    update_data: FeedbackTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a feedback template.

    Args:
        template_id: Template ID
        update_data: FeedbackTemplateUpdate with fields to update

    Returns:
        Updated FeedbackTemplateResponse
    """
    result = await db.execute(
        select(FeedbackTemplate).where(FeedbackTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if key == "category" and value is not None:
                setattr(template, key, value.value)
            else:
                setattr(template, key, value)

        await db.commit()
        await db.refresh(template)

        return FeedbackTemplateResponse(
            id=template.id,
            name=template.name,
            category=SchemaCat(template.category),
            language=template.language,
            title=template.title,
            message=template.message,
            severity=template.severity,
            tags=template.tags or [],
            variables=template.variables or [],
            is_active=template.is_active,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a feedback template.

    Args:
        template_id: Template ID
    """
    result = await db.execute(
        select(FeedbackTemplate).where(FeedbackTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        await db.delete(template)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@router.get("/categories/list")
async def list_categories():
    """
    List all available template categories.

    Returns:
        List of category names and descriptions
    """
    return [
        {"value": cat.value, "name": cat.name.replace("_", " ").title()}
        for cat in TemplateCategory
    ]


@router.post("/{template_id}/increment-usage")
async def increment_usage(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Increment the usage count for a template.

    Args:
        template_id: Template ID

    Returns:
        Updated usage count
    """
    result = await db.execute(
        select(FeedbackTemplate).where(FeedbackTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.usage_count += 1
    await db.commit()

    return {"template_id": template_id, "usage_count": template.usage_count}
