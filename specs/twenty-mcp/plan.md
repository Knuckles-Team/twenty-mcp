# CONN-TWENTY-MCP — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The `GraphQL` class in `twenty_mcp/twenty_gql.py` owns the calls. It reuses the SDK `GraphQLClient`. It keeps no transport code of its own.

## Architecture

The class builds two `GraphQLClient` instances. One targets `/graphql`. The other targets `/metadata`. Both share one resolved TLS profile. The server disables introspection, so both clients skip schema fetch.

## Interfaces and data model

The public attributes `url`, `origin`, `token`, `endpoint`, `core_endpoint`, `headers`, `client`, and `core_client` stay. The `execute_gql` method keeps its signature. A failed call raises the SDK `GraphQLExecutionError`. Packaging declares GraphQL only through the SDK `graphql` extra.

## Live integration path

An MCP tool calls `execute_gql` in `twenty_mcp/twenty_gql.py`. That method calls `GraphQLClient.execute` on the chosen client.

## Quality and release gates

Run `uv run pytest -q` and `ruff check .`.

## Risks, alternatives, and decisions

The SDK client retries HTTP 429 and 5xx responses at most twice. The old wrapper did not retry.
