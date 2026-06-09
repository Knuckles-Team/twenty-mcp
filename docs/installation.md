# Installation

`twenty-mcp` is a standard Python package and a prebuilt container image. Pick the
path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **Twenty CRM** instance and a developer access token — see
  [Backing Platform](platform.md) to deploy one locally.

## From PyPI (recommended)

```bash
pip install twenty-mcp
```

### Optional extras

The base install is intentionally minimal. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "twenty-mcp[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "twenty-mcp[agent]"` | Pydantic-AI agent + Logfire tracing (`agent-utilities[agent,logfire]`) |
| `all` | `pip install "twenty-mcp[all]"` | Everything above |
| `test` | `pip install "twenty-mcp[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run the MCP server and the agent
pip install "twenty-mcp[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/twenty-mcp.git
cd twenty-mcp
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run twenty-mcp
```

## Prebuilt Docker image

A multi-stage, slim image is published on every release (installs
`twenty-mcp[all]`, entrypoint `twenty-mcp`):

```bash
docker pull knucklessg1/twenty-mcp:latest

docker run --rm -i \
  -e TWENTY_URL=http://your-twenty:3000 \
  -e TWENTY_TOKEN=your_developer_access_token \
  knucklessg1/twenty-mcp:latest        # stdio transport (default)
```

For an HTTP server with a published port, see [Deployment](deployment.md).

## Verify the install

```bash
twenty-mcp --help
python -c "import twenty_mcp; print(twenty_mcp.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP server (and agent) behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the `Api` client, and the agent.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
