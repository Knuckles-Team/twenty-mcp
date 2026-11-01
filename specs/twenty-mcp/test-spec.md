# CONN-TWENTY-MCP — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-TWENTY-MCP-R001` | `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` | `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` shows two endpoints, Origin on both, and token-only Authorization. |

## Negative and boundary cases

Each proving test above includes the refusal or error case that its row names. A vendor outage or an unauthorised call must return the SDK typed error.

## Quality and release proof

Run `uv run pytest tests` and `pre-commit run --all-files` from the repository root. A planned test is added by the code change that lands the row.
