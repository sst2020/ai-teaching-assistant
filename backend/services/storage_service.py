"""Storage service for local and S3-backed file uploads."""
import asyncio
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
import boto3

from core.config import settings


class StorageValidationError(ValueError):
    """Raised when upload input is invalid."""


class StorageOperationError(RuntimeError):
    """Raised when storage operations fail."""


@dataclass
class StorageResult:
    original_filename: str
    file_extension: str
    stored_filename: str
    file_path: str


class StorageService:
    """Handle file storage for local disk and S3 backends."""

    def get_backend(self) -> str:
        return (settings.UPLOAD_STORAGE_BACKEND or "local").lower()

    def sanitize_filename(self, filename: str) -> str:
        filename = os.path.basename(filename or "")
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        return f"{name}{ext}"

    def get_file_extension(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return ext.lower()

    def validate_extension(self, extension: str) -> None:
        allowed_extensions = {ext.lower() for ext in settings.ALLOWED_EXTENSIONS}
        if extension.lower() not in allowed_extensions:
            raise StorageValidationError(
                f"File type '{extension}' not allowed. Allowed types: {sorted(allowed_extensions)}"
            )

    def validate_size(self, size: int) -> None:
        if size == 0:
            raise StorageValidationError("Empty files are not allowed")
        if size > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise StorageValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )

    def generate_stored_filename(self, file_id: str, extension: str) -> str:
        return f"{file_id}{extension.lower()}"

    async def save_upload(
        self,
        content: bytes,
        original_filename: str,
        file_id: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        sanitized_filename = self.sanitize_filename(original_filename)
        extension = self.get_file_extension(sanitized_filename)
        self.validate_extension(extension)
        self.validate_size(len(content))

        stored_filename = self.generate_stored_filename(file_id, extension)
        if self.get_backend() == "s3":
            file_path = await asyncio.to_thread(self._save_s3, content, stored_filename, content_type)
        else:
            file_path = await self._save_local(content, stored_filename)

        return StorageResult(
            original_filename=sanitized_filename,
            file_extension=extension,
            stored_filename=stored_filename,
            file_path=file_path,
        )

    async def _save_local(self, content: bytes, stored_filename: str) -> str:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / stored_filename
        try:
            async with aiofiles.open(file_path, "wb") as handle:
                await handle.write(content)
        except Exception as exc:  # pragma: no cover - defensive
            raise StorageOperationError("Failed to save file to local storage") from exc
        return str(file_path)

    def _save_s3(self, content: bytes, stored_filename: str, content_type: Optional[str]) -> str:
        bucket = self._require_s3_bucket()
        key = self._build_s3_key(stored_filename)
        try:
            self._get_s3_client().put_object(
                Bucket=bucket,
                Key=key,
                Body=content,
                ContentType=content_type or "application/octet-stream",
            )
        except Exception as exc:  # pragma: no cover - network/provider errors
            raise StorageOperationError("Failed to upload file to S3 storage") from exc
        return f"s3://{bucket}/{key}"

    async def read_bytes(self, file_path: str) -> bytes:
        if file_path.startswith("s3://"):
            return await asyncio.to_thread(self._read_s3_bytes, file_path)
        try:
            async with aiofiles.open(file_path, "rb") as handle:
                return await handle.read()
        except FileNotFoundError as exc:
            raise StorageOperationError("Stored file not found") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise StorageOperationError("Failed to read stored file") from exc

    async def delete_file(self, file_path: str) -> None:
        if file_path.startswith("s3://"):
            await asyncio.to_thread(self._delete_s3_file, file_path)
            return

        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
            except Exception as exc:  # pragma: no cover - defensive
                raise StorageOperationError("Failed to delete local file") from exc

    async def materialize_to_local_path(self, file_path: str, extension: str) -> Tuple[Path, bool]:
        if not file_path.startswith("s3://"):
            return Path(file_path), False

        content = await self.read_bytes(file_path)
        suffix = extension or ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content)
            return Path(temp_file.name), True

    def _build_s3_key(self, stored_filename: str) -> str:
        prefix = (settings.UPLOAD_S3_KEY_PREFIX or "uploads").strip("/")
        return f"{prefix}/{stored_filename}" if prefix else stored_filename

    def _get_s3_client(self):
        return boto3.client(
            "s3",
            region_name=settings.UPLOAD_S3_REGION,
            endpoint_url=settings.UPLOAD_S3_ENDPOINT_URL,
            aws_access_key_id=settings.UPLOAD_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.UPLOAD_S3_SECRET_ACCESS_KEY,
        )

    def _require_s3_bucket(self) -> str:
        if not settings.UPLOAD_S3_BUCKET:
            raise StorageOperationError("UPLOAD_S3_BUCKET must be configured when UPLOAD_STORAGE_BACKEND=s3")
        return settings.UPLOAD_S3_BUCKET

    def _parse_s3_uri(self, file_path: str) -> Tuple[str, str]:
        without_scheme = file_path.replace("s3://", "", 1)
        bucket, _, key = without_scheme.partition("/")
        if not bucket or not key:
            raise StorageOperationError("Invalid S3 file path")
        return bucket, key

    def _read_s3_bytes(self, file_path: str) -> bytes:
        bucket, key = self._parse_s3_uri(file_path)
        try:
            response = self._get_s3_client().get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as exc:  # pragma: no cover - network/provider errors
            raise StorageOperationError("Failed to read file from S3 storage") from exc

    def _delete_s3_file(self, file_path: str) -> None:
        bucket, key = self._parse_s3_uri(file_path)
        try:
            self._get_s3_client().delete_object(Bucket=bucket, Key=key)
        except Exception as exc:  # pragma: no cover - network/provider errors
            raise StorageOperationError("Failed to delete file from S3 storage") from exc


storage_service = StorageService()