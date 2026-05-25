import sys
import pytest

def test_startup():
    # Basic import test
    import twenty_mcp
    assert twenty_mcp.__version__ == "0.15.0"
