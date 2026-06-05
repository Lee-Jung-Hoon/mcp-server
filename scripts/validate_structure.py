"""Validate the starter layout without importing optional runtime dependencies."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "src/mcp_server_starter/__main__.py",
    "src/mcp_server_starter/core/server.py",
    "src/mcp_server_starter/core/registry.py",
    "src/mcp_server_starter/config/settings.py",
    "src/mcp_server_starter/features/__init__.py",
    "src/mcp_server_starter/features/health/tool.py",
    "src/mcp_server_starter/features/health/resource.py",
    "src/mcp_server_starter/features/echo/tool.py",
    "src/mcp_server_starter/features/planning/prompt.py",
    "tests/test_settings.py",
    "tests/test_registry.py",
]


def main() -> None:
    missing = [file for file in REQUIRED_FILES if not (ROOT / file).exists()]
    if missing:
        joined = "\n".join(f"- {file}" for file in missing)
        raise SystemExit(f"Missing required files:\n{joined}")

    server_source = (ROOT / "src/mcp_server_starter/core/server.py").read_text()
    for token in ("FastMCP", "FEATURE_MODULES", "register_feature_modules"):
        if token not in server_source:
            raise SystemExit(f"src/mcp_server_starter/core/server.py does not include {token}")

    print("Python MCP server starter structure is valid.")


if __name__ == "__main__":
    main()
