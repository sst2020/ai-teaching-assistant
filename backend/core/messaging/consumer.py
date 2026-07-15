"""
RabbitMQ Message Consumer
"""
import json
import asyncio
from typing import Callable, Any, Optional
import aio_pika
from aio_pika import IncomingMessage
from .connection import get_connection, declare_queue, declare_exchange
from utils.logger import setup_logger

logger = setup_logger(__name__)

DEFAULT_EXCHANGE = "ai_ta_exchange"
_consumers: dict[str, asyncio.Task] = {}


async def process_message(
    message: IncomingMessage,
    handler: Callable[[dict[str, Any]], Any]
):
    """Process an incoming message."""
    async with message.process():
        try:
            body = json.loads(message.body.decode())
            logger.info(f"Processing message: {body.get('task_type', 'unknown')}")
            await handler(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Message will be requeued due to exception


async def start_consumer(
    queue_name: str,
    handler: Callable[[dict[str, Any]], Any],
    routing_keys: Optional[list[str]] = None,
    exchange_name: str = DEFAULT_EXCHANGE
):
    """
    Start consuming messages from a queue.

    Args:
        queue_name: Queue to consume from
        handler: Callback function to process messages
        routing_keys: List of routing keys to bind to
        exchange_name: Exchange name
    """
    try:
        connection = await get_connection()
        if not connection:
            logger.error("Cannot start consumer: RabbitMQ not connected")
            return

        # Create channel for this consumer
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)  # Fair dispatch

        # Declare queue and exchange
        exchange = await declare_exchange(exchange_name)
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            auto_delete=False
        )

        # Bind queue to exchange with routing keys
        if routing_keys:
            for key in routing_keys:
                await queue.bind(exchange, routing_key=key)
        else:
            await queue.bind(exchange, routing_key=f"tasks.{queue_name}")

        logger.info(f"Started consumer for queue: {queue_name}")

        # Start consuming
        async def consume():
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await process_message(message, handler)

        # Store consumer task
        task = asyncio.create_task(consume())
        _consumers[queue_name] = task

    except Exception as e:
        logger.error(f"Failed to start consumer {queue_name}: {e}")


async def stop_consumer(queue_name: str):
    """Stop a running consumer."""
    if queue_name in _consumers:
        _consumers[queue_name].cancel()
        try:
            await _consumers[queue_name]
        except asyncio.CancelledError:
            pass
        del _consumers[queue_name]
        logger.info(f"Stopped consumer for queue: {queue_name}")


async def stop_all_consumers():
    """Stop all running consumers."""
    for queue_name in list(_consumers.keys()):
        await stop_consumer(queue_name)
