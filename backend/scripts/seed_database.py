"""
Database Seeding Script

This script populates the database with sample data for development and testing.
Run from the backend directory: python -m scripts.seed_database
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, async_engine, Base
from models import Student, Assignment, Submission, Rubric
from models.assignment import AssignmentType
from models.submission import SubmissionStatus


# Sample data
SAMPLE_STUDENTS = [
    {"student_id": "STU001", "name": "Alice Johnson", "email": "alice@university.edu", "course_id": "CS101"},
    {"student_id": "STU002", "name": "Bob Smith", "email": "bob@university.edu", "course_id": "CS101"},
    {"student_id": "STU003", "name": "Carol Williams", "email": "carol@university.edu", "course_id": "CS101"},
    {"student_id": "STU004", "name": "David Brown", "email": "david@university.edu", "course_id": "CS102"},
    {"student_id": "STU005", "name": "Eve Davis", "email": "eve@university.edu", "course_id": "CS102"},
]

SAMPLE_ASSIGNMENTS = [
    {
        "assignment_id": "ASN001",
        "title": "Python Basics",
        "description": "Write a Python program that demonstrates basic syntax and data types.",
        "assignment_type": AssignmentType.CODE,
        "course_id": "CS101",
        "max_score": 100.0,
        "due_date": datetime.now(timezone.utc) + timedelta(days=7),
    },
    {
        "assignment_id": "ASN002",
        "title": "Data Structures Essay",
        "description": "Write an essay comparing different data structures and their use cases.",
        "assignment_type": AssignmentType.ESSAY,
        "course_id": "CS101",
        "max_score": 50.0,
        "due_date": datetime.now(timezone.utc) + timedelta(days=14),
    },
    {
        "assignment_id": "ASN003",
        "title": "Algorithm Quiz",
        "description": "Multiple choice quiz on sorting and searching algorithms.",
        "assignment_type": AssignmentType.QUIZ,
        "course_id": "CS102",
        "max_score": 25.0,
        "due_date": datetime.now(timezone.utc) + timedelta(days=3),
    },
]

SAMPLE_SUBMISSIONS = [
    {
        "submission_id": "SUB001",
        "student_idx": 0,  # Alice
        "assignment_idx": 0,  # Python Basics
        "content": 'def hello():\n    print("Hello, World!")\n\nhello()',
        "status": SubmissionStatus.GRADED,
    },
    {
        "submission_id": "SUB002",
        "student_idx": 1,  # Bob
        "assignment_idx": 0,  # Python Basics
        "content": 'x = 10\ny = 20\nprint(f"Sum: {x + y}")',
        "status": SubmissionStatus.PENDING,
    },
    {
        "submission_id": "SUB003",
        "student_idx": 0,  # Alice
        "assignment_idx": 1,  # Essay
        "content": "Data structures are fundamental to computer science...",
        "status": SubmissionStatus.PENDING,
    },
]


async def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")
    
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        result = await session.execute(select(func.count()).select_from(Student))
        count = result.scalar()
        
        if count > 0:
            print("⚠️  Database already contains data. Skipping seeding.")
            print("   To reseed, delete the database file first.")
            return
        
        # Create students
        print("\n📚 Creating students...")
        students = []
        for data in SAMPLE_STUDENTS:
            student = Student(**data)
            session.add(student)
            students.append(student)
            print(f"   ✓ {data['name']} ({data['student_id']})")
        await session.flush()
        
        # Create assignments
        print("\n📝 Creating assignments...")
        assignments = []
        for data in SAMPLE_ASSIGNMENTS:
            assignment = Assignment(**data)
            session.add(assignment)
            assignments.append(assignment)
            print(f"   ✓ {data['title']} ({data['assignment_id']})")
        await session.flush()
        
        # Create submissions
        print("\n📤 Creating submissions...")
        for data in SAMPLE_SUBMISSIONS:
            submission = Submission(
                submission_id=data["submission_id"],
                student_id=students[data["student_idx"]].id,
                assignment_id=assignments[data["assignment_idx"]].id,
                content=data["content"],
                status=data["status"],
                submitted_at=datetime.now(timezone.utc),
            )
            session.add(submission)
            print(f"   ✓ {data['submission_id']}")
        
        await session.commit()
        print("\n✅ Database seeding completed successfully!")
        print(f"   - {len(students)} students")
        print(f"   - {len(assignments)} assignments")
        print(f"   - {len(SAMPLE_SUBMISSIONS)} submissions")


if __name__ == "__main__":
    asyncio.run(seed_database())

