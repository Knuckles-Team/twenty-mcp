"""MCP tools for OAuth and Webhooks operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from twenty_mcp.auth import get_client


def register_oauth_tools(mcp: FastMCP):
    """Register Twenty MCP OAuth tools."""

    @mcp.tool(tags={"oauth"})
    async def twenty_mcp_oauth(
        action: str = Field(
            description="Action to perform. e.g. 'register_oauth_client', 'get_oauth_discovery', 'exchange_oauth_token', 'refresh_oauth_token', 'client_credentials_oauth_token', 'validate_webhook_signature'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Twenty MCP OAuth and Webhooks operations."""
        if ctx:
            await ctx.info(f"Executing OAuth operation: {action}...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Special handling for static method 'validate_webhook_signature'
        if action == "validate_webhook_signature":
            try:
                res = client.validate_webhook_signature(**kwargs)
                return {"valid": res}
            except Exception as e:
                return {"error": f"Failed to validate webhook signature: {e}"}

        # Dynamic dispatch
        method = getattr(client, action, None)
        if not method:
            alt_action = action.replace("-", "_").replace(" ", "_").lower()
            method = getattr(client, alt_action, None)

        if not method:
            return {"error": f"Unknown action '{action}' on OAuth client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute OAuth operation {action}: {e}"}
