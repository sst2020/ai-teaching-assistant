"""
RabbitMQ Message Publisher
"""
import json
from typing import Any, Optional
import aio_pika
from .connection import get_channel, declare_exchange
from utils.logger import setup_logger

logger = setup_logger(__name__)

DEFAULT_EXCHANGE = "ai_ta_exchange"


async def publish_message(
    routing_key: str,
    message: dict[str, Any],
    exchange_name: str = DEFAULT_EXCHANGE
) -> bool:
    """
    Publish a message to RabbitMQ.

    Args:
        routing_key: Routing key for message delivery
        message: Message payload as dictionary
        exchange_name: Exchange to publish to

    Returns:
        True if message was published successfully
    """
    try:
        channel = await get_channel()
        if not channel:
            logger.warning("RabbitMQ channel not available, message dropped")
            return False

        # Ensure exchange exists
        exchange = await declare_exchange(exchange_name)
        if not exchange:
            return False

        # Create message
        message_body = json.dumps(message, default=str).encode()
        aio_message = aio_pika.Message(
            body=message_body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Persist message
        )

        # Publish
        await exchange.publish(aio_message, routing_key=routing_key)
        logger.debug(f"Published message to {routing_key}")
        return True

    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        return False


async def publish_task(
    task_type: str,
    task_data: dict[str, Any],
    task_id: Optional[str] = None
) -> bool:
    """
    Publish a background task to RabbitMQ.

    Args:
        task_type: Type of task (e.g., 'grading', 'plagiarism_check')
        task_data: Task-specific data
        task_id: Optional task ID

    Returns:
        True if task was published successfully
    """
    message = {
        "task_type": task_type,
        "task_id": task_id,
        "data": task_data
    }

    routing_key = f"tasks.{task_type}"
    return await publish_message(routing_key, message)


async def publish_grading_task(submission_id: str, assignment_id: str) -> bool:
    """Publish an auto-grading task."""
    return await publish_task(
        task_type="grading",
        task_data={
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "auto_grade": True
        }
    )


async def publish_plagiarism_task(submission_id: str) -> bool:
    """Publish a plagiarism check task."""
    return await publish_task(
        task_type="plagiarism_check",
        task_data={
            "submission_id": submission_id
        }
    )


async def publish_batch_grading_task(submission_ids: list[str]) -> bool:
    """Publish a batch grading task."""
    return await publish_task(
        task_type="batch_grading",
        task_data={
            "submission_ids": submission_ids
        }
    )
