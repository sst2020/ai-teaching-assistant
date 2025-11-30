"""
File Upload Router - Handles code file upload, parsing, and metadata management
"""
import os
import re
import uuid
import hashlib
import logging
import math
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from schemas.file_upload import (
    FileUploadResponse, FileMetadataResponse, FileListResponse,
    FileContentResponse, FileParseResult, ProgrammingLanguage, FileStatus
)
from schemas.common import APIResponse
from services.file_parsing_service import file_parsing_service
from utils.crud import crud_code_file, generate_unique_id
from models.code_file import FileStatus as DBFileStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["File Management"])

# Allowed code file extensions
ALLOWED_CODE_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.
    
    - Removes path separators
    - Removes special characters
    - Limits length
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    
    # Limit length (keep extension)
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    
    return f"{name}{ext}"


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def validate_file_extension(extension: str) -> bool:
    """Check if file extension is allowed."""
    return extension.lower() in ALLOWED_CODE_EXTENSIONS


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


async def ensure_upload_directory() -> Path:
    """Ensure upload directory exists and return path."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_code_file(
    file: UploadFile = File(..., description="Code file to upload"),
    uploader_id: Optional[str] = Form(None, description="ID of the uploader"),
    assignment_id: Optional[str] = Form(None, description="Associated assignment ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a code file for parsing and analysis.
    
    - Validates file type (only code files allowed)
    - Validates file size (max 10MB)
    - Sanitizes filename to prevent security issues
    - Stores file with unique name
    - Creates metadata record in database
    - Triggers file parsing
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Sanitize and validate filename
    original_filename = sanitize_filename(file.filename)
    extension = get_file_extension(original_filename)
    
    if not validate_file_extension(extension):
        raise HTTPException(
            status_code=400,
            detail=f"File type '{extension}' not allowed. Allowed types: {sorted(ALLOWED_CODE_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty files are not allowed")
    
    # Generate unique file ID and stored filename
    file_id = generate_unique_id("file")
    stored_filename = f"{file_id}{extension}"
    
    # Ensure upload directory exists
    upload_dir = await ensure_upload_directory()
    file_path = upload_dir / stored_filename
    
    # Calculate content hash
    content_hash = calculate_file_hash(content)
    
    # Detect language
    language = file_parsing_service.detect_language(extension)
    
    # Count lines
    try:
        text_content = content.decode('utf-8', errors='replace')
        line_count = len(text_content.split('\n'))
    except Exception:
        text_content = ""
        line_count = 0
    
    # Save file to disk
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Create database record
    try:
        file_data = {
            "file_id": file_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_extension": extension,
            "mime_type": file.content_type,
            "language": language.value,
            "status": DBFileStatus.PENDING.value,
            "uploader_id": uploader_id,
            "assignment_id": assignment_id,
            "content_hash": content_hash,
            "line_count": line_count,
        }
        
        db_file = await crud_code_file.create(db, file_data)
    except Exception as e:
        # Clean up file if database insert fails
        if file_path.exists():
            file_path.unlink()
        logger.error(f"Failed to create file record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create file record")

    return FileUploadResponse(
        file_id=file_id,
        original_filename=original_filename,
        file_size=file_size,
        file_extension=extension,
        language=language,
        status=FileStatus.PENDING,
        uploaded_at=datetime.utcnow(),
        message="File uploaded successfully"
    )


@router.get("", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    uploader_id: Optional[str] = Query(None, description="Filter by uploader ID"),
    assignment_id: Optional[str] = Query(None, description="Filter by assignment ID"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    db: AsyncSession = Depends(get_db)
):
    """
    List uploaded files with pagination and filtering.

    - Supports filtering by uploader, assignment, and language
    - Returns paginated results
    """
    skip = (page - 1) * page_size
    filters = {}
    if uploader_id:
        filters["uploader_id"] = uploader_id
    if assignment_id:
        filters["assignment_id"] = assignment_id
    if language:
        filters["language"] = language

    files = await crud_code_file.get_multi(db, skip=skip, limit=page_size, filters=filters if filters else None)
    total = await crud_code_file.count(db, filters=filters if filters else None)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return FileListResponse(
        items=[FileMetadataResponse.model_validate(f) for f in files],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{file_id}", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get file metadata by file ID.

    - Returns file metadata if found
    - Returns 404 if file not found
    """
    file = await crud_code_file.get_by_file_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File with ID '{file_id}' not found")
    return FileMetadataResponse.model_validate(file)


@router.get("/{file_id}/content", response_model=FileContentResponse)
async def get_file_content(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get file content by file ID.

    - Returns file content as text
    - Returns 404 if file not found
    """
    file = await crud_code_file.get_by_file_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File with ID '{file_id}' not found")

    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File content not found on disk")

    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = await f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read file content")

    return FileContentResponse(
        file_id=file_id,
        filename=file.original_filename,
        content=content,
        language=ProgrammingLanguage(file.language),
        line_count=file.line_count or len(content.split('\n'))
    )


@router.get("/{file_id}/parse", response_model=FileParseResult)
async def parse_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Parse a file and extract code structure.

    - Extracts imports, functions, classes
    - Calculates basic metrics
    - Validates syntax
    """
    file = await crud_code_file.get_by_file_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File with ID '{file_id}' not found")

    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File content not found on disk")

    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = await f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read file content")

    # Parse the file
    try:
        result = await file_parsing_service.parse_file(
            content=content,
            extension=file.file_extension,
            file_id=file_id
        )

        # Update file status to processed
        await crud_code_file.update_status(db, file_id, DBFileStatus.PROCESSED.value)

        return result
    except Exception as e:
        logger.error(f"Failed to parse file: {e}")
        await crud_code_file.update_status(db, file_id, DBFileStatus.FAILED.value)
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")


@router.delete("/{file_id}", response_model=APIResponse)
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a file and its metadata.

    - Removes file from disk
    - Removes metadata from database
    """
    file = await crud_code_file.get_by_file_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File with ID '{file_id}' not found")

    # Delete file from disk
    file_path = Path(file.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file from disk: {e}")

    # Delete from database
    await crud_code_file.delete(db, file.id)

    return APIResponse(
        success=True,
        message=f"File '{file_id}' deleted successfully"
    )

