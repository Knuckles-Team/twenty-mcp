# Usage — MCP / API / Agent

`twenty-mcp` exposes the same capability three ways: as **MCP tools** an agent calls,
as a **Python API** (`Api`) you import, and as an **A2A agent** you converse with.

## As an MCP server

Once [deployed](deployment.md), the server registers three action-dispatch tools, each
gated by its own registration switch. Every tool takes an `action` name and a
`params_json` JSON string, and routes the action onto the matching client method.

| Tool | Switch | Representative actions |
|---|---|---|
| `twenty_mcp_crm` | `CRMTOOL` | `get_people`, `create_person`, `get_companies`, `create_company`, `get_opportunities`, `create_opportunity`, `get_records`, `create_record`, `update_record`, `delete_record`, `batch_create_records`, `execute_gql` |
| `twenty_mcp_metadata` | `METADATATOOL` | `get_metadata`, `get_metadata_objects`, `create_metadata_object`, `create_metadata_field`, `create_metadata_relation` |
| `twenty_mcp_oauth` | `OAUTHTOOL` | `register_oauth_client`, `get_oauth_discovery`, `exchange_oauth_token`, `refresh_oauth_token`, `validate_webhook_signature` |

Example agent prompts that map onto these tools:

- *"List the people in the CRM"* → `twenty_mcp_crm` with `action="get_people"`
- *"Create a company named Acme with domain acme.com"* → `twenty_mcp_crm` with `action="create_company"`
- *"Show the metadata objects defined in the workspace"* → `twenty_mcp_metadata` with `action="get_metadata_objects"`

## As a Python API

`Api` is a multi-inheritance facade combining `CrmApi`, `MetadataApi`, and `OauthApi`
over a tolerant `requests` session.

```python
from twenty_mcp.api_client import Api

api = Api(
    base_url="http://your-twenty:3000",
    token="your_developer_access_token",
    verify=True,
)

# Reads
people = api.get_people({"limit": 50})         # CRM contacts
companies = api.get_companies()
opportunities = api.get_opportunities()
objects = api.get_metadata_objects()           # schema metadata

# Arbitrary GraphQL against core and custom schemas
result = api.execute_gql("query { people { edges { node { id name { firstName } } } } }")
```

Build a client straight from the environment:

```python
from twenty_mcp.auth import get_client
api = get_client()        # reads TWENTY_* from the environment / .env
```

### Writes

```python
api.create_person("Ada", "Lovelace", email="ada@example.com")
api.create_company("Acme", domain="acme.com")
api.create_opportunity("Q3 Renewal", amount=12000)
```

## As an A2A agent

The `twenty-agent` console script starts a Pydantic-AI agent that connects to the MCP
server over `MCP_URL` and exposes an HTTP API (and optional web UI):

```bash
twenty-agent --mcp-url http://twenty-mcp:8000/mcp \
  --host 0.0.0.0 --port 9000 --web
```

The agent reads its model configuration (`PROVIDER`, `MODEL_ID`, and the matching
provider API key) from the environment. See [Deployment](deployment.md#agent-server-a2a)
for the combined Compose stack that runs the MCP server and the agent together.
