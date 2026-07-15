"""
API endpoints for code analysis.

Provides comprehensive code analysis including:
- Code quality analysis (complexity, maintainability, duplication)
- Linting (Pylint integration)
- Security analysis (Bandit integration)
- Performance analysis (anti-patterns, best practices)
- Comprehensive analysis (all of the above)
"""
import logging
import asyncio
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.analysis_rules import (
    AnalysisRequest, AnalysisResultResponse, BatchAnalysisRequest,
    BatchAnalysisResponse, FullAnalysisResult, RuleSet, AnalysisRule
)
from schemas.analysis import (
    AnalysisCodeRequest, CodeQualityResult, LintRequest, LintResult,
    SecurityRequest, SecurityResult, PerformanceRequest, PerformanceResult,
    ComprehensiveRequest, ComprehensiveAnalysisResult
)
from services.enhanced_analysis_service import enhanced_analysis_service, EnhancedAnalysisService
from services.code_analyzer import code_quality_analyzer
from services.linter import linter_service
from services.security_analyzer import security_analyzer, performance_analyzer
from utils.crud import crud_code_file, crud_analysis_result

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResultResponse)
async def analyze_code(request: AnalysisRequest):
    """
    Analyze code for quality issues.

    Performs comprehensive analysis including:
    - Complexity metrics (cyclomatic, cognitive)
    - Naming convention checks
    - Security vulnerability detection
    - Style issues
    - Code structure analysis
    """
    try:
        result = await enhanced_analysis_service.analyze(
            code=request.code,
            language=request.language,
            file_id=request.file_id,
            rule_overrides=request.rule_overrides
        )
        return AnalysisResultResponse(
            success=True,
            result=result,
            message="Analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/file/{file_id}", response_model=AnalysisResultResponse)
async def analyze_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze an uploaded file by its ID.
    """
    try:
        # Get file from database
        file_record = await crud_code_file.get(db, id=file_id)
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")

        # Read file content
        from pathlib import Path
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File content not found")

        content = file_path.read_text(encoding='utf-8')

        # Determine language from extension
        ext_to_lang = {
            '.py': 'python', '.java': 'java', '.js': 'javascript',
            '.jsx': 'jsx', '.ts': 'typescript', '.tsx': 'tsx',
            '.c': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.h': 'c', '.hpp': 'cpp'
        }
        language = ext_to_lang.get(file_path.suffix.lower(), 'python')

        # Perform analysis
        result = await enhanced_analysis_service.analyze(
            code=content,
            language=language,
            file_id=file_id
        )

        # Update file record with analysis result
        import json
        await crud_code_file.update(
            db, db_obj=file_record,
            obj_in={"analysis_result": json.dumps(result.model_dump(), default=str)}
        )

        return AnalysisResultResponse(
            success=True,
            result=result,
            message="File analysis completed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
    request: BatchAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze multiple files in batch.
    """
    results: List[FullAnalysisResult] = []
    errors = []

    for file_id in request.file_ids:
        try:
            file_record = await crud_code_file.get(db, id=file_id)
            if not file_record:
                errors.append(f"File {file_id} not found")
                continue

            from pathlib import Path
            file_path = Path(file_record.file_path)
            if not file_path.exists():
                errors.append(f"File content for {file_id} not found")
                continue

            content = file_path.read_text(encoding='utf-8')
            ext_to_lang = {
                '.py': 'python', '.java': 'java', '.js': 'javascript',
                '.jsx': 'jsx', '.ts': 'typescript', '.tsx': 'tsx',
                '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp'
            }
            language = ext_to_lang.get(file_path.suffix.lower(), 'python')

            result = await enhanced_analysis_service.analyze(
                code=content, language=language, file_id=file_id,
                rule_overrides=request.rule_overrides
            )
            results.append(result)
        except Exception as e:
            errors.append(f"Error analyzing {file_id}: {str(e)}")

    # Generate aggregate summary
    summary = None
    if results and request.generate_comparison:
        avg_score = sum(r.summary.overall_score for r in results) / len(results)
        total_violations = sum(r.summary.total_violations for r in results)
        summary = {
            "files_analyzed": len(results),
            "average_score": round(avg_score, 1),
            "total_violations": total_violations,
            "errors": errors
        }

    return BatchAnalysisResponse(
        success=len(errors) == 0,
        results=results,
        summary=summary,
        message=f"Analyzed {len(results)} files" + (f" with {len(errors)} errors" if errors else "")
    )


@router.get("/rules", response_model=List[AnalysisRule])
async def get_analysis_rules():
    """
    Get all available analysis rules.
    """
    return [loaded.rule for loaded in enhanced_analysis_service.rules.values()]


@router.get("/rules/{rule_id}", response_model=AnalysisRule)
async def get_rule(rule_id: str):
    """
    Get a specific analysis rule by ID.
    """
    loaded = enhanced_analysis_service.rules.get(rule_id)
    if not loaded:
        raise HTTPException(status_code=404, detail="Rule not found")
    return loaded.rule


