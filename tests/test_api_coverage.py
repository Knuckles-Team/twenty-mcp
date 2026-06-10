"""Tests for the new REST/metadata coverage methods on the Twenty Api client."""

from unittest.mock import MagicMock, patch

import pytest

from twenty_mcp.api_client import Api


def _make_client_with_recorder():
    """Return (client, calls) where calls records each Session.request invocation."""
    client = Api("http://localhost:3000", token="test_token")
    calls = []

    def fake_request(method, url, headers=None, params=None, json=None):
        calls.append({"method": method, "url": url, "params": params, "json": json})
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"ok": True}
        resp.text = '{"ok": true}'
        return resp

    client._session.request = fake_request  # type: ignore[method-assign]
    return client, calls


@pytest.mark.concept("TWENTY-001")
def test_find_duplicates_by_data():
    client, calls = _make_client_with_recorder()
    res = client.find_duplicates("people", data={"emails": {"primaryEmail": "a@b.c"}})
    assert res == {"ok": True}
    assert calls[-1]["method"] == "POST"
    assert calls[-1]["url"].endswith("/rest/people/duplicates")
    assert calls[-1]["json"] == {"data": {"emails": {"primaryEmail": "a@b.c"}}}


@pytest.mark.concept("TWENTY-001")
def test_find_duplicates_by_ids():
    client, calls = _make_client_with_recorder()
    client.find_duplicates("people", ids=["1", "2"])
    assert calls[-1]["json"] == {"ids": ["1", "2"]}
    assert calls[-1]["url"].endswith("/rest/people/duplicates")


@pytest.mark.concept("TWENTY-001")
def test_find_records_maps_params():
    client, calls = _make_client_with_recorder()
    client.find_records(
        "companies",
        filter="name[eq]:Acme",
        order_by="createdAt[DescNullsLast]",
        limit=25,
        depth=1,
        starting_after="cur1",
    )
    assert calls[-1]["method"] == "GET"
    assert calls[-1]["url"].endswith("/rest/companies")
    assert calls[-1]["params"] == {
        "filter": "name[eq]:Acme",
        "order_by": "createdAt[DescNullsLast]",
        "limit": 25,
        "depth": 1,
        "starting_after": "cur1",
    }


@pytest.mark.concept("TWENTY-001")
def test_find_records_omits_none_params():
    client, calls = _make_client_with_recorder()
    client.find_records("companies", limit=5)
    assert calls[-1]["params"] == {"limit": 5}


@pytest.mark.concept("TWENTY-001")
def test_metadata_fields_and_relations_coverage():
    client, calls = _make_client_with_recorder()

    client.get_metadata_fields(params={"limit": 10})
    assert calls[-1]["method"] == "GET"
    assert calls[-1]["url"].endswith("/rest/metadata/fields")
    assert calls[-1]["params"] == {"limit": 10}

    client.get_metadata_field("field-1")
    assert calls[-1]["url"].endswith("/rest/metadata/fields/field-1")

    client.get_metadata_relations()
    assert calls[-1]["url"].endswith("/rest/metadata/relations")

    client.get_metadata_relation("rel-1")
    assert calls[-1]["url"].endswith("/rest/metadata/relations/rel-1")

    client.update_metadata_relation("rel-1", {"name": "newName"})
    assert calls[-1]["method"] == "PATCH"
    assert calls[-1]["url"].endswith("/rest/metadata/relations/rel-1")
    assert calls[-1]["json"] == {"name": "newName"}


@pytest.mark.concept("TWENTY-001")
@patch("requests.Session.send")
def test_coverage_methods_via_send_mock(mock_send):
    """Smoke test using the established Session.send patch style."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": []}
    mock_send.return_value = mock_resp

    client = Api("http://localhost:3000", token="test_token")
    assert client.find_records("people") == {"data": []}
    assert client.get_metadata_fields() == {"data": []}
    assert client.get_metadata_relations() == {"data": []}
