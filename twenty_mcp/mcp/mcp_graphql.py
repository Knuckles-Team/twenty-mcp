"""MCP tools for graphql operations.

CONCEPT:TWENTY-004 Standardized GraphQL tooling, mirroring gitlab-api.
"""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field


def register_graphql_tools(mcp: FastMCP):
    from twenty_mcp.auth import get_graphql_client

    @mcp.tool(tags={"graphql"})
    async def twenty_graphql(
        query: str = Field(
            description="The raw GraphQL query or mutation string to execute against the Twenty API."
        ),
        variables: str = Field(
            default="{}",
            description="JSON string of variables to pass along with the query.",
        ),
        operation_name: str | None = Field(
            default=None,
            description="Optional operation name if executing a specific query within the document.",
        ),
        client=Depends(get_graphql_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Execute raw GraphQL queries and mutations natively on Twenty."""
        if ctx:
            await ctx.info("Executing Twenty GraphQL query...")
        import json

        try:
            vars_dict = json.loads(variables) if variables else None
        except Exception as e:
            return {"error": f"Invalid variables JSON: {e}"}

        try:
            return client.execute_gql(
                query_str=query, variables=vars_dict, operation_name=operation_name
            )
        except Exception as e:
            return {"error": f"GraphQL execution failed: {str(e)}"}

    @mcp.tool(tags={"graphql"})
    async def twenty_discover_graphql_schema(
        type_name: str | None = Field(
            default=None,
            description="Optional specific object/type name to inspect (e.g. 'person', 'company'). If omitted, returns the full Twenty meta-model (all objects/fields/relations).",
        ),
        client=Depends(get_graphql_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Discover Twenty's underlying object/field/relation metadata (meta-model).

        Uses standard GraphQL introspection when available, and falls back to
        Twenty's Metadata API when introspection is unavailable. Twenty disables
        GraphQL introspection on its main API, so in practice the Metadata API
        fallback is what powers this discovery against a live Twenty server.

        The return value is tagged with the source used:

        * ``{"source": "graphql-introspection", "schema": <result>}``
        * ``{"source": "metadata-api", "metadata": <result>}``
        * ``{"error": <message>}`` on total failure.
        """
        from agent_utilities.mcp.context_helpers import (
            ctx_graphql_get_type_details,
            ctx_graphql_list_types,
        )

        if ctx:
            await ctx.info("Retrieving Twenty metadata (meta-model)...")

        # Safe wrapper to call execute_gql
        def execute_fn(q, variables=None):
            return client.execute_gql(query_str=q, variables=variables)

        # --- Path 1: standard GraphQL introspection (parity / if ever enabled) ---
        introspection_result: Any = None
        introspection_failed = True
        try:
            if type_name:
                introspection_result = await ctx_graphql_get_type_details(
                    execute_fn, type_name
                )
            else:
                introspection_result = await ctx_graphql_list_types(execute_fn)
            introspection_failed = _introspection_disabled(introspection_result)
        except Exception:
            introspection_failed = True

        if not introspection_failed:
            return {"source": "graphql-introspection", "schema": introspection_result}

        # --- Path 2: Twenty Metadata API fallback (introspection disabled) ---
        if ctx:
            await ctx.info(
                "GraphQL introspection unavailable; falling back to Twenty Metadata API..."
            )

        try:
            from twenty_mcp.auth import get_client

            metadata_client = get_client()
        except Exception as e:  # pragma: no cover - defensive
            return {
                "error": f"Failed to discover Twenty metadata: {str(e)}",
            }

        try:
            if type_name:
                metadata = metadata_client.get_metadata_object(type_name)
            else:
                try:
                    metadata = metadata_client.get_metadata()
                except Exception:
                    metadata = metadata_client.get_metadata_objects()
            return {"source": "metadata-api", "metadata": metadata}
        except Exception as e:
            return {"error": f"Failed to discover Twenty metadata: {str(e)}"}


def _introspection_disabled(result: Any) -> bool:
    """Return True if a GraphQL introspection response indicates it is unavailable.

    Twenty disables introspection and responds with errors such as
    "GraphQL introspection has been disabled, but the requested query contained
    the field \"__schema\"". This also treats empty results and helper-level
    error payloads as a failed introspection so the caller can fall back.
    """
    if result is None:
        return True
    if isinstance(result, dict):
        if result.get("error"):
            return True
        # GraphQL spec error payload (e.g. {"errors": [...], "data": null}).
        if result.get("errors"):
            return True
        data = result.get("data")
        if data is not None and not data:
            # data present but empty (e.g. {"__schema": null} collapses to {})
            return True
        # A structured success payload carrying introspection data is valid.
        if data:
            return False
    # No structured success data; inspect the textual form for disabled markers.
    text = str(result).lower()
    markers = (
        "introspection has been disabled",
        "introspection is not allowed",
        "cannot query field",
        "__schema",
        "__type",
    )
    return any(marker in text for marker in markers)
