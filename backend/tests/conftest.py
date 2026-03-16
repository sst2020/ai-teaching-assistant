"""
Pytest configuration and fixtures for AI Teaching Assistant tests.
"""
import os
import shutil
import uuid
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Keep unit tests DB-independent by default.
# To run against MySQL, set TEST_DATABASE_URL externally.
if "TEST_DATABASE_URL" in os.environ:
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
else:
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app


@pytest.fixture
def tmp_path():
    """Workspace-local temporary directory to avoid system temp permission issues."""
    base_dir = Path(__file__).parent.parent.parent / ".codex-test-tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"pytest-upload-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    (path / "uploads").mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    from core.database import get_db
    from tests.test_utils import (
        override_get_db,
        init_test_db,
        dispose_test_db,
        clear_test_db_state,
        is_sqlite_test_database,
        reset_test_db_sync,
    )
    import asyncio

    if is_sqlite_test_database():
        asyncio.run(init_test_db())
    else:
        clear_test_db_state()
        reset_test_db_sync()

    app = create_app(testing=True)

    # Override the get_db dependency to use in-memory database for tests
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    if is_sqlite_test_database():
        asyncio.run(dispose_test_db())
    else:
        asyncio.run(dispose_test_db())


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI."""
    from core.database import get_db
    from tests.test_utils import override_get_db, init_test_db, dispose_test_db, reset_test_db_sync

    reset_test_db_sync()
    await init_test_db()
    app = create_app(testing=True)
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await dispose_test_db()


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''


@pytest.fixture
def sample_code_with_issues():
    """Sample Python code with style issues."""
    return '''
def bad_function(a,b,c,d,e,f,g,h):
    x=1
    y=2
    if x==1:
        if y==2:
            if a==1:
                if b==2:
                    return True
    return False
'''


@pytest.fixture
def sample_question():
    """Sample Q&A question."""
    return {
        "student_id": "test_student_001",
        "course_id": "CS101",
        "question": "What is recursion and how does it work?"
    }


@pytest.fixture
def sample_assignment():
    """Sample assignment submission."""
    return {
        "student_id": "test_student_001",
        "assignment_id": "hw_001",
        "assignment_type": "code",
        "content": "def hello():\n    print('Hello World')\n\nhello()"
    }
