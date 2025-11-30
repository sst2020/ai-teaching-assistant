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
from models.code_file import CodeFile, FileStatus, ProgrammingLanguage
from models.analysis_result import AnalysisResult
from models.feedback_template import FeedbackTemplate, TemplateCategory
from models.ai_interaction import AIInteraction, AIProvider, AIInteractionType

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
    "CodeFile",
    "AnalysisResult",
    "FeedbackTemplate",
    "AIInteraction",
    # Enums
    "AssignmentType",
    "SubmissionStatus",
    "GradedBy",
    "QuestionCategory",
    "QuestionStatus",
    "FileStatus",
    "ProgrammingLanguage",
    "TemplateCategory",
    "AIProvider",
    "AIInteractionType",
]

