"""
Assignment Review Router - Handles automated grading endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import Optional, List

from schemas.assignment import (
    AssignmentSubmission, AssignmentType, GradingResult,
    BatchGradingRequest, BatchGradingResponse, PlagiarismResult
)
from schemas.code_analysis import CodeAnalysisRequest, CodeAnalysisResult
from schemas.plagiarism import PlagiarismCheckRequest, PlagiarismReport, BatchPlagiarismReport
from schemas.common import APIResponse
from services.grading_service import grading_service
from services.code_analysis_service import code_analysis_service
from services.plagiarism_service import plagiarism_service

router = APIRouter(prefix="/assignments", tags=["Assignment Review"])


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

