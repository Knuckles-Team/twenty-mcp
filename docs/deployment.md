# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`twenty-mcp` supports local stdio, a loopback-only development listener, a
least-privilege stdio container, and a remote authenticated HTTPS boundary.
Provider endpoint, credential, selector, identity, and trust material are supplied
at runtime through `AgentConfig`; none is stored in this repository.

### Installed stdio process

```json
{
  "mcpServers": {
    "twenty": {
      "command": "twenty-mcp",
      "args": [],
      "env": {"MCP_TOOL_MODE": "intent"}
    }
  }
}
```

### Loopback development listener

```bash
twenty-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require direct TLS
or an explicitly trusted TLS-terminating ingress, configured authentication, exact
`MCP_ALLOWED_HOSTS`, and an exact trusted-proxy CIDR policy.

### Least-privilege local container

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  registry.example.invalid/twenty-mcp@sha256:<digest> twenty-mcp
```

The operator projects the selected AgentConfig profile into the process at runtime;
the image remains immutable and contains no environment connection profile.

### Remote authenticated HTTPS endpoint

```json
{
  "mcpServers": {
    "twenty": {"url": "https://service.example.invalid/mcp"}
  }
}
```

Store the real remote URL, outbound identity reference, and TLS-profile reference in
`AgentConfig`, not in MCP client JSON or documentation.
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
| `TWENTY_TLS_PROFILE` | `system` | Named outbound TLS policy from AgentConfig |
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
    image: example/twenty-mcp@sha256:<digest>
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
    image: example/twenty-mcp@sha256:<digest>
    hostname: twenty-mcp
    env_file: [../.env]
    environment:
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]

  twenty-agent:
    image: example/twenty-mcp@sha256:<digest>
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
# Internal (self-signed) — homelab .example.invalid zone
twenty-mcp.example.invalid {
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
curl -s "http://technitium.example.invalid:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=twenty-mcp.example.invalid" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=192.0.2.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `twenty-mcp.example.invalid → <caddy-host-ip>` in the Technitium web
console (`http://technitium.example.invalid:5380`). The ecosystem
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

For a remote HTTP server, point the client at `http://twenty-mcp.example.invalid/mcp` instead.