@router.get("/results/{file_id}", response_model=AnalysisResultResponse)
async def get_analysis_result(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the stored analysis result for a file.
    """
    import json
    # Try to get from AnalysisResult table first
    analysis_result = await crud_analysis_result.get_latest_by_file_id(db, file_id)
    if analysis_result:
        result = FullAnalysisResult(
            analysis_id=analysis_result.id,
            file_id=analysis_result.file_id,
            language=analysis_result.language,
            analyzed_at=analysis_result.analyzed_at,
            line_metrics={
                "total_lines": analysis_result.total_lines,
                "code_lines": analysis_result.code_lines,
                "comment_lines": analysis_result.comment_lines,
                "blank_lines": analysis_result.blank_lines,
                "docstring_lines": analysis_result.docstring_lines
            },
            complexity={
                "cyclomatic_complexity": analysis_result.cyclomatic_complexity,
                "cognitive_complexity": analysis_result.cognitive_complexity,
                "max_nesting_depth": analysis_result.max_nesting_depth,
                "max_function_length": analysis_result.max_function_length,
                "max_parameters": analysis_result.max_parameters,
                "total_functions": analysis_result.total_functions
            },
            structure={
                "total_classes": analysis_result.total_classes,
                "total_methods": analysis_result.total_methods,
                "average_function_length": analysis_result.average_function_length
            },
            summary={
                "overall_score": analysis_result.overall_score,
                "grade": analysis_result.grade,
                "total_violations": analysis_result.total_violations,
                "critical_violations": analysis_result.critical_violations,
                "warnings": analysis_result.warnings,
                "info_violations": analysis_result.info_violations
            },
            violations=analysis_result.violations or [],
            recommendations=analysis_result.recommendations or []
        )
        return AnalysisResultResponse(
            success=True,
            result=result,
            message="Analysis result retrieved"
        )

    # Fallback to CodeFile.analysis_result field
    file_record = await crud_code_file.get_by_file_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    if not file_record.analysis_result:
        raise HTTPException(status_code=404, detail="No analysis result found for this file")

    try:
        result_data = json.loads(file_record.analysis_result)
        result = FullAnalysisResult(**result_data)
        return AnalysisResultResponse(
            success=True,
            result=result,
            message="Analysis result retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse analysis result: {str(e)}")


@router.get("/summary")
async def get_analysis_summary(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Get a summary of recent analysis results.
    """
    import json
    from models.code_file import FileStatus

    # Get recent analyzed files
    files = await crud_code_file.get_multi(
        db, skip=0, limit=limit
    )

    analyzed_files = []
    for f in files:
        if f.analysis_result:
            try:
                result = json.loads(f.analysis_result)
                analyzed_files.append({
                    "file_id": str(f.id),
                    "filename": f.original_filename,
                    "score": result.get("summary", {}).get("overall_score", 0),
                    "grade": result.get("summary", {}).get("grade", "N/A"),
                    "violations": result.get("summary", {}).get("total_violations", 0),
                    "analyzed_at": result.get("analyzed_at")
                })
            except:
                pass

    return {
        "total_analyzed": len(analyzed_files),
        "files": analyzed_files,
        "average_score": round(sum(f["score"] for f in analyzed_files) / len(analyzed_files), 1) if analyzed_files else 0
    }


# ============================================
# New Advanced Analysis Endpoints
# ============================================

@router.post("/quality", response_model=CodeQualityResult)
async def analyze_code_quality(request: AnalysisCodeRequest):
    """
    Perform advanced code quality analysis.

    Analyzes code for:
    - Cyclomatic complexity (using radon)
    - Cognitive complexity
    - Code duplication detection
    - Maintainability index
    - Function-level metrics

    Returns detailed metrics and recommendations for improvement.
    """
    try:
        result = await asyncio.wait_for(
            code_quality_analyzer.analyze(request),
            timeout=request.timeout
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"分析超时（超过 {request.timeout} 秒）"
        )
    except Exception as e:
        logger.error(f"Code quality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/lint", response_model=LintResult)
async def lint_code(request: LintRequest):
    """
    Perform linting analysis using Pylint.

    Checks code for:
    - Convention violations (PEP 8)
    - Refactoring suggestions
    - Warnings and errors
    - Code style issues

    Returns issues with Chinese explanations and fix suggestions.
    """
    try:
        result = await linter_service.lint(request)
        return result
    except Exception as e:
        logger.error(f"Linting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Lint 分析失败: {str(e)}")


@router.post("/security", response_model=SecurityResult)
async def analyze_security(request: SecurityRequest):
    """
    Perform security vulnerability analysis.

    Uses Bandit to detect:
    - Hardcoded passwords and secrets
    - SQL injection vulnerabilities
    - Command injection risks
    - Insecure function usage
    - Cryptographic issues

    Returns issues with severity levels and remediation advice.
    """
    try:
        result = await security_analyzer.analyze(request)
        return result
    except Exception as e:
        logger.error(f"Security analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"安全分析失败: {str(e)}")


@router.post("/performance", response_model=PerformanceResult)
async def analyze_performance(request: PerformanceRequest):
    """
    Perform performance and best practices analysis.

    Detects:
    - Inefficient algorithms (O(n²) patterns)
    - Memory issues (large file reads, memory leaks)
    - Blocking operations
    - Best practice violations

    Returns issues with performance impact and optimization suggestions.
    """
    try:
        result = await performance_analyzer.analyze(request)
        return result
    except Exception as e:
        logger.error(f"Performance analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"性能分析失败: {str(e)}")


@router.post("/comprehensive", response_model=ComprehensiveAnalysisResult)
async def analyze_comprehensive(request: ComprehensiveRequest):
    """
    Perform comprehensive code analysis.

    Combines all analysis types:
    - Code quality (complexity, maintainability)
    - Linting (style, conventions)
    - Security (vulnerabilities)
    - Performance (anti-patterns, best practices)

    Returns a unified report with overall score and recommendations.
    """
    import uuid
    from datetime import datetime, timezone

    try:
        analysis_id = str(uuid.uuid4())
        results = {}
        all_recommendations = []

        # Run analyses in parallel where possible
        tasks = []

        if request.include_quality:
            quality_req = AnalysisCodeRequest(
                code=request.code,
                language=request.language,
                timeout=request.timeout
            )
            tasks.append(("quality", code_quality_analyzer.analyze(quality_req)))

        if request.include_lint:
            lint_req = LintRequest(code=request.code, language=request.language)
            tasks.append(("lint", linter_service.lint(lint_req)))

        if request.include_security:
            security_req = SecurityRequest(code=request.code, language=request.language)
            tasks.append(("security", security_analyzer.analyze(security_req)))

        if request.include_performance:
            perf_req = PerformanceRequest(
                code=request.code,
                language=request.language,
                check_best_practices=True
            )
            tasks.append(("performance", performance_analyzer.analyze(perf_req)))

        # Execute all tasks with timeout
        async def run_with_timeout(name, coro):
            try:
                return name, await asyncio.wait_for(coro, timeout=request.timeout)
            except asyncio.TimeoutError:
                logger.warning(f"{name} analysis timed out")
                return name, None
            except Exception as e:
                logger.error(f"{name} analysis failed: {e}")
                return name, None

        completed = await asyncio.gather(
            *[run_with_timeout(name, coro) for name, coro in tasks]
        )

        for name, result in completed:
            if result:
                results[name] = result
                if hasattr(result, 'recommendations'):
                    all_recommendations.extend(result.recommendations)

        # Calculate overall score
        scores = []
        if "quality" in results:
            scores.append(results["quality"].score)
        if "lint" in results:
            scores.append(results["lint"].score)
        if "security" in results:
            scores.append(results["security"].score)
        if "performance" in results:
            scores.append(results["performance"].score)

        overall_score = sum(scores) / len(scores) if scores else 0

        # Determine grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"

        # Generate summary
        summary_parts = []
        if "quality" in results:
            summary_parts.append(f"代码质量: {results['quality'].grade}")
        if "lint" in results:
            summary_parts.append(f"规范检查: {results['lint'].total_issues} 个问题")
        if "security" in results:
            summary_parts.append(f"安全分析: {results['security'].total_issues} 个问题")
        if "performance" in results:
            summary_parts.append(f"性能分析: {results['performance'].total_issues} 个问题")

        summary = "综合分析完成。" + "；".join(summary_parts) + "。"

        # Collect metrics
        metrics = {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "analyses_completed": len(results),
            "analyses_requested": len(tasks),
        }

        if "quality" in results:
            metrics["quality_score"] = results["quality"].score
            metrics["maintainability_index"] = results["quality"].metrics.maintainability_index
            metrics["avg_complexity"] = results["quality"].metrics.avg_cyclomatic_complexity

        if "lint" in results:
            metrics["lint_score"] = results["lint"].score
            metrics["lint_issues"] = results["lint"].total_issues

        if "security" in results:
            metrics["security_score"] = results["security"].score
            metrics["security_issues"] = results["security"].total_issues
            metrics["high_severity_issues"] = results["security"].high_severity

        if "performance" in results:
            metrics["performance_score"] = results["performance"].score
            metrics["performance_issues"] = results["performance"].total_issues

        return ComprehensiveAnalysisResult(
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc),
            language=request.language,
            overall_score=round(overall_score, 1),
            grade=grade,
            quality=results.get("quality"),
            lint=results.get("lint"),
            security=results.get("security"),
            performance=results.get("performance"),
            summary=summary,
            recommendations=list(set(all_recommendations))[:10],  # Dedupe and limit
            metrics=metrics
        )

    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"综合分析失败: {str(e)}")
