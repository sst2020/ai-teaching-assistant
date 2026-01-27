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
from schemas.assignment_transfer import (
    TeacherAssignmentSubmit, BatchUploadRequest, FileManagerSyncRequest,
    AssignmentTransferResponse, BatchUploadResponse, FileManagerSyncResponse
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
from services.assignment_transfer_service import assignment_transfer_service
from utils.crud import crud_assignment
from models.assignment import AssignmentType as DBAssignmentType

router = APIRouter(prefix="/assignments", tags=["Assignment Management"])


# ============================================
# Assignment CRUD Endpoints
# ============================================

@router.post("", response_model=AssignmentResponse, status_code=201)
async def create_assignment(
    assignment_in: AssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new assignment.

    - Creates an assignment with the provided information
    - Returns the created assignment data
    """
    # Check if assignment_id already exists
    existing = await crud_assignment.get_by_assignment_id(db, assignment_in.assignment_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Assignment with ID '{assignment_in.assignment_id}' already exists"
        )

    # Map schema enum to database enum
    assignment_type_map = {
        "code": DBAssignmentType.CODE,
        "essay": DBAssignmentType.ESSAY,
        "quiz": DBAssignmentType.QUIZ,
    }

    assignment_data = assignment_in.model_dump()
    assignment_data["assignment_type"] = assignment_type_map.get(
        assignment_in.assignment_type.value, DBAssignmentType.CODE
    )

    assignment = await crud_assignment.create(db, assignment_data)
    return assignment


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


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_in: AssignmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update assignment information.

    - Updates only the provided fields
    - Returns the updated assignment data
    """
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )

    update_data = assignment_in.model_dump(exclude_unset=True)

    # Map assignment_type if provided
    if "assignment_type" in update_data and update_data["assignment_type"]:
        assignment_type_map = {
            "code": DBAssignmentType.CODE,
            "essay": DBAssignmentType.ESSAY,
            "quiz": DBAssignmentType.QUIZ,
        }
        update_data["assignment_type"] = assignment_type_map.get(
            update_data["assignment_type"].value, DBAssignmentType.CODE
        )

    updated_assignment = await crud_assignment.update(db, assignment, update_data)
    return updated_assignment


@router.delete("/{assignment_id}", response_model=APIResponse)
async def delete_assignment(
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assignment.

    - Removes the assignment and all associated submissions
    - Returns success message on deletion
    """
    assignment = await crud_assignment.get_by_assignment_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )

    await crud_assignment.delete(db, assignment.id)
    return APIResponse(
        success=True,
        message=f"Assignment '{assignment_id}' deleted successfully"
    )


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


# ============================================
# 教师端和文件管理的作业传输端点
# ============================================

@router.post("/teacher/submit", response_model=APIResponse)
async def teacher_submit_assignment(
    assignment_id: str = Form(..., description="作业ID"),
    course_id: str = Form(..., description="课程ID"),
    title: str = Form(..., description="作业标题"),
    description: str = Form(..., description="作业描述"),
    due_date: str = Form(..., description="截止日期 (YYYY-MM-DDTHH:MM:SS)"),
    max_score: float = Form(100.0, description="最高分"),
    assignment_type: AssignmentType = Form(AssignmentType.code, description="作业类型"),
    file: UploadFile = File(None, description="作业附件")
):
    """
    教师提交作业定义

    用于教师创建新的作业，可以包含附件。
    """
    try:
        # 读取文件内容（如果有）
        file_content = None
        if file:
            file_content = await file.read()

        # 创建请求对象
        assignment_data = TeacherAssignmentSubmit(
            assignment_id=assignment_id,
            course_id=course_id,
            title=title,
            description=description,
            due_date=due_date,
            max_score=max_score,
            assignment_type=assignment_type.value,
            file_attachment=file_content,
            file_name=file.filename if file else None
        )

        # 调用服务处理提交
        result = await assignment_transfer_service.submit_assignment_from_teacher(assignment_data)

        if result["success"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "assignment_id": result["assignment_id"],
                    "course_id": result["course_id"]
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teacher/batch-upload", response_model=BatchUploadResponse)
async def batch_upload_student_submissions(
    assignment_id: str = Form(..., description="作业ID"),
    course_id: str = Form(..., description="课程ID"),
    files: List[UploadFile] = File(..., description="学生作业文件列表"),
    student_ids: List[str] = Form(..., description="对应的学生ID列表"),
    sync_to_file_manager: bool = Form(True, description="是否同步到文件管理系统")
):
    """
    批量上传学生作业文件

    用于教师批量上传学生的作业文件。
    """
    try:
        if len(files) != len(student_ids):
            raise HTTPException(
                status_code=400,
                detail="文件数量与学生ID数量不匹配"
            )

        # 构建学生提交列表
        student_submissions = []
        for i, file in enumerate(files):
            # 验证文件扩展名
            allowed_extensions = [".py", ".java", ".cpp", ".c", ".js", ".ts", ".pdf", ".docx", ".txt"]
            file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件类型不被允许: {file_ext}. 允许的类型: {allowed_extensions}"
                )

            # 读取文件内容
            content = await file.read()
            content_str = content.decode("utf-8", errors="ignore")

            student_submissions.append({
                "student_id": student_ids[i],
                "student_name": f"Student {student_ids[i]}",  # 实际应用中应从数据库获取
                "file_content": content_str,
                "file_name": file.filename
            })

        # 创建批量上传请求对象
        batch_request = BatchUploadRequest(
            assignment_id=assignment_id,
            course_id=course_id,
            student_submissions=student_submissions,
            sync_to_file_manager=sync_to_file_manager
        )

        # 调用服务处理批量上传
        result = await assignment_transfer_service.batch_upload_student_submissions(batch_request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher/{assignment_id}/submissions", response_model=List[Dict])
async def get_assignment_submissions(
    assignment_id: str,
    course_id: str = Query(..., description="课程ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小")
):
    """
    获取作业提交列表

    返回指定作业的所有提交记录。
    """
    try:
        # 调用服务获取提交列表
        submissions = await assignment_transfer_service.get_assignment_submissions(
            assignment_id, course_id, page, page_size
        )

        return submissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file-manager/sync", response_model=FileManagerSyncResponse)
async def sync_with_file_manager(
    assignment_id: str = Form(..., description="作业ID"),
    course_id: str = Form(..., description="课程ID"),
    sync_type: str = Form("full", description="同步类型: full, incremental"),
    target_path: str = Form(..., description="目标路径")
):
    """
    与文件管理系统同步

    用于将作业数据与外部文件管理系统同步。
    """
    try:
        # 创建同步请求对象
        sync_request = FileManagerSyncRequest(
            assignment_id=assignment_id,
            course_id=course_id,
            sync_type=sync_type,
            target_path=target_path
        )

        # 调用服务执行同步
        result = await assignment_transfer_service.sync_with_file_manager(sync_request)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file-manager/status", response_model=Dict)
async def get_sync_status(
    assignment_id: str = Query(..., description="作业ID"),
    sync_id: str = Query(None, description="同步ID")
):
    """
    查询同步状态

    返回与文件管理系统的同步状态。
    """
    try:
        # 这里应该有查询同步状态的逻辑
        # 暂时返回模拟数据
        return {
            "assignment_id": assignment_id,
            "sync_id": sync_id or "sync_001",
            "status": "completed",
            "progress": 100,
            "total_files": 25,
            "processed_files": 25,
            "failed_files": 0,
            "last_updated": "2023-05-15T11:00:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

