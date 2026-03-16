"""File Upload Router - Handles file upload, parsing, and metadata management."""
import hashlib
import logging
import math
from datetime import datetime
from core.time import utc_now
from typing import Optional, Union

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from schemas.file_upload import (
    FileUploadResponse, FileMetadataResponse, FileListResponse,
    FileContentResponse, FileParseResult, ProgrammingLanguage, FileStatus,
    DocumentParseResponse,
)
from schemas.common import APIResponse
from services.file_parsing_service import file_parsing_service
from services.storage_service import (
    storage_service,
    StorageValidationError,
    StorageOperationError,
)
from utils.crud import crud_code_file, generate_unique_id
from models.code_file import FileStatus as DBFileStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["File Management"])

def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}
TEXT_BASED_EXTENSIONS = {ext.lower() for ext in settings.ALLOWED_EXTENSIONS if ext.lower() not in {".pdf", ".docx"}}


def is_document_extension(extension: str) -> bool:
    return extension.lower() in DOCUMENT_EXTENSIONS


def estimate_line_count(content: str) -> int:
    return len(content.splitlines()) if content else 0


@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_code_file(
    file: UploadFile = File(..., description="File to upload"),
    uploader_id: Optional[str] = Form(None, description="ID of the uploader"),
    assignment_id: Optional[str] = Form(None, description="Associated assignment ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file for parsing and analysis.
    
    - Validates file type and size
    - Validates file size (max 10MB)
    - Sanitizes filename to prevent security issues
    - Stores file with unique name in local or S3 storage
    - Creates metadata record in database
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Read file content
    content = await file.read()
    file_id = generate_unique_id("file")
    try:
        storage_result = await storage_service.save_upload(
            content=content,
            original_filename=file.filename,
            file_id=file_id,
            content_type=file.content_type,
        )
    except StorageValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StorageOperationError as exc:
        logger.error(f"Failed to persist file: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    original_filename = storage_result.original_filename
    extension = storage_result.file_extension
    file_size = len(content)
    file_path = storage_result.file_path

    content_hash = calculate_file_hash(content)
    language = file_parsing_service.detect_language(extension)
    line_count = 0
    if extension in TEXT_BASED_EXTENSIONS:
        text_content = content.decode("utf-8", errors="replace")
        line_count = estimate_line_count(text_content)
    
    # Create database record
    try:
        file_data = {
            "file_id": file_id,
            "original_filename": original_filename,
            "stored_filename": storage_result.stored_filename,
            "file_path": file_path,
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
        try:
            await storage_service.delete_file(file_path)
        except StorageOperationError as cleanup_error:
            logger.warning(f"Failed to clean up stored file after DB error: {cleanup_error}")
        logger.error(f"Failed to create file record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create file record")

    return FileUploadResponse(
        file_id=file_id,
        original_filename=original_filename,
        file_size=file_size,
        file_extension=extension,
        language=language,
        status=FileStatus.PENDING,
        uploaded_at=utc_now(),
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

    try:
        if is_document_extension(file.file_extension):
            processing_path, should_cleanup = await storage_service.materialize_to_local_path(
                file.file_path, file.file_extension
            )
            try:
                content = await file_parsing_service.parse_document_file(
                    str(processing_path), file.file_extension
                )
            finally:
                if should_cleanup and processing_path.exists():
                    processing_path.unlink(missing_ok=True)
        else:
            content = (await storage_service.read_bytes(file.file_path)).decode(
                "utf-8", errors="replace"
            )
    except StorageOperationError as exc:
        logger.error(f"Failed to read file: {exc}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read file content")

    return FileContentResponse(
        file_id=file_id,
        filename=file.original_filename,
        content=content,
        language=ProgrammingLanguage(file.language),
        line_count=file.line_count or estimate_line_count(content)
    )


@router.get("/{file_id}/parse", response_model=Union[FileParseResult, DocumentParseResponse])
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

    try:
        if is_document_extension(file.file_extension):
            processing_path, should_cleanup = await storage_service.materialize_to_local_path(
                file.file_path, file.file_extension
            )
            try:
                content = await file_parsing_service.parse_document_file(
                    str(processing_path), file.file_extension
                )
            finally:
                if should_cleanup and processing_path.exists():
                    processing_path.unlink(missing_ok=True)

            await crud_code_file.update_status(db, file_id, DBFileStatus.PROCESSED.value)
            return DocumentParseResponse(
                file_id=file_id,
                file_extension=file.file_extension,
                content=content,
                line_count=estimate_line_count(content),
                parsed_at=utc_now(),
            )

        content = (await storage_service.read_bytes(file.file_path)).decode("utf-8", errors="replace")
        result = await file_parsing_service.parse_file(
            content=content,
            extension=file.file_extension,
            file_id=file_id,
        )
        await crud_code_file.update_status(db, file_id, DBFileStatus.PROCESSED.value)
        return result
    except StorageOperationError as exc:
        logger.error(f"Failed to read file for parsing: {exc}")
        await crud_code_file.update_status(db, file_id, DBFileStatus.FAILED.value)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
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

    try:
        await storage_service.delete_file(file.file_path)
    except StorageOperationError as exc:
        logger.warning(f"Failed to delete file from storage: {exc}")

    # Delete from database
    await crud_code_file.delete(db, file.id)

    return APIResponse(
        success=True,
        message=f"File '{file_id}' deleted successfully"
    )


