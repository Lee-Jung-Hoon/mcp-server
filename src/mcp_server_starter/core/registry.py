"""Feature registration primitives for tools, resources, and prompts."""

from __future__ import annotations

from typing import Protocol, TypeAlias

from mcp_server_starter.core.context import AppContext

FastMCPServer: TypeAlias = object


class FeatureModule(Protocol):
    """A self-contained unit that registers one or more MCP capabilities."""

    name: str

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        """Register MCP capabilities on ``server``."""


def register_feature_modules(
    server: FastMCPServer,
    context: AppContext,
    modules: list[FeatureModule] | tuple[FeatureModule, ...],
) -> None:
    """Register modules once, failing fast on duplicate feature names."""
    seen: set[str] = set()

    for module in modules:
        if module.name in seen:
            msg = f"Duplicate MCP feature module name: {module.name}"
            raise ValueError(msg)

        seen.add(module.name)
        module.register(server, context)
        context.logger.debug("Registered MCP feature module: %s", module.name)
