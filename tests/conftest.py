import pytest


@pytest.fixture
def mock_ctx():
    class MockCtx:
        def info(self, msg):
            return None

        def warn(self, msg):
            return None

        def error(self, msg):
            return None

    return MockCtx()
