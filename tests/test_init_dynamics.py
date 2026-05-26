import pytest


@pytest.mark.concept("TWENTY-001")
def test_init_dynamics():
    import twenty_mcp

    assert twenty_mcp._MCP_AVAILABLE is True
