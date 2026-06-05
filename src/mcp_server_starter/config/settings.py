"""Typed runtime settings loaded from environment variables."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Mapping

_ALLOWED_LOG_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Application settings shared by all feature modules."""

    server_name: str = "mcp-server-starter"
    server_version: str = "0.1.0"
    log_level: str = "INFO"

    @property
    def logging_level(self) -> int:
        """Return the numeric Python logging level."""
        return _ALLOWED_LOG_LEVELS[self.log_level]


def _read_log_level(raw_value: str | None) -> str:
    if raw_value is None:
        return "INFO"

    normalized = raw_value.strip().upper()
    if normalized in _ALLOWED_LOG_LEVELS:
        return normalized

    return "INFO"


def load_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    """Load settings from a mapping, defaulting to ``os.environ``."""
    source = os.environ if env is None else env
    return AppSettings(
        server_name=source.get("MCP_SERVER_NAME", "mcp-server-starter"),
        server_version=source.get("MCP_SERVER_VERSION", "0.1.0"),
        log_level=_read_log_level(source.get("LOG_LEVEL")),
    )
