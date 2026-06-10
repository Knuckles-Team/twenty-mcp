"""Tests for Twenty metadata autodiscovery (introspection + Metadata API fallback).

No network is used; the GraphQL introspection path and the Metadata API client
are both mocked.
"""

import asyncio
from unittest.mock import MagicMock, patch

from fastmcp import FastMCP

from twenty_mcp.mcp.mcp_graphql import register_graphql_tools


def _get_discover_fn():
    """Extract the inner discovery tool function from a fresh FastMCP instance."""
    mcp = FastMCP("test")
    register_graphql_tools(mcp)
    tool = asyncio.run(mcp.get_tool("twenty_discover_graphql_schema"))
    return tool.fn


def test_discover_falls_back_to_metadata_api_when_introspection_disabled():
    """Introspection disabled -> Metadata API fallback (source == metadata-api)."""
    fn = _get_discover_fn()

    # GraphQL client whose introspection responds with Twenty's disabled error.
    gql_client = MagicMock()
    gql_client.execute_gql.return_value = {
        "errors": [
            {
                "message": (
                    "GraphQL introspection has been disabled, but the requested "
                    'query contained the field "__schema".'
                )
            }
        ]
    }

    sentinel = {"objects": [{"nameSingular": "person"}], "_sentinel": "meta"}
    metadata_client = MagicMock()
    metadata_client.get_metadata.return_value = sentinel

    with patch("twenty_mcp.auth.get_client", return_value=metadata_client):
        result = asyncio.run(fn(type_name=None, client=gql_client, ctx=None))

    assert result["source"] == "metadata-api"
    assert result["metadata"] == sentinel
    metadata_client.get_metadata.assert_called_once()


def test_discover_falls_back_to_metadata_object_for_named_type():
    """type_name provided -> Metadata API get_metadata_object fallback."""
    fn = _get_discover_fn()

    gql_client = MagicMock()
    gql_client.execute_gql.side_effect = Exception(
        "GraphQL introspection has been disabled"
    )

    sentinel = {"nameSingular": "company", "_sentinel": "obj"}
    metadata_client = MagicMock()
    metadata_client.get_metadata_object.return_value = sentinel

    with patch("twenty_mcp.auth.get_client", return_value=metadata_client):
        result = asyncio.run(fn(type_name="company", client=gql_client, ctx=None))

    assert result["source"] == "metadata-api"
    assert result["metadata"] == sentinel
    metadata_client.get_metadata_object.assert_called_once_with("company")


def test_discover_metadata_falls_back_to_objects_when_full_meta_errors():
    """get_metadata() error -> get_metadata_objects() fallback."""
    fn = _get_discover_fn()

    gql_client = MagicMock()
    gql_client.execute_gql.return_value = {"error": "Failed to list GraphQL types"}

    sentinel = {"data": [{"nameSingular": "person"}]}
    metadata_client = MagicMock()
    metadata_client.get_metadata.side_effect = Exception("404 not found")
    metadata_client.get_metadata_objects.return_value = sentinel

    with patch("twenty_mcp.auth.get_client", return_value=metadata_client):
        result = asyncio.run(fn(type_name=None, client=gql_client, ctx=None))

    assert result["source"] == "metadata-api"
    assert result["metadata"] == sentinel
    metadata_client.get_metadata_objects.assert_called_once()


def test_discover_uses_graphql_introspection_when_available():
    """Introspection 'succeeds' -> source == graphql-introspection, no fallback."""
    fn = _get_discover_fn()

    schema = {"data": {"__schema": {"types": [{"name": "Person", "kind": "OBJECT"}]}}}
    gql_client = MagicMock()
    gql_client.execute_gql.return_value = schema

    metadata_client = MagicMock()

    with patch("twenty_mcp.auth.get_client", return_value=metadata_client):
        result = asyncio.run(fn(type_name=None, client=gql_client, ctx=None))

    assert result["source"] == "graphql-introspection"
    assert result["schema"] == schema
    metadata_client.get_metadata.assert_not_called()
