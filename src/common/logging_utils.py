"""Shared logging helpers for ETL runtime and orchestrators."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

LOG_ORIGIN_APP = "APP"
LOG_ORIGIN_AIRFLOW = "AF"
LOG_ORIGIN_DAGSTER = "DG"

STAGE_PIPELINE = "PIPELINE"
STAGE_EXTRACT = "EXTRACT"
STAGE_TRANSFORM = "TRANSFORM"
STAGE_LOAD = "LOAD"

_log_origin: ContextVar[str] = ContextVar("log_origin", default=LOG_ORIGIN_APP)


def configure_logging() -> None:
    """Ensure the shared ETL code emits INFO logs to stdout."""
    logging.basicConfig(
        level=getattr(logging, os.getenv("ETL_LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@contextmanager
def log_origin(origin: str) -> Iterator[None]:
    """Temporarily switch log origin for nested ETL calls."""
    token = _log_origin.set(origin)
    try:
        yield
    finally:
        _log_origin.reset(token)


def tagged_message(stage: str, message: str) -> str:
    """Return a log message prefixed with origin and stage tags."""
    return f"[{_log_origin.get()}][{stage}] {message}"


def log_info(logger: logging.Logger, stage: str, message: str, *args) -> None:
    """Emit a tagged INFO log."""
    logger.info(tagged_message(stage, message), *args)


def log_exception(logger: logging.Logger, stage: str, message: str, *args) -> None:
    """Emit a tagged exception log."""
    logger.exception(tagged_message(stage, message), *args)
