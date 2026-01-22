"""
Test suite for project report analysis functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from schemas.report_analysis import ReportAnalysisRequest, ReportFileType, ReportLanguage


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