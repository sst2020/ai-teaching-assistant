"""
Code Static Analysis Service - Analyzes code for style, complexity, and quality
"""
import ast
import uuid
from typing import List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

import pycodestyle
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

from schemas.code_analysis import (
    CodeAnalysisRequest, CodeAnalysisResult, StyleAnalysisResult,
    ComplexityMetrics, FunctionAnalysis, CodeSmell, CodeIssue, IssueSeverity
)


@dataclass
class AnalysisConfig:
    """Configuration for code analysis."""
    max_line_length: int = 100
    max_complexity: int = 10
    max_function_length: int = 50
    min_comment_ratio: float = 10.0
    max_parameters: int = 5


class CodeAnalysisService:
    """Service for static code analysis."""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()

    async def analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResult:
        """Perform comprehensive code analysis."""
        analysis_id = str(uuid.uuid4())
        code = request.code

        style_analysis = self._analyze_style(code) if request.include_style else None
        complexity_metrics = self._analyze_complexity(code) if request.include_complexity else None
        functions = self._analyze_functions(code) if request.include_complexity else []
        code_smells = self._detect_code_smells(code) if request.include_smells else []

        overall_score = self._calculate_quality_score(style_analysis, complexity_metrics, code_smells)
        summary, recommendations = self._generate_summary(style_analysis, complexity_metrics, functions, code_smells)

        return CodeAnalysisResult(
            analysis_id=analysis_id, language=request.language, analyzed_at=datetime.utcnow(),
            style_analysis=style_analysis, complexity_metrics=complexity_metrics,
            functions=functions, code_smells=code_smells,
            overall_quality_score=overall_score, summary=summary, recommendations=recommendations
        )

    def _analyze_style(self, code: str) -> StyleAnalysisResult:
        """Analyze code for PEP 8 style compliance."""
        issues = []

        try:
            import tempfile
            import os

            # Write code to temp file for pycodestyle
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            try:
                style_guide = pycodestyle.StyleGuide(max_line_length=self.config.max_line_length, quiet=True)
                result = style_guide.check_files([temp_path])

                # Parse the messages from the checker
                # Since pycodestyle doesn't give us structured results easily,
                # we'll use a simpler approach - just count errors
                error_count = result.get_count()

                # For now, create a simple result based on error count
                if error_count > 0:
                    issues.append(CodeIssue(
                        line=1, column=0, code="E000",
                        message=f"Found {error_count} style issue(s)",
                        severity=IssueSeverity.WARNING,
                        suggestion="Run pycodestyle on your code for detailed issues"
                    ))
            finally:
                os.unlink(temp_path)

        except Exception:
            pass  # Return empty issues on error

        score = max(0, 100 - len(issues) * 5)
        return StyleAnalysisResult(is_compliant=len(issues) == 0, total_issues=len(issues), issues=issues[:50], score=score)

    def _analyze_complexity(self, code: str) -> ComplexityMetrics:
        """Analyze code complexity metrics."""
        try:
            raw_metrics = analyze(code)
            cc_results = cc_visit(code)
            avg_complexity = sum(b.complexity for b in cc_results) / len(cc_results) if cc_results else 1
            mi_score = mi_visit(code, True)
            comment_ratio = (raw_metrics.comments / raw_metrics.loc * 100) if raw_metrics.loc > 0 else 0

            return ComplexityMetrics(
                cyclomatic_complexity=round(avg_complexity, 2), cognitive_complexity=0,
                maintainability_index=round(mi_score, 2), lines_of_code=raw_metrics.loc,
                logical_lines=raw_metrics.lloc, comment_lines=raw_metrics.comments,
                blank_lines=raw_metrics.blank, comment_ratio=round(comment_ratio, 2)
            )
        except Exception:
            return ComplexityMetrics(
                cyclomatic_complexity=1, cognitive_complexity=0, maintainability_index=50,
                lines_of_code=len(code.split('\n')), logical_lines=0, comment_lines=0, blank_lines=0, comment_ratio=0
            )

    def _analyze_functions(self, code: str) -> List[FunctionAnalysis]:
        """Analyze individual functions in the code."""
        functions = []
        try:
            for block in cc_visit(code):
                if block.letter in ('F', 'M'):
                    is_complex = block.complexity > self.config.max_complexity
                    issues = [f"Complexity ({block.complexity}) exceeds threshold"] if is_complex else []
                    functions.append(FunctionAnalysis(
                        name=block.name, line_start=block.lineno, line_end=block.endline,
                        complexity=block.complexity, parameters=0, is_too_complex=is_complex, issues=issues
                    ))
        except Exception:
            pass
        return functions

    def _detect_code_smells(self, code: str) -> List[CodeSmell]:
        """Detect common code smells."""
        smells = []
        try:
            tree = ast.parse(code)
            lines = code.split('\n')

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = getattr(node, 'end_lineno', node.lineno) - node.lineno
                    if func_length > self.config.max_function_length:
                        smells.append(CodeSmell(
                            type="Long Function", description=f"Function '{node.name}' has {func_length} lines",
                            location=f"Line {node.lineno}", severity=IssueSeverity.WARNING,
                            refactoring_suggestion="Break into smaller functions"
                        ))
                    if len(node.args.args) > self.config.max_parameters:
                        smells.append(CodeSmell(
                            type="Too Many Parameters", description=f"Function '{node.name}' has {len(node.args.args)} parameters",
                            location=f"Line {node.lineno}", severity=IssueSeverity.WARNING,
                            refactoring_suggestion="Use a configuration object"
                        ))

                if isinstance(node, (ast.If, ast.For, ast.While)):
                    depth = self._get_nesting_depth(node)
                    if depth > 3:
                        smells.append(CodeSmell(
                            type="Deep Nesting", description=f"Code nested {depth} levels deep",
                            location=f"Line {node.lineno}", severity=IssueSeverity.WARNING,
                            refactoring_suggestion="Extract nested logic into functions"
                        ))

            # Simple duplicate detection
            seen = {}
            for i, line in enumerate(lines):
                stripped = line.strip()
                if len(stripped) > 20 and not stripped.startswith('#'):
                    if stripped in seen:
                        smells.append(CodeSmell(
                            type="Duplicate Code", description=f"Similar code at lines {seen[stripped]+1} and {i+1}",
                            location=f"Line {i+1}", severity=IssueSeverity.INFO,
                            refactoring_suggestion="Extract into reusable function"
                        ))
                    else:
                        seen[stripped] = i
        except SyntaxError:
            smells.append(CodeSmell(
                type="Syntax Error", description="Code contains syntax errors",
                location="Unknown", severity=IssueSeverity.ERROR, refactoring_suggestion="Fix syntax errors"
            ))
        return smells[:20]

    def _get_nesting_depth(self, node: ast.AST, depth: int = 1) -> int:
        """Calculate nesting depth."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                max_depth = max(max_depth, self._get_nesting_depth(child, depth + 1))
        return max_depth

    def _get_severity_from_code(self, code: str) -> IssueSeverity:
        if code.startswith('E'): return IssueSeverity.ERROR
        elif code.startswith('W'): return IssueSeverity.WARNING
        return IssueSeverity.CONVENTION

    def _get_style_suggestion(self, code: str) -> str:
        suggestions = {
            'E501': 'Break long lines', 'E302': 'Add blank lines between functions',
            'E303': 'Remove extra blank lines', 'W291': 'Remove trailing whitespace',
        }
        return suggestions.get(code, 'Review PEP 8 style guide')

    def _calculate_quality_score(self, style, complexity, smells) -> float:
        scores = []
        if style: scores.append(style.score * 0.3)
        if complexity: scores.append(complexity.maintainability_index * 0.4)
        scores.append(max(0, 30 - len(smells) * 3))
        return round(sum(scores), 2) if scores else 50.0

    def _generate_summary(self, style, complexity, functions, smells) -> Tuple[str, List[str]]:
        parts, recs = [], []
        if style:
            if style.is_compliant: parts.append("Code follows PEP 8.")
            else: parts.append(f"Found {style.total_issues} style issues."); recs.append("Fix PEP 8 violations")
        if complexity:
            if complexity.maintainability_index >= 80: parts.append("Excellent maintainability.")
            elif complexity.maintainability_index >= 60: parts.append("Good maintainability.")
            else: parts.append("Maintainability needs improvement."); recs.append("Reduce complexity")
            if complexity.comment_ratio < self.config.min_comment_ratio: recs.append("Add more comments")
        complex_funcs = [f for f in functions if f.is_too_complex]
        if complex_funcs: parts.append(f"{len(complex_funcs)} complex function(s)."); recs.append("Refactor complex functions")
        if smells: parts.append(f"Detected {len(smells)} code smell(s).")
        return " ".join(parts) or "Analysis completed.", recs


code_analysis_service = CodeAnalysisService()

