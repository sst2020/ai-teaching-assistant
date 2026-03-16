"""
Tests for Submission Management API endpoints.

覆盖 POST /submissions, GET /submissions/{id},
GET /submissions/student/{id}, GET /submissions/assignment/{id},
PUT /submissions/{id}/status 等端点。
"""
import pytest
import time
import random


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def student_factory():
    """工厂函数生成唯一的学生数据"""
    counter = {"value": 0}

    def _create(**kwargs):
        counter["value"] += 1
        unique_id = int(time.time() * 1000) + random.randint(1, 9999)
        defaults = {
            "student_id": f"SUBTEST{unique_id}_{counter['value']}",
            "name": f"Submission Test Student {counter['value']}",
            "email": f"subtest{unique_id}_{counter['value']}@test.com",
            "course_id": "CS101",
        }
        defaults.update(kwargs)
        return defaults

    return _create


@pytest.fixture
def assignment_factory():
    """工厂函数生成唯一的作业数据"""
    counter = {"value": 0}

    def _create(**kwargs):
        counter["value"] += 1
        unique_id = int(time.time() * 1000) + random.randint(1, 9999)
        defaults = {
            "assignment_id": f"ASN{unique_id}_{counter['value']}",
            "title": f"Test Assignment {counter['value']}",
            "description": "A test assignment",
            "assignment_type": "code",
            "course_id": "CS101",
            "max_score": 100.0,
        }
        defaults.update(kwargs)
        return defaults

    return _create


@pytest.fixture
def created_student(client, student_factory):
    """创建一个已注册的学生"""
    data = student_factory()
    resp = client.post("/api/v1/students/register", json=data)
    assert resp.status_code == 201
    return {**resp.json(), "external_id": data["student_id"]}


@pytest.fixture
def created_assignment(client, assignment_factory):
    """创建一个作业"""
    data = assignment_factory()
    resp = client.post("/api/v1/assignments", json=data)
    assert resp.status_code == 201
    return {**resp.json(), "external_id": data["assignment_id"]}


@pytest.fixture
def submission_factory():
    """工厂函数生成唯一的提交数据"""
    counter = {"value": 0}

    def _create(student_ext_id: str, assignment_ext_id: str, **kwargs):
        counter["value"] += 1
        unique_id = int(time.time() * 1000) + random.randint(1, 9999)
        defaults = {
            "submission_id": f"SUB{unique_id}_{counter['value']}",
            "student_id": student_ext_id,
            "assignment_id": assignment_ext_id,
            "content": f"print('hello {counter['value']}')",
        }
        defaults.update(kwargs)
        return defaults

    return _create


@pytest.fixture
def created_submission(client, created_student, created_assignment, submission_factory):
    """创建一个已提交的作业"""
    data = submission_factory(
        created_student["external_id"],
        created_assignment["external_id"],
    )
    resp = client.post("/api/v1/submissions", json=data)
    assert resp.status_code == 201
    return {**resp.json(), "submission_ext_id": data["submission_id"]}


# ============================================================================
# Test Class 1: Create Submission
# ============================================================================

class TestCreateSubmission:
    """测试创建提交 POST /api/v1/submissions"""

    def test_create_success(self, client, created_student, created_assignment, submission_factory):
        """测试成功创建提交"""
        data = submission_factory(
            created_student["external_id"],
            created_assignment["external_id"],
        )
        resp = client.post("/api/v1/submissions", json=data)
        assert resp.status_code == 201
        body = resp.json()
        assert body["submission_id"] == data["submission_id"]
        assert body["content"] == data["content"]
        assert body["status"] == "pending"

    def test_create_auto_id(self, client, created_student, created_assignment):
        """测试不提供 submission_id 时自动生成"""
        data = {
            "student_id": created_student["external_id"],
            "assignment_id": created_assignment["external_id"],
            "content": "auto id test",
        }
        resp = client.post("/api/v1/submissions", json=data)
        assert resp.status_code == 201
        body = resp.json()
        assert body["submission_id"]  # 应自动生成
        assert body["submission_id"].startswith("SUB_")

    def test_create_student_not_found(self, client, created_assignment, submission_factory):
        """测试学生不存在时返回 404"""
        data = submission_factory("NONEXISTENT_STU", created_assignment["external_id"])
        resp = client.post("/api/v1/submissions", json=data)
        assert resp.status_code == 404

    def test_create_assignment_not_found(self, client, created_student, submission_factory):
        """测试作业不存在时返回 404"""
        data = submission_factory(created_student["external_id"], "NONEXISTENT_ASN")

    def test_create_duplicate_id(self, client, created_student, created_assignment, submission_factory):
        """测试重复 submission_id 返回 400"""
        data = submission_factory(
            created_student["external_id"],
            created_assignment["external_id"],
        )
        resp1 = client.post("/api/v1/submissions", json=data)
        assert resp1.status_code == 201
        resp2 = client.post("/api/v1/submissions", json=data)
        assert resp2.status_code == 400

    def test_create_missing_fields(self, client):
        """测试缺少必填字段返回 422"""
        resp = client.post("/api/v1/submissions", json={})
        assert resp.status_code == 422

    def test_create_with_file_path(self, client, created_student, created_assignment, submission_factory):
        """测试带 file_path 的提交"""
        data = submission_factory(
            created_student["external_id"],
            created_assignment["external_id"],
            file_path="/uploads/test.py",
        )
        resp = client.post("/api/v1/submissions", json=data)
        assert resp.status_code == 201
        assert resp.json()["file_path"] == "/uploads/test.py"


