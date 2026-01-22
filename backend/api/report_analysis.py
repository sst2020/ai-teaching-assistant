"""API endpoints for project report intelligent analysis."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from schemas.report_analysis import ReportAnalysisRequest, ReportAnalysisResponse
from services.report_analysis_service import report_analysis_service
from services.file_parsing_service import file_parsing_service


router = APIRouter(prefix="/report-analysis", tags=["Report Analysis"])


@router.post("/analyze", response_model=ReportAnalysisResponse)
async def analyze_project_report(request: ReportAnalysisRequest) -> ReportAnalysisResponse:
    """Analyze a project report and return a comprehensive analysis result.

    当前端已经完成基础解析（或直接提供纯文本）时，可以使用该端点。
    未来将扩展支持文件上传（PDF/DOCX/Markdown）形式的分析接口。
    """

    try:
        result = await report_analysis_service.analyze_report(request)
        return result
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze-file", response_model=ReportAnalysisResponse)
async def analyze_uploaded_report(
    file: UploadFile = File(..., description="Project report file to analyze (PDF, DOCX, or Markdown)"),
    reference_style_preference: Optional[str] = Form(None, description="Preferred reference style for formatting checks"),
) -> ReportAnalysisResponse:
    """Upload and analyze a project report file.

    Supports PDF, DOCX, and Markdown formats. The file is parsed to extract
    text content, then analyzed using the same pipeline as the text-based endpoint.
    """

    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.md', '.markdown'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not supported. Allowed types: {allowed_extensions}"
        )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "reports"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file temporarily
    temp_file_path = upload_dir / f"temp_{file.filename}"

    try:
        # Save the uploaded file
        with open(temp_file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse the document based on file type
        try:
            text_content = await file_parsing_service.parse_document_file(str(temp_file_path), file_ext)
        except ImportError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be parsed")

        # Determine file type enum
        from schemas.report_analysis import ReportFileType
        if file_ext == '.pdf':
            file_type = ReportFileType.PDF
        elif file_ext == '.docx':
            file_type = ReportFileType.DOCX
        else:  # .md or .markdown
            file_type = ReportFileType.MARKDOWN

        # Create analysis request
        request = ReportAnalysisRequest(
            file_name=file.filename,
            file_type=file_type,
            content=text_content,
            reference_style_preference=reference_style_preference
        )

        # Perform analysis
        result = await report_analysis_service.analyze_report(request)
        return result

    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors

