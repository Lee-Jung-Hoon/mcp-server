"""Feature modules grouped by capability domain."""

from mcp_server_starter.features.echo.tool import echo_tool
from mcp_server_starter.features.health.resource import server_info_resource
from mcp_server_starter.features.health.tool import health_check_tool
from mcp_server_starter.features.pii.tool import pii_mask_tool
from mcp_server_starter.features.planning.prompt import implementation_plan_prompt

FEATURE_MODULES = (
    health_check_tool,
    echo_tool,
    pii_mask_tool,
    server_info_resource,
    implementation_plan_prompt,
)

__all__ = ["FEATURE_MODULES"]
