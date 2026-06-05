"""Health-check MCP tool."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer


@dataclass(frozen=True, slots=True)
class HealthCheckTool:
    """Register the basic health-check tool."""

    name: str = "tool.health_check"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        @server.tool(name="health_check", description="Return basic server health metadata.")
        def health_check() -> dict[str, Any]:
            return {
                "status": "ok",
                "server": context.settings.server_name,
                "version": context.settings.server_version,
                "checked_at": datetime.now(UTC).isoformat(),
            }


health_check_tool = HealthCheckTool()
