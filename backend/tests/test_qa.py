"""
Tests for Q&A triage endpoints.
"""
from types import SimpleNamespace

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


def test_pending_questions_allows_admin(client):
    """管理员应可访问待回答问题列表。"""
    from api.qa import get_current_teacher_or_admin

    client.app.dependency_overrides[get_current_teacher_or_admin] = lambda: SimpleNamespace(
        student_id="0000000001",
        name="管理员",
        role="admin"
    )

    try:
        response = client.get("/api/v1/qa/pending-questions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    finally:
        client.app.dependency_overrides.pop(get_current_teacher_or_admin, None)


def test_answer_question_allows_admin(client):
    """管理员应可进入回答问题逻辑，而不是被权限拒绝。"""
    from api.qa import get_current_teacher_or_admin

    client.app.dependency_overrides[get_current_teacher_or_admin] = lambda: SimpleNamespace(
        student_id="0000000001",
        name="管理员",
        role="admin"
    )

    try:
        response = client.post(
            "/api/v1/qa/answer-question",
            json={
                "log_id": "missing-log",
                "teacher_id": "0000000001",
                "answer": "测试回答",
                "update_knowledge_base": False,
                "new_keywords": []
            }
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Question log not found"
    finally:
        client.app.dependency_overrides.pop(get_current_teacher_or_admin, None)

