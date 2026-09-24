"""
Structured Application Logging Module.

Configures standard library logging with clean, formatted output suitable for both
local development and production container environments (JSON/structured-friendly).

Why this exists:
In Cloud & DevOps platforms, observability starts with structured, consistent logging.
Centralizing log configuration ensures all modules, services, and middleware emit logs
with timestamps, severity levels, and module origins without ad-hoc print statements.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configures and returns the root application logger.
    Sets log level dynamically based on settings.LOG_LEVEL and settings.DEBUG.
    """
    log_level = (
        logging.DEBUG
        if settings.DEBUG
        else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    )

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress overly verbose third-party loggers in debug mode
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG else logging.INFO
    )

    logger = logging.getLogger("cloudforge")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
