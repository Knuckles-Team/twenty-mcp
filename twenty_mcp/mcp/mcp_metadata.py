"""MCP tools for metadata schema operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from twenty_mcp.auth import get_client


def register_metadata_tools(mcp: FastMCP):
    """Register Twenty MCP metadata tools."""

    @mcp.tool(tags={"metadata"})
    async def twenty_mcp_metadata(
        action: str = Field(
            description="Action to perform. e.g. 'get_metadata', 'get_metadata_objects', 'get_metadata_object', 'create_metadata_object', 'update_metadata_object', 'delete_metadata_object', 'create_metadata_field', 'update_metadata_field', 'delete_metadata_field', 'create_metadata_relation', 'delete_metadata_relation'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Twenty MCP metadata schema operations."""
        if ctx:
            await ctx.info(f"Executing metadata operation: {action}...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Dynamic dispatch
        method = getattr(client, action, None)
        if not method:
            alt_action = action.replace("-", "_").replace(" ", "_").lower()
            method = getattr(client, alt_action, None)

        if not method:
            return {"error": f"Unknown action '{action}' on Metadata client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute metadata operation {action}: {e}"}
