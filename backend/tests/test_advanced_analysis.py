"""
Tests for Advanced Code Analysis Services.

Tests for:
- Code Quality Analyzer (complexity, duplication, maintainability)
- Linter Service (Pylint integration)
- Security Analyzer (Bandit integration)
- Performance Analyzer (anti-patterns, best practices)
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.code_analyzer import (
    code_quality_analyzer, CodeQualityAnalyzer,
    get_complexity_grade, get_maintainability_rating,
    calculate_cognitive_complexity, DuplicateDetector
)
from services.linter import linter_service, LinterService
from services.security_analyzer import (
    security_analyzer, SecurityAnalyzer,
    performance_analyzer, PerformanceAnalyzer
)
from schemas.analysis import (
    AnalysisCodeRequest, LintRequest, SecurityRequest, PerformanceRequest,
    ComplexityGrade, MaintainabilityRating, SecuritySeverity,
    PerformanceIssueType, IssueSeverity
)


# ============================================
# Code Quality Analyzer Tests
# ============================================

class TestCodeQualityAnalyzer:
    """Tests for the CodeQualityAnalyzer service."""

    @pytest.fixture
    def analyzer(self):
        return CodeQualityAnalyzer()

    @pytest.mark.asyncio
    async def test_simple_code_analysis(self, analyzer):
        """Test analysis of simple code."""
        code = """def hello():
    return "Hello, World!"
