"""MCP tools for crm operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from twenty_mcp.auth import get_client


def register_crm_tools(mcp: FastMCP):
    """Register Twenty MCP crm tools.
    CONCEPT:TW-OS.governance.twenty
    """

    @mcp.tool(tags={"crm"})
    async def twenty_mcp_crm(
        action: str = Field(
            description="Action to perform. e.g. 'get_people', 'get_person', 'create_person', 'update_person', 'delete_person', 'get_companies', 'get_company', 'create_company', 'update_company', 'delete_company', 'get_opportunities', 'get_opportunity', 'create_opportunity', 'update_opportunity', 'delete_opportunity', 'get_records', 'get_record', 'create_record', 'update_record', 'delete_record', 'batch_create_records', 'batch_update_records', 'batch_delete_records', 'execute_gql'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Twenty MCP crm operations."""
        if ctx:
            await ctx.info(f"Executing CRM operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on CRM client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute CRM operation {action}: {e}"}
