---
name: twenty-kg-sync
skill_type: skill
description: >-
  Ingest Twenty CRM people, companies and opportunities into the knowledge graph with `twenty_ingest_records` as typed nodes with links. Use to mirror a workspace into the graph or refresh CRM nodes before a graph query. Do NOT use for changing contacts or deals (use twenty-contacts or twenty-pipeline).
license: MIT
tags: [twenty, crm, knowledge-graph, ingestion]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty to Knowledge Graph

Scope: Ingest Twenty CRM records into the knowledge graph with `twenty_ingest_records`: people, companies and opportunities become typed `:Person`, `:Company` and `:Opportunity` nodes linked by `:worksAt`, `:opportunityFor` and `:pointOfContact`. Use when the agent must mirror a workspace into the graph, refresh CRM nodes before a graph query, or make deals and accounts available for cross-source reasoning. Do NOT use for day-to-day changes to contacts or deals (use twenty-contacts or twenty-pipeline); ingestion reads Twenty and writes only to the graph.

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

## Steps

1. List the workspace objects with `twenty_get_metadata_objects` and verify the target object name exists.
2. Ingest companies first with `twenty_ingest_records` and `object_name` set to companies, and verify the result reports a listed count.
3. Ingest people next with `twenty_ingest_records` and `object_name` set to people, and verify the count is returned.
4. Ingest opportunities last with `twenty_ingest_records` and `object_name` set to opportunities, so link targets already exist, and verify the count is returned.
5. Check the `ingested` field of each result, and verify it is not null so the graph write landed.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `"ingested": null` in the result | No graph engine is reachable | Start or point the graph engine configuration at a reachable engine and call `twenty_ingest_records` again |
| Unknown object name error | `object_name` is not one of people, companies or opportunities | Use a name from `twenty_get_metadata_objects` that the tool supports |
| `params_json` rejected | It was sent as an object | Pass a JSON string such as `{"limit": 60}` |
| Links are missing in the graph | Opportunities or people were ingested before companies | Ingest companies, then people, then opportunities in that order |

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