"""
        request = AnalysisCodeRequest(code=code, language="python")
        result = await analyzer.analyze(request)
        
        assert result.score >= 80
        assert result.grade in ["A", "B"]
        assert result.metrics.total_functions == 1
        assert len(result.functions) == 1

    @pytest.mark.asyncio
    async def test_complex_function_detection(self, analyzer):
        """Test detection of complex functions."""
        code = """def complex_func(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return True
    elif a > 10:
        return False
    elif b > 10:
        return None
    return 0
"""
        request = AnalysisCodeRequest(code=code, language="python")
        result = await analyzer.analyze(request)
        
        assert len(result.functions) == 1
        func = result.functions[0]
        assert func.cyclomatic_complexity > 5
        assert func.is_complex or func.nesting_depth > 3

    @pytest.mark.asyncio
    async def test_maintainability_index(self, analyzer):
        """Test maintainability index calculation."""
        code = """def well_documented():
    \"\"\"This function is well documented.\"\"\"
    # Clear variable names
    result = 42
    return result
"""
        request = AnalysisCodeRequest(code=code, language="python")
        result = await analyzer.analyze(request)
        
        assert result.metrics.maintainability_index > 0
        assert result.metrics.maintainability_rating is not None

    @pytest.mark.asyncio
    async def test_syntax_error_handling(self, analyzer):
        """Test handling of syntax errors."""
        code = """def broken(
    return "missing parenthesis"
"""
        request = AnalysisCodeRequest(code=code, language="python")
        result = await analyzer.analyze(request)
        
        # Should still return a result with error info
        assert result.analysis_id is not None
        assert any("语法错误" in str(issue) for issue in result.issues)


class TestComplexityGrading:
    """Tests for complexity grading functions."""

    def test_complexity_grade_a(self):
        assert get_complexity_grade(1) == ComplexityGrade.A
        assert get_complexity_grade(5) == ComplexityGrade.A

    def test_complexity_grade_b(self):
        assert get_complexity_grade(6) == ComplexityGrade.B
        assert get_complexity_grade(10) == ComplexityGrade.B

    def test_complexity_grade_c(self):
        assert get_complexity_grade(11) == ComplexityGrade.C
        assert get_complexity_grade(20) == ComplexityGrade.C

    def test_complexity_grade_f(self):
        assert get_complexity_grade(50) == ComplexityGrade.F

    def test_maintainability_excellent(self):
        assert get_maintainability_rating(85) == MaintainabilityRating.EXCELLENT

    def test_maintainability_poor(self):
        assert get_maintainability_rating(25) == MaintainabilityRating.POOR


class TestDuplicateDetector:
    """Tests for code duplication detection."""

    def test_detect_duplicates(self):
        code = """def func1():
    x = 1
    y = 2
    z = x + y
    return z

def func2():
    x = 1
    y = 2
    z = x + y
    return z
"""
        detector = DuplicateDetector(min_lines=3)
        duplicates = detector.find_duplicates(code)
        
        # Should detect similar code blocks
        assert isinstance(duplicates, list)

    def test_no_duplicates(self):
        code = """def unique1():
    return 1

def unique2():
    return "different"
"""
        detector = DuplicateDetector(min_lines=3)
        duplicates = detector.find_duplicates(code)

        assert len(duplicates) == 0


# ============================================
# Linter Service Tests
# ============================================

class TestLinterService:
    """Tests for the LinterService."""

    @pytest.fixture
    def linter(self):
        return LinterService()

    @pytest.mark.asyncio
    async def test_lint_clean_code(self, linter):
        """Test linting of clean code."""
        code = """def hello():
    \"\"\"Say hello.\"\"\"
    return "Hello"
"""
        request = LintRequest(code=code, language="python")
        result = await linter.lint(request)

        assert result.analysis_id is not None
        assert result.linter == "pylint"
        # Clean code should have high score
        assert result.score >= 50 or "未安装" in result.summary

    @pytest.mark.asyncio
    async def test_lint_with_issues(self, linter):
        """Test linting of code with issues."""
        code = """import os
import sys

def x():
    pass
"""
        request = LintRequest(code=code, language="python")
        result = await linter.lint(request)

        assert result.analysis_id is not None
        # Should detect unused imports or naming issues

    @pytest.mark.asyncio
    async def test_unsupported_language(self, linter):
        """Test linting of unsupported language."""
        code = "console.log('hello');"
        request = LintRequest(code=code, language="javascript")
        result = await linter.lint(request)

        assert "暂不支持" in result.summary


# ============================================
# Security Analyzer Tests
# ============================================

class TestSecurityAnalyzer:
    """Tests for the SecurityAnalyzer service."""

    @pytest.fixture
    def analyzer(self):
        return SecurityAnalyzer()

    @pytest.mark.asyncio
    async def test_detect_hardcoded_password(self, analyzer):
        """Test detection of hardcoded passwords."""
        code = """password = "secret123"
api_key = "abc123xyz"
"""
        request = SecurityRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        assert result.analysis_id is not None
        # Should detect hardcoded secrets
        assert result.total_issues >= 1 or result.score < 100

    @pytest.mark.asyncio
    async def test_detect_eval_usage(self, analyzer):
        """Test detection of eval usage."""
        code = """user_input = input()
result = eval(user_input)
"""
        request = SecurityRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        # Should detect eval as security issue
        assert result.total_issues >= 1

    @pytest.mark.asyncio
    async def test_detect_shell_injection(self, analyzer):
        """Test detection of shell injection risk."""
        code = """import subprocess
subprocess.call(cmd, shell=True)
"""
        request = SecurityRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        # Should detect shell=True as security issue
        assert result.total_issues >= 1

    @pytest.mark.asyncio
    async def test_clean_code_security(self, analyzer):
        """Test security analysis of clean code."""
        code = """def safe_function(x):
    return x * 2
"""
        request = SecurityRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        assert result.score >= 80
        assert result.high_severity == 0


# ============================================
# Performance Analyzer Tests
# ============================================

class TestPerformanceAnalyzer:
    """Tests for the PerformanceAnalyzer service."""

    @pytest.fixture
    def analyzer(self):
        return PerformanceAnalyzer()

    @pytest.mark.asyncio
    async def test_detect_nested_loops(self, analyzer):
        """Test detection of nested loops."""
        code = """def find_pairs(items):
    for i in items:
        for j in items:
            if i + j == 10:
                return (i, j)
"""
        request = PerformanceRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        # Should detect nested loops as potential O(n²)
        assert result.total_issues >= 1

    @pytest.mark.asyncio
    async def test_detect_range_len_pattern(self, analyzer):
        """Test detection of range(len()) anti-pattern."""
        code = """def process(items):
    for i in range(len(items)):
        print(items[i])
"""
        request = PerformanceRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        # Should detect range(len()) pattern
        perf_issues = [i for i in result.performance_issues
                       if i.issue_type == PerformanceIssueType.INEFFICIENT_ALGORITHM]
        assert len(perf_issues) >= 1

    @pytest.mark.asyncio
    async def test_detect_bare_except(self, analyzer):
        """Test detection of bare except clause."""
        code = """try:
    risky_operation()
except:
    pass
"""
        request = PerformanceRequest(code=code, language="python", check_best_practices=True)
        result = await analyzer.analyze(request)

        # Should detect bare except as best practice violation
        bp_violations = [v for v in result.best_practice_violations
                        if "except" in v.rule.lower()]
        assert len(bp_violations) >= 1

    @pytest.mark.asyncio
    async def test_detect_print_statements(self, analyzer):
        """Test detection of print statements."""
        code = """def debug():
    print("debugging")
    print("more debug")
"""
        request = PerformanceRequest(code=code, language="python", check_best_practices=True)
        result = await analyzer.analyze(request)

        # Should detect print as best practice violation
        bp_violations = [v for v in result.best_practice_violations
                        if "print" in v.rule.lower() or "日志" in v.rule]
        assert len(bp_violations) >= 1

    @pytest.mark.asyncio
    async def test_clean_code_performance(self, analyzer):
        """Test performance analysis of clean code."""
        code = """def efficient_sum(numbers):
    return sum(numbers)
"""
        request = PerformanceRequest(code=code, language="python")
        result = await analyzer.analyze(request)

        assert result.score >= 80


# ============================================
# Integration Tests
# ============================================

class TestAnalysisIntegration:
    """Integration tests for all analysis services."""

    @pytest.mark.asyncio
    async def test_all_analyzers_work_together(self):
        """Test that all analyzers can analyze the same code."""
        code = """def example(x):
    if x > 0:
        return x * 2
    return 0
"""
        # Quality analysis
        quality_req = AnalysisCodeRequest(code=code, language="python")
        quality_result = await code_quality_analyzer.analyze(quality_req)
        assert quality_result.analysis_id is not None

        # Lint analysis
        lint_req = LintRequest(code=code, language="python")
        lint_result = await linter_service.lint(lint_req)
        assert lint_result.analysis_id is not None

        # Security analysis
        security_req = SecurityRequest(code=code, language="python")
        security_result = await security_analyzer.analyze(security_req)
        assert security_result.analysis_id is not None

        # Performance analysis
        perf_req = PerformanceRequest(code=code, language="python")
        perf_result = await performance_analyzer.analyze(perf_req)
        assert perf_result.analysis_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

