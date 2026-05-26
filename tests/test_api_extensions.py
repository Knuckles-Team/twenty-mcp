import os
from unittest.mock import MagicMock, patch

import pytest

from twenty_mcp.api_client import Api


@pytest.mark.concept("TWENTY-001")
def test_dynamic_prefix_initialization():
    """Verify that TWENTY_API_PREFIX environment variable overrides the default path prefix."""
    with patch.dict(os.environ, {"TWENTY_API_PREFIX": "/api/v1"}):
        client = Api("http://localhost:3000", token="test_token")
        assert client.api_prefix == "/api/v1"

    with patch.dict(os.environ, {}):
        # Env unset / removed
        if "TWENTY_API_PREFIX" in os.environ:
            del os.environ["TWENTY_API_PREFIX"]
        client = Api("http://localhost:3000", token="test_token")
        assert client.api_prefix == "/rest"


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_crm_records_crud(mock_send):
    """Test standard REST CRUD endpoints for individual objects/records."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "123", "firstName": "Alice"}
    mock_send.return_value = mock_resp

    client = Api("http://localhost:3000", token="test_token")

    # Generic Record CRUD
    res = client.get_records("people", params={"limit": 10})
    assert res == {"id": "123", "firstName": "Alice"}

    res = client.get_record("people", "123")
    assert res == {"id": "123", "firstName": "Alice"}

    res = client.create_record("people", {"firstName": "Alice"})
    assert res == {"id": "123", "firstName": "Alice"}

    res = client.update_record("people", "123", {"lastName": "Smith"})
    assert res == {"id": "123", "firstName": "Alice"}

    res = client.delete_record("people", "123")
    assert res == {"id": "123", "firstName": "Alice"}


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_crm_batch_operations(mock_send):
    """Test CRM REST batching boundaries (up to 60 records limit)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "success"}
    mock_send.return_value = mock_resp

    client = Api("http://localhost:3000", token="test_token")

    # Valid batches
    res = client.batch_create_records(
        "people", [{"firstName": "A"}, {"firstName": "B"}]
    )
    assert res == {"status": "success"}

    res = client.batch_update_records("people", [{"id": "1", "firstName": "A"}])
    assert res == {"status": "success"}

    res = client.batch_delete_records("people", ["1", "2"])
    assert res == {"status": "success"}

    # Exceeding batch size error
    oversized_list = [{"firstName": "Name"} for _ in range(61)]
    with pytest.raises(ValueError, match="Batch size cannot exceed 60 records"):
        client.batch_create_records("people", oversized_list)

    with pytest.raises(ValueError, match="Batch size cannot exceed 60 records"):
        client.batch_update_records("people", oversized_list)

    with pytest.raises(ValueError, match="Batch size cannot exceed 60 records"):
        client.batch_delete_records("people", [str(i) for i in range(61)])


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_crm_gql_execution(mock_send):
    """Verify core and custom schema GraphQL endpoint execution."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"people": []}}
    mock_send.return_value = mock_resp

    client = Api("http://localhost:3000", token="test_token")
    res = client.execute_gql("query { people { id } }")
    assert res == {"data": {"people": []}}


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_metadata_api(mock_send):
    """Verify metadata routing behavior with prefix-dependent defaults."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"schema": "mock"}
    mock_send.return_value = mock_resp

    # /rest base URL
    client = Api("http://localhost:3000", token="test_token")
    client.api_prefix = "/rest"

    res = client.get_metadata()
    assert res == {"schema": "mock"}

    # Check that metadata prefix is combined correctly
    res = client.get_metadata_objects()
    assert res == {"schema": "mock"}

    res = client.get_metadata_object("company")
    assert res == {"schema": "mock"}

    res = client.create_metadata_object({"name": "Custom"})
    assert res == {"schema": "mock"}

    res = client.update_metadata_object("1", {"name": "Custom"})
    assert res == {"schema": "mock"}

    res = client.delete_metadata_object("1")
    assert res == {"schema": "mock"}

    res = client.create_metadata_field({"name": "Field"})
    assert res == {"schema": "mock"}

    res = client.update_metadata_field("1", {"name": "Field"})
    assert res == {"schema": "mock"}

    res = client.delete_metadata_field("1")
    assert res == {"schema": "mock"}

    res = client.create_metadata_relation({"name": "Relation"})
    assert res == {"schema": "mock"}

    res = client.delete_metadata_relation("1")
    assert res == {"schema": "mock"}


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_oauth_api(mock_send):
    """Verify OAuth flows and dynamic client registration endpoints."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"client_id": "123"}
    mock_send.return_value = mock_resp

    client = Api("http://localhost:3000", token="test_token")

    res = client.register_oauth_client("My App", ["https://app/callback"])
    assert res == {"client_id": "123"}

    res = client.get_oauth_discovery()
    assert res == {"client_id": "123"}

    # Mock form response
    mock_resp_form = MagicMock()
    mock_resp_form.status_code = 200
    mock_resp_form.json.return_value = {"access_token": "abc"}

    with patch("requests.Session.post", return_value=mock_resp_form):
        res = client.exchange_oauth_token("code", "uri", "id", "secret")
        assert res == {"access_token": "abc"}

        res = client.refresh_oauth_token("refresh", "id", "secret")
        assert res == {"access_token": "abc"}

        res = client.client_credentials_oauth_token("id", "secret")
        assert res == {"access_token": "abc"}


@pytest.mark.concept("TWENTY-001")
def test_webhook_signature_validation():
    """Verify HMAC SHA-256 webhook signature validation logic."""
    payload = '{"event":"person.created"}'
    timestamp = "1716612000"
    secret = "super_secret_webhook_key"

    # Generate true signature: hmac(secret, "timestamp:payload")
    import hashlib
    import hmac

    string_to_sign = f"{timestamp}:{payload}"
    expected_sig = hmac.new(
        secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Success check
    is_valid = Api.validate_webhook_signature(payload, expected_sig, timestamp, secret)
    assert is_valid is True

    # Bad signature
    is_valid_bad = Api.validate_webhook_signature(
        payload, "invalid_signature", timestamp, secret
    )
    assert is_valid_bad is False
