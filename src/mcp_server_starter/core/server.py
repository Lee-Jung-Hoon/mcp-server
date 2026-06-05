"""MCP server factory."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_server_starter.config.settings import AppSettings, load_settings
from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FeatureModule, register_feature_modules
from mcp_server_starter.features import FEATURE_MODULES
from mcp_server_starter.shared.logging import configure_logging


def create_server(
    settings: AppSettings | None = None,
    feature_modules: tuple[FeatureModule, ...] = FEATURE_MODULES,
) -> FastMCP:
    """Create, configure, and return the MCP server instance."""
    resolved_settings = settings or load_settings()
    logger = configure_logging(resolved_settings.logging_level)
    context = AppContext(settings=resolved_settings, logger=logger)

    server = FastMCP(
        resolved_settings.server_name,
        instructions=(
            "A minimal, extensible MCP server starter. "
            "Add new tools, resources, and prompts as feature modules."
        ),
    )

    register_feature_modules(server, context, feature_modules)
    logger.info(
        "MCP server initialized: %s %s",
        resolved_settings.server_name,
        resolved_settings.server_version,
    )
    return server
