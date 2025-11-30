"""
Feedback Generation Service - Generates personalized, constructive feedback for code submissions.
"""
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from schemas.feedback import (
    FeedbackTone, FeedbackCategory, FeedbackItem, CategoryFeedback,
    GeneratedFeedback, GenerateFeedbackRequest
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


# Singleton instance
feedback_service = FeedbackGenerationService()
