# Twenty to Knowledge Graph

Ingest Twenty CRM records into the knowledge graph with `twenty_ingest_records`: people, companies and opportunities become typed `:Person`, `:Company` and `:Opportunity` nodes linked by `:worksAt`, `:opportunityFor` and `:pointOfContact`. Use when the agent must mirror a workspace into the graph, refresh CRM nodes before a graph query, or make deals and accounts available for cross-source reasoning. Do NOT use for day-to-day changes to contacts or deals (use twenty-contacts or twenty-pipeline); ingestion reads Twenty and writes only to the graph.

# Twenty to Knowledge Graph

`twenty_ingest_records` lists one Twenty object through the CRM client and pushes each record to the
graph as a node with its relationships. It never changes Twenty.

## When to use
- Mirror people, companies or opportunities into the graph.
- Refresh CRM nodes before a graph query or a cross-source join.

## When NOT to use
- Creating, changing or deleting CRM records: `twenty-contacts`, `twenty-pipeline`, `twenty-records`.
- Schema changes: `twenty-metadata`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.
A reachable graph engine is needed for the write to land. Without one the tool returns `"ingested": null`
and still reports what it listed.

## Tools
| Tool | Use |
|---|---|
| `twenty_get_metadata_objects` | List the objects of the workspace so the right `object_name` is chosen. |
| `twenty_ingest_records` | Ingest one object. `object_name` is `people`, `companies` or `opportunities`; `params_json` is a JSON string of list filters such as `{"limit": 60}`. |

## What is written
| Object | Node | Links |
|---|---|---|
| people | `:Person` (name, primaryEmail, jobTitle) | `:worksAt` to `:Company` |
| companies | `:Company` (name, domainName, employees) | none |
| opportunities | `:Opportunity` (name, amount, currencyCode, stage, closeDate) | `:opportunityFor` to `:Company`, `:pointOfContact` to `:Person` |

Node ids follow `twenty:<class>:<record-uuid>`. Ingest companies first, then people, then opportunities,
so every link target already exists.
