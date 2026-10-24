"""Main FastMCP server and tool registration."""

from twenty_mcp.mcp.mcp_crm import register_crm_tools
from twenty_mcp.mcp.mcp_graphql import register_graphql_tools
from twenty_mcp.mcp.mcp_ingest import register_ingest_tools
from twenty_mcp.mcp.mcp_metadata import register_metadata_tools
from twenty_mcp.mcp.mcp_oauth import register_oauth_tools

# SDK discovery registers the register_<tag>_tools functions bound in this module.
__all__ = [
    "register_crm_tools",
    "register_graphql_tools",
    "register_ingest_tools",
    "register_metadata_tools",
    "register_oauth_tools",
]
