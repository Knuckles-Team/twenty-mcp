---
name: twenty-metadata
skill_type: skill
description: >-
  Inspect and change the Twenty workspace schema through the metadata tools: read objects, fields and
  relations (`twenty_get_metadata*`), define custom objects, fields and relations (`twenty_create_metadata_*`),
  update them (`twenty_update_metadata_*`) and drop them (`twenty_delete_metadata_*`). Use when the agent
  must model a new object, add a field, relate two objects, or audit the schema. Do NOT use for record data
  (use twenty-records) or for GraphQL queries (use twenty-graphql).
license: MIT
tags: [twenty, crm, metadata, schema]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty Metadata

The metadata API describes the workspace meta-model: objects hold fields, and relations join objects.
GraphQL introspection is off, so this is the way to learn the schema.

## When to use
- Audit objects, fields and relations.
- Create a custom object, add fields, relate it to people or companies.
- Rename, relabel or deactivate a field, object or relation.
- Drop a custom object, field or relation the owner asked to remove.

## When NOT to use
- Reading or writing records: `twenty-records`.
- GraphQL calls: `twenty-graphql`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Tools
| Tool | Use |
|---|---|
| `twenty_get_metadata` | The whole schema. |
| `twenty_get_metadata_objects`, `twenty_get_metadata_object` | All objects, or one by name or id. |
| `twenty_get_metadata_fields`, `twenty_get_metadata_field` | All fields (`params`), or one by `field_id`. |
| `twenty_get_metadata_relations`, `twenty_get_metadata_relation` | All relations, or one by `relation_id`. |
| `twenty_create_metadata_object`, `twenty_create_metadata_field`, `twenty_create_metadata_relation` | Create from a `data` object. |
| `twenty_update_metadata_object`, `twenty_update_metadata_field`, `twenty_update_metadata_relation` | Change by id with `data`. |
| `twenty_delete_metadata_relation`, `twenty_delete_metadata_field`, `twenty_delete_metadata_object` | Remove. Destructive; drops stored data. |
| `twenty_request_metadata` | Raw `method` and `endpoint` under `/rest/metadata`, for endpoints no typed tool covers. |

## Procedure
1. Read the current object with `twenty_get_metadata_object` before any change.
2. To add a model: create the object, then its fields, then its relations; read the object back.
3. To drop a model: delete relations, then fields, then the object, in that order, after approval.
4. Use `twenty_request_metadata` only when no typed tool fits.

## Gotchas
- Deleting a field or object removes every value stored in it. It cannot be undone.
- Standard objects cannot be deleted; only custom ones.
