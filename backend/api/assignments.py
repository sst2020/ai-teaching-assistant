"""
Assignment Review Router - Handles assignment CRUD and automated grading endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from core.database import get_db
from schemas.assignment import (
    AssignmentSubmission, AssignmentType, GradingResult,
    BatchGradingRequest, BatchGradingResponse, PlagiarismResult
)
from schemas.assignment_crud import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentListResponse
)
from schemas.code_analysis import CodeAnalysisRequest, CodeAnalysisResult
from schemas.plagiarism import (
    PlagiarismCheckRequest, PlagiarismReport, BatchPlagiarismReport,
    BatchAnalysisRequest, BatchAnalysisResponse, OriginalityReport,
    SimilarityMatrix, PlagiarismSettings
)
from schemas.common import APIResponse
from services.grading_service import grading_service
from services.code_analysis_service import code_analysis_service
from services.plagiarism_service import plagiarism_service, enhanced_plagiarism_service
from utils.crud import crud_assignment
from models.assignment import AssignmentType as DBAssignmentType

router = APIRouter(prefix="/assignments", tags=["Assignment Management"])


# ============================================
# Assignment CRUD Endpoints
# ============================================

@router.get("", response_model=AssignmentListResponse)
async def list_assignments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all assignments with pagination.

    - Supports filtering by course_id
    - Returns paginated results
    """
    skip = (page - 1) * page_size
    filters = {"course_id": course_id} if course_id else None

    assignments = await crud_assignment.get_multi(db, skip=skip, limit=page_size, filters=filters)
    total = await crud_assignment.count(db, filters=filters)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return AssignmentListResponse(
        items=[AssignmentResponse.model_validate(a) for a in assignments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/course/{course_id}", response_model=AssignmentListResponse)
async def get_course_assignments(
    course_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all assignments for a specific course.

    - Returns paginated list of assignments for the course
    """
    skip = (page - 1) * page_size
    assignments = await crud_assignment.get_by_course(db, course_id, skip=skip, limit=page_size)
    total = await crud_assignment.count_by_course(db, course_id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return AssignmentListResponse(
        items=[AssignmentResponse.model_validate(a) for a in assignments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/stats")
async def get_assignment_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取作业统计信息。

    返回:
    - total: 总作业数
    - pending_grading: 待批改数量
    - graded: 已批改数量
    - by_type: 按类型分类统计
    """
    from sqlalchemy import select, func
    from models.assignment import Assignment
    from models.submission import Submission

    # 获取总作业数
    total_result = await db.execute(select(func.count(Assignment.id)))
    total = total_result.scalar() or 0

    # 获取提交统计
    pending_result = await db.execute(
        select(func.count(Submission.id)).where(Submission.status == "pending")
    )
    pending_grading = pending_result.scalar() or 0

    graded_result = await db.execute(
        select(func.count(Submission.id)).where(Submission.status == "graded")
    )
    graded = graded_result.scalar() or 0

    # 按类型统计
    type_result = await db.execute(
        select(Assignment.assignment_type, func.count(Assignment.id))
        .group_by(Assignment.assignment_type)
    )
    by_type = {str(row[0].value) if row[0] else "unknown": row[1] for row in type_result.fetchall()}

    return {
        "total_assignments": total,
        "pending_count": pending_grading,
        "graded_count": graded,
        "by_type": by_type
    }


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get assignment details by assignment_id.

    - Returns assignment details if found
    - Returns 404 if assignment not found
    """
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    return assignment


# ============================================
# Grading and Analysis Endpoints
# ============================================

@router.post("/grade", response_model=GradingResult)
async def grade_assignment(submission: AssignmentSubmission):
    """
    Grade a single assignment submission.
    
    - Evaluates code correctness, style, and efficiency for code assignments
    - Assesses completeness, innovation, and clarity for reports
    - Generates personalized feedback and suggestions
    """
    try:
        result = await grading_service.grade_submission(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grade/batch", response_model=BatchGradingResponse)
async def batch_grade_assignments(request: BatchGradingRequest):
    """
    Grade multiple assignments in batch.
    
    Useful for grading all submissions for a particular assignment at once.
    """
    try:
        result = await grading_service.batch_grade(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plagiarism-check", response_model=PlagiarismResult)
async def check_plagiarism(submission: AssignmentSubmission):
    """
    Check an assignment for plagiarism.
    
    - Detects similarity with other submissions
    - Identifies potential code copying
    - Provides detailed analysis
    """
    try:
        result = await grading_service.check_plagiarism(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_assignment(
    student_id: str = Form(...),
    assignment_id: str = Form(...),
    assignment_type: AssignmentType = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload an assignment file for grading.
    
    Supports code files (.py, .java, .cpp, etc.) and documents (.pdf, .docx).
    """
    # Validate file extension
    allowed_extensions = [".py", ".java", ".cpp", ".c", ".js", ".ts", ".pdf", ".docx", ".txt"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {allowed_extensions}"
        )
    
    # Read file content
    content = await file.read()
    
    # Create submission
    submission = AssignmentSubmission(
        student_id=student_id,
        assignment_id=assignment_id,
        assignment_type=assignment_type,
        content=content.decode("utf-8", errors="ignore"),
        file_name=file.filename
    )
    
    # Grade the submission
    result = await grading_service.grade_submission(submission)

    return APIResponse(
        success=True,
        message="Assignment uploaded and graded successfully",
        data=result.model_dump()
    )


@router.post("/analyze-code", response_model=CodeAnalysisResult)
async def analyze_code(request: CodeAnalysisRequest):
    """
    Perform static code analysis on submitted code.

    - PEP 8 style compliance checking
    - Cyclomatic complexity analysis
    - Code smell detection
    - Maintainability metrics
    """
    try:
        result = await code_analysis_service.analyze_code(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plagiarism/check", response_model=PlagiarismReport)
async def check_code_plagiarism(request: PlagiarismCheckRequest):
    """
    Check code submission for plagiarism using AST-based analysis.

    - Compares against stored submissions
    - Uses structural similarity (not just text matching)
    - Detects copied code with renamed variables
    """
    try:
        result = await plagiarism_service.check_plagiarism(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plagiarism/batch", response_model=BatchPlagiarismReport)
async def batch_plagiarism_check(
    course_id: str = Query(..., description="Course ID for the submissions"),
    submissions: List[dict] = None
):
    """
    Check multiple submissions against each other for plagiarism.

    Useful for checking all submissions for an assignment at once.
    """
    try:
        if not submissions:
            raise HTTPException(status_code=400, detail="No submissions provided")
        result = await plagiarism_service.batch_check(course_id, submissions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 增强的查重与原创性分析端点
# ============================================

@router.post("/plagiarism/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_plagiarism(request: BatchAnalysisRequest):
    """
    批量分析多个提交的相似度（增强版）

    功能：
    - 生成完整的相似度矩阵
    - 支持多种相似度算法（AST、编辑距离、余弦相似度）
    - 检测变量/函数重命名和代码重构
    - 生成每个学生的原创性报告

    请求体示例：
    ```json
    {
        "assignment_id": "hw001",
        "course_id": "CS101",
        "submissions": [
            {"student_id": "s001", "student_name": "张三", "code": "def hello(): ..."},
            {"student_id": "s002", "student_name": "李四", "code": "def greet(): ..."}
        ],
        "similarity_threshold": 0.7,
        "algorithms": ["combined"],
        "generate_reports": true
    }
    ```
    """
    try:
        if not request.submissions or len(request.submissions) < 2:
            raise HTTPException(
                status_code=400,
                detail="至少需要2份提交才能进行对比分析"
            )
        result = await enhanced_plagiarism_service.batch_analyze(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plagiarism/originality-report/{submission_id}", response_model=OriginalityReport)
async def get_originality_report(
    submission_id: str,
    assignment_id: str = Query(..., description="作业ID")
):
    """
    获取单个提交的原创性分析报告

    返回：
    - 原创性评分（0-100）
    - 相似代码片段的精确位置
    - 与哪些其他作业存在相似性
    - 改进建议
    """
    # 注意：这里需要从缓存或数据库获取之前的分析结果
    # 当前实现返回一个示例报告，实际应用中应该存储和检索报告
    raise HTTPException(
        status_code=404,
        detail=f"未找到提交 {submission_id} 的原创性报告，请先执行批量分析"
    )


@router.put("/plagiarism/settings", response_model=PlagiarismSettings)
async def update_plagiarism_settings(settings: PlagiarismSettings):
    """
    更新查重设置

    可配置项：
    - similarity_threshold: 相似度阈值 (0-1)
    - algorithms: 启用的算法列表
    - ast_weight: AST算法权重
    - token_weight: Token算法权重
    - text_weight: 文本算法权重
    - detect_renaming: 是否检测重命名
    - detect_refactoring: 是否检测重构
    """
    try:
        enhanced_plagiarism_service.update_settings(settings)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plagiarism/settings", response_model=PlagiarismSettings)
async def get_plagiarism_settings():
    """
    获取当前查重设置
    """
    return enhanced_plagiarism_service.settings


