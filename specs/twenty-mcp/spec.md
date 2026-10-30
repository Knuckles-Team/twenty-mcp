# CONN-TWENTY-MCP — Twenty CRM connector

Owner: twenty-mcp. Cross-repo IDs: SCION-CONNECTOR-CONTROL-R030.1.
Public provenance: https://github.com/Knuckles-Team/scion-sdk/pull/192

## Purpose and user stories

An operator calls Twenty CRM through MCP tools. Each tool maps to one API operation. The connector sends its GraphQL calls through the shared SDK client.

## Requirements and acceptance

- FR-001: The connector must send every GraphQL call through the SDK shared GraphQL client.
- SC-001: The test `test_shared_client_two_endpoints_origin_auth_and_routing` passes.

## Why a new spec

I searched `specs/` in this repository with `git grep -n GraphQL -- specs`. It held only the template. No spec owns the Twenty connector, so this spec is new.

## Scope and interfaces

The connector owns the object endpoint `/graphql` and the core endpoint `/metadata`. It sends an `Origin` header on both. It sends `Authorization` only when a token exists. The SDK owns the client mechanics. Non-goal: changing any MCP tool.

## Traceability

| Requirement | Design section | Test ID | Evidence |
|---|---|---|---|
| FR-001 | plan.md Architecture | T-001 |  |

## Open questions

- None.
