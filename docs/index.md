# twenty-mcp

Twenty CRM **REST/GraphQL API + MCP Server** for the agent-utilities ecosystem —
a typed, deterministic tool surface and Pydantic-AI agent for the Twenty
customer-relationship-management platform.

!!! info "Official documentation"
    This site is the canonical reference for `twenty-mcp`, maintained alongside every
    release.

[![PyPI](https://img.shields.io/pypi/v/twenty-mcp)](https://pypi.org/project/twenty-mcp/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/twenty-mcp)](https://github.com/Knuckles-Team/twenty-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/twenty-mcp)

## Overview

`twenty-mcp` wraps the [Twenty CRM](https://twenty.com/) REST and GraphQL surface with
typed, deterministic MCP tools, and ships a Pydantic-AI agent that delegates CRM work
to those tools. It provides:

- **`Api`** — a multi-inheritance client facade (`CrmApi` + `MetadataApi` + `OauthApi`)
  over the Twenty REST/GraphQL API, built on a tolerant `requests` session.
- **Action-dispatch MCP tools** — `twenty_mcp_crm`, `twenty_mcp_metadata`, and
  `twenty_mcp_oauth`, each routing a named action onto the corresponding client method,
  with per-domain registration switches (`CRMTOOL`, `METADATATOOL`, `OAUTHTOOL`).
- **A Pydantic-AI agent** (`twenty-agent` console script) that connects to the MCP
  server over `MCP_URL` and exposes an HTTP API and optional web UI.

The server remains inactive against the CRM when credentials are absent — every
configuration value is read from the environment.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and example prompts.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy Twenty CRM with Docker.
- :material-tag-multiple: **[Overview](overview.md)** — the dynamic facade architecture.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:TWENTY-*` registry.

</div>

## Quick start

```bash
pip install "twenty-mcp[mcp]"
twenty-mcp                       # stdio MCP server (default transport)
```

Connect it to a Twenty CRM instance:

```bash
export TWENTY_URL=http://your-twenty:3000
export TWENTY_TOKEN=your_developer_access_token
twenty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
