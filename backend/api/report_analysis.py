"""API endpoints for project report intelligent analysis."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.report_analysis import ReportAnalysisRequest, ReportAnalysisResponse
from services.report_analysis_service import report_analysis_service


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

