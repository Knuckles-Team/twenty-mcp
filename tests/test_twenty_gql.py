"""Tests for the standardized Twenty GraphQL client (no network)."""

from unittest.mock import MagicMock, patch

import pytest
from agent_utilities.core.exceptions import MissingParameterError, ParameterError

from twenty_mcp.twenty_gql import GraphQL


@pytest.fixture
def mock_gql_client():
    """Patch the gql Client so no network is used; capture execute() calls."""
    with patch("twenty_mcp.twenty_gql.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.execute.return_value = {"ok": True}
        yield mock_client


@pytest.fixture(autouse=True)
def mock_gql_parser():
    """Avoid parsing/validating the GraphQL document (no schema available)."""
    with patch("twenty_mcp.twenty_gql.gql", lambda q: q):
        yield


def test_graphql_init_requires_url():
    with pytest.raises(MissingParameterError, match="URL is required"):
        GraphQL(url=None, token="test")


def test_graphql_init_no_auth_header_without_token(mock_gql_client):
    client = GraphQL(url="http://twenty.local/", token=None)
    assert client.endpoint == "http://twenty.local/graphql"
    assert "Authorization" not in client.headers


def test_graphql_init_auth_header_with_token(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    assert client.headers["Authorization"] == "Bearer abc"


def test_execute_gql_happy_path(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    result = client.execute_gql("query { foo }", variables={"a": 1})
    assert result == {"ok": True}
    # variables forwarded to underlying client
    _, kwargs = mock_gql_client.execute.call_args
    assert kwargs["variable_values"] == {"a": 1}


def test_execute_gql_error_path(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    mock_gql_client.execute.side_effect = Exception("boom")
    with pytest.raises(ParameterError, match="Query execution failed: boom"):
        client.execute_gql("query { foo }")


def test_create_api_key_builds_operation(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.create_api_key(name="ci", expires_at="2030-01-01")
    args, kwargs = mock_gql_client.execute.call_args
    query_doc = args[0]
    assert "createApiKey(input: $input)" in query_doc
    assert kwargs["variable_values"] == {
        "input": {"name": "ci", "expiresAt": "2030-01-01"}
    }


def test_generate_api_key_token_builds_operation(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.generate_api_key_token(api_key_id="k1", expires_at="2030-01-01")
    args, kwargs = mock_gql_client.execute.call_args
    assert "generateApiKeyToken(apiKeyId: $apiKeyId, expiresAt: $expiresAt)" in args[0]
    assert kwargs["variable_values"] == {
        "apiKeyId": "k1",
        "expiresAt": "2030-01-01",
    }


def test_get_login_token_from_credentials_builds_operation(mock_gql_client):
    client = GraphQL(url="http://twenty.local")  # unauthenticated
    client.get_login_token_from_credentials(email="a@b.c", password="pw")
    args, kwargs = mock_gql_client.execute.call_args
    assert "getLoginTokenFromCredentials(email: $email, password: $password)" in args[0]
    assert kwargs["variable_values"] == {"email": "a@b.c", "password": "pw"}


def test_get_auth_tokens_from_login_token_builds_operation(mock_gql_client):
    client = GraphQL(url="http://twenty.local")
    client.get_auth_tokens_from_login_token(login_token="lt")
    args, kwargs = mock_gql_client.execute.call_args
    assert "getAuthTokensFromLoginToken(loginToken: $loginToken)" in args[0]
    assert kwargs["variable_values"] == {"loginToken": "lt"}


def test_get_authorization_url_for_sso_builds_operation(mock_gql_client):
    client = GraphQL(url="http://twenty.local")
    client.get_authorization_url_for_sso(identity_provider_id="idp1")
    args, kwargs = mock_gql_client.execute.call_args
    assert "getAuthorizationUrlForSSO(input: { identityProviderId: $id })" in args[0]
    assert kwargs["variable_values"] == {"id": "idp1"}


def test_find_many_builds_dynamic_query(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.find_many(
        "people",
        fields="id name",
        first=10,
        filter={"name": {"eq": "Bob"}},
        order_by=[{"name": "AscNullsFirst"}],
        after="cursor1",
    )
    args, kwargs = mock_gql_client.execute.call_args
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


def test_find_many_minimal_variables(mock_gql_client):
    client = GraphQL(url="http://twenty.local", token="abc")
    client.find_many("companies")
    _, kwargs = mock_gql_client.execute.call_args
    # only `first` should be present when no optional args supplied
    assert kwargs["variable_values"] == {"first": 60}


def test_get_graphql_client_factory_without_token(monkeypatch):
    """The auth factory should construct without a token (Twenty allows it)."""
    monkeypatch.delenv("TWENTY_TOKEN", raising=False)
    monkeypatch.setenv("TWENTY_URL", "http://twenty.local")
    with patch("twenty_mcp.twenty_gql.Client", MagicMock()):
        from twenty_mcp.auth import get_graphql_client

        client = get_graphql_client()
        assert isinstance(client, GraphQL)
        assert "Authorization" not in client.headers
