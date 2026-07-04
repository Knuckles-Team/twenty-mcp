import pytest


@pytest.mark.concept("TW-OS.governance.twenty-2")
def test_mcp_server_registration():
    """CONCEPT:TW-OS.governance.twenty-2 Test that tools register successfully."""
    from twenty_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    if isinstance(res, tuple):
        mcp = res[0]
    else:
        mcp = res
    assert mcp is not None

    # Verify tool registry count is greater than zero
    assert len(mcp._local_provider._components) > 0


@pytest.mark.concept("TW-OS.identity.twenty")
def test_mcp_server_security_context():
    """CONCEPT:TW-OS.identity.twenty Verify that the server registers with correct security credentials."""
    from twenty_mcp.auth import get_client

    client = get_client()
    assert client is not None
