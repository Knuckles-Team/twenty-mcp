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
        verify: bool = True,
        proxies: dict | None = None,
        debug: bool = False,
    ):
        if not url:
            raise MissingParameterError("URL is required")

        self.url = url
        self.token = token
        self.api_path = api_path
        self.verify = verify
        self.proxies = proxies
        self.debug = debug

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        self.endpoint = f"{url.rstrip('/')}{api_path}"

        headers: dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.headers = headers

        self.transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=headers,
            verify=verify,
            proxies=proxies,
        )
        # Twenty disables GraphQL introspection; never fetch the schema.
        self.client = Client(
            transport=self.transport, fetch_schema_from_transport=False
        )

    def execute_gql(
        self,
        query_str: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query_str: The GraphQL query or mutation string.
            variables: Optional dictionary of variables for the query.
            operation_name: Optional name of the operation.

        Returns:
            Dict[str, Any]: The raw GraphQL response dictionary.

        Raises:
            ParameterError: If the query execution fails.
        """
        try:
            query = gql(query_str)
            result = self.client.execute(
                query, variable_values=variables, operation_name=operation_name
            )
            return result
        except Exception as e:
            logging.error(f"GraphQL execution failed: {str(e)}")
            raise ParameterError(f"Query execution failed: {str(e)}") from e

    # --- Auth / API key mutations (intentionally unauthenticated-capable) ---

    def create_api_key(self, name: str, expires_at: str) -> dict[str, Any]:
        """Create a new API key in the workspace.

        Args:
            name: Human-readable name for the API key.
            expires_at: ISO-8601 expiration timestamp.

        Returns:
            Dict[str, Any]: Raw GraphQL response with the created API key.
        """
        query = """
        mutation ($input: CreateApiKeyDTO!) {
            createApiKey(input: $input) {
                id
                name
                expiresAt
                revokedAt
            }
        }
        """
        variables = {"input": {"name": name, "expiresAt": expires_at}}
        return self.execute_gql(query, variables=variables)

    def generate_api_key_token(
        self, api_key_id: str, expires_at: str
    ) -> dict[str, Any]:
        """Generate a JWT token for an existing API key.

        Args:
            api_key_id: ID of the API key.
            expires_at: ISO-8601 expiration timestamp.

        Returns:
            Dict[str, Any]: Raw GraphQL response containing the token.
        """
        query = """
        mutation ($apiKeyId: String!, $expiresAt: String!) {
            generateApiKeyToken(apiKeyId: $apiKeyId, expiresAt: $expiresAt) {
                token
            }
        }
        """
        variables = {"apiKeyId": api_key_id, "expiresAt": expires_at}
        return self.execute_gql(query, variables=variables)

    def get_login_token_from_credentials(
        self, email: str, password: str, captcha_token: str | None = None
    ) -> dict[str, Any]:
        """Exchange email/password credentials for a short-lived login token.

        This mutation is intentionally unauthenticated.

        Args:
            email: User email.
            password: User password.
            captcha_token: Optional captcha token.

        Returns:
            Dict[str, Any]: Raw GraphQL response with the login token.
        """
        query = """
        mutation ($email: String!, $password: String!) {
            getLoginTokenFromCredentials(email: $email, password: $password) {
                loginToken {
                    token
                    expiresAt
                }
            }
        }
        """
        variables = {"email": email, "password": password}
        if captcha_token:
            variables["captchaToken"] = captcha_token
        return self.execute_gql(query, variables=variables)

    def get_auth_tokens_from_login_token(self, login_token: str) -> dict[str, Any]:
        """Exchange a login token for access and refresh tokens.

        Args:
            login_token: The login token obtained from credentials.

        Returns:
            Dict[str, Any]: Raw GraphQL response with auth tokens.
        """
        query = """
        mutation ($loginToken: String!) {
            getAuthTokensFromLoginToken(loginToken: $loginToken) {
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
        variables = {"loginToken": login_token}
        return self.execute_gql(query, variables=variables)

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
        return self.execute_gql(query, variables=variables)

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
