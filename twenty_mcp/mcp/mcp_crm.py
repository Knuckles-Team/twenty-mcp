"""MCP tools for crm operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from twenty_mcp.auth import get_client


def register_crm_tools(mcp: FastMCP):
    """Register Twenty MCP crm tools.
    CONCEPT:TWENTY-001
    """

    @mcp.tool(tags={"crm"})
    async def twenty_mcp_crm(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_people', 'create_person', 'get_companies', 'create_company', 'get_opportunities', 'create_opportunity', 'execute_gql'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Twenty MCP crm operations."""
        if ctx:
            await ctx.info("Executing crm operations...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_people":
            return client.get_people(**kwargs)
        if action == "create_person":
            return client.create_person(**kwargs)
        if action == "get_companies":
            return client.get_companies(**kwargs)
        if action == "create_company":
            return client.create_company(**kwargs)
        if action == "get_opportunities":
            return client.get_opportunities(**kwargs)
        if action == "create_opportunity":
            return client.create_opportunity(**kwargs)
        if action == "execute_gql":
            return client.execute_gql(**kwargs)

        raise ValueError(f"Unknown action: {action}")
