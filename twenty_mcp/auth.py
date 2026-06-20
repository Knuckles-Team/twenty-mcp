"""CONCEPT:TWENTY-003 Identity credentials loader and session manager."""

from typing import Any

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting

from twenty_mcp.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for twenty_mcp."""
    base_url = setting("TWENTY_URL", "") or setting("TWENTY_MCP_BASE_URL", "")
    token = setting("TWENTY_TOKEN", "")
    username = setting("TWENTY_MCP_USERNAME", "")
    password = setting("TWENTY_MCP_PASSWORD", "")
    verify = setting("TWENTY_MCP_SSL_VERIFY", True)

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        verify=verify,
    )


def get_graphql_client(
    instance: str | None = None,
    token: str | None = None,
    verify: bool | None = None,
    config: dict | None = None,
) -> Any:
    """Factory function to create the Twenty GraphQL client.

    Supports OIDC delegation (when ``agent_utilities.mcp.delegated_auth`` is
    available and delegation is enabled) and a fixed-token fallback.

    Twenty allows unauthenticated auth-flow mutations, so a missing token is
    NOT a hard failure — the GraphQL client is simply constructed without an
    ``Authorization`` header.
    """
    instance = (
        instance or setting("TWENTY_URL", "") or setting("TWENTY_MCP_BASE_URL", "")
    )
    if token is None:
        token = setting("TWENTY_TOKEN", "")
    if verify is None:
        verify = setting("TWENTY_MCP_SSL_VERIFY", True)

    if not instance:
        instance = "http://localhost"

    from twenty_mcp.twenty_gql import GraphQL

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    try:
        from agent_utilities.mcp.delegated_auth import (
            get_delegated_token,
            get_user_identity,
            is_delegation_enabled,
        )

        delegation_enabled = is_delegation_enabled(config)
    except Exception:
        delegation_enabled = False

    if delegation_enabled:
        try:
            delegated_token = get_delegated_token(
                config=config,
                audience=(config or {}).get("audience", instance),
                scopes=(config or {}).get("delegated_scopes", "api"),
                verify=verify,
            )
            identity = get_user_identity()
            logger.info(
                "Using OIDC delegated token for Twenty GraphQL API",
                extra={
                    "user_email": identity.get("email"),
                    "instance": instance,
                },
            )
            return GraphQL(url=instance, token=delegated_token, verify=verify)
        except Exception as e:
            logger.error(
                "OIDC delegation failed for Twenty GraphQL",
                extra={"error_type": type(e).__name__, "error_message": str(e)},
            )
            # Fall through to fixed-token path on delegation failure.

    # --- Path 2: Fixed Credentials (TWENTY_TOKEN) — token may be empty ---
    logger.info("Using fixed credentials for Twenty GraphQL API")
    return GraphQL(url=instance, token=token or None, verify=verify)
