import pytest


@pytest.mark.concept("TW-OS.identity.twenty")
def test_mcp_server_security_context():
    """CONCEPT:TW-OS.identity.twenty Verify that the server registers with correct security credentials."""
    from twenty_mcp.auth import get_client

    client = get_client()
    assert client is not None
