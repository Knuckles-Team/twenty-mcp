# twenty-mcp specifications

These specs follow the ecosystem [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, extend an existing spec before creating one, audits and reviews land in the owning spec, one ID and title form, one file set. The `spec-standard` gate enforces it.

## Owner

This repository owns the specs with the ID prefix `CONN-TWENTY-MCP`. The connector contract, certification, and transport rules belong to [scion-sdk](https://github.com/Knuckles-Team/scion-sdk/tree/main/specs). The spec-delivery page rules belong to [pipelines](https://github.com/Knuckles-Team/pipelines/tree/main/specs).

## Add a spec

Read the existing specs first. Extend the spec that owns the behavior. Create a spec only for a capability that no spec owns. Copy [`_template/`](_template/) to `specs/<area>/`, set the ID to `CONN-TWENTY-MCP` or `CONN-TWENTY-MCP-<AREA>`, and add one index line below.

## Local specifications

[`CONN-TWENTY-MCP`](twenty-mcp/spec.md) — The Twenty connector sends GraphQL calls through the SDK shared client.
- [`CONN-TWENTY-MCP-CONNECTOR-CONTENT`](connector-content/spec.md) — The connector serves its packaged content.
