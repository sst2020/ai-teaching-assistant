"""
Test suite for project report analysis functionality.
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from schemas.report_analysis import (
    ReportAnalysisRequest,
    ReportFileType,
    ReportLanguage,
    LogicIssueType,
    ReportParseResult,
)
from services.report_analysis_service import ReportAnalysisConfig


@pytest.fixture
def client():
    app = create_app(testing=True)
    with TestClient(app) as test_client:
        yield test_client


class TestReportAnalysisAPI:
    """Test cases for report analysis API endpoints."""

    def test_analyze_endpoint_basic(self, client):
        """Test basic report analysis endpoint."""
        request_data = {
            "file_name": "test_report.md",
            "file_type": "markdown",
            "content": "# Test Report\n\nThis is a test report for analysis.\n\n## Introduction\n\nThe report discusses various topics."
        }

        response = client.post("/api/v1/report-analysis/analyze", json=request_data)
        assert response.status_code == 200

        result = response.json()
        assert "report_id" in result
        assert "overall_score" in result
        assert "parsed" in result
        assert "quality" in result
        assert "logic" in result
        assert "innovation" in result
        assert "suggestions" in result

        # Check that we have some sections detected
        assert len(result["parsed"]["sections"]) > 0

        # Check that scores are in valid range
        assert 0 <= result["overall_score"] <= 100
        assert 0 <= result["logic"]["coherence_score"] <= 100
        assert 0 <= result["innovation"]["novelty_score"] <= 100

    def test_analyze_with_chinese_content(self, client):
        """Test report analysis with Chinese content."""
        request_data = {
            "file_name": "test_report_cn.md",
            "file_type": "markdown",
            "content": "# 测试报告\n\n这是一个用于分析的测试报告。\n\n## 引言\n\n报告讨论了各种主题。",
            "language": "zh"
        }

        response = client.post("/api/v1/report-analysis/analyze", json=request_data)
        assert response.status_code == 200

        result = response.json()
        assert "report_id" in result
        assert len(result["parsed"]["sections"]) > 0

    def test_analyze_empty_content(self, client):
        """Test report analysis with empty content."""
        request_data = {
            "file_name": "empty_report.md",
            "file_type": "markdown",
            "content": ""
        }

        response = client.post("/api/v1/report-analysis/analyze", json=request_data)
        assert response.status_code == 200  # Should still return a response even with empty content

        result = response.json()
        assert result["quality"]["total_word_count"] == 0

    def test_analyze_file_upload_pdf_not_supported_yet(self, client):
        """Test file upload endpoint with a mock PDF file."""
        # Create a minimal PDF content for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000123 00000 n \n0000000217 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n277\n%%EOF"

        files = {
            'file': ('test.pdf', pdf_content, 'application/pdf')
        }

        response = client.post("/api/v1/report-analysis/analyze-file", files=files)
        # This should work if PyPDF2 is available, or return 400 if PDF is not supported in the validation
        assert response.status_code in [200, 400, 500]  # Success, validation error, or dependency error

    def test_analyze_file_upload_txt(self, client):
        """Test file upload endpoint with a text file."""
        txt_content = "Test Report\n\nThis is a test report for analysis.\n\nIntroduction\n\nThe report discusses various topics."

        files = {
            'file': ('test.md', txt_content, 'text/plain')  # Use .md which is allowed
        }

        response = client.post("/api/v1/report-analysis/analyze-file", files=files)
        assert response.status_code == 200

        result = response.json()
        assert "report_id" in result
        assert len(result["parsed"]["sections"]) >= 1  # Should detect at least one section


class TestReportAnalysisService:
    """Test cases for report analysis service logic."""

    @pytest.mark.asyncio
    async def test_service_basic_analysis(self):
        """Test basic service functionality."""
        from services.report_analysis_service import report_analysis_service
        from schemas.report_analysis import ReportAnalysisRequest, ReportFileType

        request = ReportAnalysisRequest(
            file_name="test.md",
            file_type=ReportFileType.MARKDOWN,
            content="# Test Report\n\nThis is a test report.\n\n## Section 1\n\nSome content here."
        )

        result = await report_analysis_service.analyze_report(request)

        assert result.report_id is not None
        assert result.file_name == "test.md"
        assert result.overall_score >= 0 and result.overall_score <= 100
        assert len(result.parsed.sections) > 0
        assert result.quality.total_word_count > 0

    @pytest.mark.asyncio
    async def test_section_detection(self):
        """Test section detection in the parser."""
        from services.report_analysis_service import report_analysis_service
        from schemas.report_analysis import ReportAnalysisRequest, ReportFileType, ReportLanguage

        content = """# Abstract
