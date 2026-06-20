"""Main FastMCP server and tool registration."""

import sys
from typing import Any

from agent_utilities.mcp_utilities import (
    create_mcp_server,
    load_config,
    register_tool_surface,
)
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from twenty_mcp.api_client import Api
from twenty_mcp.auth import get_client
from twenty_mcp.mcp.mcp_crm import register_crm_tools
from twenty_mcp.mcp.mcp_graphql import register_graphql_tools
from twenty_mcp.mcp.mcp_metadata import register_metadata_tools
from twenty_mcp.mcp.mcp_oauth import register_oauth_tools

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

    register_tool_surface(
        mcp,
        client_cls=Api,
        get_client=get_client,
        service="twenty-mcp",
        registrars=[
            register_crm_tools,
            register_graphql_tools,
            register_metadata_tools,
            register_oauth_tools,
        ],
    )

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
