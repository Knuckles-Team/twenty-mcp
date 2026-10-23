# CONN-TWENTY-MCP-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `twenty-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `twenty_mcp` from it.
