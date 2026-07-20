# Twenty Kg Sync

Natively ingest Twenty CRM records into the epistemic-graph knowledge graph via the twenty-mcp MCP server's `twenty_ingest_records` tool — pushing people, companies, and opportunities as typed `:Person` / `:Company` / `:Opportunity` nodes with `:worksAt` / `:opportunityFor` / `:pointOfContact` links. Use when the agent must mirror a Twenty workspace into the KG, refresh CRM nodes before a graph query, or make deals/accounts available for cross-source reasoning. Do NOT use for day-to-day CRUD on contacts or deals (use twenty-contacts / twenty-pipeline) — this tool is read-then-ingest only.

# Twenty → Knowledge Graph Sync

Native ingestion of Twenty CRM records into the ONE epistemic-graph knowledge
graph, as typed OWL nodes federated by the `twenty` ontology. The tool lists a
Twenty object via the real CRM client and pushes each record as a graph node with
its relationships — no separate ETL job.

## When to use
- Mirror a Twenty workspace (people, companies, opportunities) into the KG.
- Refresh CRM nodes before running a graph query or cross-source join.
- Make accounts/deals available to KG-native reasoning alongside other sources.

## When NOT to use
- Creating / updating / reading individual records operationally →
  `twenty-contacts` (people & companies) or `twenty-pipeline` (opportunities).
- Deleting records or mutating Twenty — this tool is **read-then-ingest only**.
- Object/field schema changes → `twenty_mcp_metadata`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`twenty-mcp`** MCP server. A
reachable epistemic-graph engine is required for the write to land; with no engine
the tool **no-ops gracefully** (`"ingested": null`) and still reports what it listed.

| Variable | Required | Notes |
|----------|----------|-------|
| `TWENTY_URL` | ✅ | Workspace base URL (alias `TWENTY_MCP_BASE_URL`) |
| `TWENTY_TOKEN` | ✅ | Twenty API key / access token |
| `TWENTY_TLS_PROFILE` | optional | Named outbound TLS policy from AgentConfig |

## Tools & actions
| Tool | Purpose |
|------|---------|
| `twenty_ingest_records` | List one Twenty object and ingest it as typed KG nodes. |

### Key parameters
- `object_name` — one of `people`, `companies`, `opportunities` (default `people`).
- `params_json` — **JSON string** of list filters passed to the CRM client
  (e.g. `{"limit": 60}`).

### What gets written
| Object | Node type | Key props | Links |
|--------|-----------|-----------|-------|
| people | `:Person` | name, primaryEmail, jobTitle, externalToolId | `:worksAt` → `:Company` |
| companies | `:Company` | name, domainName, employees, externalToolId | — |
| opportunities | `:Opportunity` | name, amount, currencyCode, stage, closeDate | `:opportunityFor` → `:Company`, `:pointOfContact` → `:Person` |

Node ids follow `twenty:<class>:<record-uuid>`; every node carries `source=twenty-mcp`
and `domain=twenty` provenance.

## Recipes (`params_json`)
Ingest up to 60 companies:
```json
{"object_name": "companies", "params_json": "{\"limit\": 60}"}
```
Ingest the pipeline (opportunities), then the contacts they reference:
```json
{"object_name": "opportunities", "params_json": "{\"limit\": 60}"}
```
```json
{"object_name": "people", "params_json": "{\"limit\": 60}"}
```

## Gotchas
- Ingest **companies first, then people, then opportunities** so the
  `:worksAt` / `:opportunityFor` / `:pointOfContact` edges resolve to existing nodes.
- The inner `params_json` is a **string within** the tool's own `params_json` — double
  serialization when calling through a condensed wrapper.
- Ingestion is **best-effort and idempotent**: re-running MERGEs the same
  `twenty:<class>:<uuid>` ids; a missing engine returns `"ingested": null`, not an error.
- Amount is normalized from Twenty's `amountMicros` (÷ 1,000,000) into the `:amount`
  major-unit value plus `:currencyCode`.
- Twenty caps list/batch operations; page with `limit` + cursor filters for large
  workspaces rather than one unbounded pull.

## Related
- **Ontology:** the `twenty` leg (`twenty_mcp/ontology/twenty.ttl`) defines the
  `:Company` / `:Opportunity` classes and links; `:Person` is the shared hub class.
- **Operational CRUD:** `twenty-contacts`, `twenty-pipeline`.
- **Declarative sync:** the in-repo `connectors/mcp_source_presets.json` presets sync
  the same objects as KG documents via the central `source_sync` path.
