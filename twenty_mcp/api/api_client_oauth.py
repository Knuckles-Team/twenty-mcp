import hashlib
import hmac
from typing import Any
from urllib.parse import urljoin

from twenty_mcp.api.api_client_base import ApiClientBase


class OauthApi(ApiClientBase):
    """OAuth API for dynamic client registration, token operations, and webhook validation."""

    def register_oauth_client(
        self,
        client_name: str,
        redirect_uris: list[str],
        grant_types: list[str] | None = None,
        token_endpoint_auth_method: str = "client_secret_post",
    ) -> dict:
        """Register a new OAuth client dynamically per RFC 7591."""
        if grant_types is None:
            grant_types = ["authorization_code"]

        data = {
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "grant_types": grant_types,
            "token_endpoint_auth_method": token_endpoint_auth_method,
        }
        return self.request("POST", "/oauth/register", data=data)

    def get_oauth_discovery(self) -> dict:
        """Fetch the standard OAuth configuration server discovery metadata."""
        return self.request("GET", "/.well-known/oauth-authorization-server")

    def exchange_oauth_token(
        self,
        code: str,
        redirect_uri: str,
        client_id: str,
        client_secret: str,
        code_verifier: str | None = None,
    ) -> dict:
        """Exchange an authorization code for access and refresh tokens."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        return self._post_form_urlencoded("/oauth/token", data)

    def refresh_oauth_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> dict:
        """Refresh an expired access token using a refresh token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        return self._post_form_urlencoded("/oauth/token", data)

    def client_credentials_oauth_token(
        self,
        client_id: str,
        client_secret: str,
        scope: str = "api",
    ) -> dict:
        """Perform a server-to-server client credentials flow to get a workspace-scoped token."""
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
        return self._post_form_urlencoded("/oauth/token", data)

    # --- Helper Method ---

    def _post_form_urlencoded(self, endpoint: str, data: dict[str, Any]) -> dict:
        """Helper to send application/x-www-form-urlencoded POST requests."""
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = urljoin(self.base_url, endpoint)

        response = self._session.post(url, data=data)
        if response.status_code >= 400:
            raise Exception(
                f"OAuth/Token error: {response.status_code} - {response.text}"
            )

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}

    # --- Static Webhook Validation Helper ---

    @staticmethod
    def validate_webhook_signature(
        payload: str,
        signature: str,
        timestamp: str,
        secret: str,
    ) -> bool:
        """Validate an incoming webhook signature using HMAC SHA256 (timing safe)."""
        string_to_sign = f"{timestamp}:{payload}"
        expected_sig = hmac.new(
            secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
