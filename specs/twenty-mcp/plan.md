# CONN-TWENTY-MCP — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

This plan states how `twenty-mcp` delivers the rows of `CONN-TWENTY-MCP`. The live caller is the `twenty-mcp` console script. The owner is the `twenty_mcp` package. The rows reuse the `scion-sdk` helpers and add no second authority. The plan changes no runtime code.

## Technical Context

- **Language/Version**: Python >=3.12, <3.15
- **Primary Dependencies**: scion-sdk[graphql,mcp]>=0.6.4,<0.7.0; fastmcp; further pins in `pyproject.toml` (scion-sdk[graphql,mcp]>=0.6.4,<0.7.0, requests>=2.34.2)
- **Storage**: N/A, the connector keeps no store of its own
- **Testing**: pytest; each row names the proving test as `path::name`
- **Target Platform**: Linux container and stdio or streamable HTTP MCP clients
- **Project Type**: connector
- **Performance Goals**: N/A, the vendor service sets the latency
- **Constraints**: vendor calls go through the SDK governed client; no connector-local transport
- **Scale/Scope**: 1 active row(s) in this spec

## Constitution Check

- Organization constitution 1.5.0, spec-first change: pass. Every behaviour is a row of this spec with a bound or planned test.
- Repository article R-I, connector scope: pass. The rows stay inside this connector's one external system and reuse the SDK for shared capabilities.

## Project Structure

- `twenty_mcp/mcp/mcp_graphql.py` (existing)
- `twenty_mcp/api/api_client_crm.py` (existing)
- `twenty_mcp/twenty_gql.py` (existing)
- `pyproject.toml` (existing)
- `tests/test_twenty_gql.py` (existing)

## Phase 0: Research

No unknowns. Every row names its code and test; the caller chain of each row was read from the code.

## Phase 1: Design

### Summary

This plan states how `twenty-mcp` delivers the rows of `CONN-TWENTY-MCP`. The live caller is the `twenty-mcp` console script. The owner is the `twenty_mcp` package. The rows reuse the `scion-sdk` helpers and add no second authority. The plan changes no runtime code.

### Technical Context

- **Language/Version**: Python >=3.12, <3.15
- **Primary Dependencies**: scion-sdk[graphql,mcp]>=0.6.4,<0.7.0; fastmcp; further pins in `pyproject.toml` (scion-sdk[graphql,mcp]>=0.6.4,<0.7.0, requests>=2.34.2)
- **Storage**: N/A, the connector keeps no store of its own
- **Testing**: pytest; each row names the proving test as `path::name`
- **Target Platform**: Linux container and stdio or streamable HTTP MCP clients
- **Project Type**: connector
- **Performance Goals**: N/A, the vendor service sets the latency
- **Constraints**: vendor calls go through the SDK governed client; no connector-local transport
- **Scale/Scope**: 1 active row(s) in this spec

### Constitution Check

- Organization constitution 1.5.0, spec-first change: pass. Every behaviour is a row of this spec with a bound or planned test.
- Repository article R-I, connector scope: pass. The rows stay inside this connector's one external system and reuse the SDK for shared capabilities.

### Project Structure

- `twenty_mcp/mcp/mcp_graphql.py` (existing)
- `twenty_mcp/api/api_client_crm.py` (existing)
- `twenty_mcp/twenty_gql.py` (existing)
- `pyproject.toml` (existing)
- `tests/test_twenty_gql.py` (existing)

### Phase 0: Research

No unknowns. Every row names its code and test; the caller chain of each row was read from the code.

### Phase 1: Design

### Summary

This plan states how `twenty-mcp` delivers the rows of `CONN-TWENTY-MCP`. The live caller is the `twenty-mcp` console script. The owner is the `twenty_mcp` package. The rows reuse the `scion-sdk` helpers and add no second authority. The plan changes no runtime code.

### Technical Context

- **Language/Version**: Python >=3.12, <3.15
- **Primary Dependencies**: scion-sdk[graphql,mcp]>=0.6.4,<0.7.0; fastmcp; further pins in `pyproject.toml` (scion-sdk[graphql,mcp]>=0.6.4,<0.7.0, requests>=2.34.2)
- **Storage**: N/A, the connector keeps no store of its own
- **Testing**: pytest; each row names the proving test as `path::name`
- **Target Platform**: Linux container and stdio or streamable HTTP MCP clients
- **Project Type**: connector
- **Performance Goals**: N/A, the vendor service sets the latency
- **Constraints**: vendor calls go through the SDK governed client; no connector-local transport
- **Scale/Scope**: 1 active row(s) in this spec

### Constitution Check

- Organization constitution 1.5.0, spec-first change: pass. Every behaviour is a row of this spec with a bound or planned test.
- Repository article R-I, connector scope: pass. The rows stay inside this connector's one external system and reuse the SDK for shared capabilities.

### Project Structure

- `twenty_mcp/mcp/mcp_graphql.py` (existing)
- `twenty_mcp/api/api_client_crm.py` (existing)
- `twenty_mcp/twenty_gql.py` (existing)
- `pyproject.toml` (existing)
- `tests/test_twenty_gql.py` (existing)

