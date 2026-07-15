"""
RabbitMQ Messaging Module

Provides async message queue functionality for background task processing.
"""

from .connection import get_connection, close_connection
from .publisher import publish_message, publish_task
from .consumer import start_consumer, stop_consumer

__all__ = [
    "get_connection",
    "close_connection",
    "publish_message",
    "publish_task",
    "start_consumer",
    "stop_consumer",
]
