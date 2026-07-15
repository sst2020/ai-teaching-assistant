"""
Background Task Processor

Handles async tasks from RabbitMQ message queue.
Integrates with grading and plagiarism services for real processing.
"""
from typing import Any
from utils.logger import setup_logger
from core.messaging.consumer import start_consumer, stop_consumer
from core.database import AsyncSessionLocal

logger = setup_logger(__name__)


async def handle_grading_task(message: dict[str, Any]):
    """Handle auto-grading task using the grading service."""
    data = message.get("data", {})
    submission_id = data.get("submission_id")

    logger.info(f"Processing grading task for submission: {submission_id}")

    try:
        from services.ai_service import ai_service
        from services.code_analysis_service import code_analysis_service
        from utils.crud import crud_submission, crud_grading_result
        from models.grading_result import GradedBy
        from core.time import utc_now

        async with AsyncSessionLocal() as db:
            submission = await crud_submission.get(db, int(submission_id))
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return

            existing = await crud_grading_result.get_by_submission_id(db, submission.id)
            if existing:
                logger.info(f"Grading already exists for submission {submission_id}, skipping")
                return

            code_content = submission.content or ""
            language = submission.language or "python"

            analysis_result = await code_analysis_service.analyze_code(
                code_content, language
            )

            ai_feedback = await ai_service.generate_feedback(
                code=code_content,
                language=language,
                analysis=analysis_result
            )

            grading_data = {
                "submission_id": submission.id,
                "overall_score": analysis_result.get("score", 0),
                "max_score": 100,
                "feedback": {
                    "ai_analysis": analysis_result,
                    "ai_feedback": ai_feedback,
                },
                "graded_by": GradedBy.AI,
                "graded_at": utc_now(),
            }
            await crud_grading_result.create(db, grading_data)
            await db.commit()

            logger.info(f"Grading completed for submission: {submission_id}, score: {analysis_result.get('score', 0)}")

    except Exception as e:
        logger.error(f"Grading failed for submission {submission_id}: {e}")


async def handle_plagiarism_task(message: dict[str, Any]):
    """Handle plagiarism check task using the plagiarism service."""
    data = message.get("data", {})
    submission_id = data.get("submission_id")

    logger.info(f"Processing plagiarism check for submission: {submission_id}")

    try:
        from services.plagiarism_service import plagiarism_service
        from schemas.plagiarism import PlagiarismCheckRequest
        from utils.crud import crud_submission, crud_plagiarism_check
        from core.time import utc_now

        async with AsyncSessionLocal() as db:
            submission = await crud_submission.get(db, int(submission_id))
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return

            request = PlagiarismCheckRequest(
                submission_id=submission.id,
                file_paths=[submission.file_path] if submission.file_path else [],
                code_contents=[submission.content] if submission.content else [],
                languages=[submission.language or "python"],
            )

            result = await plagiarism_service.check_plagiarism(request)

            plagiarism_data = {
                "submission_id": submission.id,
                "similarity_score": result.overall_similarity,
                "matches": result.matches,
                "checked_at": utc_now(),
            }
            await crud_plagiarism_check.create(db, plagiarism_data)
            await db.commit()

            logger.info(
                f"Plagiarism check completed for submission: {submission_id}, "
                f"similarity: {result.overall_similarity:.2%}"
            )

    except Exception as e:
        logger.error(f"Plagiarism check failed for submission {submission_id}: {e}")


async def handle_batch_grading_task(message: dict[str, Any]):
    """Handle batch grading task for multiple submissions."""
    data = message.get("data", {})
    submission_ids = data.get("submission_ids", [])

    logger.info(f"Processing batch grading for {len(submission_ids)} submissions")

    success_count = 0
    fail_count = 0

    for sid in submission_ids:
        try:
            await handle_grading_task({"data": {"submission_id": sid}})
            success_count += 1
        except Exception as e:
            logger.error(f"Batch grading failed for submission {sid}: {e}")
            fail_count += 1

    logger.info(f"Batch grading completed: {success_count} succeeded, {fail_count} failed")


task_handlers = {
    "grading": handle_grading_task,
    "plagiarism_check": handle_plagiarism_task,
    "batch_grading": handle_batch_grading_task,
}


async def handle_task_message(message: dict[str, Any]):
    """Route task messages to appropriate handler."""
    task_type = message.get("task_type")
    handler = task_handlers.get(task_type)

    if handler:
        await handler(message)
    else:
        logger.warning(f"Unknown task type: {task_type}")


async def start_task_consumer():
    """Start the task consumer."""
    await start_consumer(
        queue_name="task_queue",
        handler=handle_task_message,
        routing_keys=["tasks.grading", "tasks.plagiarism_check", "tasks.batch_grading"]
    )


async def stop_task_consumer():
    """Stop the task consumer."""
    await stop_consumer("task_queue")
