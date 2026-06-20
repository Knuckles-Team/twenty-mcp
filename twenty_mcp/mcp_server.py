"""Main FastMCP server and tool registration."""

import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server, load_config
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from twenty_mcp.mcp.mcp_crm import register_crm_tools

__version__ = "0.15.0"
logger = get_logger(name="twenty_mcp")


def get_mcp_instance() -> tuple[Any, ...]:
    load_config()
    args, mcp, middlewares = create_mcp_server(
        name="Twenty MCP MCP",
        version=__version__,
        instructions="Twenty MCP MCP Server - Managed dynamic operations.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    DEFAULT_CRMTOOL = to_boolean(os.getenv("CRMTOOL", "True"))
    if DEFAULT_CRMTOOL:
        register_crm_tools(mcp)

    DEFAULT_METADATATOOL = to_boolean(os.getenv("METADATATOOL", "True"))
    if DEFAULT_METADATATOOL:
        from twenty_mcp.mcp.mcp_metadata import register_metadata_tools

        register_metadata_tools(mcp)

    DEFAULT_OAUTHTOOL = to_boolean(os.getenv("OAUTHTOOL", "True"))
    if DEFAULT_OAUTHTOOL:
        from twenty_mcp.mcp.mcp_oauth import register_oauth_tools

        register_oauth_tools(mcp)

    DEFAULT_GRAPHQLTOOL = to_boolean(os.getenv("GRAPHQLTOOL", "True"))
    if DEFAULT_GRAPHQLTOOL:
        try:
            from twenty_mcp.mcp.mcp_graphql import register_graphql_tools

            register_graphql_tools(mcp)
        except ImportError as e:
            logger.warning(f"GraphQL tools unavailable (missing 'gql'?): {e}")

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares


def mcp_server() -> None:
    mcp, args, middlewares = get_mcp_instance()
    print(f"Twenty MCP MCP v{__version__}", file=sys.stderr)
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp_server()
