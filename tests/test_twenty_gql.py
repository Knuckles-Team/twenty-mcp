"""Tests for the standardized Twenty GraphQL client (no network)."""

from unittest.mock import MagicMock, patch

import pytest
from agent_utilities.core.exceptions import MissingParameterError, ParameterError

from twenty_mcp.twenty_gql import GraphQL


@pytest.fixture
def mock_gql_clients():
    """Patch the gql Client so no network is used; capture execute() calls.

    Twenty uses TWO clients: ``client`` (object schema, ``/graphql``) and
    ``core_client`` (auth/system schema, ``/metadata``). The patched ``Client``
    constructor returns a distinct mock per call so tests can assert which
    endpoint a method routed through.
    """
    with patch("twenty_mcp.twenty_gql.Client") as mock_client_cls:
        object_client = MagicMock(name="object_client")
        object_client.execute.return_value = {"ok": True}
        core_client = MagicMock(name="core_client")
        core_client.execute.return_value = {"ok": True}
        # __init__ builds the object client first, then the core client.
        mock_client_cls.side_effect = [object_client, core_client]
        yield {"object": object_client, "core": core_client}


# Backwards-compatible alias for tests that only need the object client.
@pytest.fixture
def mock_gql_client(mock_gql_clients):
    yield mock_gql_clients["object"]


@pytest.fixture(autouse=True)
def mock_gql_parser():
    """Avoid parsing/validating the GraphQL document (no schema available)."""
    with patch("twenty_mcp.twenty_gql.gql", lambda q: q):
        yield


def test_graphql_init_requires_url():
    with pytest.raises(MissingParameterError, match="URL is required"):
        GraphQL(url=None, token="test")


def test_graphql_init_builds_dual_endpoints(mock_gql_clients):
    client = GraphQL(url="http://twenty.local/", token=None)
    assert client.endpoint == "http://twenty.local/graphql"
    assert client.core_endpoint == "http://twenty.local/metadata"
    assert "Authorization" not in client.headers


def test_graphql_init_sends_origin_header(mock_gql_clients):
    client = GraphQL(url="http://twenty.local/", token=None)
    assert client.headers["Origin"] == "http://twenty.local"
    assert client.origin == "http://twenty.local"


