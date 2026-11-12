"""
TRUSTLENS AI - Structured Logging Configuration
Provides consistent, production-grade JSON or formatted stream logging.
"""

import sys
import logging
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures root application logger with formatting and level."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger("trustlens")
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if re-initialized
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger


logger = setup_logging()
