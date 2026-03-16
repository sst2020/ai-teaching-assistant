"""
Tests for CRUD utility classes in backend/utils/crud.py.

使用 pytest-asyncio 直接测试 CRUD 层的数据库操作，
覆盖 CRUDBase、CRUDStudent、CRUDAssignment、CRUDSubmission、
CRUDTeacher、generate_unique_id 等。
"""
import pytest
import pytest_asyncio
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import (
    init_test_db,
    dispose_test_db,
    reset_test_db_sync,
    clear_test_db_state,
)
from utils.crud import (
    CRUDBase,
    CRUDStudent,
    CRUDAssignment,
    CRUDSubmission,
    CRUDTeacher,
    crud_student,
    crud_assignment,
    crud_submission,
    crud_teacher,
    generate_unique_id,
)
from models.student import Student
from models.assignment import Assignment
from models.submission import Submission, SubmissionStatus
from models.teacher import Teacher


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """每个测试前初始化内存数据库，测试后销毁"""
    clear_test_db_state()
    reset_test_db_sync()
    await init_test_db()
    yield
    await dispose_test_db()


@pytest_asyncio.fixture
async def db_session():
    """获取一个异步数据库会话"""
    from tests.test_utils import _test_sessionmaker
    async with _test_sessionmaker() as session:
        yield session
        await session.commit()


# ============================================================================
# Test: generate_unique_id
# ============================================================================

class TestGenerateUniqueId:
    """测试 generate_unique_id 工具函数"""

    def test_without_prefix(self):
        uid = generate_unique_id()
        assert uid  # 非空
        assert "_" in uid  # 包含时间戳和 uuid 部分

    def test_with_prefix(self):
        uid = generate_unique_id("STU")
        assert uid.startswith("STU_")

    def test_uniqueness(self):
        ids = {generate_unique_id("T") for _ in range(50)}
        assert len(ids) == 50  # 50 个 ID 全部唯一


# ============================================================================
# Test: CRUDStudent
# ============================================================================

class TestCRUDStudent:
    """测试 CRUDStudent 操作"""

    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session):
        """测试创建学生并通过 ID 获取"""
        student = await crud_student.create(db_session, {
            "student_id": "CRUD_STU_001",
            "name": "Test Student",
            "email": "crud_stu@test.com",
            "course_id": "CS101",
        })
        assert student.id is not None
        assert student.student_id == "CRUD_STU_001"

        fetched = await crud_student.get(db_session, student.id)
        assert fetched is not None
        assert fetched.student_id == "CRUD_STU_001"

    @pytest.mark.asyncio
    async def test_get_by_student_id(self, db_session):
        """测试通过 student_id 查找"""
        await crud_student.create(db_session, {
            "student_id": "CRUD_STU_002",
            "name": "Student 2",
            "email": "crud_stu2@test.com",
            "course_id": "CS101",
        })
        found = await crud_student.get_by_student_id(db_session, "CRUD_STU_002")
        assert found is not None
        assert found.name == "Student 2"

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session):
        """测试通过 email 查找"""
        await crud_student.create(db_session, {
            "student_id": "CRUD_STU_003",
            "name": "Student 3",
            "email": "unique_email@test.com",
            "course_id": "CS101",
        })
        found = await crud_student.get_by_email(db_session, "unique_email@test.com")
        assert found is not None
        assert found.student_id == "CRUD_STU_003"

    @pytest.mark.asyncio
    async def test_get_by_course(self, db_session):
        """测试按课程查找学生"""
        for i in range(3):
            await crud_student.create(db_session, {
                "student_id": f"COURSE_STU_{i}",
                "name": f"Course Student {i}",
                "email": f"course_stu_{i}@test.com",
                "course_id": "MATH201",
            })
        students = await crud_student.get_by_course(db_session, "MATH201")
        assert len(students) == 3

    @pytest.mark.asyncio
    async def test_get_multi_with_filters(self, db_session):
        """测试带过滤条件的批量查询"""
        await crud_student.create(db_session, {
            "student_id": "FILTER_STU_1",
            "name": "Filter 1",
            "email": "filter1@test.com",
            "course_id": "PHY101",
        })
        await crud_student.create(db_session, {
            "student_id": "FILTER_STU_2",
            "name": "Filter 2",
            "email": "filter2@test.com",
            "course_id": "PHY101",
        })
        results = await crud_student.get_multi(
            db_session, filters={"course_id": "PHY101"}
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_count(self, db_session):
        """测试计数"""
        for i in range(4):
            await crud_student.create(db_session, {
                "student_id": f"COUNT_STU_{i}",
                "name": f"Count {i}",
                "email": f"count_{i}@test.com",
                "course_id": "COUNT_COURSE",
            })
        total = await crud_student.count(
            db_session, filters={"course_id": "COUNT_COURSE"}
        )
        assert total == 4

    @pytest.mark.asyncio
    async def test_update(self, db_session):
        """测试更新学生信息"""
        student = await crud_student.create(db_session, {
            "student_id": "UPDATE_STU",
            "name": "Before Update",
            "email": "update@test.com",
            "course_id": "CS101",
        })
        updated = await crud_student.update(
            db_session, student, {"name": "After Update"}
        )
        assert updated.name == "After Update"

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """测试删除学生"""
        student = await crud_student.create(db_session, {
            "student_id": "DELETE_STU",
            "name": "To Delete",
            "email": "delete@test.com",
            "course_id": "CS101",
        })
        result = await crud_student.delete(db_session, student.id)
        assert result is True
        gone = await crud_student.get(db_session, student.id)
        assert gone is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db_session):
        """测试删除不存在的记录"""
        result = await crud_student.delete(db_session, 99999)
        assert result is False


# ============================================================================
# Test: CRUDAssignment
# ============================================================================

class TestCRUDAssignment:
    """测试 CRUDAssignment 操作"""

    @pytest.mark.asyncio
    async def test_create_and_get_by_assignment_id(self, db_session):
        """测试创建作业并通过 assignment_id 获取"""
        asn = await crud_assignment.create(db_session, {
            "assignment_id": "CRUD_ASN_001",
            "title": "Test Assignment",
            "description": "A test",
            "assignment_type": "code",
            "course_id": "CS101",
            "max_score": 100.0,
        })
        assert asn.id is not None
        found = await crud_assignment.get_by_assignment_id(db_session, "CRUD_ASN_001")
        assert found is not None
        assert found.title == "Test Assignment"

    @pytest.mark.asyncio
    async def test_get_by_course(self, db_session):
        """测试按课程查找作业"""
        for i in range(3):
            await crud_assignment.create(db_session, {
                "assignment_id": f"COURSE_ASN_{i}",
                "title": f"Course Assignment {i}",
                "description": "test",
                "assignment_type": "code",
                "course_id": "MATH301",
                "max_score": 100.0,
            })
        assignments = await crud_assignment.get_by_course(db_session, "MATH301")
        assert len(assignments) == 3

    @pytest.mark.asyncio
    async def test_count_by_course(self, db_session):
        """测试按课程计数"""
        for i in range(2):
            await crud_assignment.create(db_session, {
                "assignment_id": f"CNT_ASN_{i}",
                "title": f"Count Assignment {i}",
                "description": "test",
                "assignment_type": "code",
                "course_id": "CNT_COURSE",
                "max_score": 50.0,
            })
        count = await crud_assignment.count_by_course(db_session, "CNT_COURSE")
        assert count == 2


# ============================================================================
# Test: CRUDSubmission
# ============================================================================

