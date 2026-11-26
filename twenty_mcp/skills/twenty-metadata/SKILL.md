---
name: twenty-metadata
skill_type: skill
description: >-
  Inspect and change the Twenty workspace schema through the metadata tools: read objects, fields and relations (`twenty_get_metadata`), define custom objects, fields and relations (`twenty_create_metadata_<op>`), update them (`twenty_update_metadata_<op>`) and drop them (`twenty_delete_metadata_<op>`). Use when the agent must model a new object, add a field, relate two objects, or audit the schema.
license: MIT
tags: [twenty, crm, metadata, schema]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty Metadata

Scope: Inspect and change the Twenty workspace schema through the metadata tools: read objects, fields and relations (`twenty_get_metadata`), define custom objects, fields and relations (`twenty_create_metadata_<op>`), update them (`twenty_update_metadata_<op>`) and drop them (`twenty_delete_metadata_<op>`). Use when the agent must model a new object, add a field, relate two objects, or audit the schema. Do NOT use for record data (use twenty-records) or for GraphQL queries (use twenty-graphql).

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

## Steps

1. Read the current schema with `twenty_get_metadata_object` and verify the object and its fields are as expected before any change.
2. Create a custom object with `twenty_create_metadata_object` and verify the response returns its id.
3. Add fields and relations with `twenty_create_metadata_field` and `twenty_create_metadata_relation`, and verify each appears when the object is read back.
4. Change a definition with `twenty_update_metadata_object`, `twenty_update_metadata_field` or `twenty_update_metadata_relation`, and verify the new label or state on a re-read.
5. Drop a model only after approval, deleting relations, fields and the object in that order with `twenty_delete_metadata_relation`, `twenty_delete_metadata_field` and `twenty_delete_metadata_object`, passing `confirm=true`, and verify the object no longer lists.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Delete refused for an object | It is a standard object | Standard objects cannot be deleted, so deactivate it with `twenty_update_metadata_object` if needed |
| A delete is rejected | `confirm=true` was not supplied | Obtain the owner's approval and pass `confirm=true` |
| Create fails with a name error | The name clashes with an existing object or field | Read names with `twenty_get_metadata_objects` and choose a unique one |
| 401 or 403 from a tool | `TWENTY_TOKEN` is missing or lacks admin rights | Set an API key with metadata rights for the `twenty-mcp` server |

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
