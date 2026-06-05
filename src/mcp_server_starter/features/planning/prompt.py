"""Prompt templates for implementation planning."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer


@dataclass(frozen=True, slots=True)
class ImplementationPlanPrompt:
    """Register a prompt for planning future feature work."""

    name: str = "prompt.implementation_plan"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        @server.prompt(
            name="implementation_plan",
            description="Create a practical implementation plan for a requested feature.",
        )
        def implementation_plan(feature: str, constraints: str | None = None) -> str:
            """Build an implementation planning prompt."""
            context.logger.debug("Implementation plan prompt requested")
            lines = [
                f"Design an implementation plan for: {feature}",
                "Include API shape, data flow, error handling, tests, and rollout steps.",
            ]
            if constraints:
                lines.insert(1, f"Constraints: {constraints}")
            return "\n".join(lines)


implementation_plan_prompt = ImplementationPlanPrompt()
