# Twenty Contacts & Companies

Manage people (contacts) and companies (accounts) in Twenty CRM through the twenty-mcp tools: find, read, create, update and delete a person or a company with the typed `twenty_*_person` and `twenty_*_company` tools. Use when the agent must find a contact by name or email, look up or create a company, link a person to an employer, or keep account details current. Do NOT use for deals (use twenty-pipeline), for any other object or bulk change (use twenty-records), or for pushing records into the knowledge graph (use twenty-kg-sync).

# Twenty Contacts & Companies

People (`people`) and companies (`companies`) are the core of a Twenty workspace. A person links to
its employer through `companyId`; an opportunity links to both.

## When to use
- Find a person by name or email, or a company by name or domain.
- Read one contact or account by its record UUID.
- Create a person (first name, last name, email) or a company (name, domain).
- Change contact or account fields, or set a person's `companyId`.
- Delete a contact or account that the owner asked to remove.

## When NOT to use
- Deals and pipeline stages: `twenty-pipeline`.
- Notes, tasks, custom objects and batch changes: `twenty-records`.
- Mirroring the workspace into the knowledge graph: `twenty-kg-sync`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Tools
| Tool | Use |
|---|---|
| `twenty_find_records` | Search an object (`object_name` = `people` or `companies`) with `filter`, `order_by`, `limit`, `depth` and cursor arguments. |
| `twenty_get_people`, `twenty_get_person` | List contacts (`params`), read one (`person_id`). |
| `twenty_get_companies`, `twenty_get_company` | List accounts, read one (`company_id`). |
| `twenty_find_duplicates` | Screen a payload (`data`) or a list of `ids` for duplicates before creating. |
| `twenty_create_person`, `twenty_create_company` | Create a record; extra fields go in `params_json`. |
| `twenty_update_person`, `twenty_update_company` | Change fields with a `data` object. |
| `twenty_delete_person`, `twenty_delete_company` | Delete by id. Destructive. |

## Procedure
1. Search first: `twenty_find_records` with a filter such as `emails.primaryEmail[eq]:<address>`.
2. Before a create, run `twenty_find_duplicates` on the new payload. Reuse an existing record when one matches.
3. Create or update, then read the record back with `twenty_get_person` or `twenty_get_company` and report its id.
4. For a delete, read the record, show the owner what will go, and delete only after approval.

## Gotchas
- Composite fields nest: a person's name is `name.firstName` and `name.lastName`, the email is
  `emails.primaryEmail`, a company's domain is `domainName.primaryLinkUrl`.
- Record ids are UUIDs. List reads nest under `data.people` or `data.companies`.
- `params_json` is a JSON string, not an object.
