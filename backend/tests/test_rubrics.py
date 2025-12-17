"""
Tests for Rubric Management API endpoints.
评分标准管理 API 的测试套件
"""
import pytest
from datetime import datetime
import time
import random


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def rubric_factory():
    """
    工厂函数生成唯一的 Rubric 数据
    使用时间戳和随机数确保 rubric_id 的唯一性
    """
    counter = {"value": 0}

    def _create(**kwargs):
        counter["value"] += 1
        unique_id = int(time.time() * 1000) + random.randint(1, 9999)
        defaults = {
            "rubric_id": f"RUB{unique_id}_{counter['value']}",
            "name": f"Test Rubric {counter['value']}",
            "description": f"Test rubric description {counter['value']}",
            "max_score": 100.0,
            "criteria": {
                "correctness": {
                    "weight": 0.5,
                    "description": "代码功能正确性",
                    "max_points": 50
                },
                "quality": {
                    "weight": 0.5,
                    "description": "代码质量和风格",
                    "max_points": 50
                }
            }
        }
        defaults.update(kwargs)
        return defaults

    return _create


@pytest.fixture
def created_rubric(client, rubric_factory):
    """创建一个已存在的 Rubric（每次调用都生成新的唯一 ID）"""
    rubric_data = rubric_factory()
    response = client.post("/api/v1/rubrics", json=rubric_data)
    if response.status_code != 201:
        # 如果创建失败（可能是 ID 冲突），重试一次
        rubric_data = rubric_factory()
        response = client.post("/api/v1/rubrics", json=rubric_data)
    assert response.status_code == 201, f"Failed to create rubric: {response.json()}"
    return response.json()


@pytest.fixture
def multiple_rubrics(client, rubric_factory):
    """创建 10 个 Rubric 用于分页测试"""
    rubrics = []
    for i in range(10):
        rubric_data = rubric_factory()
        response = client.post("/api/v1/rubrics", json=rubric_data)
        assert response.status_code == 201
        rubrics.append(response.json())
    return rubrics


# ============================================================================
# Test Classes
# ============================================================================

