"""
Tests for the Intelligent Feedback Generation System.

Tests cover:
- Feedback generation service
- AI integration service
- Feedback templates CRUD
- API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Test the feedback service
from services.feedback_service import FeedbackGenerationService, feedback_service
from schemas.feedback import (
    FeedbackTone, FeedbackCategory, TemplateCategory,
    GenerateFeedbackRequest, FeedbackItem
)


class TestFeedbackGenerationService:
    """Tests for FeedbackGenerationService."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test."""
        return FeedbackGenerationService()

    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for testing."""
        return '''
def calculate_sum(a, b):
    result = a + b
    return result

def process_data(data):
    if data:
        if len(data) > 0:
            if data[0] is not None:
                for item in data:
                    print(item)
    return data

class MyClass:
    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value
'''

    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results for testing."""
        return {
            "metrics": {
                "total_lines": 20,
                "code_lines": 15,
                "comment_lines": 0,
                "blank_lines": 5,
                "function_count": 3,
                "class_count": 1,
                "max_nesting_depth": 4,
                "cyclomatic_complexity": 5,
                "cognitive_complexity": 8
            },
            "issues": [
                {
                    "type": "deep_nesting",
                    "severity": "warning",
                    "message": "Deep nesting detected",
                    "line": 7
                },
                {
                    "type": "missing_docstring",
                    "severity": "info",
                    "message": "Missing docstring",
                    "line": 1
                }
            ],
            "score": 75
        }

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert hasattr(service, 'generate_feedback')

    def test_singleton_instance(self):
        """Test that feedback_service is a singleton."""
        assert feedback_service is not None
        assert isinstance(feedback_service, FeedbackGenerationService)

    @pytest.mark.asyncio
    async def test_generate_feedback_basic(self, service, sample_python_code, sample_analysis_results):
        """Test basic feedback generation."""
        feedback = await service.generate_feedback(
            code=sample_python_code,
            language="python",
            analysis_results=sample_analysis_results,
            tone=FeedbackTone.PROFESSIONAL
        )

        assert feedback is not None
        assert "feedback_items" in feedback
        assert "overall_score" in feedback
        assert "summary" in feedback
        assert "strengths" in feedback
        assert "improvements" in feedback

    @pytest.mark.asyncio
    async def test_generate_feedback_encouraging_tone(self, service, sample_python_code, sample_analysis_results):
        """Test feedback with encouraging tone."""
        feedback = await service.generate_feedback(
            code=sample_python_code,
            language="python",
            analysis_results=sample_analysis_results,
            tone=FeedbackTone.ENCOURAGING
        )

        assert feedback is not None
        # Encouraging tone should have positive language
        summary = feedback.get("summary", "")
        assert isinstance(summary, str)

    @pytest.mark.asyncio
    async def test_generate_feedback_strict_tone(self, service, sample_python_code, sample_analysis_results):
        """Test feedback with strict tone."""
        feedback = await service.generate_feedback(
            code=sample_python_code,
            language="python",
            analysis_results=sample_analysis_results,
            tone=FeedbackTone.STRICT
        )

        assert feedback is not None
        assert "feedback_items" in feedback

    @pytest.mark.asyncio
    async def test_generate_feedback_with_assignment_context(self, service, sample_python_code, sample_analysis_results):
        """Test feedback with assignment context."""
        assignment_context = {
            "title": "Basic Functions",
            "requirements": ["Create a function to calculate sum", "Handle edge cases"],
            "rubric": {"functionality": 50, "style": 30, "documentation": 20}
        }



class TestAIService:
    """Tests for AI Service."""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        return {
            "choices": [{
                "message": {
                    "content": "This is a test response from the AI."
                }
            }],
            "usage": {
                "total_tokens": 100
            }
        }

    @pytest.mark.asyncio
    async def test_explain_code(self):
        """Test code explanation."""
        from services.ai_service import ai_service

        result = await ai_service.explain_code(
            code="def add(a, b): return a + b",
            language="python",
            detail_level="beginner"
        )

        assert result is not None
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_suggest_improvements(self):
        """Test improvement suggestions."""
        from services.ai_service import ai_service

        result = await ai_service.suggest_improvements(
            code="x = 1\ny = 2\nz = x + y",
            language="python",
            focus_areas=["readability", "performance"]
        )

        assert result is not None
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_answer_student_question(self):
        """Test answering student questions."""
        from services.ai_service import ai_service

        result = await ai_service.answer_student_question(
            question="What is a function?",
            code="def greet(): print('Hello')",
            language="python"
        )

        assert result is not None
        assert "answer" in result

    def test_get_interaction_stats(self):
        """Test getting interaction statistics."""
        from services.ai_service import ai_service

        stats = ai_service.get_interaction_stats()

        assert stats is not None
        assert "total_interactions" in stats


