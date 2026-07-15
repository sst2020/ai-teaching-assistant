"""
RabbitMQ Connection Management
"""
import aio_pika
import os
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.Channel] = None


async def get_connection() -> Optional[aio_pika.RobustConnection]:
    """Get or create RabbitMQ connection."""
    global _connection

    if _connection is None or _connection.is_closed:
        try:
            rabbitmq_url = os.getenv("RABBITMQ_URL", "")
            # Skip connection if RABBITMQ_URL is empty or not set
            if not rabbitmq_url:
                return None
            _connection = await aio_pika.connect_robust(rabbitmq_url)
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return None

    return _connection


async def get_channel() -> Optional[aio_pika.Channel]:
    """Get or create RabbitMQ channel."""
    global _channel

    if _channel is None or _channel.is_closed:
        connection = await get_connection()
        if connection:
            _channel = await connection.channel()
            logger.info("Created RabbitMQ channel")

    return _channel


async def close_connection():
    """Close RabbitMQ connection."""
    global _connection, _channel

    if _channel and not _channel.is_closed:
        await _channel.close()
        _channel = None
        logger.info("Closed RabbitMQ channel")

    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None
        logger.info("Closed RabbitMQ connection")


async def declare_queue(queue_name: str) -> Optional[aio_pika.Queue]:
    """Declare a queue if it doesn't exist."""
    channel = await get_channel()
    if not channel:
        return None

    queue = await channel.declare_queue(
        queue_name,
        durable=True,  # Queue survives broker restart
        auto_delete=False
    )
    return queue


async def declare_exchange(exchange_name: str) -> Optional[aio_pika.Exchange]:
    """Declare a topic exchange."""
    channel = await get_channel()
    if not channel:
        return None

    exchange = await channel.declare_exchange(
        exchange_name,
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )
    return exchange
