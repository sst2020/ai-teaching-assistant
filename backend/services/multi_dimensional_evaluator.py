"""
Multi-Dimensional Evaluator Service - Evaluates code across multiple dimensions.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from schemas.evaluation import (
    EvaluationDimension, DIMENSION_METADATA,
    DimensionScore, RadarChartData, ClassComparison,
    AbilityAnalysisReport, MultiDimensionalEvaluationRequest
)
from services.enhanced_analysis_service import enhanced_analysis_service

logger = logging.getLogger(__name__)


class MultiDimensionalEvaluator:
    """Service for multi-dimensional code evaluation."""

    def __init__(self):
        self.analysis_service = enhanced_analysis_service

    async def evaluate(
        self,
        request: MultiDimensionalEvaluationRequest,
        db_session=None
    ) -> AbilityAnalysisReport:
        """
        Perform multi-dimensional evaluation of code.

        Args:
            request: Evaluation request
            db_session: Optional database session for class comparison

        Returns:
            AbilityAnalysisReport with comprehensive evaluation
        """
        # Run code analysis
        analysis = await self.analysis_service.analyze(
            code=request.code,
            language=request.language,
            file_id=None
        )

        # Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(analysis, request.language)

        # Calculate overall score (weighted average)
        overall_score = sum(d.score * d.weight for d in dimension_scores)
        overall_grade = self._score_to_grade(overall_score)

        # Generate radar chart data
        radar_chart = self._generate_radar_chart_data(dimension_scores)

        # Get class comparison if requested
        class_comparison = None
        if request.include_class_comparison and db_session and request.class_id:
            class_comparison = await self._get_class_comparison(
                request.student_id, request.class_id, overall_score,
                dimension_scores, db_session
            )
            # Update radar chart with class average
            if class_comparison:
                radar_chart.class_average = [
                    class_comparison.dimension_comparisons.get(d.value, {}).get("class_avg", 0)
                    for d in EvaluationDimension
                ]

        # Generate summaries and recommendations
        summary, summary_zh = self._generate_overall_summary(
            overall_score, dimension_scores
        )
        top_strengths, top_strengths_zh = self._identify_top_strengths(dimension_scores)
        priority_improvements, priority_improvements_zh = self._identify_priority_improvements(
            dimension_scores
        )
        focus_areas, focus_areas_zh = self._recommend_focus_areas(dimension_scores)

        return AbilityAnalysisReport(
            report_id=str(uuid.uuid4()),
            student_id=request.student_id,
            generated_at=datetime.now(timezone.utc),
            overall_score=overall_score,
            overall_grade=overall_grade,
            overall_summary=summary,
            overall_summary_zh=summary_zh,
            dimension_scores=dimension_scores,
            radar_chart=radar_chart,
            class_comparison=class_comparison,
            top_strengths=top_strengths,
            top_strengths_zh=top_strengths_zh,
            priority_improvements=priority_improvements,
            priority_improvements_zh=priority_improvements_zh,
            recommended_focus_areas=focus_areas,
            recommended_focus_areas_zh=focus_areas_zh
        )

    def _calculate_dimension_scores(
        self, analysis, language: str
    ) -> List[DimensionScore]:
        """Calculate scores for each evaluation dimension."""
        scores = []

        # Technical Ability
        tech_score = self._calculate_technical_ability(analysis, language)
        scores.append(tech_score)

        # Code Quality
        quality_score = self._calculate_code_quality(analysis)
        scores.append(quality_score)

        # Innovation
        innovation_score = self._calculate_innovation(analysis)
        scores.append(innovation_score)

        # Best Practices
        practices_score = self._calculate_best_practices(analysis, language)
        scores.append(practices_score)

        # Efficiency
        efficiency_score = self._calculate_efficiency(analysis)
        scores.append(efficiency_score)

        # Documentation
        doc_score = self._calculate_documentation(analysis)
        scores.append(doc_score)

        return scores

    def _calculate_technical_ability(self, analysis, language: str) -> DimensionScore:
        """Calculate technical ability score."""
        meta = DIMENSION_METADATA[EvaluationDimension.TECHNICAL_ABILITY]
        score = 100.0
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Check function count and structure
        if analysis.complexity.function_count >= 2:
            strengths.append("Good use of functions for code organization")
            strengths_zh.append("良好地使用函数进行代码组织")
        else:
            improvements.append("Consider breaking code into more functions")
            improvements_zh.append("考虑将代码拆分为更多函数")
            score -= 10

        # Check class usage (if applicable)
        if analysis.complexity.class_count > 0:
            strengths.append("Uses object-oriented programming concepts")
            strengths_zh.append("使用了面向对象编程概念")
        elif analysis.lines.total_lines > 50:
            improvements.append("Consider using classes for larger programs")
            improvements_zh.append("对于较大的程序，考虑使用类")
            score -= 5

        # Check for proper error handling (basic check)
        if "try" in str(analysis) or "except" in str(analysis):
            strengths.append("Implements error handling")
            strengths_zh.append("实现了错误处理")
        else:
            improvements.append("Add error handling for robustness")
            improvements_zh.append("添加错误处理以提高健壮性")
            score -= 10

        return DimensionScore(
            dimension=EvaluationDimension.TECHNICAL_ABILITY,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Technical ability score: {score:.0f}/100",
            description_zh=f"技术能力得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _calculate_code_quality(self, analysis) -> DimensionScore:
        """Calculate code quality score."""
        meta = DIMENSION_METADATA[EvaluationDimension.CODE_QUALITY]
        score = 100.0
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Cyclomatic complexity
        if analysis.complexity.cyclomatic_complexity <= 5:
            strengths.append("Low cyclomatic complexity - easy to understand")
            strengths_zh.append("低圈复杂度 - 易于理解")
        elif analysis.complexity.cyclomatic_complexity <= 10:
            score -= 10
        else:
            improvements.append("High complexity - consider refactoring")
            improvements_zh.append("复杂度过高 - 考虑重构")
            score -= 25

        # Nesting depth
        if analysis.complexity.max_nesting_depth <= 3:
            strengths.append("Good nesting depth - well-structured")
            strengths_zh.append("良好的嵌套深度 - 结构清晰")
        elif analysis.complexity.max_nesting_depth <= 4:
            score -= 10
        else:
            improvements.append("Deep nesting - flatten the structure")
            improvements_zh.append("嵌套过深 - 扁平化结构")
            score -= 20

        # Function length
        if analysis.complexity.avg_function_length <= 20:
            strengths.append("Functions are appropriately sized")
            strengths_zh.append("函数大小适中")
        elif analysis.complexity.max_function_length > 50:
            improvements.append("Some functions are too long")
            improvements_zh.append("部分函数过长")
            score -= 15

        # Naming issues
        if len(analysis.naming_issues) == 0:
            strengths.append("Consistent naming conventions")
            strengths_zh.append("命名规范一致")
        else:
            improvements.append(f"Fix {len(analysis.naming_issues)} naming issues")
            improvements_zh.append(f"修复 {len(analysis.naming_issues)} 个命名问题")
            score -= min(20, len(analysis.naming_issues) * 3)

        return DimensionScore(
            dimension=EvaluationDimension.CODE_QUALITY,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Code quality score: {score:.0f}/100",
            description_zh=f"代码质量得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _calculate_innovation(self, analysis) -> DimensionScore:
        """Calculate innovation score."""
        meta = DIMENSION_METADATA[EvaluationDimension.INNOVATION]
        score = 70.0  # Base score for innovation
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Check for advanced features usage
        if analysis.complexity.class_count > 0:
            score += 10
            strengths.append("Uses object-oriented design")
            strengths_zh.append("使用面向对象设计")

        if analysis.complexity.function_count >= 3:
            score += 10
            strengths.append("Good modular design")
            strengths_zh.append("良好的模块化设计")

        # Check for variety in code structure
        if analysis.lines.total_lines > 20 and analysis.complexity.function_count >= 2:
            score += 10
            strengths.append("Well-organized code structure")
            strengths_zh.append("代码结构组织良好")

        if score < 80:
            improvements.append("Try exploring more advanced language features")
            improvements_zh.append("尝试探索更多高级语言特性")

        return DimensionScore(
            dimension=EvaluationDimension.INNOVATION,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Innovation score: {score:.0f}/100",
            description_zh=f"创新性得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _calculate_best_practices(self, analysis, language: str) -> DimensionScore:
        """Calculate best practices score."""
        meta = DIMENSION_METADATA[EvaluationDimension.BEST_PRACTICES]
        score = 100.0
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Security issues
        if not analysis.security_issues:
            strengths.append("No security vulnerabilities detected")
            strengths_zh.append("未检测到安全漏洞")
        else:
            for issue in analysis.security_issues:
                if issue.severity == "high":
                    score -= 20
                elif issue.severity == "medium":
                    score -= 10
                else:
                    score -= 5
            improvements.append(f"Address {len(analysis.security_issues)} security issues")
            improvements_zh.append(f"解决 {len(analysis.security_issues)} 个安全问题")

        # Naming conventions
        if len(analysis.naming_issues) == 0:
            strengths.append("Follows naming conventions")
            strengths_zh.append("遵循命名规范")
        else:
            score -= min(15, len(analysis.naming_issues) * 2)

        # Code violations
        violation_count = len(analysis.violations)
        if violation_count == 0:
            strengths.append("No code style violations")
            strengths_zh.append("无代码风格违规")
        else:
            score -= min(20, violation_count * 2)
            improvements.append(f"Fix {violation_count} style violations")
            improvements_zh.append(f"修复 {violation_count} 个风格违规")

        return DimensionScore(
            dimension=EvaluationDimension.BEST_PRACTICES,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Best practices score: {score:.0f}/100",
            description_zh=f"最佳实践得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _calculate_efficiency(self, analysis) -> DimensionScore:
        """Calculate efficiency score."""
        meta = DIMENSION_METADATA[EvaluationDimension.EFFICIENCY]
        score = 85.0  # Base score
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Cognitive complexity (affects efficiency understanding)
        if analysis.complexity.cognitive_complexity <= 10:
            score += 10
            strengths.append("Low cognitive complexity - efficient logic")
            strengths_zh.append("低认知复杂度 - 逻辑高效")
        elif analysis.complexity.cognitive_complexity > 20:
            score -= 15
            improvements.append("Simplify complex logic for better efficiency")
            improvements_zh.append("简化复杂逻辑以提高效率")

        # Function count vs lines (modularity)
        if analysis.lines.total_lines > 0 and analysis.complexity.function_count > 0:
            lines_per_func = analysis.lines.total_lines / analysis.complexity.function_count
            if lines_per_func <= 25:
                strengths.append("Good function granularity")
                strengths_zh.append("良好的函数粒度")
            elif lines_per_func > 50:
                score -= 10
                improvements.append("Break down large functions")
                improvements_zh.append("拆分大型函数")

        return DimensionScore(
            dimension=EvaluationDimension.EFFICIENCY,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Efficiency score: {score:.0f}/100",
            description_zh=f"效率得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _calculate_documentation(self, analysis) -> DimensionScore:
        """Calculate documentation score."""
        meta = DIMENSION_METADATA[EvaluationDimension.DOCUMENTATION]
        score = 50.0  # Base score
        strengths = []
        strengths_zh = []
        improvements = []
        improvements_zh = []

        # Comment ratio
        if analysis.lines.total_lines > 0:
            comment_ratio = analysis.lines.comment_lines / analysis.lines.total_lines
            if comment_ratio >= 0.15:
                score += 40
                strengths.append("Good comment coverage")
                strengths_zh.append("良好的注释覆盖率")
            elif comment_ratio >= 0.05:
                score += 20
                strengths.append("Some comments present")
                strengths_zh.append("有一些注释")
            else:
                improvements.append("Add more comments to explain code")
                improvements_zh.append("添加更多注释来解释代码")

        # Docstrings (check if any exist in the code)
        if analysis.lines.comment_lines > 0:
            score += 10
            strengths.append("Code includes documentation")
            strengths_zh.append("代码包含文档")
        else:
            improvements.append("Add docstrings to functions and classes")
            improvements_zh.append("为函数和类添加文档字符串")

        return DimensionScore(
            dimension=EvaluationDimension.DOCUMENTATION,
            score=max(0, min(100, score)),
            weight=meta["weight"],
            name=meta["name"],
            name_zh=meta["name_zh"],
            description=f"Documentation score: {score:.0f}/100",
            description_zh=f"文档得分：{score:.0f}/100",
            strengths=strengths,
            strengths_zh=strengths_zh,
            improvements=improvements,
            improvements_zh=improvements_zh
        )

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_radar_chart_data(
        self, dimension_scores: List[DimensionScore]
    ) -> RadarChartData:
        """Generate radar chart data from dimension scores."""
        labels = [d.name for d in dimension_scores]
        labels_zh = [d.name_zh for d in dimension_scores]
        scores = [d.score for d in dimension_scores]

        return RadarChartData(
            labels=labels,
            labels_zh=labels_zh,
            student_scores=scores,
            class_average=None,
            max_scores=[100] * len(dimension_scores)
        )

    async def _get_class_comparison(
        self, student_id: str, class_id: str, student_overall: float,
        dimension_scores: List[DimensionScore], db_session
    ) -> Optional[ClassComparison]:
        """Get class comparison statistics."""
        from sqlalchemy import select, func
        from models.submission import Submission
        from models.grading_result import GradingResult
        from models.student import Student

        try:
            # Query all students in the class with their grades
            query = (
                select(GradingResult.overall_score, GradingResult.max_score)
                .join(Submission, GradingResult.submission_id == Submission.submission_id)
                .join(Student, Submission.student_id == Student.student_id)
                .where(Student.class_id == class_id)
            )

            result = await db_session.execute(query)
            grades = result.all()

            if not grades:
                return None

            # Calculate statistics
            scores = [g.overall_score / g.max_score * 100 if g.max_score > 0 else 0
                     for g in grades]
            scores.sort(reverse=True)

            class_avg = sum(scores) / len(scores)
            class_median = scores[len(scores) // 2]
            class_max = max(scores)
            class_min = min(scores)

            # Calculate rank and percentile
            rank = sum(1 for s in scores if s > student_overall) + 1
            percentile = (1 - (rank - 1) / len(scores)) * 100

            # Per-dimension comparison (simplified - using overall for now)
            dimension_comparisons = {}
            for d in dimension_scores:
                dimension_comparisons[d.dimension.value] = {
                    "student": d.score,
                    "class_avg": class_avg,  # Simplified
                }

            return ClassComparison(
                student_id=student_id,
                student_overall=student_overall,
                class_average=class_avg,
                class_median=class_median,
                class_max=class_max,
                class_min=class_min,
                percentile=percentile,
                rank=rank,
                total_students=len(scores),
                dimension_comparisons=dimension_comparisons
            )

        except Exception as e:
            logger.error(f"Failed to get class comparison: {e}")
            return None

    def _generate_overall_summary(
        self, overall_score: float, dimension_scores: List[DimensionScore]
    ) -> Tuple[str, str]:
        """Generate overall summary."""
        grade = self._score_to_grade(overall_score)

        # Find best and worst dimensions
        sorted_dims = sorted(dimension_scores, key=lambda d: d.score, reverse=True)
        best = sorted_dims[0]
        worst = sorted_dims[-1]

        summary_en = f"Overall score: {overall_score:.0f}/100 (Grade: {grade}). "
        summary_en += f"Strongest area: {best.name} ({best.score:.0f}). "
        summary_en += f"Area for improvement: {worst.name} ({worst.score:.0f})."

        summary_zh = f"总分：{overall_score:.0f}/100（等级：{grade}）。"
        summary_zh += f"最强领域：{best.name_zh}（{best.score:.0f}分）。"
        summary_zh += f"待改进领域：{worst.name_zh}（{worst.score:.0f}分）。"

        return summary_en, summary_zh

    def _identify_top_strengths(
        self, dimension_scores: List[DimensionScore]
    ) -> Tuple[List[str], List[str]]:
        """Identify top strengths across all dimensions."""
        all_strengths = []
        all_strengths_zh = []

        for d in sorted(dimension_scores, key=lambda x: x.score, reverse=True)[:3]:
            all_strengths.extend(d.strengths[:2])
            all_strengths_zh.extend(d.strengths_zh[:2])

        return all_strengths[:5], all_strengths_zh[:5]

    def _identify_priority_improvements(
        self, dimension_scores: List[DimensionScore]
    ) -> Tuple[List[str], List[str]]:
        """Identify priority improvements."""
        all_improvements = []
        all_improvements_zh = []

        for d in sorted(dimension_scores, key=lambda x: x.score)[:3]:
            all_improvements.extend(d.improvements[:2])
            all_improvements_zh.extend(d.improvements_zh[:2])

        return all_improvements[:5], all_improvements_zh[:5]

    def _recommend_focus_areas(
        self, dimension_scores: List[DimensionScore]
    ) -> Tuple[List[str], List[str]]:
        """Recommend focus areas for improvement."""
        focus = []
        focus_zh = []

        # Find dimensions below 70
        weak_dims = [d for d in dimension_scores if d.score < 70]
        for d in weak_dims[:3]:
            focus.append(f"Focus on improving {d.name}")
            focus_zh.append(f"重点提升{d.name_zh}")

        if not focus:
            focus.append("Continue maintaining your strong performance")
            focus_zh.append("继续保持你的优秀表现")

        return focus, focus_zh


# Singleton instance
multi_dimensional_evaluator = MultiDimensionalEvaluator()