# ============================================================================
# Test Class 2: Get Submission
# ============================================================================

class TestGetSubmission:
    """测试获取提交详情 GET /api/v1/submissions/{submission_id}"""

    def test_get_success(self, client, created_submission):
        """测试成功获取提交详情"""
        sub_id = created_submission["submission_ext_id"]
        resp = client.get(f"/api/v1/submissions/{sub_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["submission_id"] == sub_id
        assert "student_name" in body
        assert "assignment_title" in body

    def test_get_not_found(self, client):
        """测试获取不存在的提交返回 404"""
        resp = client.get("/api/v1/submissions/NONEXISTENT_SUB")
        assert resp.status_code == 404


# ============================================================================
# Test Class 3: Get Student Submissions
# ============================================================================

class TestGetStudentSubmissions:
    """测试获取学生提交列表 GET /api/v1/submissions/student/{student_id}"""

    def test_get_student_submissions(self, client, created_student, created_assignment, submission_factory):
        """测试获取学生的所有提交"""
        ext_stu = created_student["external_id"]
        ext_asn = created_assignment["external_id"]
        # 创建 3 个提交
        for _ in range(3):
            data = submission_factory(ext_stu, ext_asn)
            resp = client.post("/api/v1/submissions", json=data)
            assert resp.status_code == 201

        resp = client.get(f"/api/v1/submissions/student/{ext_stu}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 3
        assert len(body["items"]) >= 3

    def test_get_student_submissions_pagination(self, client, created_student, created_assignment, submission_factory):
        """测试分页"""
        ext_stu = created_student["external_id"]
        ext_asn = created_assignment["external_id"]
        for _ in range(5):
            data = submission_factory(ext_stu, ext_asn)
            client.post("/api/v1/submissions", json=data)

        resp = client.get(f"/api/v1/submissions/student/{ext_stu}?page=1&page_size=2")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["page"] == 1
        assert body["total_pages"] >= 3

    def test_get_student_not_found(self, client):
        """测试学生不存在返回 404"""
        resp = client.get("/api/v1/submissions/student/NONEXISTENT_STU")
        assert resp.status_code == 404


# ============================================================================
# Test Class 4: Get Assignment Submissions
# ============================================================================

class TestGetAssignmentSubmissions:
    """测试获取作业提交列表 GET /api/v1/submissions/assignment/{assignment_id}"""

    def test_get_assignment_submissions(self, client, created_assignment, student_factory, submission_factory):
        """测试获取作业的所有提交"""
        ext_asn = created_assignment["external_id"]
        # 创建 2 个不同学生的提交
        for _ in range(2):
            stu_data = student_factory()
            stu_resp = client.post("/api/v1/students/register", json=stu_data)
            assert stu_resp.status_code == 201
            sub_data = submission_factory(stu_data["student_id"], ext_asn)
            sub_resp = client.post("/api/v1/submissions", json=sub_data)
            assert sub_resp.status_code == 201

        resp = client.get(f"/api/v1/submissions/assignment/{ext_asn}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2

    def test_get_assignment_not_found(self, client):
        """测试作业不存在返回 404"""
        resp = client.get("/api/v1/submissions/assignment/NONEXISTENT_ASN")
        assert resp.status_code == 404


# ============================================================================
# Test Class 5: Update Submission Status
# ============================================================================

class TestUpdateSubmissionStatus:
    """测试更新提交状态 PUT /api/v1/submissions/{submission_id}/status"""

    def test_update_to_graded(self, client, created_submission):
        """测试将状态更新为 graded"""
        sub_id = created_submission["submission_ext_id"]
        resp = client.put(
            f"/api/v1/submissions/{sub_id}/status",
            json={"status": "graded"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "graded"

    def test_update_to_flagged(self, client, created_submission):
        """测试将状态更新为 flagged"""
        sub_id = created_submission["submission_ext_id"]
        resp = client.put(
            f"/api/v1/submissions/{sub_id}/status",
            json={"status": "flagged"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "flagged"

    def test_update_to_pending(self, client, created_submission):
        """测试将状态更新回 pending"""
        sub_id = created_submission["submission_ext_id"]
        # 先改为 graded
        client.put(f"/api/v1/submissions/{sub_id}/status", json={"status": "graded"})
        # 再改回 pending
        resp = client.put(
            f"/api/v1/submissions/{sub_id}/status",
            json={"status": "pending"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending"

    def test_update_not_found(self, client):
        """测试更新不存在的提交返回 404"""
        resp = client.put(
            "/api/v1/submissions/NONEXISTENT_SUB/status",
            json={"status": "graded"},
        )
        assert resp.status_code == 404

    def test_update_invalid_status(self, client, created_submission):
        """测试无效状态值返回 422"""
        sub_id = created_submission["submission_ext_id"]
        resp = client.put(
            f"/api/v1/submissions/{sub_id}/status",
            json={"status": "invalid_status"},
        )
        assert resp.status_code == 422
