"""Server information MCP resource."""

from __future__ import annotations

import json
from dataclasses import dataclass

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer


@dataclass(frozen=True, slots=True)
class ServerInfoResource:
    """Register a JSON resource describing the server."""

    name: str = "resource.server_info"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        @server.resource(
            "mcp://server/info",
            name="server_info",
            description="Static metadata for this MCP server.",
            mime_type="application/json",
        )
        def server_info() -> str:
            return json.dumps(
                {
                    "name": context.settings.server_name,
                    "version": context.settings.server_version,
                    "capabilities": ["tools", "resources", "prompts"],
                },
                indent=2,
            )


server_info_resource = ServerInfoResource()
