"""Context object passed into feature modules."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from mcp_server_starter.config.settings import AppSettings


@dataclass(frozen=True, slots=True)
class AppContext:
    """Shared dependencies available during feature registration."""

    settings: AppSettings
    logger: logging.Logger
