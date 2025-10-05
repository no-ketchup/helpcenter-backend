"""
Provides JSON logging with correlation IDs and request tracking.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Optional

from ..utils.time import utcnow

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        if correlation_id.get():
            log_entry["correlation_id"] = correlation_id.get()

        # Add request info if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "endpoint"):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "duration"):
            log_entry["duration_ms"] = record.duration

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging for the application."""

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())

    # Configure root logger
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Add request logging
    logging.getLogger("common.requests").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"common.{name}")


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set correlation ID for the current context."""
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


def log_request(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **extra: Any,
) -> None:
    """Log HTTP request details."""
    logger.info(
        f"{method} {endpoint} - {status_code}",
        extra={
            "request_id": request_id,
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration": duration * 1000,  # Convert to milliseconds
            **extra,
        },
    )


def log_error(
    logger: logging.Logger,
    message: str,
    error: Exception,
    request_id: Optional[str] = None,
    **extra: Any,
) -> None:
    """Log error with context."""
    logger.error(
        message,
        exc_info=error,
        extra={
            "request_id": request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            **extra,
        },
    )