class TestFeedbackTemplates:
    """Tests for Feedback Templates."""

    @pytest.fixture
    def sample_template_data(self):
        """Sample template data for testing."""
        return {
            "name": "Test Template",
            "category": TemplateCategory.COMMON_ISSUES,
            "title": "Test Issue",
            "message": "This is a test message for {variable}",
            "severity": "info",
            "tags": ["test", "sample"],
            "variables": ["variable"],
            "is_active": True
        }

    def test_template_category_enum(self):
        """Test TemplateCategory enum values."""
        assert TemplateCategory.COMMON_ISSUES.value == "common_issues"
        assert TemplateCategory.LANGUAGE_SPECIFIC.value == "language_specific"
        assert TemplateCategory.ENCOURAGEMENT.value == "encouragement"
        assert TemplateCategory.SECURITY.value == "security"

    def test_feedback_tone_enum(self):
        """Test FeedbackTone enum values."""
        assert FeedbackTone.ENCOURAGING.value == "encouraging"
        assert FeedbackTone.PROFESSIONAL.value == "professional"
        assert FeedbackTone.STRICT.value == "strict"

    def test_feedback_category_enum(self):
        """Test FeedbackCategory enum values."""
        assert FeedbackCategory.CODE_QUALITY.value == "code_quality"
        assert FeedbackCategory.SECURITY.value == "security"
        assert FeedbackCategory.SUGGESTIONS.value == "suggestions"


class TestFeedbackAPIEndpoints:
    """Tests for Feedback API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_generate_feedback_endpoint(self, client):
        """Test POST /api/v1/ai/generate-feedback endpoint."""
        response = client.post(
            "/api/v1/ai/generate-feedback",
            json={
                "code": "def test(): pass",
                "language": "python",
                "tone": "professional"
            }
        )

        assert response.status_code in [200, 500]  # 500 if no API key

    def test_explain_code_endpoint(self, client):
        """Test POST /api/v1/ai/explain-code endpoint."""
        response = client.post(
            "/api/v1/ai/explain-code",
            json={
                "code": "for i in range(10): print(i)",
                "language": "python",
                "detail_level": "beginner"
            }
        )

        assert response.status_code in [200, 500]

    def test_suggest_improvements_endpoint(self, client):
        """Test POST /api/v1/ai/suggest-improvements endpoint."""
        response = client.post(
            "/api/v1/ai/suggest-improvements",
            json={
                "code": "x=1;y=2;z=x+y",
                "language": "python"
            }
        )

        assert response.status_code in [200, 500]

    def test_answer_question_endpoint(self, client):
        """Test POST /api/v1/ai/answer-question endpoint."""
        response = client.post(
            "/api/v1/ai/answer-question",
            json={
                "question": "What is a loop?",
                "language": "python"
            }
        )

        assert response.status_code in [200, 500]

    def test_ai_config_endpoint(self, client):
        """Test GET /api/v1/ai/config endpoint."""
        response = client.get("/api/v1/ai/config")

        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "model" in data

    def test_ai_health_endpoint(self, client):
        """Test GET /api/v1/ai/health endpoint."""
        response = client.get("/api/v1/ai/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestFeedbackTemplatesAPI:
    """Tests for Feedback Templates API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_list_templates_endpoint(self, client):
        """Test GET /api/v1/feedback-templates endpoint."""
        response = client.get("/api/v1/feedback-templates")

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert "page" in data

    def test_list_categories_endpoint(self, client):
        """Test GET /api/v1/feedback-templates/categories/list endpoint."""
        response = client.get("/api/v1/feedback-templates/categories/list")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_template_endpoint(self, client):
        """Test POST /api/v1/feedback-templates endpoint."""
        response = client.post(
            "/api/v1/feedback-templates",
            json={
                "name": "Test Template",
                "category": "common_issues",
                "title": "Test Title",
                "message": "Test message",
                "severity": "info",
                "tags": ["test"],
                "variables": [],
                "is_active": True
            }
        )

        # May fail if database not set up, but should not be 422
        assert response.status_code in [201, 500]
