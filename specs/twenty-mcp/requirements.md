# CONN-TWENTY-MCP — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-TWENTY-MCP-R001` | **Shared GraphQL client.** The connector must send GraphQL calls through the SDK shared GraphQL client. It must declare GraphQL only through the SDK `graphql` extra. Caller chain: an MCP tool of `twenty_mcp/mcp/mcp_graphql.py` calls `execute_gql` (`twenty_mcp/api/api_client_crm.py:193`), which calls `execute_gql` of `twenty_mcp/twenty_gql.py` (`twenty_mcp/twenty_gql.py:94`); that module builds the SDK `GraphQLClient` (`twenty_mcp/twenty_gql.py:86`). Shape: `twenty_mcp/twenty_gql.py` builds two `scion_sdk.transports.graphql.GraphQLClient` objects (core and metadata endpoints); `pyproject.toml` declares `scion-sdk[graphql,mcp]`. Proving test: `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing`. | `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` shows two endpoints, Origin on both, and token-only Authorization. |
