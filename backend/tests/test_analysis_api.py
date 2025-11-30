"""
Tests for the Code Analysis API endpoints.
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


# ============================================
# Analyze Code Endpoint Tests
# ============================================

class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/analysis/analyze endpoint."""

    def test_analyze_python_code(self, client):
        """Test analyzing Python code."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "code": "def hello():\n    print('Hello')\n",
                "language": "python"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        result = data["result"]
        assert "summary" in result
        assert "overall_score" in result["summary"]
        assert result["language"] == "python"

    def test_analyze_javascript_code(self, client):
        """Test analyzing JavaScript code."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "code": "function hello() {\n    console.log('Hello');\n}\n",
                "language": "javascript"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["language"] == "javascript"

    def test_analyze_with_rule_overrides(self, client):
        """Test analyzing with custom rule overrides."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "code": "def hello():\n    pass\n",
                "language": "python",
                "rule_overrides": [
                    {"rule_id": "COMPLEXITY_001", "enabled": False}
                ]
            }
        )
        assert response.status_code == 200

    def test_analyze_empty_code(self, client):
        """Test analyzing empty code."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "code": "",
                "language": "python"
            }
        )
        assert response.status_code == 200

    def test_analyze_invalid_language(self, client):
        """Test analyzing with invalid language."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "code": "print('hello')",
                "language": "invalid_lang"
            }
        )
        # Should still work but with limited analysis
        assert response.status_code in [200, 400]


# ============================================
# Rules Endpoint Tests
# ============================================

class TestRulesEndpoint:
    """Tests for GET /api/v1/analysis/rules endpoint."""

    def test_get_all_rules(self, client):
        """Test getting all analysis rules."""
        response = client.get("/api/v1/analysis/rules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check rule structure
        rule = data[0]
        assert "rule_id" in rule
        assert "name" in rule
        assert "category" in rule
        assert "severity" in rule

    def test_get_specific_rule(self, client):
        """Test getting a specific rule by ID."""
        response = client.get("/api/v1/analysis/rules/COMPLEXITY_001")
        assert response.status_code == 200
        data = response.json()
        assert data["rule_id"] == "COMPLEXITY_001"

    def test_get_nonexistent_rule(self, client):
        """Test getting a rule that doesn't exist."""
        response = client.get("/api/v1/analysis/rules/NONEXISTENT_RULE")
        assert response.status_code == 404


# ============================================
# Summary Endpoint Tests
# ============================================

class TestSummaryEndpoint:
    """Tests for GET /api/v1/analysis/summary endpoint."""

    def test_get_analysis_summary(self, client):
        """Test getting analysis summary."""
        response = client.get("/api/v1/analysis/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyzed" in data
        assert "files" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

