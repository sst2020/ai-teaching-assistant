"""
Tests for Q&A triage endpoints.
"""
import pytest


def test_ask_question(client, sample_question):
    """Test asking a question."""
    response = client.post("/api/v1/qa/ask", json=sample_question)
    assert response.status_code == 200
    data = response.json()
    assert "question_id" in data
    assert "status" in data
    assert "ai_answer" in data
    assert data["student_id"] == sample_question["student_id"]
    assert data["course_id"] == sample_question["course_id"]


def test_ask_question_missing_fields(client):
    """Test asking question with missing fields."""
    response = client.post("/api/v1/qa/ask", json={
        "question": "What is Python?"
    })
    assert response.status_code == 422  # Missing student_id and course_id


def test_escalate_question(client, sample_question):
    """Test escalating a question to teacher."""
    # First ask a question
    ask_response = client.post("/api/v1/qa/ask", json=sample_question)
    question_id = ask_response.json()["question_id"]

    # Then escalate it
    response = client.post("/api/v1/qa/escalate", json={
        "question_id": question_id,
        "reason": "Need more detailed explanation"
    })
    assert response.status_code == 200
    data = response.json()
    # Check that escalation was processed (response contains question data)
    assert "question_id" in data or "status" in data


def test_qa_analytics(client):
    """Test Q&A analytics endpoint."""
    response = client.get("/api/v1/qa/analytics/CS101")
    assert response.status_code == 200
    data = response.json()
    assert "course_id" in data
    assert "total_questions" in data
    # Check for actual fields in the response
    assert "ai_resolved_count" in data or "knowledge_gaps" in data

