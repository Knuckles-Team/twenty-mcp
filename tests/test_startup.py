import pytest
@pytest.mark.concept("TWENTY-002")
def test_startup():
    # Basic import test
    import twenty_mcp

    assert twenty_mcp.__version__ == "0.15.0"