def test_graphql_init_auth_header_with_token(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    assert client.headers["Authorization"] == "Bearer abc"


def test_execute_gql_happy_path(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    result = client.execute_gql("query { foo }", variables={"a": 1})
    assert result == {"ok": True}
    # default routes to the OBJECT client
    _, kwargs = mock_gql_clients["object"].execute.call_args
    assert kwargs["variable_values"] == {"a": 1}
    mock_gql_clients["core"].execute.assert_not_called()


def test_execute_gql_core_routes_to_core_client(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.execute_gql("query { foo }", variables={"a": 1}, core=True)
    mock_gql_clients["core"].execute.assert_called_once()
    mock_gql_clients["object"].execute.assert_not_called()


def test_execute_gql_error_path(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    mock_gql_clients["object"].execute.side_effect = Exception("boom")
    with pytest.raises(ParameterError, match="Query execution failed: boom"):
        client.execute_gql("query { foo }")


def test_create_api_key_builds_operation_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.create_api_key(name="ci", expires_at="2030-01-01", role_id="role-uuid")
    # routed through the CORE client
    mock_gql_clients["object"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["core"].execute.call_args
    query_doc = args[0]
    assert (
        "createApiKey(input: { name: $name, expiresAt: $expiresAt, roleId: $roleId })"
        in query_doc
    )
    assert "$roleId: UUID!" in query_doc
    assert "$name: String!" in query_doc
    assert "$expiresAt: String!" in query_doc
    assert kwargs["variable_values"] == {
        "name": "ci",
        "expiresAt": "2030-01-01",
        "roleId": "role-uuid",
    }


def test_generate_api_key_token_builds_operation_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.generate_api_key_token(api_key_id="k1", expires_at="2030-01-01")
    mock_gql_clients["object"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["core"].execute.call_args
    query_doc = args[0]
    assert (
        "generateApiKeyToken(apiKeyId: $apiKeyId, expiresAt: $expiresAt)" in query_doc
    )
    assert "$apiKeyId: UUID!" in query_doc
    assert "$expiresAt: String!" in query_doc
    assert kwargs["variable_values"] == {
        "apiKeyId": "k1",
        "expiresAt": "2030-01-01",
    }


def test_get_roles_builds_operation_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.get_roles()
    mock_gql_clients["object"].execute.assert_not_called()
    args, _ = mock_gql_clients["core"].execute.call_args
    assert "getRoles" in args[0]
    assert "canUpdateAllSettings" in args[0]


def test_get_login_token_from_credentials_includes_origin_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local")  # unauthenticated
    client.get_login_token_from_credentials(email="a@b.c", password="pw")
    mock_gql_clients["object"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["core"].execute.call_args
    query_doc = args[0]
    assert (
        "getLoginTokenFromCredentials(email: $email, password: $password, origin: $origin)"
        in query_doc
    )
    assert "$origin: String!" in query_doc
    assert kwargs["variable_values"] == {
        "email": "a@b.c",
        "password": "pw",
        "origin": "http://twenty.local",
    }


def test_get_auth_tokens_from_login_token_includes_origin_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local")
    client.get_auth_tokens_from_login_token(login_token="lt")
    mock_gql_clients["object"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["core"].execute.call_args
    assert (
        "getAuthTokensFromLoginToken(loginToken: $loginToken, origin: $origin)"
        in args[0]
    )
    assert kwargs["variable_values"] == {
        "loginToken": "lt",
        "origin": "http://twenty.local",
    }


def test_get_authorization_url_for_sso_on_core(mock_gql_clients):
    client = GraphQL(url="http://twenty.local")
    client.get_authorization_url_for_sso(identity_provider_id="idp1")
    mock_gql_clients["object"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["core"].execute.call_args
    assert "getAuthorizationUrlForSSO(input: { identityProviderId: $id })" in args[0]
    assert kwargs["variable_values"] == {"id": "idp1"}


def test_find_many_builds_dynamic_query_on_object(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.find_many(
        "people",
        fields="id name",
        first=10,
        filter={"name": {"eq": "Bob"}},
        order_by=[{"name": "AscNullsFirst"}],
        after="cursor1",
    )
    # object data stays on the default /graphql client
    mock_gql_clients["core"].execute.assert_not_called()
    args, kwargs = mock_gql_clients["object"].execute.call_args
    query_doc = args[0]
    assert "people(first: $first" in query_doc
    assert "id name" in query_doc
    assert "edges" in query_doc
    assert "totalCount" in query_doc
    assert kwargs["variable_values"] == {
        "first": 10,
        "filter": {"name": {"eq": "Bob"}},
        "orderBy": [{"name": "AscNullsFirst"}],
        "after": "cursor1",
    }


def test_find_many_minimal_variables(mock_gql_clients):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.find_many("companies")
    _, kwargs = mock_gql_clients["object"].execute.call_args
    # only `first` should be present when no optional args supplied
    assert kwargs["variable_values"] == {"first": 60}


def test_provision_api_key_chains_full_flow(mock_gql_clients):
    """provision_api_key should chain login->exchange->roles->create->token."""
    client = GraphQL(url="http://twenty.local")

    with (
        patch.object(client, "get_login_token_from_credentials") as m_login,
        patch.object(client, "get_auth_tokens_from_login_token") as m_auth,
        patch.object(client, "get_roles") as m_roles,
        patch.object(client, "create_api_key") as m_create,
        patch.object(client, "generate_api_key_token") as m_token,
    ):
        m_login.return_value = {
            "getLoginTokenFromCredentials": {"loginToken": {"token": "LOGIN"}}
        }
        m_auth.return_value = {
            "getAuthTokensFromLoginToken": {
                "tokens": {"accessOrWorkspaceAgnosticToken": {"token": "ACCESS"}}
            }
        }
        m_roles.return_value = {
            "getRoles": [
                {"id": "viewer", "label": "Viewer", "canUpdateAllSettings": False},
                {"id": "admin", "label": "Admin", "canUpdateAllSettings": True},
            ]
        }
        m_create.return_value = {"createApiKey": {"id": "KEY-ID", "name": "k"}}
        m_token.return_value = {"generateApiKeyToken": {"token": "FINAL-TOKEN"}}

        result = client.provision_api_key(email="a@b.c", password="pw", name="k")

    m_login.assert_called_once()
    m_auth.assert_called_once_with(login_token="LOGIN", origin="http://twenty.local")
    m_roles.assert_called_once()
    # Admin role (canUpdateAllSettings True) selected, not the first.
    m_create.assert_called_once()
    assert m_create.call_args.kwargs["role_id"] == "admin"
    m_token.assert_called_once()
    assert m_token.call_args.kwargs["api_key_id"] == "KEY-ID"
    assert result == {
        "api_key": "FINAL-TOKEN",
        "api_key_id": "KEY-ID",
        "role_id": "admin",
    }


def test_provision_api_key_raises_when_no_login_token(mock_gql_clients):
    client = GraphQL(url="http://twenty.local")
    with patch.object(client, "get_login_token_from_credentials") as m_login:
        m_login.return_value = {"getLoginTokenFromCredentials": {"loginToken": {}}}
        with pytest.raises(ParameterError, match="no login token"):
            client.provision_api_key(email="a@b.c", password="pw")


def test_provision_api_key_raises_when_no_token_generated(mock_gql_clients):
    client = GraphQL(url="http://twenty.local")
    with (
        patch.object(client, "get_login_token_from_credentials") as m_login,
        patch.object(client, "get_auth_tokens_from_login_token") as m_auth,
        patch.object(client, "get_roles") as m_roles,
        patch.object(client, "create_api_key") as m_create,
        patch.object(client, "generate_api_key_token") as m_token,
    ):
        m_login.return_value = {
            "getLoginTokenFromCredentials": {"loginToken": {"token": "LOGIN"}}
        }
        m_auth.return_value = {
            "getAuthTokensFromLoginToken": {
                "tokens": {"accessOrWorkspaceAgnosticToken": {"token": "ACCESS"}}
            }
        }
        m_roles.return_value = {
            "getRoles": [{"id": "admin", "canUpdateAllSettings": True}]
        }
        m_create.return_value = {"createApiKey": {"id": "KEY-ID"}}
        m_token.return_value = {"generateApiKeyToken": {}}
        with pytest.raises(ParameterError, match="no token"):
            client.provision_api_key(email="a@b.c", password="pw")


def test_get_graphql_client_factory_without_token(monkeypatch):
    """The auth factory should construct without a token (Twenty allows it)."""
    monkeypatch.delenv("TWENTY_TOKEN", raising=False)
    monkeypatch.setenv("TWENTY_URL", "http://twenty.local")
    with patch("twenty_mcp.twenty_gql.Client", MagicMock()):
        from twenty_mcp.auth import get_graphql_client

        client = get_graphql_client()
        assert isinstance(client, GraphQL)
        assert "Authorization" not in client.headers
