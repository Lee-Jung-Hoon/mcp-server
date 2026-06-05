"""MCP tool for GLiNER2-PII masking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer
from mcp_server_starter.features.pii.masking import DEFAULT_MASK_TEMPLATE, Gliner2PiiMasker


@dataclass(frozen=True, slots=True)
class PiiMaskTool:
    """Register a text PII masking tool backed by GLiNER2-PII."""

    name: str = "tool.mask_pii"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        masker = Gliner2PiiMasker(
            model_name=context.settings.pii_model_name,
            default_threshold=context.settings.pii_threshold,
        )

        @server.tool(
            name="mask_pii",
            description=(
                "Detect PII in text with GLiNER2-PII, return masked text and metadata "
                "for each masked entity."
            ),
        )
        def mask_pii(
            text: str,
            labels: list[str] | None = None,
            threshold: float | None = None,
            mask_template: str = DEFAULT_MASK_TEMPLATE,
        ) -> dict[str, Any]:
            """Mask PII in ``text`` and return masked entity details."""
            context.logger.info("PII masking requested", extra={"custom_labels": labels is not None})
            return masker.mask_text(
                text=text,
                labels=labels,
                threshold=threshold,
                mask_template=mask_template,
            ).to_dict()


pii_mask_tool = PiiMaskTool()
