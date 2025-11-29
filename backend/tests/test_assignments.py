"""
Tests for assignment grading endpoints.
"""
import pytest


def test_grade_assignment(client, sample_assignment):
    """Test grading a single assignment."""
    response = client.post("/api/v1/assignments/grade", json=sample_assignment)
    assert response.status_code == 200
    data = response.json()
    assert "submission_id" in data
    assert "overall_score" in data
    assert "status" in data
    assert data["status"] == "completed"


def test_grade_assignment_missing_fields(client):
    """Test grading with missing required fields."""
    response = client.post("/api/v1/assignments/grade", json={})
    assert response.status_code == 422  # Validation error


def test_analyze_code(client, sample_python_code):
    """Test code analysis endpoint."""
    response = client.post("/api/v1/assignments/analyze-code", json={
        "code": sample_python_code,
        "language": "python",
        "include_style": True,
        "include_complexity": True,
        "include_smells": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "overall_quality_score" in data
    assert "complexity_metrics" in data
    assert "style_analysis" in data


def test_analyze_code_with_issues(client, sample_code_with_issues):
    """Test code analysis detects issues."""
    response = client.post("/api/v1/assignments/analyze-code", json={
        "code": sample_code_with_issues,
        "language": "python"
    })
    assert response.status_code == 200
    data = response.json()
    # Code with issues should have lower quality score
    assert data["overall_quality_score"] < 100


def test_plagiarism_check(client):
    """Test plagiarism check endpoint."""
    # First submission
    response1 = client.post("/api/v1/assignments/plagiarism/check", json={
        "submission_id": "sub_001",
        "student_id": "student_001",
        "course_id": "CS101",
        "code": "def hello():\n    print('Hello')"
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["is_flagged"] == False  # First submission, no matches
    
    # Similar submission from different student
    response2 = client.post("/api/v1/assignments/plagiarism/check", json={
        "submission_id": "sub_002",
        "student_id": "student_002",
        "course_id": "CS101",
        "code": "def greet():\n    print('Hello')"  # Same structure, different name
    })
    assert response2.status_code == 200
    data2 = response2.json()
    # Should detect similarity
    assert data2["overall_similarity"] > 0.5


def test_batch_grading(client):
    """Test batch grading endpoint."""
    submissions = [
        {
            "student_id": "student_001",
            "assignment_id": "hw_001",
            "assignment_type": "code",
            "content": "def add(a, b): return a + b"
        },
        {
            "student_id": "student_002",
            "assignment_id": "hw_001",
            "assignment_type": "code",
            "content": "def subtract(a, b): return a - b"
        }
    ]
    response = client.post("/api/v1/assignments/grade/batch", json={
        "assignment_id": "hw_001",
        "submissions": submissions
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2

