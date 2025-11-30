"""
CodeFile Model - Represents uploaded code files and their metadata.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Integer, Text, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class FileStatus(str, PyEnum):
    """Status of the uploaded file."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class ProgrammingLanguage(str, PyEnum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    C = "c"
    CPP = "cpp"
    JSX = "jsx"
    TSX = "tsx"
    UNKNOWN = "unknown"


class CodeFile(Base, TimestampMixin):
    """
    CodeFile model representing uploaded code files.
    
    Attributes:
        id: Primary key
        file_id: Unique file identifier (UUID-based)
        original_filename: Original name of the uploaded file
        stored_filename: Name used for storage (sanitized, unique)
        file_path: Full path to the stored file
        file_size: Size of the file in bytes
        file_extension: File extension (e.g., .py, .java)
        mime_type: MIME type of the file
        language: Detected programming language
        status: Processing status of the file
        uploader_id: ID of the student who uploaded the file
        assignment_id: Optional associated assignment ID
        content_hash: SHA-256 hash of file content for deduplication
        line_count: Number of lines in the file
        analysis_result: JSON string containing analysis results
    """
    __tablename__ = "code_files"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ProgrammingLanguage.UNKNOWN.value,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=FileStatus.PENDING.value,
    )
    uploader_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    line_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    analysis_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="code_file", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_code_files_uploader_assignment", "uploader_id", "assignment_id"),
        Index("ix_code_files_language_status", "language", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<CodeFile(id={self.id}, file_id='{self.file_id}', filename='{self.original_filename}')>"