### Phase 0: Research

No unknowns. Every row names its code and test; the caller chain of each row was read from the code.

### Phase 1: Design

### Summary

This plan states how `twenty-mcp` delivers the rows of `CONN-TWENTY-MCP`. The live caller is the `twenty-mcp` console script. The owner is the `twenty_mcp` package. The rows reuse the `scion-sdk` helpers and add no second authority. The plan changes no runtime code.

### Technical Context

- **Language/Version**: Python >=3.12, <3.15
- **Primary Dependencies**: scion-sdk[graphql,mcp]>=0.6.4,<0.7.0; fastmcp; further pins in `pyproject.toml` (scion-sdk[graphql,mcp]>=0.6.4,<0.7.0, requests>=2.34.2)
- **Storage**: N/A, the connector keeps no store of its own
- **Testing**: pytest; each row names the proving test as `path::name`
- **Target Platform**: Linux container and stdio or streamable HTTP MCP clients
- **Project Type**: connector
- **Performance Goals**: N/A, the vendor service sets the latency
- **Constraints**: vendor calls go through the SDK governed client; no connector-local transport
- **Scale/Scope**: 1 active row(s) in this spec

### Constitution Check

- Organization constitution 1.5.0, spec-first change: pass. Every behaviour is a row of this spec with a bound or planned test.
- Repository article R-I, connector scope: pass. The rows stay inside this connector's one external system and reuse the SDK for shared capabilities.

### Project Structure

- `twenty_mcp/mcp/mcp_graphql.py` (existing)
- `twenty_mcp/api/api_client_crm.py` (existing)
- `twenty_mcp/twenty_gql.py` (existing)
- `pyproject.toml` (existing)
- `tests/test_twenty_gql.py` (existing)

### Phase 0: Research

No unknowns. Every row names its code and test; the caller chain of each row was read from the code.

### Phase 1: Design

### Summary

This plan states how `twenty-mcp` delivers the rows of `CONN-TWENTY-MCP`. The live caller is the `twenty-mcp` console script. The owner is the `twenty_mcp` package. The rows reuse the `scion-sdk` helpers and add no second authority. The plan changes no runtime code.

### Technical Context

- **Language/Version**: Python >=3.12, <3.15
- **Primary Dependencies**: scion-sdk[graphql,mcp]>=0.6.4,<0.7.0; fastmcp; further pins in `pyproject.toml` (scion-sdk[graphql,mcp]>=0.6.4,<0.7.0, requests>=2.34.2)
- **Storage**: N/A, the connector keeps no store of its own
- **Testing**: pytest; each row names the proving test as `path::name`
- **Target Platform**: Linux container and stdio or streamable HTTP MCP clients
- **Project Type**: connector
- **Performance Goals**: N/A, the vendor service sets the latency
- **Constraints**: vendor calls go through the SDK governed client; no connector-local transport
- **Scale/Scope**: 1 active row(s) in this spec

### Constitution Check

- Organization constitution 1.5.0, spec-first change: pass. Every behaviour is a row of this spec with a bound or planned test.
- Repository article R-I, connector scope: pass. The rows stay inside this connector's one external system and reuse the SDK for shared capabilities.

### Project Structure

- `tests/test_twenty_gql.py` (existing)

### Phase 0: Research

No unknowns. Every row names its code and test; the caller chain of each row was read from the code.

### Phase 1: Design

### Existing system and reuse

The `GraphQL` class in `twenty_mcp/twenty_gql.py` owns the calls. It reuses the SDK `GraphQLClient`. It keeps no transport code of its own.

### Architecture

The class builds two `GraphQLClient` instances. One targets `/graphql`. The other targets `/metadata`. Both share one resolved TLS profile. The server disables introspection, so both clients skip schema fetch.

### Interfaces and data model

The public attributes `url`, `origin`, `token`, `endpoint`, `core_endpoint`, `headers`, `client`, and `core_client` stay. The `execute_gql` method keeps its signature. A failed call raises the SDK `GraphQLExecutionError`. Packaging declares GraphQL only through the SDK `graphql` extra.

### Live integration path

An MCP tool calls `execute_gql` in `twenty_mcp/twenty_gql.py`. That method calls `GraphQLClient.execute` on the chosen client.

### Quality and release gates

Run `uv run pytest -q` and `ruff check .`.

### Risks, alternatives, and decisions

The SDK client retries HTTP 429 and 5xx responses at most twice. The old wrapper did not retry.

### Phase 2: Task approach

`tasks.md` holds one task per row, producer first. Rows that depend on none run in parallel. A task is checked when its `Spec:` trailer is on the default branch.

### Complexity Tracking

None. The constitution check passed.

### Build contract

- `pre-commit run --all-files` runs ruff check, ruff format, the shared `connector-standard`, `spec`, `secrets` and `dependency-readiness` gates at the pinned shared revision.
- `uv run pytest tests` runs the proving tests; the shared complexity, duplication and KISS gates apply their org thresholds and this repository sets no local override.
- A change adds no scanner suppression and no duplicate implementation of an SDK helper.

