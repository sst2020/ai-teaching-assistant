"""
Feedback Generation Service - Generates personalized, constructive feedback for code submissions.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

from schemas.feedback import (
    FeedbackTone, FeedbackCategory, FeedbackItem, CategoryFeedback,
    GeneratedFeedback, GenerateFeedbackRequest,
    # New personalized feedback schemas
    FeedbackDetailLevel, SuggestionDifficulty, StudentLevel, PerformanceTrend,
    ProgressiveSuggestion, LearningPath, StudentHistoryAnalysis,
    PersonalizedFeedbackRequest, PersonalizedFeedback, PersonalizedFeedbackResponse
)
from services.enhanced_analysis_service import enhanced_analysis_service

logger = logging.getLogger(__name__)


@dataclass
class FeedbackConfig:
    """Configuration for feedback generation."""
    max_items_per_category: int = 5
    include_code_snippets: bool = True
    include_suggestions: bool = True
    min_score_for_encouragement: float = 70.0
    language_specific_tips: bool = True


# Language-specific best practices
LANGUAGE_BEST_PRACTICES = {
    "python": {
        "naming": "Use snake_case for variables and functions, PascalCase for classes",
        "docstrings": "Add docstrings to all public functions and classes",
        "imports": "Group imports: standard library, third-party, local",
        "type_hints": "Consider adding type hints for better code clarity",
    },
    "javascript": {
        "naming": "Use camelCase for variables and functions, PascalCase for classes",
        "const_let": "Prefer const over let, avoid var",
        "arrow_functions": "Use arrow functions for callbacks",
        "async_await": "Use async/await instead of raw promises when possible",
    },
    "java": {
        "naming": "Use camelCase for methods, PascalCase for classes, UPPER_CASE for constants",
        "access_modifiers": "Use appropriate access modifiers (private, protected, public)",
        "exceptions": "Handle exceptions properly, don't catch generic Exception",
        "javadoc": "Add Javadoc comments to public methods",
    },
    "typescript": {
        "types": "Define explicit types instead of using 'any'",
        "interfaces": "Use interfaces for object shapes",
        "strict_mode": "Enable strict mode in tsconfig",
        "null_checks": "Use strict null checks",
    },
    "c": {
        "memory": "Always free allocated memory to prevent leaks",
        "pointers": "Check for NULL before dereferencing pointers",
        "bounds": "Validate array bounds before access",
        "headers": "Use header guards to prevent multiple inclusion",
    },
    "cpp": {
        "smart_pointers": "Use smart pointers instead of raw pointers",
        "raii": "Follow RAII principles for resource management",
        "const": "Use const correctness",
        "references": "Prefer references over pointers when possible",
    }
}

# Tone-specific message templates
TONE_TEMPLATES = {
    FeedbackTone.ENCOURAGING: {
        "prefix": "Great effort! ",
        "suggestion_prefix": "Here's a tip to make it even better: ",
        "closing": "Keep up the excellent work! You're making great progress.",
    },
    FeedbackTone.PROFESSIONAL: {
        "prefix": "",
        "suggestion_prefix": "Recommendation: ",
        "closing": "Please review the feedback and make the necessary improvements.",
    },
    FeedbackTone.DETAILED: {
        "prefix": "Analysis: ",
        "suggestion_prefix": "Detailed suggestion: ",
        "closing": "For further improvement, consider reviewing the detailed feedback above.",
    },
    FeedbackTone.CONCISE: {
        "prefix": "",
        "suggestion_prefix": "Fix: ",
        "closing": "",
    },
    FeedbackTone.FRIENDLY: {
        "prefix": "Hey! ",
        "suggestion_prefix": "Quick tip: ",
        "closing": "You're doing great! Let me know if you have questions.",
    },
    FeedbackTone.STRICT: {
        "prefix": "Issue: ",
        "suggestion_prefix": "Required fix: ",
        "closing": "Address all issues before resubmission.",
    }
}

# Detail level configurations
DETAIL_LEVEL_CONFIG = {
    FeedbackDetailLevel.BRIEF: {
        "max_items": 3,
        "include_examples": False,
        "include_resources": False,
        "summary_length": "short",
    },
    FeedbackDetailLevel.STANDARD: {
        "max_items": 5,
        "include_examples": True,
        "include_resources": False,
        "summary_length": "medium",
    },
    FeedbackDetailLevel.DETAILED: {
        "max_items": 8,
        "include_examples": True,
        "include_resources": True,
        "summary_length": "long",
    },
    FeedbackDetailLevel.COMPREHENSIVE: {
        "max_items": 15,
        "include_examples": True,
        "include_resources": True,
        "summary_length": "full",
    },
}

# Student level specific messages
LEVEL_MESSAGES = {
    StudentLevel.BEGINNER: {
        "prefix": "作为初学者，",
        "prefix_en": "As a beginner, ",
        "encouragement": "每一步进步都值得庆祝！继续保持学习的热情。",
        "encouragement_en": "Every step forward is worth celebrating! Keep up your enthusiasm for learning.",
        "complexity_threshold": 5,
        "suggestion_style": "simple",
    },
    StudentLevel.INTERMEDIATE: {
        "prefix": "作为中级学习者，",
        "prefix_en": "As an intermediate learner, ",
        "encouragement": "你已经掌握了基础，现在是时候挑战更高级的概念了。",
        "encouragement_en": "You've mastered the basics, now it's time to challenge yourself with advanced concepts.",
        "complexity_threshold": 10,
        "suggestion_style": "moderate",
    },
    StudentLevel.ADVANCED: {
        "prefix": "作为高级学习者，",
        "prefix_en": "As an advanced learner, ",
        "encouragement": "你的代码展现了扎实的功底，继续追求卓越！",
        "encouragement_en": "Your code shows solid foundations, keep striving for excellence!",
        "complexity_threshold": 15,
        "suggestion_style": "advanced",
    },
}

# Trend-specific messages
TREND_MESSAGES = {
    PerformanceTrend.IMPROVING: {
        "message": "你的表现持续进步！",
        "message_en": "Your performance is continuously improving!",
        "emoji": "📈",
    },
    PerformanceTrend.DECLINING: {
        "message": "最近的表现有所下滑，让我们一起找出原因。",
        "message_en": "Recent performance has declined, let's find out why together.",
        "emoji": "📉",
    },
    PerformanceTrend.STABLE: {
        "message": "你的表现保持稳定。",
        "message_en": "Your performance remains stable.",
        "emoji": "➡️",
    },
    PerformanceTrend.FLUCTUATING: {
        "message": "你的表现有些波动，让我们找到更稳定的学习节奏。",
        "message_en": "Your performance fluctuates, let's find a more stable learning rhythm.",
        "emoji": "📊",
    },
}


class FeedbackGenerationService:
    """Service for generating personalized code feedback."""

    def __init__(self, config: Optional[FeedbackConfig] = None):
        self.config = config or FeedbackConfig()
        self.analysis_service = enhanced_analysis_service

    async def generate_feedback(
        self,
        request: GenerateFeedbackRequest
    ) -> GeneratedFeedback:
        """
        Generate comprehensive feedback for code.

        Args:
            request: Feedback generation request

        Returns:
            GeneratedFeedback with categorized feedback items
        """
        # Run code analysis
        analysis_result = await self.analysis_service.analyze(
            code=request.code,
            language=request.language,
            file_id=request.file_id
        )

        # Generate feedback for each category
        categories = []

        # Code Quality Feedback
        quality_feedback = self._generate_quality_feedback(
            analysis_result, request.language, request.tone
        )
        if quality_feedback.items:
            categories.append(quality_feedback)

        # Logic & Efficiency Feedback
        logic_feedback = self._generate_logic_feedback(
            analysis_result, request.language, request.tone
        )
        if logic_feedback.items:
            categories.append(logic_feedback)

        # Style & Readability Feedback
        style_feedback = self._generate_style_feedback(
            analysis_result, request.language, request.tone
        )
        if style_feedback.items:
            categories.append(style_feedback)

        # Suggestions Feedback
        suggestions_feedback = self._generate_suggestions_feedback(
            analysis_result, request.language, request.tone
        )
        if suggestions_feedback.items:
            categories.append(suggestions_feedback)

        # Calculate overall score and grade
        overall_score = analysis_result.summary.overall_score
        overall_grade = analysis_result.summary.grade

        # Generate summary, strengths, and improvements
        summary = self._generate_summary(analysis_result, request.tone)
        strengths = self._identify_strengths(analysis_result, request.language)
        improvements = self._identify_improvements(analysis_result)
        next_steps = self._generate_next_steps(analysis_result, request.language)

        return GeneratedFeedback(
            submission_id=request.submission_id,
            file_id=request.file_id,
            overall_score=overall_score,
            overall_grade=overall_grade,
            summary=summary,
            categories=categories,
            strengths=strengths,
            improvements=improvements,
            next_steps=next_steps,
            generated_at=datetime.utcnow(),
            tone=request.tone,
            language=request.language
        )

    def _generate_quality_feedback(
        self, analysis, language: str, tone: FeedbackTone
    ) -> CategoryFeedback:
        """Generate code quality feedback."""
        items = []
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])

        # Complexity issues
        if analysis.complexity.cyclomatic_complexity > 10:
            items.append(FeedbackItem(
                category=FeedbackCategory.CODE_QUALITY,
                title="High Cyclomatic Complexity",
                message=f"{tone_config['prefix']}The code has a cyclomatic complexity of {analysis.complexity.cyclomatic_complexity}. Consider breaking down complex functions into smaller, more focused functions.",
                severity="warning",
                suggestion="Extract complex logic into separate helper functions"
            ))

        # Nesting depth
        if analysis.complexity.max_nesting_depth > 4:
            items.append(FeedbackItem(
                category=FeedbackCategory.CODE_QUALITY,
                title="Deep Nesting",
                message=f"{tone_config['prefix']}Maximum nesting depth is {analysis.complexity.max_nesting_depth}. Deep nesting makes code harder to read and maintain.",
                severity="warning",
                suggestion="Use early returns or extract nested logic into separate functions"
            ))

        # Long functions
        if analysis.complexity.max_function_length > 50:
            items.append(FeedbackItem(
                category=FeedbackCategory.CODE_QUALITY,
                title="Long Function",
                message=f"{tone_config['prefix']}Found a function with {analysis.complexity.max_function_length} lines. Long functions are harder to understand and test.",
                severity="info",
                suggestion="Break down into smaller functions with single responsibilities"
            ))

        # Too many parameters
        if analysis.complexity.max_parameters > 5:
            items.append(FeedbackItem(
                category=FeedbackCategory.CODE_QUALITY,
                title="Too Many Parameters",
                message=f"{tone_config['prefix']}A function has {analysis.complexity.max_parameters} parameters. This can indicate the function is doing too much.",
                severity="info",
                suggestion="Consider using a configuration object or breaking down the function"
            ))

        # Calculate category score
        score = 100.0
        if analysis.complexity.cyclomatic_complexity > 10:
            score -= 15
        if analysis.complexity.max_nesting_depth > 4:
            score -= 10
        if analysis.complexity.max_function_length > 50:
            score -= 10
        if analysis.complexity.max_parameters > 5:
            score -= 5

        return CategoryFeedback(
            category=FeedbackCategory.CODE_QUALITY,
            score=max(0, score),
            items=items[:self.config.max_items_per_category],
            summary=f"Code quality score: {max(0, score):.0f}/100"
        )

    def _generate_logic_feedback(
        self, analysis, language: str, tone: FeedbackTone
    ) -> CategoryFeedback:
        """Generate logic and efficiency feedback."""
        items = []
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])

        # Check for cognitive complexity
        if analysis.complexity.cognitive_complexity > 15:
            items.append(FeedbackItem(
                category=FeedbackCategory.LOGIC_EFFICIENCY,
                title="High Cognitive Complexity",
                message=f"{tone_config['prefix']}Cognitive complexity is {analysis.complexity.cognitive_complexity}. This indicates the code may be difficult to understand.",
                severity="warning",
                suggestion="Simplify conditional logic and reduce nested structures"
            ))

        score = 100.0
        if analysis.complexity.cognitive_complexity > 15:
            score -= 20

        return CategoryFeedback(
            category=FeedbackCategory.LOGIC_EFFICIENCY,
            score=max(0, score),
            items=items[:self.config.max_items_per_category],
            summary=f"Logic efficiency score: {max(0, score):.0f}/100"
        )


    def _generate_style_feedback(
        self, analysis, language: str, tone: FeedbackTone
    ) -> CategoryFeedback:
        """Generate style and readability feedback."""
        items = []
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])

        # Naming convention issues
        for issue in analysis.naming_issues[:self.config.max_items_per_category]:
            items.append(FeedbackItem(
                category=FeedbackCategory.STYLE_READABILITY,
                title="Naming Convention Issue",
                message=f"{tone_config['prefix']}{issue.message}",
                severity=issue.severity,
                line_number=issue.line_number,
                suggestion=f"Rename '{issue.identifier}' to follow {issue.expected_convention} convention"
            ))

        # Line length issues
        if analysis.lines.total_lines > 0:
            long_lines = [v for v in analysis.violations if 'line length' in v.message.lower()]
            for violation in long_lines[:2]:
                items.append(FeedbackItem(
                    category=FeedbackCategory.STYLE_READABILITY,
                    title="Line Too Long",
                    message=f"{tone_config['prefix']}Line exceeds recommended length.",
                    severity="info",
                    line_number=violation.line_number,
                    suggestion="Break long lines for better readability"
                ))

        score = 100.0
        score -= len(analysis.naming_issues) * 2

        return CategoryFeedback(
            category=FeedbackCategory.STYLE_READABILITY,
            score=max(0, min(100, score)),
            items=items[:self.config.max_items_per_category],
            summary=f"Style score: {max(0, min(100, score)):.0f}/100"
        )

    def _generate_security_feedback(
        self, analysis, tone: FeedbackTone
    ) -> CategoryFeedback:
        """Generate security feedback."""
        items = []
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])

        for issue in analysis.security_issues[:self.config.max_items_per_category]:
            items.append(FeedbackItem(
                category=FeedbackCategory.SECURITY,
                title=f"Security: {issue.issue_type}",
                message=f"{tone_config['prefix']}{issue.message}",
                severity="error" if issue.severity == "high" else "warning",
                line_number=issue.line_number,
                suggestion=issue.recommendation
            ))

        score = 100.0
        for issue in analysis.security_issues:
            if issue.severity == "high":
                score -= 20
            elif issue.severity == "medium":
                score -= 10
            else:
                score -= 5

        return CategoryFeedback(
            category=FeedbackCategory.SECURITY,
            score=max(0, score),
            items=items,
            summary=f"Security score: {max(0, score):.0f}/100"
        )

    def _generate_suggestions_feedback(
        self, analysis, language: str, tone: FeedbackTone
    ) -> CategoryFeedback:
        """Generate improvement suggestions."""
        items = []
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])

        # Language-specific best practices
        best_practices = LANGUAGE_BEST_PRACTICES.get(language, {})
        for key, tip in list(best_practices.items())[:3]:
            items.append(FeedbackItem(
                category=FeedbackCategory.SUGGESTIONS,
                title=f"Best Practice: {key.replace('_', ' ').title()}",
                message=f"{tone_config['suggestion_prefix']}{tip}",
                severity="info"
            ))

        return CategoryFeedback(
            category=FeedbackCategory.SUGGESTIONS,
            score=100.0,
            items=items[:self.config.max_items_per_category],
            summary="Suggestions for improvement"
        )

    def _generate_summary(self, analysis, tone: FeedbackTone) -> str:
        """Generate overall feedback summary."""
        tone_config = TONE_TEMPLATES.get(tone, TONE_TEMPLATES[FeedbackTone.PROFESSIONAL])
        score = analysis.summary.overall_score
        grade = analysis.summary.grade

        if score >= 90:
            summary = f"Excellent work! Your code scored {score:.0f}/100 (Grade: {grade}). "
        elif score >= 80:
            summary = f"Good job! Your code scored {score:.0f}/100 (Grade: {grade}). "
        elif score >= 70:
            summary = f"Your code scored {score:.0f}/100 (Grade: {grade}). "
        elif score >= 60:
            summary = f"Your code needs improvement. Score: {score:.0f}/100 (Grade: {grade}). "
        else:
            summary = f"Your code requires significant work. Score: {score:.0f}/100 (Grade: {grade}). "

        summary += tone_config.get("closing", "")
        return summary

    def _identify_strengths(self, analysis, language: str) -> List[str]:
        """Identify code strengths."""
        strengths = []

        if analysis.complexity.cyclomatic_complexity <= 5:
            strengths.append("Low cyclomatic complexity - code is easy to follow")
        if analysis.complexity.max_nesting_depth <= 2:
            strengths.append("Good nesting depth - code is well-structured")
        if analysis.complexity.avg_function_length <= 20:
            strengths.append("Functions are appropriately sized")
        if not analysis.security_issues:
            strengths.append("No security issues detected")
        if len(analysis.naming_issues) == 0:
            strengths.append("Consistent naming conventions")
        if analysis.lines.comment_lines > 0:
            strengths.append("Code includes comments for documentation")

        return strengths[:5]

    def _identify_improvements(self, analysis) -> List[str]:
        """Identify areas for improvement."""
        improvements = []

        if analysis.complexity.cyclomatic_complexity > 10:
            improvements.append("Reduce code complexity by breaking down large functions")
        if analysis.complexity.max_nesting_depth > 4:
            improvements.append("Reduce nesting depth for better readability")
        if analysis.security_issues:
            improvements.append("Address security vulnerabilities")
        if analysis.naming_issues:
            improvements.append("Fix naming convention inconsistencies")
        if analysis.lines.comment_lines == 0:
            improvements.append("Add comments to explain complex logic")

        return improvements[:5]

    def _generate_next_steps(self, analysis, language: str) -> List[str]:
        """Generate recommended next steps."""
        steps = []

        if analysis.security_issues:
            steps.append("Priority: Fix security issues before deployment")
        if analysis.complexity.cyclomatic_complexity > 15:
            steps.append("Refactor complex functions into smaller units")
        if analysis.naming_issues:
            steps.append("Review and fix naming convention issues")

        # Add language-specific tips
        best_practices = LANGUAGE_BEST_PRACTICES.get(language, {})
        if best_practices:
            first_tip = list(best_practices.values())[0]
            steps.append(f"Consider: {first_tip}")

        if not steps:
            steps.append("Continue maintaining code quality")

        return steps[:5]

    # ============================================
    # Personalized Feedback Methods
    # ============================================

    async def generate_personalized_feedback(
        self,
        request: PersonalizedFeedbackRequest,
        db_session=None
    ) -> PersonalizedFeedback:
        """
        Generate personalized feedback based on student history.

        Args:
            request: Personalized feedback request
            db_session: Optional database session for history queries

        Returns:
            PersonalizedFeedback with history-aware feedback
        """
        import time
        start_time = time.time()

        # Run code analysis
        analysis_result = await self.analysis_service.analyze(
            code=request.code,
            language=request.language,
            file_id=None
        )

        # Get student history analysis
        history_analysis = None
        if request.include_history_analysis and db_session:
            history_analysis = await self._analyze_student_history(
                request.student_id, db_session
            )
        else:
            # Create default history analysis
            history_analysis = StudentHistoryAnalysis(
                student_id=request.student_id,
                total_submissions=0,
                average_score=0.0,
                trend=PerformanceTrend.STABLE,
                trend_zh="稳定",
                level=StudentLevel.INTERMEDIATE,
                level_zh="中级",
                strengths=[],
                strengths_zh=[],
                weaknesses=[],
                weaknesses_zh=[],
                recurring_issues=[],
                recurring_issues_zh=[],
                improvement_rate=0.0,
                recent_scores=[]
            )

        # Determine student level from history or default
        student_level = history_analysis.level if history_analysis else StudentLevel.INTERMEDIATE

        # Generate feedback categories
        categories = await self._generate_personalized_categories(
            analysis_result, request.language, request.tone,
            request.detail_level, student_level
        )

        # Generate personalized message
        personalized_msg, personalized_msg_zh = self._generate_personalized_message(
            analysis_result, history_analysis, request.tone
        )

        # Generate progressive suggestions
        suggestions = self._generate_progressive_suggestions(
            analysis_result, request.language, student_level, request.max_suggestions
        )

        # Generate learning path if requested
        learning_path = None
        if request.include_learning_path and suggestions:
            learning_path = self._create_learning_path(suggestions, student_level)

        # Generate encouragement
        encouragement, encouragement_zh = self._generate_encouragement(
            analysis_result, history_analysis, request.tone
        )

        # Calculate overall score and grade
        overall_score = analysis_result.summary.overall_score
        overall_grade = analysis_result.summary.grade

        # Generate summary
        summary = self._generate_summary(analysis_result, request.tone)
        summary_zh = self._generate_summary_zh(analysis_result, request.tone)

        processing_time = (time.time() - start_time) * 1000

        return PersonalizedFeedback(
            feedback_id=str(uuid.uuid4()),
            student_id=request.student_id,
            submission_id=request.submission_id,
            generated_at=datetime.now(timezone.utc),
            overall_score=overall_score,
            overall_grade=overall_grade,
            summary=summary,
            summary_zh=summary_zh,
            personalized_message=personalized_msg,
            personalized_message_zh=personalized_msg_zh,
            history_analysis=history_analysis,
            categories=categories,
            suggestions=suggestions,
            learning_path=learning_path,
            encouragement=encouragement,
            encouragement_zh=encouragement_zh,
            tone=request.tone,
            detail_level=request.detail_level,
            language=request.language
        )

    async def _analyze_student_history(
        self,
        student_id: str,
        db_session
    ) -> StudentHistoryAnalysis:
        """
        Analyze student's historical performance.

        Args:
            student_id: Student ID
            db_session: Database session

        Returns:
            StudentHistoryAnalysis with trend and level information
        """
        from sqlalchemy import select, desc
        from models.submission import Submission
        from models.grading_result import GradingResult

        # Query recent submissions with grades
        query = (
            select(Submission, GradingResult)
            .join(GradingResult, Submission.submission_id == GradingResult.submission_id, isouter=True)
            .where(Submission.student_id == student_id)
            .order_by(desc(Submission.submitted_at))
            .limit(20)
        )

        result = await db_session.execute(query)
        submissions = result.all()

        if not submissions:
            return StudentHistoryAnalysis(
                student_id=student_id,
                total_submissions=0,
                average_score=0.0,
                trend=PerformanceTrend.STABLE,
                trend_zh="稳定",
                level=StudentLevel.BEGINNER,
                level_zh="初学者",
                strengths=[],
                strengths_zh=[],
                weaknesses=[],
                weaknesses_zh=[],
                recurring_issues=[],
                recurring_issues_zh=[],
                improvement_rate=0.0,
                recent_scores=[]
            )

        # Extract scores
        scores = []
        for submission, grading in submissions:
            if grading and grading.overall_score is not None:
                scores.append(grading.percentage_score)

        total_submissions = len(submissions)
        average_score = sum(scores) / len(scores) if scores else 0.0
        recent_scores = scores[:10]

        # Determine trend
        trend, trend_zh = self._calculate_trend(scores)

        # Determine level based on average score
        level, level_zh = self._determine_level(average_score, total_submissions)

        # Analyze strengths and weaknesses from feedback
        strengths, strengths_zh, weaknesses, weaknesses_zh = await self._analyze_feedback_patterns(
            submissions, db_session
        )

        # Find recurring issues
        recurring_issues, recurring_issues_zh = await self._find_recurring_issues(
            submissions, db_session
        )

        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(scores)

        return StudentHistoryAnalysis(
            student_id=student_id,
            total_submissions=total_submissions,
            average_score=average_score,
            trend=trend,
            trend_zh=trend_zh,
            level=level,
            level_zh=level_zh,
            strengths=strengths,
            strengths_zh=strengths_zh,
            weaknesses=weaknesses,
            weaknesses_zh=weaknesses_zh,
            recurring_issues=recurring_issues,
            recurring_issues_zh=recurring_issues_zh,
            improvement_rate=improvement_rate,
            recent_scores=recent_scores
        )

    def _calculate_trend(self, scores: List[float]) -> Tuple[PerformanceTrend, str]:
        """Calculate performance trend from scores."""
        if len(scores) < 3:
            return PerformanceTrend.STABLE, "稳定"

        recent = scores[:5]
        older = scores[5:10] if len(scores) > 5 else scores[len(scores)//2:]

        if not older:
            return PerformanceTrend.STABLE, "稳定"

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        diff = recent_avg - older_avg

        # Check for fluctuation
        if len(scores) >= 5:
            variance = sum((s - recent_avg) ** 2 for s in recent) / len(recent)
            if variance > 200:  # High variance
                return PerformanceTrend.FLUCTUATING, "波动"

        if diff > 5:
            return PerformanceTrend.IMPROVING, "进步中"
        elif diff < -5:
            return PerformanceTrend.DECLINING, "退步中"
        else:
            return PerformanceTrend.STABLE, "稳定"

    def _determine_level(self, average_score: float, total_submissions: int) -> Tuple[StudentLevel, str]:
        """Determine student level based on performance."""
        if total_submissions < 3:
            return StudentLevel.BEGINNER, "初学者"

        if average_score >= 85:
            return StudentLevel.ADVANCED, "高级"
        elif average_score >= 65:
            return StudentLevel.INTERMEDIATE, "中级"
        else:
            return StudentLevel.BEGINNER, "初学者"

    async def _analyze_feedback_patterns(
        self, submissions, db_session
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Analyze feedback patterns to identify strengths and weaknesses."""
        strengths = []
        strengths_zh = []
        weaknesses = []
        weaknesses_zh = []

        # Analyze grading feedback for patterns
        strength_counts = {}
        weakness_counts = {}

        for submission, grading in submissions:
            if grading and grading.feedback:
                feedback = grading.feedback
                if isinstance(feedback, dict):
                    # Check for strengths in feedback
                    if "strengths" in feedback:
                        for s in feedback["strengths"]:
                            strength_counts[s] = strength_counts.get(s, 0) + 1
                    # Check for improvements/weaknesses
                    if "improvements" in feedback:
                        for w in feedback["improvements"]:
                            weakness_counts[w] = weakness_counts.get(w, 0) + 1

        # Get top strengths
        sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
        for s, _ in sorted_strengths[:3]:
            strengths.append(s)
            strengths_zh.append(self._translate_to_chinese(s))

        # Get top weaknesses
        sorted_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
        for w, _ in sorted_weaknesses[:3]:
            weaknesses.append(w)
            weaknesses_zh.append(self._translate_to_chinese(w))

        return strengths, strengths_zh, weaknesses, weaknesses_zh

    async def _find_recurring_issues(
        self, submissions, db_session
    ) -> Tuple[List[str], List[str]]:
        """Find issues that appear repeatedly in submissions."""
        issues = []
        issues_zh = []

        issue_counts = {}

        for submission, grading in submissions:
            if grading and grading.feedback:
                feedback = grading.feedback
                if isinstance(feedback, dict):
                    # Check for issues in categories
                    if "categories" in feedback:
                        for cat in feedback["categories"]:
                            if "items" in cat:
                                for item in cat["items"]:
                                    if "title" in item:
                                        issue_counts[item["title"]] = issue_counts.get(item["title"], 0) + 1

        # Get recurring issues (appeared more than once)
        for issue, count in issue_counts.items():
            if count >= 2:
                issues.append(issue)
                issues_zh.append(self._translate_to_chinese(issue))

        return issues[:5], issues_zh[:5]

    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate improvement rate from scores."""
        if len(scores) < 2:
            return 0.0

        # Compare first half to second half
        mid = len(scores) // 2
        recent = scores[:mid] if mid > 0 else scores[:1]
        older = scores[mid:] if mid > 0 else scores[1:]

        if not older:
            return 0.0

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        # Calculate improvement as percentage
        if older_avg == 0:
            return 0.0

        improvement = ((recent_avg - older_avg) / older_avg) * 100
        return max(-100, min(100, improvement))

    def _translate_to_chinese(self, text: str) -> str:
        """Translate common feedback terms to Chinese."""
        translations = {
            "Low cyclomatic complexity - code is easy to follow": "低圈复杂度 - 代码易于理解",
            "Good nesting depth - code is well-structured": "良好的嵌套深度 - 代码结构清晰",
            "Functions are appropriately sized": "函数大小适中",
            "No security issues detected": "未检测到安全问题",
            "Consistent naming conventions": "命名规范一致",
            "Code includes comments for documentation": "代码包含注释文档",
            "Reduce code complexity by breaking down large functions": "通过拆分大函数来降低代码复杂度",
            "Reduce nesting depth for better readability": "减少嵌套深度以提高可读性",
            "Address security vulnerabilities": "解决安全漏洞",
            "Fix naming convention inconsistencies": "修复命名规范不一致问题",
            "Add comments to explain complex logic": "添加注释解释复杂逻辑",
            "High Cyclomatic Complexity": "高圈复杂度",
            "Deep Nesting": "嵌套过深",
            "Long Function": "函数过长",
            "Too Many Parameters": "参数过多",
            "Naming Convention Issue": "命名规范问题",
        }
        return translations.get(text, text)

    async def _generate_personalized_categories(
        self, analysis, language: str, tone: FeedbackTone,
        detail_level: FeedbackDetailLevel, student_level: StudentLevel
    ) -> List[CategoryFeedback]:
        """Generate feedback categories with personalization."""
        detail_config = DETAIL_LEVEL_CONFIG.get(detail_level, DETAIL_LEVEL_CONFIG[FeedbackDetailLevel.STANDARD])
        level_config = LEVEL_MESSAGES.get(student_level, LEVEL_MESSAGES[StudentLevel.INTERMEDIATE])

        # Temporarily adjust max items based on detail level
        original_max = self.config.max_items_per_category
        self.config.max_items_per_category = detail_config["max_items"]

        categories = []

        # Generate categories with level-appropriate complexity thresholds
        quality_feedback = self._generate_quality_feedback(analysis, language, tone)
        if quality_feedback.items:
            categories.append(quality_feedback)

        logic_feedback = self._generate_logic_feedback(analysis, language, tone)
        if logic_feedback.items:
            categories.append(logic_feedback)

        style_feedback = self._generate_style_feedback(analysis, language, tone)
        if style_feedback.items:
            categories.append(style_feedback)

        suggestions_feedback = self._generate_suggestions_feedback(analysis, language, tone)
        if suggestions_feedback.items:
            categories.append(suggestions_feedback)

        # Restore original config
        self.config.max_items_per_category = original_max

        return categories

    def _generate_personalized_message(
        self, analysis, history: Optional[StudentHistoryAnalysis], tone: FeedbackTone
    ) -> Tuple[str, str]:
        """Generate personalized message based on history."""
        if not history or history.total_submissions == 0:
            return (
                "Welcome! This is your first submission. Let's see how you did.",
                "欢迎！这是你的第一次提交。让我们看看你的表现如何。"
            )

        level_config = LEVEL_MESSAGES.get(history.level, LEVEL_MESSAGES[StudentLevel.INTERMEDIATE])
        trend_config = TREND_MESSAGES.get(history.trend, TREND_MESSAGES[PerformanceTrend.STABLE])

        # Build personalized message
        msg_en = f"{level_config['prefix_en']}"
        msg_zh = f"{level_config['prefix']}"

        # Add trend information
        msg_en += f"{trend_config['message_en']} "
        msg_zh += f"{trend_config['message']} "

        # Add comparison to average
        current_score = analysis.summary.overall_score
        if current_score > history.average_score + 5:
            msg_en += f"This submission ({current_score:.0f}) is above your average ({history.average_score:.0f})!"
            msg_zh += f"本次提交（{current_score:.0f}分）高于你的平均水平（{history.average_score:.0f}分）！"
        elif current_score < history.average_score - 5:
            msg_en += f"This submission ({current_score:.0f}) is below your average ({history.average_score:.0f}). Let's work on improving."
            msg_zh += f"本次提交（{current_score:.0f}分）低于你的平均水平（{history.average_score:.0f}分）。让我们一起努力提高。"
        else:
            msg_en += f"This submission ({current_score:.0f}) is consistent with your average ({history.average_score:.0f})."
            msg_zh += f"本次提交（{current_score:.0f}分）与你的平均水平（{history.average_score:.0f}分）持平。"

        return msg_en, msg_zh

    def _generate_progressive_suggestions(
        self, analysis, language: str, student_level: StudentLevel, max_suggestions: int
    ) -> List[ProgressiveSuggestion]:
        """Generate progressive improvement suggestions."""
        suggestions = []
        order = 1

        # Easy suggestions (immediate fixes)
        if analysis.naming_issues:
            suggestions.append(ProgressiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                difficulty=SuggestionDifficulty.EASY,
                title="Fix Naming Conventions",
                title_zh="修复命名规范",
                description=f"You have {len(analysis.naming_issues)} naming convention issues. Fix these for better code readability.",
                description_zh=f"你有 {len(analysis.naming_issues)} 个命名规范问题。修复这些问题可以提高代码可读性。",
                estimated_time="5-10 minutes",
                estimated_time_zh="5-10 分钟",
                order=order,
                learning_resources=["PEP 8 Style Guide" if language == "python" else "Language Style Guide"]
            ))
            order += 1

        # Medium suggestions (require some learning)
        if analysis.complexity.cyclomatic_complexity > 10:
            suggestions.append(ProgressiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                difficulty=SuggestionDifficulty.MEDIUM,
                title="Reduce Code Complexity",
                title_zh="降低代码复杂度",
                description=f"Your code has a cyclomatic complexity of {analysis.complexity.cyclomatic_complexity}. Consider breaking down complex functions.",
                description_zh=f"你的代码圈复杂度为 {analysis.complexity.cyclomatic_complexity}。考虑拆分复杂函数。",
                estimated_time="30-60 minutes",
                estimated_time_zh="30-60 分钟",
                code_example="# Extract complex logic into helper functions\ndef process_data(data):\n    validated = validate(data)\n    transformed = transform(validated)\n    return save(transformed)",
                order=order,
                learning_resources=["Clean Code by Robert Martin", "Refactoring Techniques"]
            ))
            order += 1

        if analysis.complexity.max_nesting_depth > 4:
            suggestions.append(ProgressiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                difficulty=SuggestionDifficulty.MEDIUM,
                title="Reduce Nesting Depth",
                title_zh="减少嵌套深度",
                description=f"Maximum nesting depth is {analysis.complexity.max_nesting_depth}. Use early returns or extract nested logic.",
                description_zh=f"最大嵌套深度为 {analysis.complexity.max_nesting_depth}。使用提前返回或提取嵌套逻辑。",
                estimated_time="20-40 minutes",
                estimated_time_zh="20-40 分钟",
                code_example="# Use early returns\ndef process(item):\n    if not item:\n        return None\n    if not item.valid:\n        return None\n    return item.process()",
                order=order,
                learning_resources=["Guard Clauses Pattern"]
            ))
            order += 1

        # Hard suggestions (advanced improvements)
        if analysis.security_issues:
            suggestions.append(ProgressiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                difficulty=SuggestionDifficulty.HARD,
                title="Address Security Vulnerabilities",
                title_zh="解决安全漏洞",
                description=f"Found {len(analysis.security_issues)} security issues. These require careful attention.",
                description_zh=f"发现 {len(analysis.security_issues)} 个安全问题。这些需要仔细处理。",
                estimated_time="1-2 hours",
                estimated_time_zh="1-2 小时",
                order=order,
                learning_resources=["OWASP Security Guidelines", "Secure Coding Practices"]
            ))
            order += 1

        # Add language-specific suggestions
        best_practices = LANGUAGE_BEST_PRACTICES.get(language, {})
        for key, tip in list(best_practices.items())[:2]:
            if len(suggestions) < max_suggestions:
                suggestions.append(ProgressiveSuggestion(
                    suggestion_id=str(uuid.uuid4()),
                    difficulty=SuggestionDifficulty.EASY if student_level == StudentLevel.ADVANCED else SuggestionDifficulty.MEDIUM,
                    title=f"Best Practice: {key.replace('_', ' ').title()}",
                    title_zh=f"最佳实践：{key.replace('_', ' ').title()}",
                    description=tip,
                    description_zh=self._translate_to_chinese(tip) if self._translate_to_chinese(tip) != tip else tip,
                    estimated_time="15-30 minutes",
                    estimated_time_zh="15-30 分钟",
                    order=order,
                    learning_resources=[f"{language.title()} Best Practices Guide"]
                ))
                order += 1

        return suggestions[:max_suggestions]

    def _create_learning_path(
        self, suggestions: List[ProgressiveSuggestion], student_level: StudentLevel
    ) -> LearningPath:
        """Create a structured learning path from suggestions."""
        # Sort suggestions by difficulty
        sorted_suggestions = sorted(suggestions, key=lambda s: {
            SuggestionDifficulty.EASY: 0,
            SuggestionDifficulty.MEDIUM: 1,
            SuggestionDifficulty.HARD: 2
        }.get(s.difficulty, 1))

        # Update order
        for i, s in enumerate(sorted_suggestions):
            s.order = i + 1

        # Calculate total time
        total_minutes = 0
        for s in sorted_suggestions:
            # Parse estimated time
            time_str = s.estimated_time.lower()
            if "hour" in time_str:
                hours = int(time_str.split("-")[0].strip().split()[0])
                total_minutes += hours * 60
            elif "minute" in time_str:
                mins = int(time_str.split("-")[0].strip().split()[0])
                total_minutes += mins

        if total_minutes >= 60:
            hours = total_minutes // 60
            mins = total_minutes % 60
            total_time = f"{hours} hour{'s' if hours > 1 else ''}" + (f" {mins} minutes" if mins else "")
            total_time_zh = f"{hours} 小时" + (f" {mins} 分钟" if mins else "")
        else:
            total_time = f"{total_minutes} minutes"
            total_time_zh = f"{total_minutes} 分钟"

        level_config = LEVEL_MESSAGES.get(student_level, LEVEL_MESSAGES[StudentLevel.INTERMEDIATE])

        return LearningPath(
            path_id=str(uuid.uuid4()),
            title=f"Improvement Path for {student_level.value.title()} Learner",
            title_zh=f"{level_config['prefix'].replace('作为', '').replace('，', '')}的提升路径",
            description="Follow these steps in order to improve your code quality.",
            description_zh="按顺序完成这些步骤来提升你的代码质量。",
            steps=sorted_suggestions,
            total_estimated_time=total_time,
            total_estimated_time_zh=total_time_zh
        )

    def _generate_encouragement(
        self, analysis, history: Optional[StudentHistoryAnalysis], tone: FeedbackTone
    ) -> Tuple[str, str]:
        """Generate encouraging message based on performance."""
        score = analysis.summary.overall_score

        if not history or history.total_submissions == 0:
            if score >= 80:
                return (
                    "Great start! You're showing strong coding skills.",
                    "开局不错！你展现了扎实的编程能力。"
                )
            elif score >= 60:
                return (
                    "Good first attempt! Keep practicing and you'll improve quickly.",
                    "第一次尝试不错！继续练习，你会很快进步的。"
                )
            else:
                return (
                    "Everyone starts somewhere. Focus on the feedback and keep learning!",
                    "每个人都是从零开始的。关注反馈，继续学习！"
                )

        level_config = LEVEL_MESSAGES.get(history.level, LEVEL_MESSAGES[StudentLevel.INTERMEDIATE])
        trend_config = TREND_MESSAGES.get(history.trend, TREND_MESSAGES[PerformanceTrend.STABLE])

        # Build encouragement based on trend
        if history.trend == PerformanceTrend.IMPROVING:
            return (
                f"{trend_config['emoji']} {level_config['encouragement_en']} Your improvement rate is {history.improvement_rate:.1f}%!",
                f"{trend_config['emoji']} {level_config['encouragement']} 你的进步率是 {history.improvement_rate:.1f}%！"
            )
        elif history.trend == PerformanceTrend.DECLINING:
            return (
                f"{trend_config['emoji']} Don't be discouraged. Review the feedback carefully and focus on one improvement at a time.",
                f"{trend_config['emoji']} 不要气馁。仔细查看反馈，一次专注于一个改进点。"
            )
        else:
            return (
                f"{level_config['encouragement_en']}",
                f"{level_config['encouragement']}"
            )

    def _generate_summary_zh(self, analysis, tone: FeedbackTone) -> str:
        """Generate overall feedback summary in Chinese."""
        score = analysis.summary.overall_score
        grade = analysis.summary.grade

        if score >= 90:
            summary = f"优秀！你的代码得分 {score:.0f}/100（等级：{grade}）。"
        elif score >= 80:
            summary = f"做得好！你的代码得分 {score:.0f}/100（等级：{grade}）。"
        elif score >= 70:
            summary = f"你的代码得分 {score:.0f}/100（等级：{grade}）。"
        elif score >= 60:
            summary = f"你的代码需要改进。得分：{score:.0f}/100（等级：{grade}）。"
        else:
            summary = f"你的代码需要大量改进。得分：{score:.0f}/100（等级：{grade}）。"

        return summary


# Singleton instance
feedback_service = FeedbackGenerationService()
