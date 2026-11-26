---
name: twenty-graphql
skill_type: skill
description: >-
  Run GraphQL against a Twenty workspace with `twenty_graphql` and `twenty_execute_gql`, and look up types with `twenty_discover_graphql_schema`. Use when a read or write needs a nested selection, a filter, or an operation the REST record tools cannot express.
license: MIT
tags: [twenty, crm, graphql]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty GraphQL

Scope: Run GraphQL against a Twenty workspace with `twenty_graphql` and `twenty_execute_gql`, and look up types with `twenty_discover_graphql_schema`. Use when a read or write needs a nested selection, a filter, or an operation the REST record tools cannot express. Do NOT use for simple record reads and writes (use twenty-records, twenty-contacts or twenty-pipeline) or for schema definition (use twenty-metadata).

Twenty serves a per-workspace object schema over GraphQL. Introspection is disabled, so types are
discovered through the metadata tools.

## When to use
- A query selects nested relations in one round trip.
- A mutation or filter has no REST equivalent.

## When NOT to use
- Plain reads and writes: use the typed record tools.
- Auth and API key operations: `twenty-provisioner`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Steps

1. Look up the type with `twenty_discover_graphql_schema` and verify the object and field names appear in the result.
2. Draft the smallest selection and run it with `twenty_graphql` or `twenty_execute_gql`, and verify the response has a `data` object.
3. Inspect the response with `twenty_graphql` output for an `errors` array, and verify it is absent even when the HTTP status is 200.
4. Page large results with cursors in `variables`, and verify the page info reports whether more pages remain.
5. Run a mutation with `twenty_execute_gql` only after a read of the target, and verify by re-reading the changed record.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Response has `errors` with HTTP 200 | A field name or type is wrong | Call `twenty_get_metadata` for the exact camelCase field names and fix the query |
| Authentication error | `TWENTY_TOKEN` is missing or expired | Set a valid `TWENTY_TOKEN` for the `twenty-mcp` server and call the tool again |
| Introspection query fails | Introspection is disabled on this server | Use `twenty_discover_graphql_schema` to read the types instead |

## Tools
| Tool | Use |
|---|---|
| `twenty_discover_graphql_schema` | Describe the object, field and relation meta-model; `type_name` narrows it to one type. |
| `twenty_get_metadata` | The full schema, to confirm field names. |
| `twenty_graphql` | Run a `query` with `variables` and an `operation_name`. |
| `twenty_execute_gql` | Run a `query` with `variables` on the core API. |

## Procedure
1. Look up the type with `twenty_discover_graphql_schema`.
2. Write the smallest selection that answers the question; page with cursors.
3. Treat a mutation as a write: read first and report what changed.

## Gotchas
- A GraphQL response can carry `errors` with HTTP 200. Check it before reporting success.
- Field names are camelCase and composite fields are nested objects.