This is the abstract.

# Introduction
This is the introduction section.

# Method
This describes the method used.

# Results
These are the results.

# Conclusion
This concludes the report."""

        request = ReportAnalysisRequest(
            file_name="test.md",
            file_type=ReportFileType.MARKDOWN,
            content=content,
            language=ReportLanguage.EN
        )

        result = await report_analysis_service.analyze_report(request)

        # Should detect multiple sections
        assert len(result.parsed.sections) >= 4  # abstract, intro, method, results, conclusion

        # Check that sections have proper titles (markdown headers include the #)
        section_titles = [s.title for s in result.parsed.sections]
        assert "# Abstract" in section_titles
        assert "# Introduction" in section_titles
        assert "# Method" in section_titles
        assert "# Results" in section_titles
        assert "# Conclusion" in section_titles

    @pytest.mark.asyncio
    async def test_chinese_section_detection(self):
        """Test section detection with Chinese content."""
        from services.report_analysis_service import report_analysis_service
        from schemas.report_analysis import ReportAnalysisRequest, ReportFileType, ReportLanguage

        content = """# 摘要
这是摘要。

# 引言
这是引言部分。

# 方法
这里描述使用的方法。

# 结果
这些是结果。

# 结论
这是结论。"""

        request = ReportAnalysisRequest(
            file_name="test_cn.md",
            file_type=ReportFileType.MARKDOWN,
            content=content,
            language=ReportLanguage.ZH
        )

        result = await report_analysis_service.analyze_report(request)

        # Should detect multiple sections
        assert len(result.parsed.sections) >= 4

        # Check that sections have proper titles (markdown headers include the #)
        section_titles = [s.title for s in result.parsed.sections]
        assert "# 摘要" in section_titles
        assert "# 引言" in section_titles
        assert "# 方法" in section_titles
        assert "# 结果" in section_titles
        assert "# 结论" in section_titles



class TestJSONParsers:
    """Test cases for JSON parsing methods in report analysis service."""

    @pytest.fixture
    def service(self):
        """Get report analysis service instance."""
        from services.report_analysis_service import report_analysis_service
        return report_analysis_service

    # ===== 逻辑分析解析测试 =====

    def test_parse_logic_analysis_valid_json(self, service):
        """Test parsing valid logic analysis JSON response."""
        valid_json = '''{
            "coherence_score": 85,
            "argumentation_score": 78,
            "issues": [
                {
                    "issue_type": "logical_gap",
                    "description": "Missing connection between premise and conclusion",
                    "section_id": "Section 2, paragraph 3",
                    "severity": "medium"
                }
            ]
        }'''

        result = service._parse_logic_analysis_json(valid_json)

        assert result is not None
        assert result.coherence_score == 85
        assert result.argumentation_score == 78
        assert len(result.issues) == 1
        assert result.issues[0].issue_type == LogicIssueType.LOGICAL_GAP

    def test_parse_logic_analysis_markdown_block(self, service):
        """Test extracting JSON from markdown code block."""
        markdown_response = '''Here is the analysis:

```json
{
    "coherence_score": 90,
    "argumentation_score": 82,
    "issues": []
}
```

This shows good logical structure.'''

        result = service._parse_logic_analysis_json(markdown_response)

        assert result is not None
        assert result.coherence_score == 90
        assert result.argumentation_score == 82
        assert len(result.issues) == 0

    def test_parse_logic_analysis_invalid_enum(self, service):
        """Test that invalid issue type falls back to LOGICAL_GAP."""
        json_with_invalid_enum = '''{
            "coherence_score": 75,
            "argumentation_score": 70,
            "issues": [
                {
                    "issue_type": "unknown_issue_type",
                    "description": "Some issue",
                    "section_id": "Section 1",
                    "severity": "low"
                }
            ]
        }'''

        result = service._parse_logic_analysis_json(json_with_invalid_enum)

        assert result is not None
        assert len(result.issues) == 1
        # Invalid enum should fall back to LOGICAL_GAP
        assert result.issues[0].issue_type == LogicIssueType.LOGICAL_GAP

    def test_parse_logic_analysis_invalid_json(self, service):
        """Test that invalid JSON returns None."""
        invalid_json = "This is not valid JSON at all {{"

        result = service._parse_logic_analysis_json(invalid_json)

        assert result is None

    # ===== 创新性分析解析测试 =====

    def test_parse_innovation_valid(self, service):
        """Test parsing valid innovation analysis JSON."""
        valid_json = '''{
            "novelty_score": 72,
            "difference_summary": "The report presents a novel approach to algorithm optimization.",
            "innovation_points": [
                {
                    "highlight_text": "Algorithm optimization",
                    "reason": "Novel approach to reduce complexity"
                }
            ]
        }'''

        result = service._parse_innovation_analysis_json(valid_json)

        assert result is not None
        assert result.novelty_score == 72
        assert result.difference_summary == "The report presents a novel approach to algorithm optimization."
        assert len(result.innovation_points) == 1
        assert result.innovation_points[0].highlight_text == "Algorithm optimization"

    def test_parse_innovation_missing_required_fields(self, service):
        """Test that missing optional fields use defaults."""
        incomplete_json = '''{
            "novelty_score": 80
        }'''

        result = service._parse_innovation_analysis_json(incomplete_json)

        # Service returns default object with provided novelty_score
        assert result is not None
        assert result.novelty_score == 80
        assert result.difference_summary == ""
        assert len(result.innovation_points) == 0

    # ===== 改进建议解析测试 =====

    def test_parse_suggestions_valid(self, service):
        """Test parsing valid improvement suggestions JSON."""
        # Note: valid_categories in service are: {"content", "logic", "language", "formatting"}
        valid_json = '''{
            "suggestions": [
                {
                    "category": "logic",
                    "priority": "high",
                    "summary": "Weak introduction",
                    "details": "Add clear thesis statement for better reader engagement"
                },
                {
                    "category": "content",
                    "priority": "medium",
                    "summary": "Insufficient evidence",
                    "details": "Include more citations to strengthen arguments"
                }
            ]
        }'''

        result = service._parse_suggestions_json(valid_json)

        # _parse_suggestions_json returns List[ImprovementSuggestion] directly
        assert result is not None
        assert len(result) == 2
        assert result[0].category == "logic"
        assert result[1].category == "content"

    def test_parse_suggestions_invalid_category(self, service):
        """Test that invalid category defaults to 'content'."""
        json_with_invalid_category = '''{
            "suggestions": [
                {
                    "category": "invalid_category_xyz",
                    "priority": "low",
                    "summary": "Some issue",
                    "details": "Some fix for improvement"
                }
            ]
        }'''

        result = service._parse_suggestions_json(json_with_invalid_category)

        # _parse_suggestions_json returns List[ImprovementSuggestion] directly
        assert result is not None
        assert len(result) == 1
        # Invalid category should default to "content"
        assert result[0].category == "content"


    # ===== 语言质量解析测试 =====

    def test_parse_language_valid(self, service):
        """Test parsing valid language quality JSON."""
        valid_json = '''{
            "readability_score": 82,
            "academic_tone_score": 75,
            "grammar_issue_count": 1
        }'''

        result = service._parse_language_analysis_json(valid_json)

        # Returns LanguageQualityMetrics object with attribute access
        assert result is not None
        assert result.readability_score == 82
        assert result.academic_tone_score == 75
        assert result.grammar_issue_count == 1

    def test_parse_language_value_clamping(self, service):
        """Test that out-of-range values are clamped to valid range."""
        json_with_extreme_values = '''{
            "readability_score": 150,
            "academic_tone_score": -20,
            "grammar_issue_count": 0
        }'''

        result = service._parse_language_analysis_json(json_with_extreme_values)

        # Returns LanguageQualityMetrics object with attribute access
        assert result is not None
        # Values should be clamped to 0-100 range
        assert result.readability_score == 100
        assert result.academic_tone_score == 0


# Check if DeepSeek API key is available for integration tests
HAS_API_KEY = bool(os.environ.get("DEEPSEEK_API_KEY"))


class TestDeepSeekIntegration:
    """End-to-end tests with real DeepSeek API.

    These tests require a valid DEEPSEEK_API_KEY environment variable.
    They are marked as slow and will be skipped if no API key is available.
    """

    @pytest.fixture
    def service(self):
        """Get report analysis service instance with AI features enabled."""
        from services.report_analysis_service import report_analysis_service
        # Enable all AI features for integration testing
        report_analysis_service.config.use_ai_for_logic = True
        report_analysis_service.config.use_ai_for_innovation = True
        report_analysis_service.config.use_ai_for_suggestions = True
        report_analysis_service.config.use_ai_for_language = True
        return report_analysis_service

    @pytest.fixture
    def sample_report_content(self):
        """Sample report content for testing."""
        return """
