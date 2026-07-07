"""
logger.py
=========
Professional rotating-file logging configuration shared across the whole
application. Every module obtains its logger via `get_logger(__name__)`
so log records carry the originating module name.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.config import get_config

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def _initialize_root_logger() -> None:
    """Attach a rotating file handler + console handler to the root
    logger exactly once per process."""
    global _initialized
    if _initialized:
        return

    config = get_config()
    log_dir: Path = config.logs_root
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / config.logging.log_filename

    level = getattr(logging, config.logging.level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _initialized = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-scoped logger, ensuring the root logging
    configuration has been initialized."""
    _initialize_root_logger()
    return logging.getLogger(name if name else "visionguard")
