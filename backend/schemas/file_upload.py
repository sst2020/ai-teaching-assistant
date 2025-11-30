"""
Schemas for File Upload and Parsing API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FileStatus(str, Enum):
    """Status of the uploaded file."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class ProgrammingLanguage(str, Enum):
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


# ============================================
# Code Structure Extraction Schemas
# ============================================

class ImportInfo(BaseModel):
    """Information about an import statement."""
    module: str = Field(..., description="Module being imported")
    names: List[str] = Field(default_factory=list, description="Names imported from module")
    line: int = Field(..., description="Line number of import")
    is_from_import: bool = Field(False, description="Whether it's a 'from x import y' style")


class FunctionInfo(BaseModel):
    """Information about a function definition."""
    name: str = Field(..., description="Function name")
    line_start: int = Field(..., description="Starting line number")
    line_end: Optional[int] = Field(None, description="Ending line number")
    parameters: List[str] = Field(default_factory=list, description="Parameter names")
    return_type: Optional[str] = Field(None, description="Return type annotation")
    docstring: Optional[str] = Field(None, description="Function docstring")
    is_async: bool = Field(False, description="Whether function is async")
    decorators: List[str] = Field(default_factory=list, description="Decorator names")


class ClassInfo(BaseModel):
    """Information about a class definition."""
    name: str = Field(..., description="Class name")
    line_start: int = Field(..., description="Starting line number")
    line_end: Optional[int] = Field(None, description="Ending line number")
    base_classes: List[str] = Field(default_factory=list, description="Base class names")
    methods: List[FunctionInfo] = Field(default_factory=list, description="Class methods")
    docstring: Optional[str] = Field(None, description="Class docstring")
    decorators: List[str] = Field(default_factory=list, description="Decorator names")


class CodeStructure(BaseModel):
    """Extracted code structure from a file."""
    imports: List[ImportInfo] = Field(default_factory=list, description="Import statements")
    functions: List[FunctionInfo] = Field(default_factory=list, description="Top-level functions")
    classes: List[ClassInfo] = Field(default_factory=list, description="Class definitions")
    global_variables: List[str] = Field(default_factory=list, description="Global variable names")


# ============================================
# Static Analysis Schemas
# ============================================

class BasicMetrics(BaseModel):
    """Basic code metrics."""
    total_lines: int = Field(..., description="Total number of lines")
    code_lines: int = Field(..., description="Lines of actual code")
    comment_lines: int = Field(..., description="Lines of comments")
    blank_lines: int = Field(..., description="Blank lines")
    function_count: int = Field(0, description="Number of functions")
    class_count: int = Field(0, description="Number of classes")
    import_count: int = Field(0, description="Number of imports")


class SyntaxValidation(BaseModel):
    """Syntax validation result."""
    is_valid: bool = Field(..., description="Whether syntax is valid")
    errors: List[str] = Field(default_factory=list, description="Syntax error messages")
    error_line: Optional[int] = Field(None, description="Line number of first error")


class FileParseResult(BaseModel):
    """Complete file parsing result."""
    file_id: str = Field(..., description="Unique file identifier")
    language: ProgrammingLanguage = Field(..., description="Detected programming language")
    structure: CodeStructure = Field(..., description="Extracted code structure")
    metrics: BasicMetrics = Field(..., description="Basic code metrics")
    syntax_validation: SyntaxValidation = Field(..., description="Syntax validation result")
    parsed_at: datetime = Field(..., description="Timestamp of parsing")


# ============================================
# File Upload Request/Response Schemas
# ============================================

class FileUploadResponse(BaseModel):
    """Response after successful file upload."""
    file_id: str = Field(..., description="Unique file identifier")
    original_filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_extension: str = Field(..., description="File extension")
    language: ProgrammingLanguage = Field(..., description="Detected programming language")
    status: FileStatus = Field(..., description="Processing status")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    message: str = Field("File uploaded successfully", description="Status message")


class FileMetadataResponse(BaseModel):
    """File metadata response."""
    file_id: str = Field(..., description="Unique file identifier")
    original_filename: str = Field(..., description="Original filename")
    stored_filename: str = Field(..., description="Stored filename")
    file_size: int = Field(..., description="File size in bytes")
    file_extension: str = Field(..., description="File extension")
    language: ProgrammingLanguage = Field(..., description="Programming language")
    status: FileStatus = Field(..., description="Processing status")
    uploader_id: Optional[str] = Field(None, description="Uploader ID")
    assignment_id: Optional[str] = Field(None, description="Associated assignment ID")
    line_count: Optional[int] = Field(None, description="Number of lines")
    content_hash: Optional[str] = Field(None, description="Content hash")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Paginated list of files."""
    items: List[FileMetadataResponse] = Field(..., description="List of files")
    total: int = Field(..., description="Total number of files")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class FileContentResponse(BaseModel):
    """Response with file content."""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="File content")
    language: ProgrammingLanguage = Field(..., description="Programming language")
    line_count: int = Field(..., description="Number of lines")

