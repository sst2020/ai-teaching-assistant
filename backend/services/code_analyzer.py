"""
Advanced Code Quality Analyzer Service.

This module provides comprehensive code quality analysis including:
- Cyclomatic complexity calculation using radon
- Cognitive complexity detection
- Code duplication detection using AST
- Maintainability index calculation
"""
import ast
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timezone
from collections import defaultdict

from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze

from schemas.analysis import (
    CodeQualityResult, CodeQualityMetrics, FunctionComplexity,
    DuplicateCodeBlock, ComplexityGrade, MaintainabilityRating,
    AnalysisCodeRequest
)

logger = logging.getLogger(__name__)


def get_complexity_grade(complexity: int) -> ComplexityGrade:
    """Convert cyclomatic complexity to letter grade."""
    if complexity <= 5:
        return ComplexityGrade.A
    elif complexity <= 10:
        return ComplexityGrade.B
    elif complexity <= 20:
        return ComplexityGrade.C
    elif complexity <= 30:
        return ComplexityGrade.D
    elif complexity <= 40:
        return ComplexityGrade.E
    else:
        return ComplexityGrade.F


def get_maintainability_rating(mi: float) -> MaintainabilityRating:
    """Convert maintainability index to rating."""
    if mi >= 80:
        return MaintainabilityRating.EXCELLENT
    elif mi >= 60:
        return MaintainabilityRating.GOOD
    elif mi >= 40:
        return MaintainabilityRating.MODERATE
    elif mi >= 20:
        return MaintainabilityRating.POOR
    else:
        return MaintainabilityRating.VERY_POOR


class CognitiveComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cognitive complexity."""
    
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0
        self.max_nesting = 0
    
    def _increment(self, node, nesting_increment: bool = True):
        """Increment complexity with nesting penalty."""
        if nesting_increment:
            self.complexity += 1 + self.nesting_level
        else:
            self.complexity += 1
    
    def visit_If(self, node):
        self._increment(node)
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
        # Handle elif as separate increment without nesting
        for child in node.orelse:
            if isinstance(child, ast.If):
                self.complexity += 1  # elif doesn't add nesting penalty
    
    def visit_For(self, node):
        self._increment(node)
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_While(self, node):
        self._increment(node)
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_ExceptHandler(self, node):
        self._increment(node)
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_BoolOp(self, node):
        # Each boolean operator adds to complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_Lambda(self, node):
        self._increment(node, nesting_increment=False)
        self.generic_visit(node)
    
    def visit_comprehension(self, node):
        self._increment(node, nesting_increment=False)
        self.generic_visit(node)


def calculate_cognitive_complexity(func_node: ast.AST) -> Tuple[int, int]:
    """Calculate cognitive complexity for a function node.
    
    Returns:
        Tuple of (cognitive_complexity, max_nesting_depth)
    """
    visitor = CognitiveComplexityVisitor()
    visitor.visit(func_node)
    return visitor.complexity, visitor.max_nesting


class DuplicateDetector:
    """Detects duplicate code blocks using AST normalization."""
    
    def __init__(self, min_lines: int = 3):
        self.min_lines = min_lines
        self.blocks: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
    
    def _normalize_node(self, node: ast.AST) -> str:
        """Normalize an AST node to a canonical string representation."""
        if isinstance(node, ast.Name):
            return "NAME"
        elif isinstance(node, ast.Constant):
            return f"CONST:{type(node.value).__name__}"
        elif isinstance(node, ast.Num):  # Python 3.7 compatibility
            return "NUM"
        elif isinstance(node, ast.Str):  # Python 3.7 compatibility
            return "STR"
        else:
            return node.__class__.__name__
    
    def _get_block_signature(self, nodes: List[ast.AST]) -> str:
        """Generate a signature for a block of AST nodes."""
        parts = []
        for node in nodes:
            parts.append(self._normalize_node(node))
            for child in ast.iter_child_nodes(node):
                parts.append(self._normalize_node(child))
        return hashlib.md5(":".join(parts).encode()).hexdigest()

    def find_duplicates(self, code: str) -> List[DuplicateCodeBlock]:
        """Find duplicate code blocks in the source code."""
        duplicates = []
        try:
            tree = ast.parse(code)
            lines = code.split('\n')

            # Extract all statement blocks
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    body = getattr(node, 'body', [])

                    # Check sliding windows of statements
                    for i in range(len(body) - self.min_lines + 1):
                        block = body[i:i + self.min_lines]
                        if all(hasattr(n, 'lineno') for n in block):
                            start_line = block[0].lineno
                            end_line = getattr(block[-1], 'end_lineno', block[-1].lineno)
                            signature = self._get_block_signature(block)
                            snippet = '\n'.join(lines[start_line-1:end_line])
                            self.blocks[signature].append((start_line, end_line, snippet))

            # Find duplicates (signatures with multiple occurrences)
            block_id = 0
            for signature, occurrences in self.blocks.items():
                if len(occurrences) > 1:
                    block_id += 1
                    lines_list = [occ[0] for occ in occurrences]
                    snippet = occurrences[0][2]
                    duplicates.append(DuplicateCodeBlock(
                        block_id=block_id,
                        lines=lines_list,
                        code_snippet=snippet[:200] + "..." if len(snippet) > 200 else snippet,
                        similarity=100.0,
                        suggestion="考虑将重复代码提取为独立函数或方法"
                    ))
        except SyntaxError:
            pass

        return duplicates


class CodeQualityAnalyzer:
    """Main code quality analyzer service."""

    def __init__(self, complexity_threshold: int = 10, nesting_threshold: int = 4):
        self.complexity_threshold = complexity_threshold
        self.nesting_threshold = nesting_threshold

    async def analyze(self, request: AnalysisCodeRequest) -> CodeQualityResult:
        """Perform comprehensive code quality analysis."""
        analysis_id = str(uuid.uuid4())
        code = request.code
        language = request.language

        # Initialize result
        functions: List[FunctionComplexity] = []
        issues: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        # Calculate metrics
        metrics = CodeQualityMetrics()
        duplicates: List[DuplicateCodeBlock] = []

        if language == "python":
            try:
                # Use radon for cyclomatic complexity
                cc_results = cc_visit(code)

                # Calculate maintainability index
                try:
                    mi_score = mi_visit(code, True)
                    metrics.maintainability_index = round(mi_score, 2)
                    metrics.maintainability_rating = get_maintainability_rating(mi_score)
                except Exception:
                    metrics.maintainability_index = 50.0
                    metrics.maintainability_rating = MaintainabilityRating.MODERATE

                # Analyze raw metrics
                try:
                    raw = analyze(code)
                    metrics.total_lines = raw.loc
                    metrics.code_lines = raw.lloc
                    metrics.comment_lines = raw.comments
                    metrics.blank_lines = raw.blank
                    metrics.comment_ratio = round(
                        (raw.comments / raw.lloc * 100) if raw.lloc > 0 else 0, 2
                    )
                except Exception:
                    lines = code.split('\n')
                    metrics.total_lines = len(lines)

                # Parse AST for detailed analysis
                tree = ast.parse(code)

                # Analyze each function
                complexities = []
                cognitive_complexities = []

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_analysis = self._analyze_function(node, code, cc_results)
                        functions.append(func_analysis)
                        complexities.append(func_analysis.cyclomatic_complexity)
                        cognitive_complexities.append(func_analysis.cognitive_complexity)

                        # Check for issues
                        if func_analysis.is_complex:
                            issues.append({
                                "type": "high_complexity",
                                "severity": "warning",
                                "line": func_analysis.line_start,
                                "message": f"函数 '{func_analysis.name}' 圈复杂度为 {func_analysis.cyclomatic_complexity}，超过阈值 {self.complexity_threshold}",
                                "suggestion": "考虑将函数拆分为更小的函数"
                            })

                        if func_analysis.nesting_depth > self.nesting_threshold:
                            issues.append({
                                "type": "deep_nesting",
                                "severity": "warning",
                                "line": func_analysis.line_start,
                                "message": f"函数 '{func_analysis.name}' 嵌套深度为 {func_analysis.nesting_depth}，超过阈值 {self.nesting_threshold}",
                                "suggestion": "使用提前返回或提取子函数来减少嵌套"
                            })

                # Update metrics
                if complexities:
                    metrics.avg_cyclomatic_complexity = round(sum(complexities) / len(complexities), 2)
                    metrics.max_cyclomatic_complexity = max(complexities)
                    metrics.total_functions = len(functions)
                    metrics.complex_functions = sum(1 for c in complexities if c > self.complexity_threshold)

                if cognitive_complexities:
                    metrics.avg_cognitive_complexity = round(sum(cognitive_complexities) / len(cognitive_complexities), 2)
                    metrics.max_cognitive_complexity = max(cognitive_complexities)
                    metrics.deep_nesting_count = sum(1 for f in functions if f.nesting_depth > self.nesting_threshold)

                # Detect duplicates
                detector = DuplicateDetector()
                duplicates = detector.find_duplicates(code)
                metrics.duplicate_blocks = len(duplicates)

                if duplicates:
                    total_dup_lines = sum(len(d.lines) for d in duplicates)
                    metrics.duplication_percentage = round(
                        (total_dup_lines / metrics.total_lines * 100) if metrics.total_lines > 0 else 0, 2
                    )

            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "error",
                    "line": getattr(e, 'lineno', 1),
                    "message": f"语法错误: {str(e)}",
                    "suggestion": "请修复语法错误后重新分析"
                })

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, functions, duplicates)

        # Calculate overall score
        score = self._calculate_score(metrics, issues)
        grade = self._get_grade(score)

        # Generate summary
        summary = self._generate_summary(metrics, len(issues), len(duplicates))

        return CodeQualityResult(
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc),
            language=language,
            score=score,
            grade=grade,
            metrics=metrics,
            functions=functions,
            duplicates=duplicates,
            issues=issues,
            summary=summary,
            recommendations=recommendations
        )

    def _analyze_function(
        self, node: ast.AST, code: str, cc_results: List
    ) -> FunctionComplexity:
        """Analyze a single function."""
        name = node.name
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line + 10)

        # Get cyclomatic complexity from radon results
        cc = 1
        for block in cc_results:
            if block.name == name and block.lineno == start_line:
                cc = block.complexity
                break

        # Calculate cognitive complexity
        cog_complexity, max_nesting = calculate_cognitive_complexity(node)

        # Count parameters
        params = len(node.args.args) if hasattr(node, 'args') else 0

        # Lines of code
        loc = end_line - start_line + 1

        # Generate suggestions
        suggestions = []
        if cc > self.complexity_threshold:
            suggestions.append(f"圈复杂度 {cc} 过高，建议拆分函数")
        if max_nesting > self.nesting_threshold:
            suggestions.append(f"嵌套深度 {max_nesting} 过深，建议使用提前返回")
        if params > 5:
            suggestions.append(f"参数数量 {params} 过多，建议使用配置对象")
        if loc > 50:
            suggestions.append(f"函数过长 ({loc} 行)，建议拆分")

        return FunctionComplexity(
            name=name,
            line_start=start_line,
            line_end=end_line,
            cyclomatic_complexity=cc,
            cognitive_complexity=cog_complexity,
            grade=get_complexity_grade(cc),
            is_complex=cc > self.complexity_threshold,
            nesting_depth=max_nesting,
            parameters=params,
            lines_of_code=loc,
            suggestions=suggestions
        )

    def _calculate_score(self, metrics: CodeQualityMetrics, issues: List) -> float:
        """Calculate overall quality score."""
        score = 100.0

        # Deduct for complexity
        if metrics.max_cyclomatic_complexity > 20:
            score -= 15
        elif metrics.max_cyclomatic_complexity > 10:
            score -= 8

        # Deduct for maintainability
        if metrics.maintainability_index < 40:
            score -= 15
        elif metrics.maintainability_index < 60:
            score -= 8

        # Deduct for duplicates
        if metrics.duplicate_blocks > 5:
            score -= 10
        elif metrics.duplicate_blocks > 0:
            score -= 5

        # Deduct for issues
        for issue in issues:
            if issue.get("severity") == "error":
                score -= 10
            elif issue.get("severity") == "warning":
                score -= 3

        return max(0, min(100, round(score, 1)))

    def _get_grade(self, score: float) -> str:
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

    def _generate_recommendations(
        self, metrics: CodeQualityMetrics,
        functions: List[FunctionComplexity],
        duplicates: List[DuplicateCodeBlock]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if metrics.max_cyclomatic_complexity > 15:
            recommendations.append(
                f"📊 重构复杂函数 - 最高圈复杂度为 {metrics.max_cyclomatic_complexity}，建议拆分为更小的函数"
            )

        if metrics.maintainability_index < 60:
            recommendations.append(
                f"🔧 提高可维护性 - 当前可维护性指数为 {metrics.maintainability_index:.1f}，"
                "建议简化代码结构、添加注释"
            )

        if metrics.deep_nesting_count > 0:
            recommendations.append(
                f"🔄 减少嵌套深度 - 有 {metrics.deep_nesting_count} 个函数嵌套过深，"
                "建议使用提前返回或提取方法"
            )

        if duplicates:
            recommendations.append(
                f"♻️ 消除重复代码 - 发现 {len(duplicates)} 处重复代码块，"
                "建议提取为可复用的函数"
            )

        if metrics.comment_ratio < 10:
            recommendations.append(
                f"📝 增加注释 - 当前注释比例为 {metrics.comment_ratio:.1f}%，"
                "建议添加更多文档说明"
            )

        complex_funcs = [f for f in functions if f.is_complex]
        if complex_funcs:
            names = ", ".join(f.name for f in complex_funcs[:3])
            recommendations.append(
                f"⚠️ 关注高复杂度函数: {names}"
            )

        if not recommendations:
            recommendations.append("✅ 代码质量良好！继续保持。")

        return recommendations

    def _generate_summary(
        self, metrics: CodeQualityMetrics,
        issue_count: int,
        duplicate_count: int
    ) -> str:
        """Generate analysis summary."""
        parts = []

        parts.append(f"分析了 {metrics.total_functions} 个函数")
        parts.append(f"平均圈复杂度 {metrics.avg_cyclomatic_complexity:.1f}")
        parts.append(f"可维护性指数 {metrics.maintainability_index:.1f} ({metrics.maintainability_rating.value})")

        if metrics.complex_functions > 0:
            parts.append(f"发现 {metrics.complex_functions} 个高复杂度函数")

        if duplicate_count > 0:
            parts.append(f"检测到 {duplicate_count} 处重复代码")

        if issue_count > 0:
            parts.append(f"共 {issue_count} 个问题需要关注")

        return "。".join(parts) + "。"


# Create singleton instance
code_quality_analyzer = CodeQualityAnalyzer()

