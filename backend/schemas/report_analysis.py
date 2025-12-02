"""Schemas for project report intelligent analysis system.

Defines data models for:
- Report structure parsing
- Quality evaluation
- Logic and innovation analysis
- Language and formatting checks
- Comprehensive report analysis request/response
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ReportFileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"


class ReportLanguage(str, Enum):
    ZH = "zh"
    EN = "en"
    MIXED = "mixed"


class ReferenceFormat(str, Enum):
    APA = "apa"
    MLA = "mla"
    GBT7714 = "gbt7714"
    UNKNOWN = "unknown"


class SectionType(str, Enum):
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHOD = "method"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    APPENDIX = "appendix"
    OTHER = "other"


class LogicIssueType(str, Enum):
    MISSING_EVIDENCE = "missing_evidence"
    LOGICAL_GAP = "logical_gap"
    WEAK_CONCLUSION = "weak_conclusion"
    REDUNDANT_CONTENT = "redundant_content"


class FormattingIssueType(str, Enum):
    TITLE_INCONSISTENT = "title_inconsistent"
    FIGURE_TABLE_NUMBERING = "figure_table_numbering"
    REFERENCE_FORMAT = "reference_format"
    PAGINATION = "pagination"
    FONT_STYLE = "font_style"


class ReportSection(BaseModel):
    """A logical section of the project report."""

    id: str = Field(..., description="Section ID")
    title: str = Field("", description="Section title")
    level: int = Field(1, ge=1, le=6, description="Heading level (1-6)")
    section_type: SectionType = Field(SectionType.OTHER, description="Detected section type")
    order_index: int = Field(..., ge=0, description="Order index in document")
    text: str = Field("", description="Plain text content of section")
    children: List["ReportSection"] = Field(default_factory=list, description="Subsections")


class ReferenceEntry(BaseModel):
    """Single reference item in the references section."""

    raw_text: str = Field(..., description="Original reference text")
    detected_format: ReferenceFormat = Field(ReferenceFormat.UNKNOWN, description="Detected reference style")
    is_valid: bool = Field(False, description="Whether the reference matches the expected format")
    problems: List[str] = Field(default_factory=list, description="Detected issues in this reference entry")


class ReportParseResult(BaseModel):
    """Unified result of parsing a project report file."""

    file_id: Optional[str] = Field(None, description="Optional file identifier")
    file_name: str = Field(..., description="Original file name")
    file_type: ReportFileType = Field(..., description="Report file type")
    language: ReportLanguage = Field(ReportLanguage.MIXED, description="Detected report language")
    sections: List[ReportSection] = Field(default_factory=list, description="Parsed section tree (flattened list)")
    references: List[ReferenceEntry] = Field(default_factory=list, description="Parsed references list")
    raw_text: str = Field(..., description="Full plain text of the report")


class ChapterLengthStats(BaseModel):
    """Length statistics for a single top-level chapter."""

    section_id: str = Field(..., description="Reference to ReportSection.id")
    title: str = Field(..., description="Chapter title")
    word_count: int = Field(..., ge=0, description="Word count of this chapter")
    proportion: float = Field(..., ge=0.0, le=1.0, description="Proportion of total words")
    evaluation: str = Field(..., description="Qualitative evaluation (too_short/normal/too_long)")


class FigureTableStats(BaseModel):
    """Statistics for figures and tables in the report."""

    figure_count: int = Field(0, ge=0, description="Number of figures")
    table_count: int = Field(0, ge=0, description="Number of tables")
    evaluation: str = Field("", description="Qualitative evaluation of figure/table usage")


class ReferenceStats(BaseModel):
    """Statistics for references section."""

    total_count: int = Field(0, ge=0, description="Total number of reference entries")
    valid_count: int = Field(0, ge=0, description="Number of entries that match expected format")
    expected_min_count: int = Field(0, ge=0, description="Expected minimum references for this assignment")
    format_compliance_ratio: float = Field(0.0, ge=0.0, le=1.0, description="Ratio of properly formatted references")
    evaluation: str = Field("", description="Overall evaluation of reference section")


class ReportQualityMetrics(BaseModel):
    """Quality metrics focusing on completeness and structure."""

    total_word_count: int = Field(..., ge=0, description="Total word count of the report")
    word_count_evaluation: str = Field(..., description="Word count evaluation: too_short/normal/too_long")

    required_sections_present: Dict[SectionType, bool] = Field(
        default_factory=dict,
        description="Whether each required section is present",
    )

    chapter_length_stats: List[ChapterLengthStats] = Field(
        default_factory=list, description="Per-chapter length statistics"
    )
    figure_table_stats: FigureTableStats = Field(
        default_factory=FigureTableStats, description="Figure/table statistics"
    )
    reference_stats: ReferenceStats = Field(
        default_factory=ReferenceStats, description="Reference statistics"
    )
    overall_completeness_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall completeness score (0-100)"
    )


class LogicIssue(BaseModel):
    """Single logic issue detected in the report."""

    issue_type: LogicIssueType = Field(..., description="Type of logic issue")
    section_id: Optional[str] = Field(None, description="Related section ID, if applicable")
    paragraph_index: Optional[int] = Field(
        None, ge=0, description="Paragraph index inside the section (0-based)"
    )
    description: str = Field(..., description="Description of the issue")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for this issue")


class LogicAnalysisResult(BaseModel):
    """Analysis result about logic and argumentation structure."""

    section_order_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Score for section ordering (0-100)"
    )
    coherence_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Score for paragraph coherence (0-100)"
    )
    argumentation_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Score for argumentation completeness (0-100)"
    )
    issues: List[LogicIssue] = Field(default_factory=list, description="Detected logic issues")
    summary: str = Field("", description="Natural language summary of logic analysis")


class InnovationPoint(BaseModel):
    """Single potential innovation point in the report."""

    section_id: Optional[str] = Field(None, description="Related section ID")
    highlight_text: str = Field(..., description="Highlighted text that shows innovation")
    reason: str = Field(..., description="Why this is considered innovative")


class InnovationAnalysisResult(BaseModel):
    """Analysis result about novelty and innovation."""

    novelty_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Overall novelty score (0-100)"
    )
    difference_summary: str = Field(
        "", description="Summary of differences compared to existing reports"
    )
    innovation_points: List[InnovationPoint] = Field(
        default_factory=list, description="List of detected innovation points"
    )


class LanguageQualityMetrics(BaseModel):
    """Metrics about language quality of the report."""

    average_sentence_length: float = Field(
        0.0, ge=0.0, description="Average sentence length (words)"
    )
    long_sentence_ratio: float = Field(
        0.0, ge=0.0, le=1.0, description="Ratio of long sentences"
    )
    vocabulary_richness: float = Field(
        0.0, ge=0.0, le=1.0, description="Type-token ratio or similar metric"
    )
    grammar_issue_count: int = Field(
        0, ge=0, description="Number of detected grammar issues"
    )
    academic_tone_score: float = Field(
        0.0, ge=0.0, le=100.0, description="How academic/formal the writing style is (0-100)"
    )
    readability_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Readability score (e.g., Flesch or custom 0-100)"
    )


class FormattingIssue(BaseModel):
    """Single formatting issue detected in the report."""

    issue_type: FormattingIssueType = Field(..., description="Formatting issue type")
    location: Optional[str] = Field(
        None, description="Human-readable location description (e.g. section/line)"
    )
    description: str = Field(..., description="Description of the formatting problem")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for this issue")


class FormattingCheckResult(BaseModel):
    """Result of formatting and style checks."""

    reference_style: ReferenceFormat = Field(
        ReferenceFormat.UNKNOWN, description="Detected or expected reference style"
    )
    title_consistency_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Consistency score for headings (0-100)"
    )
    figure_table_consistency_score: float = Field(
        0.0, ge=0.0, le=100.0, description="Consistency score for figure/table numbering and references (0-100)"
    )
    issues: List[FormattingIssue] = Field(
        default_factory=list, description="List of detected formatting issues"
    )


class ImprovementSuggestion(BaseModel):
    """High-level improvement suggestion for the report."""

    category: str = Field(..., description="Category: content/logic/language/formatting")
    section_id: Optional[str] = Field(None, description="Related section ID, if any")
    summary: str = Field(..., description="Short title/summary of the suggestion")
    details: str = Field(..., description="Detailed explanation of the suggestion")


class ReportAnalysisRequest(BaseModel):
    """Request body for project report analysis.

    Note: when used with file upload endpoints, most fields will be inferred
    from the uploaded file. This schema is mainly for direct text-based analysis.
    """

    file_name: str = Field(..., description="Original report file name")
    file_type: ReportFileType = Field(..., description="Report file type")
    content: str = Field(..., description="Plain text content of the report")
    language: Optional[ReportLanguage] = Field(
        None, description="Optional language hint for analysis"
    )
    reference_style_preference: Optional[ReferenceFormat] = Field(
        None, description="Preferred reference style for formatting checks"
    )


class ReportAnalysisResponse(BaseModel):
    """Full analysis result for a project report."""

    report_id: str = Field(..., description="Unique report analysis ID")
    file_name: str = Field(..., description="Original report file name")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

    parsed: ReportParseResult = Field(..., description="Parsed report structure and text")
    quality: ReportQualityMetrics = Field(..., description="Completeness and quality metrics")
    logic: LogicAnalysisResult = Field(..., description="Logic and argumentation analysis")
    innovation: InnovationAnalysisResult = Field(..., description="Innovation and novelty analysis")
    language_quality: LanguageQualityMetrics = Field(..., description="Language quality metrics")
    formatting: FormattingCheckResult = Field(..., description="Formatting and style check result")
    suggestions: List[ImprovementSuggestion] = Field(
        default_factory=list, description="High-level improvement suggestions"
    )

    overall_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall quality score (0-100)"
    )
    summary: str = Field("", description="Natural language summary of the analysis")


__all__ = [
    "ReportFileType",
    "ReportLanguage",
    "ReferenceFormat",
    "SectionType",
    "LogicIssueType",
    "FormattingIssueType",
    "ReportSection",
    "ReferenceEntry",
    "ReportParseResult",
    "ChapterLengthStats",
    "FigureTableStats",
    "ReferenceStats",
    "ReportQualityMetrics",
    "LogicIssue",
    "LogicAnalysisResult",
    "InnovationPoint",
    "InnovationAnalysisResult",
    "LanguageQualityMetrics",
    "FormattingIssue",
    "FormattingCheckResult",
    "ImprovementSuggestion",
    "ReportAnalysisRequest",
    "ReportAnalysisResponse",
]
