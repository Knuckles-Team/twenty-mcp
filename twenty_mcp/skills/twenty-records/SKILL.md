---
name: twenty-records
skill_type: skill
description: >-
  Read and change any Twenty object, built-in or custom, through the generic record tools:
  `twenty_get_records`, `twenty_get_record`, `twenty_create_record`, `twenty_update_record`,
  `twenty_delete_record`, `twenty_find_records`, `twenty_find_duplicates` and the batch tools that
  create, update or delete up to 60 records per call. Use when the agent works with notes, tasks, custom
  objects, or any change that touches many records. Do NOT use for people, companies and deals one at a
  time (use twenty-contacts or twenty-pipeline) or for schema changes (use twenty-metadata).
license: MIT
tags: [twenty, crm, records, batch]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty Records

One set of tools serves every object because Twenty exposes each object at the same REST path. The
`object_name` argument is the plural API name (`notes`, `tasks`, `people`, or a custom object).

## When to use
- Read, create, update or delete a record of a note, task or custom object.
- Select many records with a filter and change them in a batch.
- Screen a batch for duplicates before creating it.

## When NOT to use
- One person, company or deal: `twenty-contacts`, `twenty-pipeline`.
- Creating objects, fields or relations: `twenty-metadata`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Tools
| Tool | Use |
|---|---|
| `twenty_get_metadata_object` | Resolve an object name or id and read its fields before writing. |
| `twenty_get_records`, `twenty_get_record` | List an object, read one record. |
| `twenty_find_records` | Search with `filter`, `order_by`, `limit`, `depth`, `starting_after`, `ending_before`. |
| `twenty_find_duplicates` | Duplicate check by `data` or by `ids`. |
| `twenty_create_record`, `twenty_update_record` | Create or change one record. |
| `twenty_batch_create_records`, `twenty_batch_update_records` | Up to 60 records per call; a larger list is refused. |
| `twenty_delete_record`, `twenty_batch_delete_records` | Delete one or many by id. Destructive. |

## Procedure
1. Resolve the object with `twenty_get_metadata_object` so field names are exact.
2. Select the target set with `twenty_find_records` and page with `starting_after`.
3. Write in batches of at most 60. Read a sample back after each batch.
4. For deletes, list the ids and get approval first.

## Gotchas
- Batch update records must each carry their `id`.
- A batch is not atomic across records: read the response for per-record errors.
