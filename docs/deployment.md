# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`twenty-mcp` exposes its MCP server (console script `twenty-mcp`) four ways. Pick the row that
matches where the server runs relative to your MCP client, then copy the matching
`mcp_config.json` below. Replace the `<your-…>` placeholders with the values from the **Configuration / Environment Variables** section.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container / uv | `stdio` or `streamable-http` | Docker / Podman / uv on this host | `command` or `url` |
| 4 | Remote URL | `streamable-http` | a remote host behind Caddy | `url` |

### 1. stdio (local subprocess)

The client launches the server over stdio via `uvx` — best for local IDEs
(Cursor, Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "twenty-mcp": {
      "command": "uvx",
      "args": ["--from", "twenty-mcp", "twenty-mcp"],
      "env": {
        "TWENTY_URL": "<your-twenty_url>",
        "TWENTY_MCP_BASE_URL": "<your-twenty_mcp_base_url>",
        "TWENTY_TOKEN": "<your-twenty_token>"
      }
    }
  }
}
```

### 2. Streamable-HTTP (local process)

Run the server as a long-lived HTTP process:

```bash
uvx --from twenty-mcp twenty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/health        # {"status":"OK"}
```

Then either let the client launch it:

```json
{
  "mcpServers": {
    "twenty-mcp": {
      "command": "uvx",
      "args": ["--from", "twenty-mcp", "twenty-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "TWENTY_URL": "<your-twenty_url>",
        "TWENTY_MCP_BASE_URL": "<your-twenty_mcp_base_url>",
        "TWENTY_TOKEN": "<your-twenty_token>"
      }
    }
  }
}
```

…or connect to the already-running process by URL:

```json
{
  "mcpServers": {
    "twenty-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

### 3. Local container / uv

**(a) Launch a container directly from `mcp_config.json`** (stdio over the container —
no ports to manage). Swap `docker` for `podman` for a daemonless runtime:

```json
{
  "mcpServers": {
    "twenty-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TRANSPORT=stdio",
        "-e", "TWENTY_URL=<your-twenty_url>",
        "-e", "TWENTY_MCP_BASE_URL=<your-twenty_mcp_base_url>",
        "-e", "TWENTY_TOKEN=<your-twenty_token>",
        "knucklessg1/twenty-mcp:latest"
      ]
    }
  }
}
```

**(b) Run a local streamable-http container, then connect by URL:**

```bash
docker run -d --name twenty-mcp -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e TWENTY_URL="<your-twenty_url>" \
  -e TWENTY_MCP_BASE_URL="<your-twenty_mcp_base_url>" \
  -e TWENTY_TOKEN="<your-twenty_token>" \
  knucklessg1/twenty-mcp:latest
# or, from a clone of this repo:
docker compose -f docker/mcp.compose.yml up -d
```

```json
{
  "mcpServers": {
    "twenty-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

**(c) From a local checkout with `uv`:**

```bash
uv run twenty-mcp --transport streamable-http --port 8000
```

### 4. Remote URL (deployed behind Caddy)

When the server is deployed remotely (e.g. as a Docker service) and published through
Caddy on the internal `*.arpa` zone, connect with the `"url"` key — no local process or
image required:

```json
{
  "mcpServers": {
    "twenty-mcp": { "url": "http://twenty-mcp.arpa/mcp" }
  }
}
```

Caddy reverse-proxies `http://twenty-mcp.arpa` to the container's `:8000`
streamable-http listener; `http://twenty-mcp.arpa/health` returns
`{"status":"OK"}` when the service is live.
<!-- END GENERATED: deployment-options -->

This page covers running `twenty-mcp` as a long-lived service: the transports, the
optional A2A agent server, a Docker Compose stack, putting it behind a Caddy reverse
proxy, and giving it a DNS name with Technitium. To provision the **Twenty CRM
platform** it connects to, see [Backing Platform](platform.md).

> `twenty-mcp` ships an **MCP server** (console script `twenty-mcp`) and an **A2A
> agent server** (console script `twenty-agent`) that delegates CRM work to the MCP
> tools. Deploy the MCP server alone, or both together.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    twenty-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    twenty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    twenty-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`twenty-mcp` is configured entirely from the environment. The **required** set:

| Var | Default | Meaning |
|---|---|---|
| `TWENTY_URL` | `http://localhost:3000` | Twenty CRM base server URL |
| `TWENTY_TOKEN` | `twenty_developer_access_token` | Developer access token (Bearer) |
| `TWENTY_MCP_BASE_URL` | `http://localhost:3000/api` | Base API URL to query |
| `TWENTY_MCP_USERNAME` | `admin` | Auth username (used if no token) |
| `TWENTY_MCP_PASSWORD` | `secure_password` | Auth password (used if no token) |
| `TWENTY_MCP_SSL_VERIFY` | `True` | Verify TLS |
| `TWENTY_API_PREFIX` | `/rest` | API path prefix for record operations |
| `CRMTOOL` | `True` | Register the CRM tool |
| `METADATATOOL` | `True` | Register the metadata tool |
| `OAUTHTOOL` | `True` | Register the OAuth/webhooks tool |

Plus `HOST` / `PORT` / `TRANSPORT` for HTTP transports. The full set is documented in
[`.env.example`](https://github.com/Knuckles-Team/twenty-mcp/blob/main/.env.example).
Copy it to `.env` and populate only what you use; an absent `TWENTY_TOKEN` leaves the
client unauthenticated rather than raising.

### Backing service

Twenty CRM is **self-hostable** — a Docker recipe to deploy the platform that
`TWENTY_URL` points at is provided in [Backing Platform](platform.md). Twenty also
offers a managed cloud instance; in that case only the connection configuration above
is required.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/twenty-mcp/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
services:
  twenty-mcp:
    image: knucklessg1/twenty-mcp:latest
    container_name: twenty-mcp
    hostname: twenty-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
      - TWENTY_URL
      - TWENTY_TOKEN
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit TWENTY_* values
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## Agent server (A2A)

The A2A agent is published as the `twenty-agent` console script and
[`docker/agent.compose.yml`](https://github.com/Knuckles-Team/twenty-mcp/blob/main/docker/agent.compose.yml),
which provisions the MCP server **and** the agent together. The agent reaches the MCP
server over `MCP_URL` and publishes its own HTTP API (and optional web UI) on `:9000`:

```yaml
services:
  twenty-mcp:
    image: knucklessg1/twenty-mcp:latest
    hostname: twenty-mcp
    env_file: [../.env]
    environment:
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]

  twenty-agent:
    image: knucklessg1/twenty-mcp:latest
    depends_on: [twenty-mcp]
    command: ["twenty-agent"]
    env_file: [../.env]
    environment:
      - HOST=0.0.0.0
      - PORT=9000
      - MCP_URL=http://twenty-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
    ports: ["9000:9000"]
```

```bash
docker compose -f docker/agent.compose.yml up -d
curl -s http://localhost:9000/health        # agent health
```

Configure the agent's model with `PROVIDER`, `MODEL_ID`, and the matching provider
API key (for example `LLM_API_KEY` / `OPENAI_API_KEY`).

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
twenty-mcp.arpa {
    tls internal
    reverse_proxy twenty-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
twenty-mcp.example.com {
    reverse_proxy twenty-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=twenty-mcp.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `twenty-mcp.arpa → <caddy-host-ip>` in the Technitium web
console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "twenty_mcp": {
      "command": "python",
      "args": ["-m", "twenty_mcp.mcp_server"],
      "env": {
        "TWENTY_URL": "http://your-twenty:3000",
        "TWENTY_TOKEN": "your_developer_access_token"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://twenty-mcp.arpa/mcp` instead.
