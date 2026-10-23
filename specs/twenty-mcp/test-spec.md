# CONN-TWENTY-MCP — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | CONN-TWENTY-MCP-R001 | Unit | Build `GraphQL` with and without a token | Two clients, Origin on both, Authorization only with a token, core routing | `tests/test_twenty_gql.py` |

## Negative and boundary cases

A failed call raises `GraphQLExecutionError` through `execute_gql`.

## Quality and release proof

Run `uv run pytest -q`.
