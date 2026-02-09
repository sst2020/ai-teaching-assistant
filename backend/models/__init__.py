"""
Database Models Package

This package contains all SQLAlchemy ORM models for the AI Teaching Assistant.
"""
from models.base import TimestampMixin
from models.user import User
from models.refresh_token import RefreshToken
from models.token_blacklist import TokenBlacklist
from models.auth_log import AuthLog
from models.student import Student
from models.teacher import Teacher
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
from models.knowledge_base import (
    KnowledgeBaseEntry,
    KnowledgeBaseCategory as KBCategory,
    DifficultyLevel,
)
from models.qa_log import QALog, TriageResult, QALogStatus

__all__ = [
    # Base
    "TimestampMixin",
    # Authentication Models
    "User",
    "RefreshToken",
    "TokenBlacklist",
    "AuthLog",
    # Business Models
    "Student",
    "Teacher",
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
    "KnowledgeBaseEntry",
    "QALog",
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
    "KBCategory",
    "DifficultyLevel",
    "TriageResult",
    "QALogStatus",
]
