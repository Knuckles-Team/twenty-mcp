---
name: twenty-pipeline
skill_type: skill
description: >-
  Drive the sales pipeline in Twenty CRM through the twenty-mcp tools: list, read, open, update and delete opportunities with `twenty_get_opportunities`, `twenty_create_opportunity`, `twenty_update_opportunity` and related tools. Use when the agent must triage deals by stage, open a deal for a company, move a deal to a new stage, or change its amount or close date.
license: MIT
tags: [twenty, crm, pipeline, opportunities]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty Pipeline

Scope: Drive the sales pipeline in Twenty CRM through the twenty-mcp tools: list, read, open, update and delete opportunities with `twenty_get_opportunities`, `twenty_create_opportunity`, `twenty_update_opportunity` and related tools. Use when the agent must triage deals by stage, open a deal for a company, move a deal to a new stage, or change its amount or close date. Do NOT use for people and companies (use twenty-contacts), for other objects (use twenty-records), or for knowledge graph ingestion (use twenty-kg-sync).

An opportunity is a deal. It carries a name, an `amount`, a `stage`, a `closeDate`, a company
(`companyId`) and a point of contact (`pointOfContactId`).

## When to use
- Review the pipeline by stage and find stale or large deals.
- Open a deal for an existing company.
- Move a deal to its next stage, or change its amount, close date or contact.
- Delete a deal the owner asked to remove.

## When NOT to use
- Managing the people and companies behind a deal: `twenty-contacts`.
- Notes, tasks and custom objects: `twenty-records`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Steps

1. List the deals with `twenty_get_opportunities`, ordered by `updatedAt` or `closeDate`, and verify the stages returned.
2. Confirm the company for a new deal with `twenty_get_company` and verify the id and name match the request.
3. Open the deal with `twenty_create_opportunity`, passing `companyId` in `params_json`, and verify the response returns the opportunity id.
4. Move a deal with `twenty_update_opportunity`, changing only the stage or amount, and verify with `twenty_get_opportunity` that the new value is stored.
5. Delete with `twenty_delete_opportunity` only after the owner approves and `confirm=true` is passed, and verify a follow-up read returns not found.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Update rejects the stage value | The stage spelling differs from the workspace labels | Read a deal with `twenty_get_opportunity` and copy its exact stage value |
| `amount` is rejected | It was sent as a plain number | Send the composite shape with `amountMicros` and `currencyCode` copied from an existing deal |
| 401 or 403 from a tool | `TWENTY_TOKEN` is missing or expired | Set a valid `TWENTY_TOKEN` for the `twenty-mcp` server |
| A delete is refused | `confirm=true` was not supplied | Obtain the owner's approval and pass `confirm=true` |

## Tools
| Tool | Use |
|---|---|
| `twenty_get_opportunities` | List deals; `params` takes `filter`, `order_by`, `limit`. |
| `twenty_get_opportunity` | Read one deal by `opportunity_id`. |
| `twenty_create_opportunity` | Create a deal from `name`, `amount` and extra fields in `params_json`. |
| `twenty_update_opportunity` | Change fields with a `data` object, for example `{"stage": "MEETING"}`. |
| `twenty_delete_opportunity` | Delete by id. Destructive. |
| `twenty_get_company` | Confirm the company a new deal belongs to. |

## Procedure
1. List with `twenty_get_opportunities`, ordered by `updatedAt` or `closeDate`, and group by `stage`.
2. To open a deal, read the company with `twenty_get_company`, create the opportunity with its `companyId` in `params_json`, then read it back.
3. To advance a deal, read it, then update only the changed fields. Report the old and new stage.
4. Delete only after the owner approves; read the deal first.

## Gotchas
- Stage values are the workspace's own labels (NEW, SCREENING, MEETING, PROPOSAL, CUSTOMER by default). Read a deal first to copy the exact spelling.
- `amount` is a composite object (`amountMicros`, `currencyCode`) in Twenty's REST schema; copy the shape of an existing deal.
