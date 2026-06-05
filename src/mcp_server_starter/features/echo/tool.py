"""Echo MCP tool used as a template for future tools."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer


@dataclass(frozen=True, slots=True)
class EchoTool:
    """Register a minimal echo tool."""

    name: str = "tool.echo"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        @server.tool(name="echo", description="Echo a message back to the caller.")
        def echo(message: str, uppercase: bool = False) -> str:
            """Return ``message`` unchanged, or uppercased when requested."""
            context.logger.debug("Echo tool called", extra={"uppercase": uppercase})
            return message.upper() if uppercase else message


echo_tool = EchoTool()