class TestCRUDSubmission:
    """测试 CRUDSubmission 操作"""

    @pytest_asyncio.fixture
    async def student_and_assignment(self, db_session):
        """创建测试用的学生和作业"""
        student = await crud_student.create(db_session, {
            "student_id": "SUB_STU",
            "name": "Sub Student",
            "email": "sub_stu@test.com",
            "course_id": "CS101",
        })
        assignment = await crud_assignment.create(db_session, {
            "assignment_id": "SUB_ASN",
            "title": "Sub Assignment",
            "description": "test",
            "assignment_type": "code",
            "course_id": "CS101",
            "max_score": 100.0,
        })
        return student, assignment

    @pytest.mark.asyncio
    async def test_create_and_get_by_submission_id(self, db_session, student_and_assignment):
        """测试创建提交并通过 submission_id 获取"""
        student, assignment = student_and_assignment
        sub = await crud_submission.create(db_session, {
            "submission_id": "CRUD_SUB_001",
            "student_id": student.id,
            "assignment_id": assignment.id,
            "content": "print('hello')",
            "submitted_at": datetime.now(timezone.utc),
            "status": SubmissionStatus.PENDING,
        })
        assert sub.id is not None
        found = await crud_submission.get_by_submission_id(db_session, "CRUD_SUB_001")
        assert found is not None
        assert found.content == "print('hello')"

    @pytest.mark.asyncio
    async def test_get_by_student(self, db_session, student_and_assignment):
        """测试按学生查找提交"""
        student, assignment = student_and_assignment
        for i in range(3):
            await crud_submission.create(db_session, {
                "submission_id": f"STU_SUB_{i}",
                "student_id": student.id,
                "assignment_id": assignment.id,
                "content": f"code {i}",
                "submitted_at": datetime.now(timezone.utc),
                "status": SubmissionStatus.PENDING,
            })
        subs = await crud_submission.get_by_student(db_session, student.id)
        assert len(subs) == 3

    @pytest.mark.asyncio
    async def test_get_by_assignment(self, db_session, student_and_assignment):
        """测试按作业查找提交"""
        student, assignment = student_and_assignment
        for i in range(2):
            await crud_submission.create(db_session, {
                "submission_id": f"ASN_SUB_{i}",
                "student_id": student.id,
                "assignment_id": assignment.id,
                "content": f"code {i}",
                "submitted_at": datetime.now(timezone.utc),
                "status": SubmissionStatus.PENDING,
            })
        subs = await crud_submission.get_by_assignment(db_session, assignment.id)
        assert len(subs) == 2

    @pytest.mark.asyncio
    async def test_count_by_student(self, db_session, student_and_assignment):
        """测试按学生计数"""
        student, assignment = student_and_assignment
        for i in range(4):
            await crud_submission.create(db_session, {
                "submission_id": f"CNT_SUB_{i}",
                "student_id": student.id,
                "assignment_id": assignment.id,
                "content": f"code {i}",
                "submitted_at": datetime.now(timezone.utc),
                "status": SubmissionStatus.PENDING,
            })
        count = await crud_submission.count_by_student(db_session, student.id)
        assert count == 4

    @pytest.mark.asyncio
    async def test_update_status(self, db_session, student_and_assignment):
        """测试更新提交状态"""
        student, assignment = student_and_assignment
        sub = await crud_submission.create(db_session, {
            "submission_id": "STATUS_SUB",
            "student_id": student.id,
            "assignment_id": assignment.id,
            "content": "code",
            "submitted_at": datetime.now(timezone.utc),
            "status": SubmissionStatus.PENDING,
        })
        updated = await crud_submission.update_status(
            db_session, "STATUS_SUB", SubmissionStatus.GRADED
        )
        assert updated is not None
        assert updated.status == SubmissionStatus.GRADED

    @pytest.mark.asyncio
    async def test_update_status_nonexistent(self, db_session):
        """测试更新不存在的提交状态"""
        result = await crud_submission.update_status(
            db_session, "NONEXISTENT", SubmissionStatus.GRADED
        )
        assert result is None


# ============================================================================
# Test: CRUDTeacher
# ============================================================================

class TestCRUDTeacher:
    """测试 CRUDTeacher 操作"""

    @pytest.mark.asyncio
    async def test_create_and_get_by_teacher_id(self, db_session):
        """测试创建教师并通过 teacher_id 获取"""
        teacher = await crud_teacher.create(db_session, {
            "teacher_id": "CRUD_TCH_001",
            "name": "Test Teacher",
            "email": "crud_tch@test.com",
            "department": "CS",
        })
        assert teacher.id is not None
        found = await crud_teacher.get_by_teacher_id(db_session, "CRUD_TCH_001")
        assert found is not None
        assert found.name == "Test Teacher"

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session):
        """测试通过 email 查找教师"""
        await crud_teacher.create(db_session, {
            "teacher_id": "CRUD_TCH_002",
            "name": "Teacher 2",
            "email": "tch_email@test.com",
            "department": "MATH",
        })
        found = await crud_teacher.get_by_email(db_session, "tch_email@test.com")
        assert found is not None
        assert found.teacher_id == "CRUD_TCH_002"

    @pytest.mark.asyncio
    async def test_get_by_department(self, db_session):
        """测试按部门查找教师"""
        for i in range(3):
            await crud_teacher.create(db_session, {
                "teacher_id": f"DEPT_TCH_{i}",
                "name": f"Dept Teacher {i}",
                "email": f"dept_tch_{i}@test.com",
                "department": "PHYSICS",
            })
        teachers = await crud_teacher.get_by_department(db_session, "PHYSICS")
        assert len(teachers) == 3

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db_session):
        """测试查找不存在的教师"""
        found = await crud_teacher.get_by_teacher_id(db_session, "NONEXISTENT")
        assert found is None
