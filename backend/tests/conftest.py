"""
Pytest configuration and fixtures for AI Teaching Assistant tests.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app


@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    from core.database import get_db
    from tests.test_utils import override_get_db, init_test_db, dispose_test_db
    import asyncio

    # Initialize the test database
    asyncio.run(init_test_db())

    app = create_app(testing=True)

    # Override the get_db dependency to use in-memory database for tests
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up the test database
    asyncio.run(dispose_test_db())


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI."""
    app = create_app(testing=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


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

