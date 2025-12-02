"""
Multi-Dimensional Evaluation API - Endpoints for comprehensive code evaluation.
"""
import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.evaluation import (
    MultiDimensionalEvaluationRequest, MultiDimensionalEvaluationResponse,
    EvaluationDimension, DIMENSION_METADATA, RadarChartData, ClassComparison
)
from services.multi_dimensional_evaluator import multi_dimensional_evaluator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["Multi-Dimensional Evaluation"])


@router.post("/multi-dimensional", response_model=MultiDimensionalEvaluationResponse)
async def evaluate_multi_dimensional(
    request: MultiDimensionalEvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform multi-dimensional code evaluation.

    Evaluates code across six dimensions:
    - Technical Ability (技术能力)
    - Code Quality (代码质量)
    - Innovation (创新性)
    - Best Practices (最佳实践)
    - Efficiency (效率)
    - Documentation (文档)

    Args:
        request: MultiDimensionalEvaluationRequest with code and student_id

    Returns:
        MultiDimensionalEvaluationResponse with comprehensive evaluation report
    """
    try:
        start_time = time.time()

        report = await multi_dimensional_evaluator.evaluate(
            request=request,
            db_session=db if request.include_class_comparison else None
        )

        processing_time = (time.time() - start_time) * 1000

        return MultiDimensionalEvaluationResponse(
            success=True,
            report=report,
            message="多维度评估完成",
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Failed to perform multi-dimensional evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"多维度评估失败: {str(e)}"
        )


@router.get("/dimensions")
async def list_evaluation_dimensions():
    """
    List all evaluation dimensions with metadata.

    Returns:
        List of dimensions with names, descriptions, and weights
    """
    return [
        {
            "value": dim.value,
            "name": meta["name"],
            "name_zh": meta["name_zh"],
            "description": meta["description"],
            "description_zh": meta["description_zh"],
            "weight": meta["weight"],
        }
        for dim, meta in DIMENSION_METADATA.items()
    ]


@router.get("/radar-chart/{student_id}")
async def get_radar_chart_data(
    student_id: str,
    assignment_id: Optional[str] = Query(None, description="Filter by assignment"),
    include_class_average: bool = Query(False, description="Include class average"),
    class_id: Optional[str] = Query(None, description="Class ID for comparison"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get radar chart data for a student's evaluation.

    This endpoint retrieves the most recent evaluation for a student
    and formats it for radar chart visualization.

    Args:
        student_id: Student ID
        assignment_id: Optional assignment filter
        include_class_average: Whether to include class average
        class_id: Class ID for comparison

    Returns:
        RadarChartData for visualization
    """
    try:
        # For now, return sample data structure
        # In production, this would query the database for stored evaluations
        labels = [meta["name"] for meta in DIMENSION_METADATA.values()]
        labels_zh = [meta["name_zh"] for meta in DIMENSION_METADATA.values()]

        return {
            "student_id": student_id,
            "labels": labels,
            "labels_zh": labels_zh,
            "student_scores": [0] * len(labels),  # Would be populated from DB
            "class_average": None,
            "max_scores": [100] * len(labels),
            "message": "请先进行多维度评估以获取雷达图数据"
        }

    except Exception as e:
        logger.error(f"Failed to get radar chart data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取雷达图数据失败: {str(e)}"
        )


@router.get("/class-comparison/{student_id}")
async def get_class_comparison(
    student_id: str,
    class_id: str = Query(..., description="Class ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get class comparison statistics for a student.

    Compares the student's performance with class statistics including:
    - Class average, median, max, min
    - Student's percentile rank
    - Per-dimension comparison

    Args:
        student_id: Student ID
        class_id: Class ID

    Returns:
        ClassComparison with statistics
    """
    try:
        # This would query the database for actual comparison
        # For now, return a placeholder response
        return {
            "student_id": student_id,
            "class_id": class_id,
            "message": "请先进行包含班级对比的多维度评估",
            "available": False
        }

    except Exception as e:
        logger.error(f"Failed to get class comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取班级对比数据失败: {str(e)}"
        )

