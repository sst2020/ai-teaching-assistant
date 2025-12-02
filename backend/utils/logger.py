"""
Enhanced logging utilities for AI Teaching Assistant Backend
Provides structured logging with colors, performance tracking, and request correlation
"""

import logging
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
from pathlib import Path

# Context variable for request tracking
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add request ID to log record if available
        request_id = request_id_context.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = 'N/A'
        
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname_colored = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class PerformanceLogger:
    """Logger for tracking API performance metrics"""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = str(uuid.uuid4())[:8]
        self.start_times[timer_id] = time.time()
        logger.debug(f"⏱️ Started timing: {operation} (ID: {timer_id})")
        return timer_id
    
    def end_timer(self, timer_id: str, operation: str, extra_data: Optional[Dict[str, Any]] = None) -> float:
        """End timing an operation and log the duration"""
        if timer_id not in self.start_times:
            logger.warning(f"Timer ID {timer_id} not found for operation: {operation}")
            return 0.0
        
        duration = time.time() - self.start_times[timer_id]
        del self.start_times[timer_id]
        
        # Determine log level based on duration
        if duration > 5.0:
            log_level = logging.ERROR
            emoji = "🐌"
        elif duration > 2.0:
            log_level = logging.WARNING
            emoji = "⚠️"
        elif duration > 1.0:
            log_level = logging.INFO
            emoji = "⏰"
        else:
            log_level = logging.DEBUG
            emoji = "⚡"
        
        extra_info = f" | {extra_data}" if extra_data else ""
        logger.log(log_level, f"{emoji} Completed: {operation} in {duration:.3f}s{extra_info}")
        
        return duration

def setup_logger(
    name: str = "ai_teaching_assistant",
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    pretty_print: bool = True
) -> logging.Logger:
    """
    Setup enhanced logger with colors and structured formatting
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
        enable_colors: Enable colored output for console
        pretty_print: Enable pretty formatting
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if pretty_print and enable_colors:
        # Colored formatter for console
        console_format = (
            "%(levelname_colored)s | "
            "%(asctime)s | "
            "%(request_id)s | "
            "%(name)s:%(lineno)d | "
            "%(message)s"
        )
        console_formatter = ColoredFormatter(
            console_format,
            datefmt="%H:%M:%S"
        )
    else:
        # Simple formatter
        console_format = (
            "%(levelname)s | "
            "%(asctime)s | "
            "%(request_id)s | "
            "%(name)s:%(lineno)d | "
            "%(message)s"
        )
        console_formatter = logging.Formatter(
            console_format,
            datefmt="%H:%M:%S"
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_format = (
            "%(levelname)s | "
            "%(asctime)s | "
            "%(request_id)s | "
            "%(name)s:%(lineno)d | "
            "%(message)s"
        )
        file_formatter = logging.Formatter(
            file_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def set_request_id(request_id: str) -> None:
    """Set request ID for current context"""
    request_id_context.set(request_id)

def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_context.get()

def generate_request_id() -> str:
    """Generate a new request ID"""
    return str(uuid.uuid4())[:8]

# Global logger instance
logger = setup_logger()

# Global performance logger
perf_logger = PerformanceLogger()

# Convenience functions
def log_request_start(method: str, url: str, request_id: str) -> None:
    """Log the start of an API request"""
    set_request_id(request_id)
    logger.info(f"🚀 {method} {url}")

def log_request_end(method: str, url: str, status_code: int, duration: float) -> None:
    """Log the end of an API request"""
    if status_code >= 500:
        emoji = "💥"
        level = logging.ERROR
    elif status_code >= 400:
        emoji = "⚠️"
        level = logging.WARNING
    elif status_code >= 300:
        emoji = "🔄"
        level = logging.INFO
    else:
        emoji = "✅"
        level = logging.INFO
    
    logger.log(level, f"{emoji} {method} {url} - {status_code} ({duration:.3f}s)")

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """Log an error with context"""
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"❌ {type(error).__name__}: {str(error)}{context_str}", exc_info=True)