### Production caller chain


### Cross-repo seams

None. The rows depend only on the published `scion-sdk` package, which the connector imports.

### Phase 2: Task approach

`tasks.md` holds one task per row, producer first. Rows that depend on none run in parallel. A task is checked when its `Spec:` trailer is on the default branch.

### Complexity Tracking

None. The constitution check passed.

### Build contract

- `pre-commit run --all-files` runs ruff check, ruff format, the shared `connector-standard`, `spec`, `secrets` and `dependency-readiness` gates at the pinned shared revision.
- `uv run pytest tests` runs the proving tests; the shared complexity, duplication and KISS gates apply their org thresholds and this repository sets no local override.
- A change adds no scanner suppression and no duplicate implementation of an SDK helper.

### Production caller chain

- `CONN-TWENTY-MCP-R001`: an MCP tool of `twenty_mcp/mcp/mcp_graphql.py` calls `execute_gql` (`twenty_mcp/api/api_client_crm.py:193`), which calls `execute_gql` of `twenty_mcp/twenty_gql.py` (`twenty_mcp/twenty_gql.py:94`); that module builds the SDK `GraphQLClient` (`twenty_mcp/twenty_gql.py:86`).

### Cross-repo seams

None. The rows depend only on the published `scion-sdk` package, which the connector imports.

### Phase 2: Task approach

`tasks.md` holds one task per row, producer first. Rows that depend on none run in parallel. A task is checked when its `Spec:` trailer is on the default branch.

### Complexity Tracking

None. The constitution check passed.

### Build contract

- `pre-commit run --all-files` runs ruff check, ruff format, the shared `connector-standard`, `spec`, `secrets` and `dependency-readiness` gates at the pinned shared revision.
- `uv run pytest tests` runs the proving tests; the shared complexity, duplication and KISS gates apply their org thresholds and this repository sets no local override.
- A change adds no scanner suppression and no duplicate implementation of an SDK helper.

### Production caller chain

- `CONN-TWENTY-MCP-R001`: an MCP tool of `twenty_mcp/mcp/mcp_graphql.py` calls `execute_gql` (`twenty_mcp/api/api_client_crm.py:193`), which calls `execute_gql` of `twenty_mcp/twenty_gql.py` (`twenty_mcp/twenty_gql.py:94`); that module builds the SDK `GraphQLClient` (`twenty_mcp/twenty_gql.py:86`).

### Cross-repo seams

None. The rows depend only on the published `scion-sdk` package, which the connector imports.

### Phase 2: Task approach

`tasks.md` holds one task per row, producer first. Rows that depend on none run in parallel. A task is checked when its `Spec:` trailer is on the default branch.

### Complexity Tracking

None. The constitution check passed.

### Build contract

- `pre-commit run --all-files` runs ruff check, ruff format, the shared `connector-standard`, `spec`, `secrets` and `dependency-readiness` gates at the pinned shared revision.
- `uv run pytest tests` runs the proving tests; the shared complexity, duplication and KISS gates apply their org thresholds and this repository sets no local override.
- A change adds no scanner suppression and no duplicate implementation of an SDK helper.

### Production caller chain

- `CONN-TWENTY-MCP-R001`: an MCP tool of `twenty_mcp/mcp/mcp_graphql.py` calls `execute_gql` (`twenty_mcp/api/api_client_crm.py:193`), which calls `execute_gql` of `twenty_mcp/twenty_gql.py` (`twenty_mcp/twenty_gql.py:94`); that module builds the SDK `GraphQLClient` (`twenty_mcp/twenty_gql.py:86`).

### Cross-repo seams

None. The rows depend only on the published `scion-sdk` package, which the connector imports.

## Phase 2: Task approach

`tasks.md` holds one task per row, producer first. Rows that depend on none run in parallel. A task is checked when its `Spec:` trailer is on the default branch.

## Complexity Tracking

None. The constitution check passed.

## Build contract

- `pre-commit run --all-files` runs ruff check, ruff format, the shared `connector-standard`, `spec`, `secrets` and `dependency-readiness` gates at the pinned shared revision.
- `uv run pytest tests` runs the proving tests; the shared complexity, duplication and KISS gates apply their org thresholds and this repository sets no local override.
- A change adds no scanner suppression and no duplicate implementation of an SDK helper.

## Production caller chain

- `CONN-TWENTY-MCP-R001`: an MCP tool of `twenty_mcp/mcp/mcp_graphql.py` calls `execute_gql` (`twenty_mcp/api/api_client_crm.py:193`), which calls `execute_gql` of `twenty_mcp/twenty_gql.py` (`twenty_mcp/twenty_gql.py:94`); that module builds the SDK `GraphQLClient` (`twenty_mcp/twenty_gql.py:86`).

## Cross-repo seams

None. The rows depend only on the published `scion-sdk` package, which the connector imports.
