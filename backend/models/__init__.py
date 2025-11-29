"""
Database Models Package

This package contains all SQLAlchemy ORM models for the AI Teaching Assistant.
"""
from models.base import TimestampMixin
from models.student import Student
from models.rubric import Rubric
from models.assignment import Assignment, AssignmentType
from models.submission import Submission, SubmissionStatus
from models.grading_result import GradingResult, GradedBy
from models.question import Question, QuestionCategory, QuestionStatus
from models.answer import Answer
from models.plagiarism_check import PlagiarismCheck

__all__ = [
    # Base
    "TimestampMixin",
    # Models
    "Student",
    "Rubric",
    "Assignment",
    "Submission",
    "GradingResult",
    "Question",
    "Answer",
    "PlagiarismCheck",
    # Enums
    "AssignmentType",
    "SubmissionStatus",
    "GradedBy",
    "QuestionCategory",
    "QuestionStatus",
]

