"""
Feedback Templates API - CRUD operations for feedback templates.
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc, asc

from core.database import get_db
from models.feedback_template import FeedbackTemplate, TemplateCategory, TemplateTone
from schemas.feedback import (
    FeedbackTemplateCreate, FeedbackTemplateUpdate,
    FeedbackTemplateResponse, FeedbackTemplateListResponse,
    TemplateCategory as SchemaCat, TemplateTone as SchemaTone,
    TemplateSearchRequest
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
            is_active=template.is_active,
            tone=template.tone.value if template.tone else TemplateTone.NEUTRAL.value,
            locale=template.locale or "en"
        )
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)

        return _template_to_response(db_template)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


def _template_to_response(template: FeedbackTemplate) -> FeedbackTemplateResponse:
    """Convert a FeedbackTemplate model to FeedbackTemplateResponse."""
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
        tone=SchemaTone(template.tone) if template.tone else SchemaTone.NEUTRAL,
        locale=template.locale or "en",
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.get("", response_model=FeedbackTemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    tone: Optional[str] = Query(None, description="Filter by tone"),
    locale: Optional[str] = Query(None, description="Filter by locale"),
    search: Optional[str] = Query(None, description="Search in name, title, message, and tags"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort field: name, usage_count, created_at"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
    db: AsyncSession = Depends(get_db)
):
    """
    List feedback templates with filtering and pagination.

    Args:
        category: Optional category filter
        language: Optional language filter
        tone: Optional tone filter
        locale: Optional locale filter
        search: Optional search term (searches name, title, message, tags)
        is_active: Optional active status filter
        page: Page number (1-based)
        page_size: Number of items per page
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

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

        if tone:
            query = query.where(FeedbackTemplate.tone == tone)
            count_query = count_query.where(FeedbackTemplate.tone == tone)

        if locale:
            query = query.where(FeedbackTemplate.locale == locale)
            count_query = count_query.where(FeedbackTemplate.locale == locale)

        if is_active is not None:
            query = query.where(FeedbackTemplate.is_active == is_active)
            count_query = count_query.where(FeedbackTemplate.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            search_filter = or_(
                FeedbackTemplate.name.ilike(search_pattern),
                FeedbackTemplate.title.ilike(search_pattern),
                FeedbackTemplate.message.ilike(search_pattern)
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(FeedbackTemplate, sort_by, FeedbackTemplate.name)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()

        return FeedbackTemplateListResponse(
            templates=[_template_to_response(t) for t in templates],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.post("/search", response_model=FeedbackTemplateListResponse)
async def search_templates(
    request: TemplateSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search for feedback templates.

    Supports multiple filters, tag matching, and flexible sorting.
    """
    try:
        query = select(FeedbackTemplate)
        count_query = select(func.count(FeedbackTemplate.id))
        filters = []

        # Text search
        if request.query:
            search_pattern = f"%{request.query}%"
            filters.append(or_(
                FeedbackTemplate.name.ilike(search_pattern),
                FeedbackTemplate.title.ilike(search_pattern),
                FeedbackTemplate.message.ilike(search_pattern)
            ))

        # Category filter
        if request.categories:
            category_values = [c.value for c in request.categories]
            filters.append(FeedbackTemplate.category.in_(category_values))

        # Language filter
        if request.languages:
            filters.append(or_(
                FeedbackTemplate.language.in_(request.languages),
                FeedbackTemplate.language.is_(None)
            ))

        # Tone filter
        if request.tones:
            tone_values = [t.value for t in request.tones]
            filters.append(FeedbackTemplate.tone.in_(tone_values))

        # Locale filter
        if request.locales:
            filters.append(FeedbackTemplate.locale.in_(request.locales))

        # Severity filter
        if request.severities:
            filters.append(FeedbackTemplate.severity.in_(request.severities))

        # Active status filter
        if request.is_active is not None:
            filters.append(FeedbackTemplate.is_active == request.is_active)

        # Minimum usage count filter
        if request.min_usage_count is not None:
            filters.append(FeedbackTemplate.usage_count >= request.min_usage_count)

        # Apply all filters
        if filters:
            combined_filter = and_(*filters)
            query = query.where(combined_filter)
            count_query = count_query.where(combined_filter)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(FeedbackTemplate, request.sort_by or "name", FeedbackTemplate.name)
        if request.sort_order and request.sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        offset = (request.page - 1) * request.page_size
        query = query.offset(offset).limit(request.page_size)

        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()

        return FeedbackTemplateListResponse(
            templates=[_template_to_response(t) for t in templates],
            total=total,
            page=request.page,
            page_size=request.page_size
        )

    except Exception as e:
        logger.error(f"Failed to search templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search templates: {str(e)}")


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

    return _template_to_response(template)


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
            elif key == "tone" and value is not None:
                setattr(template, key, value.value)
            else:
                setattr(template, key, value)

        await db.commit()
        await db.refresh(template)

        return _template_to_response(template)

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


@router.get("/tones/list")
async def list_tones():
    """
    List all available template tones.

    Returns:
        List of tone names and descriptions
    """
    tone_descriptions = {
        "neutral": "Neutral - Balanced and objective feedback",
        "encouraging": "Encouraging - Positive and motivating feedback",
        "strict": "Strict - Direct and professional feedback",
        "professional": "Professional - Formal and detailed feedback"
    }
    return [
        {
            "value": tone.value,
            "name": tone.name.replace("_", " ").title(),
            "description": tone_descriptions.get(tone.value, "")
        }
        for tone in TemplateTone
    ]


@router.get("/stats/summary")
async def get_template_stats(db: AsyncSession = Depends(get_db)):
    """
    Get summary statistics for feedback templates.

    Returns:
        Template statistics including counts by category, language, tone
    """
    try:
        # Total count
        total_result = await db.execute(select(func.count(FeedbackTemplate.id)))
        total = total_result.scalar() or 0

        # Active count
        active_result = await db.execute(
            select(func.count(FeedbackTemplate.id)).where(FeedbackTemplate.is_active == True)
        )
        active = active_result.scalar() or 0

        # Count by category
        category_result = await db.execute(
            select(FeedbackTemplate.category, func.count(FeedbackTemplate.id))
            .group_by(FeedbackTemplate.category)
        )
        by_category = {row[0]: row[1] for row in category_result.all()}

        # Count by language
        language_result = await db.execute(
            select(FeedbackTemplate.language, func.count(FeedbackTemplate.id))
            .group_by(FeedbackTemplate.language)
        )
        by_language = {row[0] or "universal": row[1] for row in language_result.all()}

        # Count by tone
        tone_result = await db.execute(
            select(FeedbackTemplate.tone, func.count(FeedbackTemplate.id))
            .group_by(FeedbackTemplate.tone)
        )
        by_tone = {row[0] or "neutral": row[1] for row in tone_result.all()}

        # Count by locale
        locale_result = await db.execute(
            select(FeedbackTemplate.locale, func.count(FeedbackTemplate.id))
            .group_by(FeedbackTemplate.locale)
        )
        by_locale = {row[0] or "en": row[1] for row in locale_result.all()}

        # Most used templates
        most_used_result = await db.execute(
            select(FeedbackTemplate)
            .order_by(desc(FeedbackTemplate.usage_count))
            .limit(10)
        )
        most_used = [
            {"id": t.id, "name": t.name, "usage_count": t.usage_count}
            for t in most_used_result.scalars().all()
        ]

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_category": by_category,
            "by_language": by_language,
            "by_tone": by_tone,
            "by_locale": by_locale,
            "most_used": most_used
        }

    except Exception as e:
        logger.error(f"Failed to get template stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template stats: {str(e)}")


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
