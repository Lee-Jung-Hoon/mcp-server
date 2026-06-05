"""Logging helpers.

MCP stdio transports reserve stdout for JSON-RPC protocol messages, so Python's default
stderr-backed logging handler is intentionally used here.
"""

from __future__ import annotations

import logging


def configure_logging(level: int) -> logging.Logger:
    """Configure and return the application logger."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger = logging.getLogger("mcp_server_starter")
    logger.setLevel(level)
    return logger