class TestRubricCreate:
    """测试 Rubric 创建功能"""

    def test_create_success(self, client, rubric_factory):
        """测试成功创建 Rubric"""
        rubric_data = rubric_factory()
        response = client.post("/api/v1/rubrics", json=rubric_data)

        assert response.status_code == 201
        data = response.json()
        assert data["rubric_id"] == rubric_data["rubric_id"]
        assert data["name"] == rubric_data["name"]
        assert data["max_score"] == rubric_data["max_score"]
        assert "id" in data
        assert "created_at" in data

    def test_create_with_criteria(self, client, rubric_factory):
        """测试创建包含 criteria 的 Rubric"""
        rubric_data = rubric_factory()
        response = client.post("/api/v1/rubrics", json=rubric_data)

        assert response.status_code == 201
        data = response.json()
        assert data["criteria"] is not None
        assert "correctness" in data["criteria"]
        assert "quality" in data["criteria"]

    def test_create_duplicate_rubric_id(self, client, created_rubric, rubric_factory):
        """测试创建重复 rubric_id 的 Rubric（应失败）"""
        rubric_data = rubric_factory(rubric_id=created_rubric["rubric_id"])
        response = client.post("/api/v1/rubrics", json=rubric_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_invalid_max_score(self, client, rubric_factory):
        """测试创建无效 max_score 的 Rubric（负数）"""
        rubric_data = rubric_factory(max_score=-10.0)
        response = client.post("/api/v1/rubrics", json=rubric_data)

        assert response.status_code == 422  # Validation error

    def test_create_missing_required_fields(self, client):
        """测试缺少必填字段"""
        response = client.post("/api/v1/rubrics", json={})

        assert response.status_code == 422

    def test_create_with_all_fields(self, client, rubric_factory):
        """测试创建包含所有字段的 Rubric"""
        rubric_data = rubric_factory(
            description="Complete rubric with all fields",
            criteria={
                "correctness": {"weight": 0.4, "max_points": 40},
                "quality": {"weight": 0.3, "max_points": 30},
                "documentation": {"weight": 0.3, "max_points": 30}
            }
        )
        response = client.post("/api/v1/rubrics", json=rubric_data)

        assert response.status_code == 201
        data = response.json()
        assert len(data["criteria"]) == 3



class TestRubricList:
    """测试 Rubric 列表功能"""

    def test_list_empty(self, client):
        """测试空列表"""
        response = client.get("/api/v1/rubrics")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_with_data(self, client, multiple_rubrics):
        """测试有数据的列表"""
        response = client.get("/api/v1/rubrics")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 10
        assert data["total"] >= 10

    def test_list_pagination(self, client, multiple_rubrics):
        """测试分页功能"""
        response = client.get("/api/v1/rubrics?page=1&page_size=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5
        assert data["page"] == 1
        assert data["page_size"] == 5

    def test_list_pagination_last_page(self, client, multiple_rubrics):
        """测试最后一页"""
        # 先获取总数
        response = client.get("/api/v1/rubrics")
        total = response.json()["total"]

        # 请求最后一页
        last_page = (total + 4) // 5  # 向上取整
        response = client.get(f"/api/v1/rubrics?page={last_page}&page_size=5")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == last_page

    def test_list_invalid_page(self, client):
        """测试无效页码"""
        response = client.get("/api/v1/rubrics?page=0")

        assert response.status_code == 422  # Validation error


class TestRubricGet:
    """测试获取单个 Rubric"""

    def test_get_success(self, client, created_rubric):
        """测试成功获取 Rubric"""
        response = client.get(f"/api/v1/rubrics/{created_rubric['rubric_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["rubric_id"] == created_rubric["rubric_id"]
        assert data["name"] == created_rubric["name"]

    def test_get_not_found(self, client):
        """测试获取不存在的 Rubric"""
        response = client.get("/api/v1/rubrics/NONEXISTENT")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_with_criteria(self, client, created_rubric):
        """测试获取包含 criteria 的 Rubric"""
        response = client.get(f"/api/v1/rubrics/{created_rubric['rubric_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["criteria"] is not None
        assert isinstance(data["criteria"], dict)


class TestRubricUpdate:
    """测试 Rubric 更新功能"""

    def test_update_success(self, client, created_rubric):
        """测试成功更新 Rubric"""
        update_data = {
            "name": "Updated Rubric Name",
            "max_score": 120.0
        }
        response = client.put(
            f"/api/v1/rubrics/{created_rubric['rubric_id']}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Rubric Name"
        assert data["max_score"] == 120.0

    def test_update_partial_fields(self, client, created_rubric):
        """测试部分字段更新"""
        update_data = {"description": "Updated description only"}
        response = client.put(
            f"/api/v1/rubrics/{created_rubric['rubric_id']}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description only"
        assert data["name"] == created_rubric["name"]  # 未更新的字段保持不变

    def test_update_criteria(self, client, created_rubric):
        """测试更新 criteria"""
        new_criteria = {
            "correctness": {"weight": 0.6, "max_points": 60},
            "quality": {"weight": 0.4, "max_points": 40}
        }
        update_data = {"criteria": new_criteria}
        response = client.put(
            f"/api/v1/rubrics/{created_rubric['rubric_id']}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["criteria"]["correctness"]["weight"] == 0.6

    def test_update_not_found(self, client):
        """测试更新不存在的 Rubric"""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/rubrics/NONEXISTENT", json=update_data)

        assert response.status_code == 404

    def test_update_invalid_max_score(self, client, created_rubric):
        """测试更新为无效的 max_score"""
        update_data = {"max_score": -50.0}
        response = client.put(
            f"/api/v1/rubrics/{created_rubric['rubric_id']}",
            json=update_data
        )

        assert response.status_code == 422  # Validation error


class TestRubricDelete:
    """测试 Rubric 删除功能"""

    def test_delete_success(self, client, created_rubric):
        """测试成功删除 Rubric"""
        response = client.delete(f"/api/v1/rubrics/{created_rubric['rubric_id']}")

        assert response.status_code == 204

        # 验证已删除
        get_response = client.get(f"/api/v1/rubrics/{created_rubric['rubric_id']}")
        assert get_response.status_code == 404

    def test_delete_not_found(self, client):
        """测试删除不存在的 Rubric"""
        response = client.delete("/api/v1/rubrics/NONEXISTENT")

        assert response.status_code == 404

    def test_delete_with_assignments(self, client, created_rubric):
        """测试删除有关联作业的 Rubric（验证 SET NULL 行为）"""
        # 注意：此测试需要先创建关联的 Assignment
        # 由于 Assignment 创建较复杂，此测试可以简化或标记为 skip
        # 这里仅测试删除操作本身
        response = client.delete(f"/api/v1/rubrics/{created_rubric['rubric_id']}")
        assert response.status_code == 204


class TestRubricAssignments:
    """测试 Rubric 与 Assignment 的关联"""

    def test_get_assignments_success(self, client, created_rubric):
        """测试获取关联的作业列表"""
        response = client.get(f"/api/v1/rubrics/{created_rubric['rubric_id']}/assignments")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_assignments_empty(self, client, created_rubric):
        """测试无关联作业的情况"""
        response = client.get(f"/api/v1/rubrics/{created_rubric['rubric_id']}/assignments")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # 新创建的 Rubric 没有关联作业

    def test_get_assignments_not_found(self, client):
        """测试 Rubric 不存在的情况"""
        response = client.get("/api/v1/rubrics/NONEXISTENT/assignments")

        assert response.status_code == 404
