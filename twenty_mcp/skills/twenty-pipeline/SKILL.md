---
name: twenty-pipeline
description: >-
  Drive the sales pipeline in Twenty CRM via the twenty-mcp MCP server — list,
  read, create, update, and advance opportunities (deals) with the domain-typed
  `twenty_mcp_crm` tool. Use when the agent must triage the deal pipeline by stage,
  create a new opportunity for a company, set or move a deal's stage, update its
  amount/close-date, or attach a point-of-contact. Do NOT use for managing the
  underlying people/companies (use twenty-contacts), for ingesting deals into the
  knowledge graph (use twenty-kg-sync), or for object-schema changes (use the
  twenty_mcp_metadata tool).
license: MIT
tags: [twenty, crm, opportunities, pipeline, sales, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Twenty Sales Pipeline

Domain-typed access to Twenty's **Opportunities** (`opportunities`) object for
sales-pipeline management. Prefer the typed `twenty_mcp_crm` tool over raw GraphQL —
it carries Twenty's opportunity field conventions and returns record-shaped payloads.

## When to use
- Triage the pipeline: list opportunities filtered/ordered by stage, amount, or close date.
- Read a single opportunity by its record UUID.
- Create a new opportunity for a company, with amount and expected close date.
- Advance a deal's `stage`, revise its `amount`, or attach a point-of-contact.

## When NOT to use
- Creating/reading the people or companies a deal references → `twenty-contacts`.
- Bulk-loading opportunities into the knowledge graph → `twenty-kg-sync`.
- Adding custom pipeline stages or fields (schema) → `twenty_mcp_metadata`.
- Ad-hoc cross-object GraphQL → `twenty_mcp_graphql` / `execute_gql` action.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`twenty-mcp`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `TWENTY_URL` | ✅ | Workspace base URL (alias `TWENTY_MCP_BASE_URL`) |
| `TWENTY_TOKEN` | ✅ | Twenty API key / access token |
| `TWENTY_MCP_SSL_VERIFY` | optional | TLS verification toggle |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface vs. the
one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `twenty_mcp_crm` | `get_opportunities`, `get_opportunity`, `create_opportunity`, `update_opportunity`, `delete_opportunity`, `find_records`, `find_duplicates` |

### Key parameters
- `opportunity_id` — required for the single-record and update/delete actions.
- `name`, `amount` — for `create_opportunity` (extra fields like `stage`,
  `closeDate`, `companyId`, `pointOfContactId` pass through `**kwargs`).
- `data` — object of field→value for `update_opportunity` (e.g. move `stage`).
- `find_records` with `object_name: "opportunities"` plus `filter` / `order_by` /
  `limit` for pipeline queries.

## Recipes (`params_json`)
List open pipeline, highest-value first:
```json
{"params": {"order_by": "amount", "limit": 25}}
```
Filter opportunities at a given stage:
```json
{"object_name": "opportunities", "filter": "stage[eq]:PROPOSAL", "order_by": "closeDate", "limit": 50}
```
Create an opportunity for a company with a point-of-contact:
```json
{"name": "Acme — Platform expansion", "amount": 48000, "stage": "NEW", "companyId": "<company_uuid>", "pointOfContactId": "<person_uuid>"}
```
Advance a deal to the next stage:
```json
{"opportunity_id": "<uuid>", "data": {"stage": "MEETING"}}
```
Revise amount and close date:
```json
{"opportunity_id": "<uuid>", "data": {"amount": {"amountMicros": 52000000000, "currencyCode": "USD"}, "closeDate": "2026-09-30T00:00:00Z"}}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Amount is a composite money field: reads/writes use
  `{"amount": {"amountMicros": <int>, "currencyCode": "USD"}}` — `amountMicros` is the
  major-unit value × 1,000,000. The convenience `create_opportunity(amount=…)` accepts
  a plain number, but `update_opportunity` writes the raw composite shape.
- `stage` values are the workspace's pipeline enum (e.g. `NEW`, `SCREENING`,
  `MEETING`, `PROPOSAL`, `CUSTOMER`) — confirm the enum via `twenty_mcp_metadata`
  before setting an unfamiliar value.
- `companyId` / `pointOfContactId` are **UUIDs** of existing records — create the
  company/person via `twenty-contacts` first.
- Record ids are UUIDs; list reads nest under `data.opportunities`.

## Related
- **Contacts:** `twenty-contacts` for the people/companies a deal links to.
- **KG:** `twenty-kg-sync` ingests opportunities as typed `:Opportunity` nodes with
  `:opportunityFor` / `:pointOfContact` links.
