---
name: twenty-oauth
skill_type: skill
description: >-
  Handle Twenty OAuth and webhooks: read the server metadata (`twenty_get_oauth_discovery`), register a client
  (`twenty_register_oauth_client`), exchange or refresh tokens (`twenty_exchange_oauth_token`,
  `twenty_refresh_oauth_token`), get a server-to-server token (`twenty_client_credentials_oauth_token`) and
  verify webhook signatures (`twenty_validate_webhook_signature`). Use when an application must sign in to
  Twenty, renew a token, or trust an incoming webhook. Do NOT use for first-time workspace bootstrap and API
  key creation (use twenty-provisioner) or for record data (use twenty-records).
license: MIT
tags: [twenty, crm, oauth, webhooks]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# Twenty OAuth and Webhooks

## When to use
- Register an OAuth client for an application (RFC 7591).
- Exchange an authorization code (with PKCE `code_verifier`), then refresh before expiry.
- Obtain a workspace-scoped token for a backend job with client credentials.
- Verify that a webhook came from Twenty.

## When NOT to use
- Day-0 admin account and API key: `twenty-provisioner`.
- Record reads and writes: `twenty-records`.

## Prerequisites & environment
Connect to the **`twenty-mcp`** MCP server. It needs `TWENTY_URL` (workspace base URL) and `TWENTY_TOKEN`
(API key or access token). Every tool is a typed, per-operation call; there is no `action` argument.
Tools that delete or drop data are marked destructive and need an explicit `confirm`.

## Tools
| Tool | Use |
|---|---|
| `twenty_get_oauth_discovery` | The issuer, endpoints and supported grants. Read first. |
| `twenty_register_oauth_client` | `client_name`, `redirect_uris`, `grant_types`, `token_endpoint_auth_method`. |
| `twenty_exchange_oauth_token` | `code`, `redirect_uri`, `client_id`, `client_secret`, `code_verifier`. |
| `twenty_refresh_oauth_token` | `refresh_token`, `client_id`, `client_secret`. |
| `twenty_client_credentials_oauth_token` | `client_id`, `client_secret`, `scope`. |
| `twenty_validate_webhook_signature` | HMAC-SHA256 check of `payload`, `signature`, `timestamp` with `secret`; timing safe. |

## Procedure
1. Read discovery and use only grants it lists.
2. Keep `client_secret`, tokens and webhook secrets out of replies, logs and notes.
3. Verify a webhook before acting on its payload; reject an old `timestamp`.

## Gotchas
- A refresh token may rotate; store the new one.
- The signature covers the exact raw payload bytes, so do not reformat the JSON before checking.
