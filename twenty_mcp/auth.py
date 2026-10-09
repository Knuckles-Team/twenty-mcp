"""CONCEPT:TW-OS.identity.twenty Identity credentials loader and session manager."""

import logging
from typing import Any

from agent_connector_sdk.config import setting
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from twenty_mcp.api_client import Api

logger = logging.getLogger(__name__)


def get_client() -> Api:
    """Get authenticated client for twenty_mcp."""
    base_url = setting("TWENTY_URL", "") or setting("TWENTY_MCP_BASE_URL", "")
    token = setting("TWENTY_TOKEN", "")
    username = setting("TWENTY_MCP_USERNAME", "")
    password = setting("TWENTY_MCP_PASSWORD", "")
    tls_profile = resolve_tls_profile(
        "twenty",
        profile_name=setting("TWENTY_TLS_PROFILE", None),
        profile_ref=setting("TWENTY_TLS_PROFILE_REF", None),
    )

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        tls_profile=tls_profile,
    )


def get_graphql_client(
    instance: str | None = None,
    token: str | None = None,
    tls_profile: ResolvedTLSProfile | None = None,
    config: dict | None = None,
) -> Any:
    """Factory function to create the Twenty GraphQL client.

    Supports OIDC delegation (RFC 8693 token exchange via
    ``agent_connector_sdk.auth.delegation``, when enabled) and a fixed-token
    fallback.

    Twenty allows unauthenticated auth-flow mutations, so a missing token is
    NOT a hard failure — the GraphQL client is simply constructed without an
    ``Authorization`` header.
    """
    instance = (
        instance or setting("TWENTY_URL", "") or setting("TWENTY_MCP_BASE_URL", "")
    )
    if token is None:
        token = setting("TWENTY_TOKEN", "")
    profile = tls_profile or resolve_tls_profile(
        "twenty",
        profile_name=setting("TWENTY_TLS_PROFILE", None),
        profile_ref=setting("TWENTY_TLS_PROFILE_REF", None),
    )

    if not instance:
        instance = "http://localhost"

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    from agent_connector_sdk.auth.delegation import DelegationSettings

    from twenty_mcp.twenty_gql import GraphQL

    delegation_enabled = (
        bool(config.get("enable_delegation", False))
        if config is not None
        else DelegationSettings.from_settings().enabled
    )

    if delegation_enabled:
        try:
            import httpx
            from agent_connector_sdk.auth.delegation import (
                current_user_token,
                exchange_token,
            )
            from agent_connector_sdk.exceptions import LoginRequiredError

            settings = DelegationSettings.from_settings()
            subject_token = current_user_token()
            if not subject_token:
                raise LoginRequiredError("no verified caller token to delegate")
            with httpx.Client(timeout=30) as http_client:
                access_token = exchange_token(
                    settings, subject_token=subject_token, http_client=http_client
                )
            logger.info("Using OIDC delegated token for Twenty GraphQL API")
            return GraphQL(
                url=instance,
                token=access_token.value,
                tls_profile=profile,
            )
        except Exception as e:
            logger.error(
                "OIDC delegation failed for Twenty GraphQL",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": type(e).__name__,
                },
            )
            # Fall through to fixed-token path on delegation failure.

    # --- Path 2: Fixed Credentials (TWENTY_TOKEN) — token may be empty ---
    logger.info("Using fixed credentials for Twenty GraphQL API")
    return GraphQL(url=instance, token=token or None, tls_profile=profile)
