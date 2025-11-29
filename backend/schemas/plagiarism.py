"""
Schemas for Plagiarism Detection Feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class SimilarityLevel(str, Enum):
    """Levels of similarity detection."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MatchType(str, Enum):
    """Types of code matching."""
    EXACT = "exact"
    STRUCTURAL = "structural"  # AST structure match
    TOKEN_SEQUENCE = "token_sequence"  # Token pattern match
    RENAMED = "renamed"  # Same structure, different variable names
    PARTIAL = "partial"


class CodeMatch(BaseModel):
    """A matched code segment between two submissions."""
    match_type: MatchType = Field(..., description="Type of match detected")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    code_snippet_1: str = Field("", description="Code snippet from first submission")
    code_snippet_2: str = Field("", description="Code snippet from second submission")
    line_range_1: tuple = Field((1, 1), description="Line range in first submission")
    line_range_2: tuple = Field((1, 1), description="Line range in second submission")
    explanation: str = Field("", description="Explanation of the match")


class SubmissionComparison(BaseModel):
    """Comparison result between two submissions."""
    submission_id_1: str = Field(..., description="First submission ID")
    submission_id_2: str = Field(..., description="Second submission ID")
    student_id_1: str = Field(..., description="First student ID")
    student_id_2: str = Field(..., description="Second student ID")
    similarity_score: float = Field(..., ge=0, le=1, description="Overall similarity (0-1)")
    matches: List[CodeMatch] = Field(default_factory=list, description="List of matching segments")
    analysis_notes: str = Field("", description="Analysis notes")


class PlagiarismCheckRequest(BaseModel):
    """Request for plagiarism check."""
    submission_id: str = Field(..., description="Submission ID")
    student_id: str = Field(..., description="Student ID of submission to check")
    course_id: str = Field(..., description="Course ID")
    code: str = Field(..., description="Code to check for plagiarism")
    compare_with_history: bool = Field(True, description="Compare with historical submissions")
    similarity_threshold: float = Field(0.7, ge=0, le=1, description="Threshold for flagging (0-1)")


class PlagiarismReport(BaseModel):
    """Comprehensive plagiarism detection report."""
    report_id: str = Field(..., description="Unique report identifier")
    submission_id: str = Field(..., description="Submission ID checked")
    checked_at: datetime = Field(..., description="Timestamp of check")

    # Overall Results
    overall_similarity: float = Field(..., ge=0, le=1, description="Highest similarity found (0-1)")
    similarity_level: SimilarityLevel = Field(..., description="Overall similarity level")
    is_flagged: bool = Field(..., description="Whether submission is flagged")

    # Detailed Comparisons
    comparisons: List[SubmissionComparison] = Field(default_factory=list)

    # Summary
    summary: str = Field("", description="Human-readable summary")


class SubmissionRecord(BaseModel):
    """Record of a submission for plagiarism database."""
    submission_id: str = Field(..., description="Unique submission ID")
    student_id: str = Field(..., description="Student ID")
    assignment_id: str = Field(..., description="Assignment ID")
    code: str = Field(..., description="Submitted code")
    code_hash: str = Field(..., description="Hash of normalized code")
    ast_fingerprint: str = Field(..., description="AST-based fingerprint")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    token_sequence: List[str] = Field(default_factory=list, description="Tokenized code sequence")


class BatchPlagiarismRequest(BaseModel):
    """Request for batch plagiarism check."""
    assignment_id: str = Field(..., description="Assignment ID")
    submissions: List[PlagiarismCheckRequest] = Field(..., description="List of submissions to check")
    cross_compare: bool = Field(True, description="Compare submissions against each other")


class BatchPlagiarismReport(BaseModel):
    """Batch plagiarism check report."""
    report_id: str = Field(..., description="Unique report ID")
    course_id: str = Field(..., description="Course ID")
    checked_at: datetime = Field(..., description="Timestamp of check")
    total_submissions: int = Field(..., description="Total submissions checked")
    flagged_pairs: int = Field(..., description="Number of flagged pairs")
    comparisons: List[SubmissionComparison] = Field(default_factory=list)
    summary: str = Field("", description="Summary of batch check")

