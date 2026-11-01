# CONN-TWENTY-MCP — Twenty CRM connector

Owner: twenty-mcp. Cross-repo IDs: SCION-CONNECTOR-CONTROL-R030.1.
Public provenance: https://github.com/Knuckles-Team/scion-sdk/pull/192

## Purpose and user stories

An operator calls Twenty CRM through MCP tools. Each tool maps to one API operation. The connector sends its GraphQL calls through the shared SDK client.

## Why a new spec

I searched `specs/` in this repository with `git grep -n GraphQL -- specs`. It held only the template. No spec owns the Twenty connector, so this spec is new.

## Scope and interfaces

The connector owns the object endpoint `/graphql` and the core endpoint `/metadata`. It sends an `Origin` header on both. It sends `Authorization` only when a token exists. The SDK owns the client mechanics. Non-goal: changing any MCP tool.

## Open questions

- None.

## Delivery mapping

Component: twenty-mcp connector

Code: ../../twenty_mcp/__init__.py

## User Scenarios & Testing

### User Story 1 - Shared GraphQL client (Priority: P1)

The fleet operator and the engine rely on this behaviour of `twenty-mcp`: The connector must send GraphQL calls through the SDK shared GraphQL client. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `twenty-mcp` connector built from the default branch, **When** `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` runs, **Then** `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` shows two endpoints, Origin on both, and token-only Authorization.

### Edge Cases

- The vendor service is unreachable or rejects the credential: the connector returns the SDK typed error and never a partial result.
- An argument outside the documented inputs is refused with the SDK typed refusal and causes no effect on the vendor service.

## Requirements

- **FR-001**: Shared GraphQL client. Rows: `CONN-TWENTY-MCP-R001`.

## Success Criteria

- **SC-001**: `tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing` shows two endpoints, Origin on both, and token-only Authorization. Rows: `CONN-TWENTY-MCP-R001`.

## Assumptions

- The `twenty-mcp` package keeps the entry point and module layout named in the rows.
- The shared SDK supplies the transport, authentication, retry and certification helpers the rows reuse.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-TWENTY-MCP-R001` | plan.md Production caller chain | T-001 | tests/test_twenty_gql.py::test_shared_client_two_endpoints_origin_auth_and_routing |
