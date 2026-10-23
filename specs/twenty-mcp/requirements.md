# CONN-TWENTY-MCP — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-TWENTY-MCP-R001` | **Shared GraphQL client.** The connector must send GraphQL calls through the SDK shared GraphQL client. It must declare GraphQL only through the SDK `graphql` extra. | `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` shows two endpoints, Origin on both, and token-only Authorization. |
