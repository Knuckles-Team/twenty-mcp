---
name: twenty-records
skill_type: skill
description: >-
  Read and change any Twenty object, built-in or custom, through the generic record tools, including batch create, update and delete of up to 60 records per call. Use for notes, tasks, custom objects or changes touching many records. Do NOT use for single people, companies or deals (twenty-contacts, twenty-pipeline) or schema changes (twenty-metadata).
license: MIT
tags: [twenty, crm, records, batch]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty Records

Scope: Read and change any Twenty object, built-in or custom, through the generic record tools: `twenty_get_records`, `twenty_get_record`, `twenty_create_record`, `twenty_update_record`, `twenty_delete_record`, `twenty_find_records`, `twenty_find_duplicates` and the batch tools that create, update or delete up to 60 records per call. Use when the agent works with notes, tasks, custom objects, or any change that touches many records. Do NOT use for people, companies and deals one at a time (use twenty-contacts or twenty-pipeline) or for schema changes (use twenty-metadata).

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

## Steps

1. Resolve the object with `twenty_get_metadata_object` and verify the plural `object_name` and field names.
2. Select the target set with `twenty_find_records`, paging with `starting_after`, and verify the count and ids.
3. Screen new data with `twenty_find_duplicates` and verify no matching record exists.
4. Write with `twenty_create_record`, `twenty_update_record` or the batch tools in groups of at most 60, and verify a sample with `twenty_get_record`.
5. Delete with `twenty_delete_record` or `twenty_batch_delete_records` only after the owner approves the id list, passing `confirm=true`, and verify the ids no longer return.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| A batch call is refused | More than 60 records were sent | Split the list into groups of 60 or fewer and send each group |
| Batch update reports missing id errors | Records were sent without their `id` | Include the `id` in every record of the batch |
| Some records fail inside a successful batch | Batches are not atomic | Read the per-record errors in the response and resend only the failed records |
| Unknown object error | `object_name` is not the plural API name | Take the name from `twenty_get_metadata_object` |

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