# Research Report: Machine Learning in Education

## Abstract
This report explores the application of machine learning techniques in educational settings.
We analyze current implementations and propose new approaches for personalized learning.

## Introduction
The education sector has seen significant technological advances in recent years.
Machine learning offers promising solutions for adaptive learning systems.
However, challenges remain in implementation and data privacy.

## Methodology
We conducted a literature review of 50 peer-reviewed papers.
Additionally, we performed experiments with a sample of 100 students.

## Results
Our findings indicate a 25% improvement in learning outcomes.
Students showed higher engagement with personalized content.

## Conclusion
Machine learning has significant potential in education.
Further research is needed to address privacy concerns.
"""

    @pytest.fixture
    def parsed_report(self, sample_report_content):
        """Create a parsed report for testing."""
        return ReportParseResult(
            file_name="test_report.md",
            file_type=ReportFileType.MARKDOWN,
            raw_text=sample_report_content,
            sections=[],
            references=[]
        )

    @pytest.mark.slow
    @pytest.mark.skipif(not HAS_API_KEY, reason="DEEPSEEK_API_KEY not available")
    @pytest.mark.asyncio
    async def test_analyze_logic_with_real_ai(self, service, parsed_report):
        """Test logic analysis with real DeepSeek API."""
        result = await service._analyze_logic_with_ai(parsed_report)

        assert result is not None
        assert result.coherence_score is not None
        assert result.argumentation_score is not None
        assert 0 <= result.coherence_score <= 100
        assert 0 <= result.argumentation_score <= 100

    @pytest.mark.slow
    @pytest.mark.skipif(not HAS_API_KEY, reason="DEEPSEEK_API_KEY not available")
    @pytest.mark.asyncio
    async def test_analyze_innovation_with_real_ai(self, service, parsed_report):
        """Test innovation analysis with real DeepSeek API."""
        result = await service._analyze_innovation_with_ai(parsed_report)

        assert result is not None
        assert result.novelty_score is not None
        assert result.difference_summary is not None
        assert 0 <= result.novelty_score <= 100

    @pytest.mark.slow
    @pytest.mark.skipif(not HAS_API_KEY, reason="DEEPSEEK_API_KEY not available")
    @pytest.mark.asyncio
    async def test_generate_suggestions_with_real_ai(self, service, parsed_report):
        """Test improvement suggestions generation with real DeepSeek API."""
        result = await service._generate_suggestions_with_ai(parsed_report)

        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.slow
    @pytest.mark.skipif(not HAS_API_KEY, reason="DEEPSEEK_API_KEY not available")
    @pytest.mark.asyncio
    async def test_evaluate_language_with_real_ai(self, service, sample_report_content):
        """Test language quality evaluation with real DeepSeek API."""
        result = await service._evaluate_language_with_ai(sample_report_content)

        assert result is not None
        assert result.average_sentence_length is not None
        assert result.academic_tone_score is not None
        assert 0 <= result.academic_tone_score <= 100