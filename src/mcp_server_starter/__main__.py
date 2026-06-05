"""Command-line entry point for the MCP server."""

from mcp_server_starter.core.server import create_server


def main() -> None:
    """Run the MCP server over stdio."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
