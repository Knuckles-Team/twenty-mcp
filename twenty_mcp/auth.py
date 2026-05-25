import os
from agent_utilities.base_utilities import get_logger, to_boolean
from twenty_mcp.api_client import Api

logger = get_logger(__name__)

def get_client() -> Api:
    """Get authenticated client for twenty_mcp."""
    base_url = os.getenv("TWENTY_URL") or os.getenv("TWENTY_MCP_BASE_URL", "")
    token = os.getenv("TWENTY_TOKEN", "")
    username = os.getenv("TWENTY_MCP_USERNAME", "")
    password = os.getenv("TWENTY_MCP_PASSWORD", "")
    verify = to_boolean(os.getenv("TWENTY_MCP_SSL_VERIFY", "True"))

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    return Api(base_url=base_url, token=token, username=username, password=password, verify=verify)
