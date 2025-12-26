"""
Tests for Student Management API endpoints.
"""
import pytest
from datetime import datetime
import time
import random


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def student_factory():
    """
    工厂函数生成唯一的学生数据
    使用时间戳和随机数确保 student_id 和 email 的唯一性
    """
    counter = {"value": 0}

    def _create(**kwargs):
        counter["value"] += 1
        # 使用时间戳和随机数确保唯一性
        unique_id = int(time.time() * 1000) + random.randint(1, 9999)
        defaults = {
            "student_id": f"TEST{unique_id}_{counter['value']}",
            "name": f"Test Student {counter['value']}",
            "email": f"test{unique_id}_{counter['value']}@test.com",
            "course_id": "CS101"
        }
        defaults.update(kwargs)
        return defaults

    return _create


@pytest.fixture
def created_student(client, student_factory):
    """
    创建一个已注册的学生
    用于测试 get/update/delete 端点
    """
    student_data = student_factory()
    response = client.post("/api/v1/students/register", json=student_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def multiple_students(client, student_factory):
    """
    创建 15 个学生用于分页测试
    - 10 个学生在 CS101 课程
    - 5 个学生在 CS102 课程
    """
    students = []
    for i in range(15):
        course_id = "CS101" if i < 10 else "CS102"
        student_data = student_factory(course_id=course_id)
        response = client.post("/api/v1/students/register", json=student_data)
        assert response.status_code == 201
        students.append(response.json())
    return students


# ============================================================================
# Test Class 1: Student Registration
# ============================================================================

class TestStudentRegistration:
    """测试学生注册端点 POST /api/v1/students/register"""
    
    def test_register_success(self, client, student_factory):
        """测试成功注册新学生"""
        student_data = student_factory()
        response = client.post("/api/v1/students/register", json=student_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # 验证返回的数据结构
        assert "id" in data
        assert "student_id" in data
        assert "name" in data
        assert "email" in data
        assert "course_id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # 验证返回的字段值
        assert data["student_id"] == student_data["student_id"]
        assert data["name"] == student_data["name"]
        assert data["email"] == student_data["email"]
        assert data["course_id"] == student_data["course_id"]
    
    def test_register_with_all_fields(self, client, student_factory):
        """测试使用所有字段注册学生（包括可选字段）"""
        student_data = student_factory()
        student_data["enrollment_date"] = "2024-01-15T00:00:00"
        
        response = client.post("/api/v1/students/register", json=student_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["enrollment_date"] is not None
    
    def test_register_duplicate_student_id(self, client, created_student, student_factory):
        """测试注册重复的 student_id 返回 400 错误"""
        # 使用已存在的 student_id
        student_data = student_factory()
        student_data["student_id"] = created_student["student_id"]
        
        response = client.post("/api/v1/students/register", json=student_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"]
    
    def test_register_duplicate_email(self, client, created_student, student_factory):
        """测试注册重复的 email 返回 400 错误"""
        # 使用已存在的 email
        student_data = student_factory()
        student_data["email"] = created_student["email"]
        
        response = client.post("/api/v1/students/register", json=student_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"]
    
    def test_register_invalid_email_format(self, client, student_factory):
        """测试无效的 email 格式返回 422 验证错误"""
        student_data = student_factory()
        student_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/students/register", json=student_data)
        
        assert response.status_code == 422
    
    def test_register_missing_required_fields(self, client):
        """测试缺少必填字段返回 422 验证错误"""
        response = client.post("/api/v1/students/register", json={})

        assert response.status_code == 422


# ============================================================================
# Test Class 2: Student Login
# ============================================================================

class TestStudentLogin:
    """测试学生登录端点 POST /api/v1/students/login"""

    def test_login_success(self, client, created_student):
        """测试成功登录"""
        login_data = {
            "student_id": created_student["student_id"]
        }
        response = client.post("/api/v1/students/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert "success" in data
        assert "message" in data
        assert "student" in data

        # 验证登录成功
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert data["student"] is not None
        assert data["student"]["student_id"] == created_student["student_id"]

    def test_login_with_email_verification(self, client, created_student):
        """测试使用 email 验证的登录"""
        login_data = {
            "student_id": created_student["student_id"],
            "email": created_student["email"]
        }
        response = client.post("/api/v1/students/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"

    def test_login_student_not_found(self, client):
        """测试不存在的 student_id 登录失败"""
        login_data = {
            "student_id": "NONEXISTENT999"
        }
        response = client.post("/api/v1/students/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # 验证登录失败
        assert data["success"] is False
        assert "not found" in data["message"]
        assert data["student"] is None

    def test_login_email_mismatch(self, client, created_student):
        """测试 email 不匹配登录失败"""
        login_data = {
            "student_id": created_student["student_id"],
            "email": "wrong@example.com"
        }
        response = client.post("/api/v1/students/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # 验证登录失败
        assert data["success"] is False
        assert data["message"] == "Email verification failed"
        assert data["student"] is None


# ============================================================================
# Test Class 3: Student List
# ============================================================================

class TestStudentList:
    """测试学生列表端点 GET /api/v1/students"""

    def test_list_default_pagination(self, client, multiple_students):
        """测试默认分页参数（page=1, page_size=20）"""
        # multiple_students 创建了 15 个学生
        response = client.get("/api/v1/students")

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # 验证分页参数
        assert data["page"] == 1
        assert data["page_size"] == 20
        # 验证至少包含我们创建的 15 个学生
        assert data["total"] >= 15
        assert len(data["items"]) >= 15

    def test_list_custom_pagination(self, client, multiple_students):
        """测试自定义分页参数"""
        response = client.get("/api/v1/students?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()

        # 验证分页参数
        assert data["page"] == 1
        assert data["page_size"] == 10
        # 验证返回的数量不超过 page_size
        assert len(data["items"]) <= 10
        # 验证至少有 15 个学生（我们创建的）
        assert data["total"] >= 15
        # 验证至少有 2 页
        assert data["total_pages"] >= 2

    def test_list_second_page(self, client, multiple_students):
        """测试获取第二页数据"""
        response = client.get("/api/v1/students?page=2&page_size=10")

        assert response.status_code == 200
        data = response.json()

        # 验证分页参数
        assert data["page"] == 2
        assert data["page_size"] == 10
        # 验证返回的数量不超过 page_size
        assert len(data["items"]) <= 10
        # 验证至少有 15 个学生
        assert data["total"] >= 15

    def test_list_filter_by_course(self, client, multiple_students):
        """测试按 course_id 过滤"""
        # 测试 CS101 课程（我们创建了 10 个）
        response = client.get("/api/v1/students?course_id=CS101")

        assert response.status_code == 200
        data = response.json()
        # 验证至少有 10 个 CS101 学生
        assert data["total"] >= 10

        # 验证所有返回的学生都是 CS101
        for student in data["items"]:
            assert student["course_id"] == "CS101"

        # 测试 CS102 课程（我们创建了 5 个）
        response = client.get("/api/v1/students?course_id=CS102")

        assert response.status_code == 200
        data = response.json()
        # 验证至少有 5 个 CS102 学生
        assert data["total"] >= 5

        # 验证所有返回的学生都是 CS102
        for student in data["items"]:
            assert student["course_id"] == "CS102"

    def test_list_empty_result(self, client):
        """测试空结果集（或验证响应结构）"""
        response = client.get("/api/v1/students")

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构（不验证具体数据，因为数据库可能有旧数据）
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert data["total"] >= 0

    def test_list_page_size_boundary(self, client, multiple_students):
        """测试分页边界条件"""
        # 测试最小 page_size
        response = client.get("/api/v1/students?page_size=1")

        assert response.status_code == 200
        data = response.json()
        # 验证每页只返回 1 个学生
        assert len(data["items"]) == 1
        assert data["page_size"] == 1
        # 验证至少有 15 页（我们创建了 15 个学生）
        assert data["total_pages"] >= 15

        # 测试最大 page_size
        response = client.get("/api/v1/students?page_size=100")

        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 100
        # 验证至少返回 15 个学生
        assert len(data["items"]) >= 15
        # 验证总数至少 15
        assert data["total"] >= 15

    def test_list_filter_by_course_no_results(self, client, multiple_students):
        """测试按 course_id 过滤但无匹配结果的情况"""
        # 使用一个不会被创建的 course_id，确保过滤后结果为空
        course_id = f"NO_SUCH_COURSE_{int(time.time() * 1000)}"
        response = client.get(f"/api/v1/students?course_id={course_id}")

        assert response.status_code == 200
        data = response.json()

        # 验证分页结构和空结果
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] == 0
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 0

    def test_list_page_out_of_range(self, client, multiple_students):
        """测试 page 超过总页数时返回空结果但分页信息仍然合理"""
        response = client.get("/api/v1/students?page=100&page_size=10")

        assert response.status_code == 200
        data = response.json()

        # 验证分页参数按请求回显
        assert data["page"] == 100
        assert data["page_size"] == 10
        # 由于 page 远超总页数，应无结果
        assert len(data["items"]) == 0
        # total/total_pages 仍反映真实总量
        assert data["total"] >= 15
        assert data["total_pages"] >= 2


# ============================================================================
# Test Class 4: Get Student
# ============================================================================

class TestStudentGet:
    """测试获取单个学生端点 GET /api/v1/students/{student_id}"""

    def test_get_success(self, client, created_student):
        """测试成功获取学生信息"""
        student_id = created_student["student_id"]
        response = client.get(f"/api/v1/students/{student_id}")

        assert response.status_code == 200
        data = response.json()

        # 验证返回的数据与创建时一致
        assert data["student_id"] == created_student["student_id"]
        assert data["name"] == created_student["name"]
        assert data["email"] == created_student["email"]
        assert data["course_id"] == created_student["course_id"]

    def test_get_not_found(self, client):
        """测试获取不存在的学生返回 404"""
        response = client.get("/api/v1/students/NONEXISTENT999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]


# ============================================================================
# Test Class 5: Update Student
# ============================================================================

class TestStudentUpdate:
    """测试更新学生端点 PUT /api/v1/students/{student_id}"""

    def test_update_success(self, client, created_student):
        """测试成功更新学生信息"""
        student_id = created_student["student_id"]
        update_data = {
            "name": "Updated Name",
            "course_id": "CS202"
        }

        response = client.put(f"/api/v1/students/{student_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        # 验证返回的数据已更新
        assert data["name"] == "Updated Name"
        assert data["course_id"] == "CS202"
        # 验证其他字段未改变
        assert data["student_id"] == created_student["student_id"]
        assert data["email"] == created_student["email"]

    def test_update_partial_fields(self, client, created_student):
        """测试部分字段更新"""
        student_id = created_student["student_id"]
        update_data = {
            "name": "Partially Updated Name"
        }

        response = client.put(f"/api/v1/students/{student_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        # 验证仅更新的字段改变
        assert data["name"] == "Partially Updated Name"
        # 验证其他字段未改变
        assert data["email"] == created_student["email"]
        assert data["course_id"] == created_student["course_id"]

    def test_update_email(self, client, created_student, student_factory):
        """测试更新 email"""
        student_id = created_student["student_id"]
        new_email = f"newemail{student_factory()['email']}"
        update_data = {
            "email": new_email
        }

        response = client.put(f"/api/v1/students/{student_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == new_email

    def test_update_duplicate_email(self, client, created_student, student_factory):
        """测试更新为已存在的 email 返回 400 错误"""
        # 创建第二个学生
        second_student_data = student_factory()
        response = client.post("/api/v1/students/register", json=second_student_data)
        assert response.status_code == 201
        second_student = response.json()

        # 尝试将第一个学生的 email 更新为第二个学生的 email
        student_id = created_student["student_id"]
        update_data = {
            "email": second_student["email"]
        }

        response = client.put(f"/api/v1/students/{student_id}", json=update_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already in use" in data["detail"]

    def test_update_invalid_email(self, client, created_student):
        """测试更新为无效的 email 格式返回 422 错误"""
        student_id = created_student["student_id"]
        update_data = {
            "email": "invalid-email-format"
        }

        response = client.put(f"/api/v1/students/{student_id}", json=update_data)

        assert response.status_code == 422

    def test_update_not_found(self, client):
        """测试更新不存在的学生返回 404"""
        update_data = {
            "name": "Updated Name"
        }

        response = client.put("/api/v1/students/NONEXISTENT999", json=update_data)

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]


# ============================================================================
# Test Class 6: Delete Student
# ============================================================================

class TestStudentDelete:
    """测试删除学生端点 DELETE /api/v1/students/{student_id}"""

    def test_delete_success(self, client, created_student):
        """测试成功删除学生"""
        student_id = created_student["student_id"]

        # 删除学生
        response = client.delete(f"/api/v1/students/{student_id}")

        assert response.status_code == 200
        data = response.json()

        # 验证响应
        assert "success" in data
        assert "message" in data
        assert data["success"] is True
        assert student_id in data["message"]

        # 验证再次获取该学生返回 404
        get_response = client.get(f"/api/v1/students/{student_id}")
        assert get_response.status_code == 404

    def test_delete_not_found(self, client):
        """测试删除不存在的学生返回 404"""
        response = client.delete("/api/v1/students/NONEXISTENT999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

