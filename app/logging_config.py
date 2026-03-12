from __future__ import annotations

from typing import Any, Dict

import logging

import structlog


def configure_logging() -> None:
    """Configure structured logging for the application."""

    logging.basicConfig(
        format="%(message)s",
        stream=None,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with the given name."""

    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger

