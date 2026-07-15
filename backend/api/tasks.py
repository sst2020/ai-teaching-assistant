"""
Task Queue API Endpoints

Provides API for async task management and status checking.
"""
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.deps import get_current_user
from core.messaging.publisher import (
    publish_grading_task,
    publish_plagiarism_task,
    publish_batch_grading_task,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# In-memory task status store (replace with Redis in production)
task_status: dict[str, dict[str, Any]] = {}


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    task_type: str | None = None
    result: dict | None = None
    error: str | None = None


class BatchGradingRequest(BaseModel):
    submission_ids: list[str]


@router.post("/tasks/grade/{submission_id}", response_model=TaskResponse)
async def submit_grading_task(
    submission_id: str,
    assignment_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    """Submit an auto-grading task to the queue."""
    task_id = str(uuid.uuid4())

    success = await publish_grading_task(submission_id, assignment_id or "")

    if success:
        task_status[task_id] = {
            "status": "pending",
            "task_type": "grading",
            "submission_id": submission_id,
        }
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Grading task submitted successfully",
        )
    else:
        raise HTTPException(status_code=503, detail="Failed to queue grading task")


@router.post("/tasks/plagiarism/{submission_id}", response_model=TaskResponse)
async def submit_plagiarism_task(
    submission_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Submit a plagiarism check task to the queue."""
    task_id = str(uuid.uuid4())

    success = await publish_plagiarism_task(submission_id)

    if success:
        task_status[task_id] = {
            "status": "pending",
            "task_type": "plagiarism_check",
            "submission_id": submission_id,
        }
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Plagiarism check task submitted successfully",
        )
    else:
        raise HTTPException(status_code=503, detail="Failed to queue plagiarism task")


@router.post("/tasks/batch-grade", response_model=TaskResponse)
async def submit_batch_grading(
    request: BatchGradingRequest,
    current_user: dict = Depends(get_current_user),
):
    """Submit a batch grading task to the queue."""
    task_id = str(uuid.uuid4())

    success = await publish_batch_grading_task(request.submission_ids)

    if success:
        task_status[task_id] = {
            "status": "pending",
            "task_type": "batch_grading",
            "submission_count": len(request.submission_ids),
        }
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message=f"Batch grading task submitted for {len(request.submission_ids)} submissions",
        )
    else:
        raise HTTPException(status_code=503, detail="Failed to queue batch grading task")


@router.get("/tasks/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the status of a background task."""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task_id,
        **task_status[task_id]
    )
