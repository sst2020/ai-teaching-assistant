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
    """分析项目报告并返回综合分析结果。

    使用 DeepSeek AI 对项目报告进行多维度智能分析，包括逻辑结构、
    创新性、语言质量等方面的评估，并生成个性化改进建议。

    当前端已完成文档解析（或直接提供纯文本）时，调用此端点进行分析。
    支持的分析维度：逻辑分析、创新性评估、改进建议、语言质量评分。

    Args:
        request: 报告分析请求对象
            - file_name: 文件名称（用于识别和记录）
            - file_type: 文件类型（PDF/DOCX/MARKDOWN/TEXT）
            - content: 报告文本内容
            - reference_style_preference: 可选的参考文献格式偏好

    Returns:
        ReportAnalysisResponse: 综合分析结果
            - overall_score: 总体评分（0-100）
            - logic_analysis: 逻辑结构分析结果
            - innovation_analysis: 创新性评估结果
            - improvement_suggestions: 个性化改进建议列表
            - language_quality: 语言质量评估结果

    Raises:
        HTTPException(500): 分析过程中发生内部错误
    """

    try:
        result = await report_analysis_service.analyze_report(request)
        return result
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze-file", response_model=ReportAnalysisResponse)
async def analyze_uploaded_report(
    file: UploadFile = File(..., description="待分析的项目报告文件（PDF、DOCX 或 Markdown）"),
    reference_style_preference: Optional[str] = Form(None, description="参考文献格式偏好"),
) -> ReportAnalysisResponse:
    """上传并分析项目报告文件。

    支持 PDF、DOCX 和 Markdown 格式的文件上传。系统会自动解析文件内容，
    提取文本后使用与文本端点相同的 AI 分析管道进行智能分析。

    文件处理流程：
    1. 验证文件类型（仅允许 .pdf/.docx/.md/.markdown）
    2. 临时保存上传文件
    3. 根据文件类型调用相应解析器提取文本
    4. 执行多维度 AI 智能分析
    5. 清理临时文件并返回结果

    Args:
        file: 上传的报告文件
            - 支持格式：PDF、DOCX、Markdown (.md/.markdown)
            - 大小限制：由服务器配置决定
        reference_style_preference: 可选的参考文献格式偏好
            - 用于检查报告中引用格式的一致性

    Returns:
        ReportAnalysisResponse: 综合分析结果
            - overall_score: 总体评分（0-100）
            - logic_analysis: 逻辑结构分析结果
            - innovation_analysis: 创新性评估结果
            - improvement_suggestions: 个性化改进建议列表
            - language_quality: 语言质量评估结果

    Raises:
        HTTPException(400): 不支持的文件类型或文件内容为空
        HTTPException(500): 文件解析失败或分析过程发生错误
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

