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
from schemas.plagiarism import PlagiarismCheckRequest, PlagiarismReport, BatchPlagiarismReport
from schemas.common import APIResponse
from services.grading_service import grading_service
from services.code_analysis_service import code_analysis_service
from services.plagiarism_service import plagiarism_service
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

