#!/usr/bin/python
"""CONCEPT:TWENTY-004 Standardized GraphQL client for the Twenty CRM API.

Mirrors the ``gitlab-api`` GraphQL pattern (``gql`` library +
``RequestsHTTPTransport`` + ``execute_gql``) while accounting for Twenty's
specifics:

* Introspection is **disabled** on Twenty, so the ``gql`` ``Client`` is built
  with ``fetch_schema_from_transport=False`` (constructing with ``True`` would
  fail).
* Auth-flow mutations (e.g. ``getLoginTokenFromCredentials``) are intentionally
  unauthenticated, so ``token`` is **optional** — the ``Authorization`` header
  is only attached when a token is present, and no ``@require_auth`` decorator
  is used.
* Twenty serves its **core/auth/system** GraphQL schema at ``/metadata`` (NOT
  ``/graphql``). The ``/graphql`` endpoint only exposes the per-workspace
  OBJECT schema (companies/people CRUD). Auth, API-key, role, and SSO
  operations therefore route through the dedicated *core* client/endpoint.
* Twenty validates the request ``Origin`` header against the configured base
  URL; both clients send ``Origin: <url>`` and the auth mutations also pass an
  ``origin`` argument equal to the base URL.
"""

import logging
from typing import Any

from agent_utilities.core.exceptions import MissingParameterError, ParameterError
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class GraphQL:
    """Interact with Twenty's GraphQL API.

    Provides a raw ``execute_gql`` passthrough plus GraphQL-native parity
    methods (API keys, auth tokens, SSO, and a generic ``find_many`` reader).
    """

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        api_path: str = "/graphql",
        core_path: str = "/metadata",
        verify: bool = True,
        proxies: dict | None = None,
        debug: bool = False,
    ):
        if not url:
            raise MissingParameterError("URL is required")

        self.url = url.rstrip("/")
        # Twenty validates Origin against the base URL.
        self.origin = self.url
        self.token = token
        self.api_path = api_path
        self.core_path = core_path
        self.verify = verify
        self.proxies = proxies
        self.debug = debug

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        # Object/data schema (companies/people CRUD).
        self.endpoint = f"{self.url}{api_path}"
        # Core/auth/system schema (auth, API keys, roles, SSO, clientConfig).
        self.core_endpoint = f"{self.url}{core_path}"

        headers: dict[str, str] = {"Origin": self.origin}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.headers = headers

        self.transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=headers,
            verify=verify,
            proxies=proxies,
        )
        self.core_transport = RequestsHTTPTransport(
            url=self.core_endpoint,
            headers=headers,
            verify=verify,
            proxies=proxies,
        )
        # Twenty disables GraphQL introspection; never fetch the schema.
        self.client = Client(
            transport=self.transport, fetch_schema_from_transport=False
        )
        self.core_client = Client(
            transport=self.core_transport, fetch_schema_from_transport=False
        )

    def execute_gql(
        self,
        query_str: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        core: bool = False,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query_str: The GraphQL query or mutation string.
            variables: Optional dictionary of variables for the query.
            operation_name: Optional name of the operation.
            core: When True, route to Twenty's core/auth schema at
                ``/metadata`` instead of the object schema at ``/graphql``.

        Returns:
            Dict[str, Any]: The raw GraphQL response dictionary.

        Raises:
            ParameterError: If the query execution fails.
        """
        client = self.core_client if core else self.client
        try:
            query = gql(query_str)
            result = client.execute(
                query, variable_values=variables, operation_name=operation_name
            )
            return result
        except Exception as e:
            logging.error(f"GraphQL execution failed: {str(e)}")
            raise ParameterError(f"Query execution failed: {str(e)}") from e

    # --- Auth / API key mutations (route through the CORE /metadata schema) ---

    def create_api_key(
        self, name: str, expires_at: str, role_id: str
    ) -> dict[str, Any]:
        """Create a new API key in the workspace.

        Args:
            name: Human-readable name for the API key.
            expires_at: ISO-8601 expiration timestamp.
            role_id: UUID of the role to assign to the key (REQUIRED).

        Returns:
            Dict[str, Any]: Raw GraphQL response with the created API key.
        """
        query = """
        mutation ($name: String!, $expiresAt: String!, $roleId: UUID!) {
            createApiKey(input: { name: $name, expiresAt: $expiresAt, roleId: $roleId }) {
                id
                name
                expiresAt
            }
        }
        """
        variables = {"name": name, "expiresAt": expires_at, "roleId": role_id}
        return self.execute_gql(query, variables=variables, core=True)

    def generate_api_key_token(
        self, api_key_id: str, expires_at: str
    ) -> dict[str, Any]:
        """Generate a JWT token for an existing API key.

        Args:
            api_key_id: UUID of the API key.
            expires_at: ISO-8601 expiration timestamp.

        Returns:
            Dict[str, Any]: Raw GraphQL response containing the token.
        """
        query = """
        mutation ($apiKeyId: UUID!, $expiresAt: String!) {
            generateApiKeyToken(apiKeyId: $apiKeyId, expiresAt: $expiresAt) {
                token
            }
        }
        """
        variables = {"apiKeyId": api_key_id, "expiresAt": expires_at}
        return self.execute_gql(query, variables=variables, core=True)

    def get_roles(self) -> dict[str, Any]:
        """List the workspace roles (authenticated; core schema).

        Returns:
            Dict[str, Any]: Raw GraphQL response with ``getRoles`` entries,
            each carrying ``id``, ``label`` and ``canUpdateAllSettings``.
        """
        query = """
        query {
            getRoles {
                id
                label
                canUpdateAllSettings
            }
        }
        """
        return self.execute_gql(query, core=True)

    def get_login_token_from_credentials(
        self,
        email: str,
        password: str,
        origin: str | None = None,
        captcha_token: str | None = None,
    ) -> dict[str, Any]:
        """Exchange email/password credentials for a short-lived login token.

        This mutation is intentionally unauthenticated. Twenty requires an
        ``origin`` argument matching the workspace base URL.

        Args:
            email: User email.
            password: User password.
            origin: Workspace origin URL; defaults to the client base URL.
            captcha_token: Optional captcha token.

        Returns:
            Dict[str, Any]: Raw GraphQL response with the login token.
        """
        query = """
        mutation ($email: String!, $password: String!, $origin: String!) {
            getLoginTokenFromCredentials(email: $email, password: $password, origin: $origin) {
                loginToken {
                    token
                    expiresAt
                }
            }
        }
        """
        variables: dict[str, Any] = {
            "email": email,
            "password": password,
            "origin": origin or self.url,
        }
        if captcha_token:
            variables["captchaToken"] = captcha_token
        return self.execute_gql(query, variables=variables, core=True)

    def get_auth_tokens_from_login_token(
        self, login_token: str, origin: str | None = None
    ) -> dict[str, Any]:
        """Exchange a login token for access and refresh tokens.

        Args:
            login_token: The login token obtained from credentials.
            origin: Workspace origin URL; defaults to the client base URL.

        Returns:
            Dict[str, Any]: Raw GraphQL response with auth tokens.
        """
        query = """
        mutation ($loginToken: String!, $origin: String!) {
            getAuthTokensFromLoginToken(loginToken: $loginToken, origin: $origin) {
                tokens {
                    accessOrWorkspaceAgnosticToken {
                        token
                        expiresAt
                    }
                    refreshToken {
                        token
                        expiresAt
                    }
                }
            }
        }
        """
        variables = {"loginToken": login_token, "origin": origin or self.url}
        return self.execute_gql(query, variables=variables, core=True)

    def get_authorization_url_for_sso(
        self, identity_provider_id: str
    ) -> dict[str, Any]:
        """Get the SSO authorization URL for a configured identity provider.

        Args:
            identity_provider_id: ID of the SSO identity provider.

        Returns:
            Dict[str, Any]: Raw GraphQL response with the authorization URL.
        """
        query = """
        mutation ($id: String!) {
            getAuthorizationUrlForSSO(input: { identityProviderId: $id }) {
                authorizationURL
            }
        }
        """
        variables = {"id": identity_provider_id}
        return self.execute_gql(query, variables=variables, core=True)

    # --- High-value provisioning primitive ---

    def provision_api_key(
        self,
        email: str,
        password: str,
        name: str = "egeria-harvester",
        expires_at: str = "2125-01-01T00:00:00.000Z",
        origin: str | None = None,
    ) -> dict[str, Any]:
        """Provision a long-lived Twenty API key from user credentials.

        Runs the full day-0 token-provisioning flow against ``/metadata``:
        login -> exchange -> getRoles (pick ``canUpdateAllSettings`` or first)
        -> createApiKey -> generateApiKeyToken.

        Args:
            email: User email.
            password: User password.
            name: Name for the created API key.
            expires_at: ISO-8601 expiration for the key/token.
            origin: Workspace origin URL; defaults to the client base URL.

        Returns:
            Dict[str, Any]: ``{"api_key": <token>, "api_key_id": <id>,
            "role_id": <id>}``.

        Raises:
            ParameterError: If any step yields no usable result.
        """
        origin = origin or self.url

        login = self.get_login_token_from_credentials(
            email=email, password=password, origin=origin
        )
        login_token = (
            (login or {})
            .get("getLoginTokenFromCredentials", {})
            .get("loginToken", {})
            .get("token")
        )
        if not login_token:
            raise ParameterError(
                f"provision_api_key: no login token returned ({login})"
            )

        # Temporarily authenticate the client with the access token for the
        # authenticated steps (getRoles / createApiKey / generateApiKeyToken).
        auth = self.get_auth_tokens_from_login_token(
            login_token=login_token, origin=origin
        )
        access_token = (
            (auth or {})
            .get("getAuthTokensFromLoginToken", {})
            .get("tokens", {})
            .get("accessOrWorkspaceAgnosticToken", {})
            .get("token")
        )
        if not access_token:
            raise ParameterError(
                f"provision_api_key: no access token returned ({auth})"
            )
        self._set_token(access_token)

        roles_resp = self.get_roles()
        roles = (roles_resp or {}).get("getRoles") or []
        if not roles:
            raise ParameterError(f"provision_api_key: no roles returned ({roles_resp})")
        admin = next((r for r in roles if r.get("canUpdateAllSettings")), roles[0])
        role_id = admin.get("id")
        if not role_id:
            raise ParameterError(
                f"provision_api_key: selected role has no id ({admin})"
            )

        created = self.create_api_key(name=name, expires_at=expires_at, role_id=role_id)
        api_key_id = (created or {}).get("createApiKey", {}).get("id")
        if not api_key_id:
            raise ParameterError(
                f"provision_api_key: createApiKey returned no id ({created})"
            )

        token_resp = self.generate_api_key_token(
            api_key_id=api_key_id, expires_at=expires_at
        )
        api_key = (token_resp or {}).get("generateApiKeyToken", {}).get("token")
        if not api_key:
            raise ParameterError(
                f"provision_api_key: generateApiKeyToken returned no token "
                f"({token_resp})"
            )

        return {
            "api_key": api_key,
            "api_key_id": api_key_id,
            "role_id": role_id,
        }

    def _set_token(self, token: str) -> None:
        """Attach a Bearer token to both clients' transports (in-place).

        Used by :meth:`provision_api_key` to authenticate the authenticated
        steps once a login exchange has yielded an access token.
        """
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
        for transport in (self.transport, self.core_transport):
            existing = getattr(transport, "headers", None) or {}
            existing["Authorization"] = f"Bearer {token}"
            transport.headers = existing

    # --- Generic record reader ---

    def find_many(
        self,
        object_name_plural: str,
        fields: str = "id",
        first: int = 60,
        filter: dict | None = None,
        order_by: list | dict | None = None,
        after: str | None = None,
    ) -> dict[str, Any]:
        """Query many records of any object via Twenty's GraphQL core schema.

        Args:
            object_name_plural: Plural object name (e.g. ``people``, ``companies``).
            fields: Space-separated field selection string for each node.
            first: Page size.
            filter: Optional filter object.
            order_by: Optional ordering specification.
            after: Optional pagination cursor.

        Returns:
            Dict[str, Any]: Raw GraphQL response with edges, pageInfo, totalCount.
        """
        query = f"""
        query ($first: Int, $filter: {object_name_plural}FilterInput, $orderBy: [{object_name_plural}OrderByInput], $after: String) {{
            {object_name_plural}(first: $first, filter: $filter, orderBy: $orderBy, after: $after) {{
                edges {{
                    node {{
                        {fields}
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                totalCount
            }}
        }}
        """
        variables: dict[str, Any] = {"first": first}
        if filter is not None:
            variables["filter"] = filter
        if order_by is not None:
            variables["orderBy"] = order_by
        if after is not None:
            variables["after"] = after
        return self.execute_gql(query, variables=variables)
