"""Application-wide logging setup for `ai_notes.*` package loggers."""

from __future__ import annotations

import logging
import sys
from typing import Final

from ai_notes.config import AppSettings

_LOGGER_NAME: Final[str] = "ai_notes"
_CONFIGURED = False

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _parse_level(value: str) -> int:
    v = value.strip().upper()
    mapping: dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return mapping.get(v, logging.INFO)


def configure_app_logging(settings: AppSettings) -> None:
    """Attach stderr handler + formatter for loggers named `ai_notes.*`.

    Idempotent. Uses ``LOG_LEVEL`` / ``settings.log_level``, or DEBUG when ``DEBUG=true``.
    """
    global _CONFIGURED  # noqa: PLW0603
    if _CONFIGURED:
        return

    lvl = _parse_level(settings.log_level)
    if settings.debug:
        lvl = logging.DEBUG

    root_pkg = logging.getLogger(_LOGGER_NAME)
    root_pkg.setLevel(lvl)
    if not root_pkg.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))
        root_pkg.addHandler(h)
    root_pkg.propagate = False

    _CONFIGURED = True
