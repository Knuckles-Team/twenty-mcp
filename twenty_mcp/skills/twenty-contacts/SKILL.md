---
name: twenty-contacts
description: >-
  Manage people (contacts) and companies (accounts) in Twenty CRM via the
  twenty-mcp MCP server — list, search, read, create, and update person and
  company records with the domain-typed `twenty_mcp_crm` tool. Use when the agent
  must find a contact by name/email, look up or create a company, link a person to
  their employer, or keep account details current. Do NOT use for sales
  opportunities / deal pipeline (use twenty-pipeline), for pushing CRM records into
  the knowledge graph (use twenty-kg-sync), or for schema/object-metadata changes
  (use the twenty_mcp_metadata tool).
license: MIT
tags: [twenty, crm, contacts, companies, people, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Twenty Contacts & Companies

Domain-typed access to Twenty's **People** (`people`) and **Companies**
(`companies`) objects for CRM contact and account management. Prefer the typed
`twenty_mcp_crm` tool over raw GraphQL — it carries the Twenty REST field
conventions and returns record-shaped payloads.

## When to use
- Find a person by name or email, or a company by name/domain.
- Read a single contact or account by its record UUID.
- Create a new person (firstName/lastName/email) or company (name/domain).
- Update contact/account fields, or link a person to their employer company.

## When NOT to use
- Sales opportunities / deal stages → `twenty-pipeline`.
- Bulk-loading CRM records into the knowledge graph → `twenty-kg-sync`.
- Creating or altering custom objects/fields (schema) → `twenty_mcp_metadata`.
- Arbitrary GraphQL against custom schemas → `twenty_mcp_graphql` /
  `execute_gql` action.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`twenty-mcp`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `TWENTY_URL` | ✅ | Workspace base URL (alias `TWENTY_MCP_BASE_URL`) |
| `TWENTY_TOKEN` | ✅ | Twenty API key / access token |
| `TWENTY_MCP_SSL_VERIFY` | optional | TLS verification toggle |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface
(used below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `twenty_mcp_crm` | `get_people`, `get_person`, `create_person`, `update_person`, `delete_person`, `get_companies`, `get_company`, `create_company`, `update_company`, `delete_company`, `find_records`, `find_duplicates` |

### Key parameters
- `person_id` / `company_id` — required for the single-record and update/delete actions.
- `first_name`, `last_name`, `email` — for `create_person`; `name`, `domain` — for `create_company`.
- `data` — object of field→value for `update_person` / `update_company`.
- `find_records` takes `object_name` ("people"|"companies") plus `filter`,
  `order_by`, `limit`, `depth`, and cursor params (`starting_after` / `ending_before`).

## Recipes (`params_json`)
List the 25 most recently updated people:
```json
{"params": {"order_by": "updatedAt", "limit": 25}}
```
Search people by email with the ergonomic finder:
```json
{"object_name": "people", "filter": "emails.primaryEmail[eq]:jane@acme.com", "limit": 5}
```
Create a contact:
```json
{"first_name": "Jane", "last_name": "Doe", "email": "jane@acme.com", "jobTitle": "VP Sales"}
```
Create a company:
```json
{"name": "Acme Corp", "domain": "acme.com"}
```
Link a person to their employer (update the person's `companyId`):
```json
{"person_id": "<uuid>", "data": {"companyId": "<company_uuid>"}}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Twenty stores composite fields nested: a person's name is
  `{"name": {"firstName", "lastName"}}` and email is `{"emails": {"primaryEmail"}}`;
  a company's domain is `{"domainName": {"primaryLinkUrl"}}`. Filters and reads use
  these dotted paths.
- Record ids are **UUIDs**, not sequential integers.
- List reads nest under `data.<object>` (e.g. `data.people`); a single read returns
  `data.<singular>`.
- Use `find_duplicates` before a bulk `create_person`/`create_company` to avoid
  duplicate accounts.

## Related
- **Deals:** `twenty-pipeline` for opportunities that reference these people/companies.
- **KG:** `twenty-kg-sync` ingests these records as typed `:Person` / `:Company` nodes.
