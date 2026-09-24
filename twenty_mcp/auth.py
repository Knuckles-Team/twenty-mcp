"""CONCEPT:TW-OS.identity.twenty Identity credentials loader and session manager."""

from typing import Any

from agent_connector_sdk.config import setting
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile
from agent_connector_sdk.utilities import get_logger

from twenty_mcp.api_client import Api

logger = get_logger(__name__)


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

    Supports OIDC delegation (when ``agent_connector_sdk.auth.delegation`` is
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
    profile = tls_profile or resolve_tls_profile(
        "twenty",
        profile_name=setting("TWENTY_TLS_PROFILE", None),
        profile_ref=setting("TWENTY_TLS_PROFILE_REF", None),
    )

    if not instance:
        instance = "http://localhost"

    from twenty_mcp.twenty_gql import GraphQL

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    # `config` is unused here (agent_connector_sdk.auth.delegation.DelegationSettings
    # always reads live env settings, like AU's fallback path did when config was
    # None; no caller in this codebase ever passes a non-default config). Unlike
    # AU's get_delegated_token (which defaulted a missing audience to `instance`),
    # the SDK's DelegationSettings requires AUDIENCE to be set whenever delegation
    # is enabled and fails closed (ValueError) otherwise — a stricter, intentional
    # contract, not silently reproduced here.
    try:
        import httpx
        from agent_connector_sdk.auth.delegation import (
            DelegationSettings,
            current_user_token,
            exchange_token,
        )

        delegation_settings = DelegationSettings.from_settings()
        delegation_enabled = delegation_settings.enabled
    except Exception:
        delegation_enabled = False

    if delegation_enabled:
        try:
            subject_token = current_user_token()
            if not subject_token:
                raise RuntimeError("no verified caller token is available")
            with httpx.Client(timeout=30) as exchange_client:
                delegated_token = exchange_token(
                    delegation_settings,
                    subject_token=subject_token,
                    http_client=exchange_client,
                )
            logger.info("Using OIDC delegated token for Twenty GraphQL API")
            return GraphQL(
                url=instance,
                token=delegated_token.value,
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
