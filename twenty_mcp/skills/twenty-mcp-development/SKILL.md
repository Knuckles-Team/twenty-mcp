---
name: twenty-mcp-development
skill_type: skill
description: >-
  Develop, test, and publish twenty-mcp without breaking its typed Twenty CRM
  REST/GraphQL, authentication, MCP action, packaged-content, spec-dashboard,
  or governed Pages contracts. Use when changing connector code, docs, skills,
  workflows, or repository-owned specifications.
license: MIT
tags: [twenty, crm, graphql, connector, development, testing, pages, specs]
metadata:
  author: Genius
  version: '0.1.0'
---
# Twenty MCP Development

Use this skill for changes inside the twenty-mcp package. The connector exposes
typed CRM, metadata, OAuth, GraphQL, and knowledge-graph ingestion operations
through action-routed MCP tools and a Pydantic-AI agent. Keep the API facade,
auth lifecycle, MCP registrations, and packaged resources aligned.

## Repository map

- `twenty_mcp/api_client.py` composes the REST facade from CRM, metadata, and
  OAuth modules; keep request parameter and response-envelope conventions stable.
- `twenty_mcp/twenty_gql.py` owns the shared GraphQL client. Object operations
  use `/graphql`; core/auth/system operations use `/metadata` with the required
  Origin and bearer-header behavior.
- `twenty_mcp/auth.py` loads and validates environment credentials and builds
  clients. Never put tokens in source, fixtures, logs, or error messages.
- `twenty_mcp/mcp/` registers CRM, metadata, OAuth, GraphQL, and ingest actions;
  action names and registration switches are part of the connector contract.
- `twenty_mcp/__init__.py` is the connector entry point: it binds the
  `Connector` to `Api`/`get_client`, `twenty_mcp.mcp_server`, and the supported
  transports.
- `twenty_mcp/connector_sources.py` declares the live source and resource
  mappings served through `connector://resources`.
- `twenty_mcp/mcp_config.json`, `twenty_mcp/skills/`, and
  `twenty_mcp/ontology/` are the actual package resource paths. The checked-in
  repository prompt is `prompts/main_agent.md`.
- `specs/connector-content/` and `specs/twenty-mcp/` own the specifications and
  generated status evidence.

## Before editing

1. Work from a real worktree based on current `origin/main` and identify the
   owning requirement under `specs/`; generated status files are never hand
   edited.
2. Trace a changed action from its Pydantic input through the MCP dispatcher,
   API facade or GraphQL client, auth boundary, and response shape. Preserve the
   stable connector identity `twenty-mcp`.
3. Use the existing fake `requests.Session`, GraphQL mocks, and task-local
   transports. Never make live Twenty calls or require a CRM token in tests.
4. Remember that Twenty disables GraphQL introspection in production. Discovery
   must fall back to the `/metadata` REST/GraphQL surface and must not assume
   that `/graphql` contains core auth or system mutations.

## Implementation contract

- Keep action discovery and routing stable for `twenty_mcp_crm`,
  `twenty_mcp_metadata`, `twenty_mcp_oauth`, GraphQL, and ingest tools. Route each
  action to the existing typed client method instead of adding duplicate paths.
- Preserve the uniform status/data response conventions, request parameter
  filtering, pagination cursors, and redaction of bearer tokens and credentials.
- Route object CRUD through `/graphql` or the typed REST facade as intended;
  route login, API-key, role, SSO, and client-configuration operations through
  `/metadata` with the workspace Origin header.
- Keep ingestion read-then-write and graceful when no graph engine is present;
  do not turn a connector call into an unbounded background job.
- Extend mock tests for invalid actions, missing credentials, disabled
  introspection, endpoint selection, request shape, and successful responses.
- Keep all package resources under the existing setuptools package-data globs so
  wheels and sdists expose the same skills, prompts, ontology, and manifests.

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver one small, reviewable change at a time.

- Name the owning requirement and its proof before editing.
- Keep a slice to one connector concern: source behavior, one test seam, one
  workflow/configuration repair, or one substantive skill.
- Run focused checks first, then the repository pre-commit suite and required
  pre-push hooks. Fix failures and warnings rather than bypassing hooks.
- Record exact source and test commands in the review handoff. Stage only
  reviewed paths; never stage caches, credentials, generated site output, or a
  whole shared checkout.
- Never claim a spec or Pages row from a YAML marker alone. Generated status
  records, the successful exact-source workflow, and the published snapshot
  must agree.

## Spec delivery and Pages

The canonical Pages caller is `.github/workflows/pages.yml`. It uses the `docs`
content source, enables the version-1 dashboard with
`.config/spec-dashboard.json`, and runs on the default branch plus an explicit
`workflow_dispatch`. Keep the `specs/**`, dashboard config, and workflow paths
in the push trigger. The shared renderer owns the HTML layout and writes
`spec-delivery/snapshot.json`; do not commit generated site output.

Add or preserve the `spec-delivery/` documentation link. Rebuild status evidence
through the central pipeline hook after a spec change and inspect the diff. The
Pages proof is complete only when a successful hosted run has `headSha` equal to
the source revision and the public snapshot returns HTTP 200 with the connector
records. Local rendering proves wiring, not publication.

## Verification

From the repository root:

    pre-commit run --all-files
    pytest -v

For Pages changes, also validate the JSON configuration, the generated status
records, and the exact-source hosted snapshot. Use mock sessions and task-local
output directories; do not run live Twenty or graph-engine calls.

## Safety

Never commit `.env` files, tokens, raw CRM identifiers, generated site output,
or request dumps. Preserve credential validation, token redaction, endpoint
selection, introspection fallback, and destructive-operation guards. If packaged
metadata changes, bump the canonical project version and refresh `uv.lock` in
the same coherent release slice, explaining why in the review.
